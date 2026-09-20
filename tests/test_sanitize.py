"""Third-party text is cleaned before it enters the data.

A GitHub description, a topic, a licence name and a language name are written
by somebody else. `tools/build.py` refuses markup and private data in the
data file - so `tools/update.py` must not be able to produce it. These tests
hold the two ends together: whatever the cleaner returns passes the build.
"""

import json
import os
import unittest

from helpers import BaseCase, write
from test_schema import base_record
from test_update import FakeGh, gh_meta

import build
import update


#: Descriptions a real repository could carry, and a few nobody should.
HOSTILE = [
    "An AI moderation workflow powered by the [TypeSafe/Jev model](https://typesafe.ai).",
    "![screenshot](https://example.org/a.png) a gate",
    "[a](b) [c](d) [e](f)",
    "foo](bar",
    "](",
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "<b>[a](https://x.example)</b>",
    "javascript:alert(1)",
    "DATA:text/html;base64,AAAA",
    "line one\nline two\r\nline three",
    "tab\tseparated\x00and\x1fcontrol",
    "x" * 5000,
    "write to me: someone@example.com",
    "notes in C:\\Users\\somebody\\secret\\notes.md",
    "see /home/somebody/jev/run.sh",
    "see /mnt/d/jev/run.sh",
    "server at 192.168.0.10 and 10.0.0.4",
    "copy of ham/readme/a@one.md",
    "",
    # the auditor's own two inputs, and the rest of the family
    "\\\\PRIVATE-SERVER\\share\\alice\\secret.txt",
    "/Users/alice/private/notes.md",
    "run from ~alice/bin/deploy.sh",
    "key in /root/.ssh/id_rsa",
    "log at /var/log/private/app.log",
    "config in /etc/jev/private.conf",
    "open file:///Users/alice/private/notes.md",
    "FILE://PRIVATE-SERVER/share/alice",
]

#: Text that merely looks like a path and is nobody's machine. A pattern that
#: fires on any of these would stop the build on the real data.
NOT_A_LOCAL_PATH = [
    "https://example.org/Users/alice",
    "https://github.com/a/one",
    "see the /etc section of the manual",
    "owner/name",
    "read and/or write",
    "released 2026/09",
    "lib/utils/helper.js",
    "a ~/Downloads folder that sorts itself",
    "the key sits in ~/.config/commentlint/key.txt",
    "profile: /var",
    "a profile file, not a scheme",
]


class CleanThirdPartyTest(BaseCase):
    def test_a_markdown_link_keeps_its_label_and_loses_its_target(self):
        text, _notes = build.clean_third_party("powered by [the Jev model](https://typesafe.ai).")
        self.assertEqual(text, "powered by the Jev model.")

    def test_an_image_is_reduced_to_its_alt_text(self):
        text, _notes = build.clean_third_party("![screenshot](https://example.org/a.png) gate")
        self.assertEqual(text, "screenshot gate")

    def test_a_nested_link_is_reduced_too(self):
        text, _notes = build.clean_third_party("<b>[a](https://x.example)</b>")
        self.assertEqual(text, "a")

    def test_html_tags_are_dropped(self):
        text, _notes = build.clean_third_party("a <script>alert(1)</script> gate")
        self.assertNotIn("<", text)
        self.assertNotIn(">", text)

    def test_javascript_and_data_schemes_are_dropped(self):
        for value in ("javascript:alert(1)", "DATA:text/html;base64,AAAA"):
            text, _notes = build.clean_third_party(value)
            self.assertNotIn("javascript", text.lower())
            self.assertNotIn("data:", text.lower())

    def test_newlines_and_control_characters_become_one_space(self):
        text, _notes = build.clean_third_party("line one\n\nline two\r\nthree\tfour\x00five")
        self.assertEqual(text, "line one line two three four five")

    def test_overlong_text_is_cut_and_says_so(self):
        text, notes = build.clean_third_party("x " * 4000)
        self.assertLessEqual(len(text), build.THIRD_PARTY_LIMIT + 2)
        self.assertTrue(text.endswith("…"), text[-10:])
        self.assertIn("kısaltıldı", notes)

    def test_a_short_text_is_left_alone(self):
        text, notes = build.clean_third_party("A small router for Jev calls")
        self.assertEqual(text, "A small router for Jev calls")
        self.assertEqual(notes, [])

    def test_none_stays_none_and_a_non_string_becomes_none(self):
        self.assertEqual(build.clean_third_party(None), (None, []))
        self.assertEqual(build.clean_third_party(17), (None, []))

    def test_private_data_is_redacted_and_the_note_says_what_it_was(self):
        text, notes = build.clean_third_party("write to me: someone@example.com")
        self.assertNotIn("someone@example.com", text)
        self.assertIn("[redacted]", text)
        self.assertIn("e-posta adresi", notes)

    def test_a_local_path_is_redacted_whole_not_only_its_head(self):
        text, _notes = build.clean_third_party("notes in C:\\Users\\somebody\\secret.md")
        self.assertNotIn("somebody", text)
        self.assertNotIn("secret", text)

    def test_a_unc_share_is_caught_and_redacted_whole(self):
        raw = "notes on \\\\PRIVATE-SERVER\\share\\alice\\secret.txt"
        self.assertTrue(build.privacy_hits(raw), raw)
        text, notes = build.clean_third_party(raw)
        self.assertNotIn("PRIVATE-SERVER", text)
        self.assertNotIn("alice", text)
        self.assertNotIn("secret", text)
        self.assertIn("[redacted]", text)
        self.assertTrue(notes)

    def test_a_mac_home_directory_is_caught_and_redacted_whole(self):
        raw = "see /Users/alice/private/notes.md"
        self.assertTrue(build.privacy_hits(raw), raw)
        text, _notes = build.clean_third_party(raw)
        self.assertNotIn("alice", text)
        self.assertNotIn("notes.md", text)

    def test_a_named_tilde_home_is_caught(self):
        self.assertTrue(build.privacy_hits("run ~alice/bin/deploy.sh"))
        text, _notes = build.clean_third_party("run ~alice/bin/deploy.sh")
        self.assertNotIn("alice", text)

    def test_an_absolute_system_path_is_caught(self):
        for raw in ("/root/.ssh/id_rsa", "/var/log/private/app.log",
                    "/etc/jev/private.conf", "/opt/jev/secret",
                    "/srv/jev/secret"):
            self.assertTrue(build.privacy_hits(raw), raw)

    def test_a_file_url_is_caught_in_either_casing(self):
        for raw in ("open file:///Users/alice/notes.md",
                    "FILE://PRIVATE-SERVER/share"):
            self.assertTrue(build.privacy_hits(raw), raw)
            text, _notes = build.clean_third_party(raw)
            self.assertNotIn("file:", text.lower())

    def test_text_that_only_looks_like_a_path_is_left_alone(self):
        """The narrowness is the point: no false positive, no stopped build."""
        for clean in NOT_A_LOCAL_PATH:
            self.assertEqual(build.privacy_hits(clean), [], clean)
            text, notes = build.clean_third_party(clean)
            self.assertEqual(text, clean, notes)

    def test_every_privacy_pattern_has_a_redaction_pattern(self):
        self.assertEqual(sorted(l for l, _p in build.PRIVACY_PATTERNS),
                         sorted(l for l, _p in build.REDACT_PATTERNS))

    def test_whatever_it_returns_passes_the_build(self):
        """The property that matters: cleaned text never fails validation."""
        for value in HOSTILE:
            text, _notes = build.clean_third_party(value)
            self.assertEqual(build.privacy_hits(text), [], value)
            rec = base_record()
            rec["meta"]["description"] = text
            rec["summary_tr"] = text
            rec["takeaway_tr"] = text
            rec["risk_tr"] = text
            errors, _warnings = build.validate([rec])
            self.assertEqual(errors, [], "%r -> %r" % (value, text))


class UpdateCleansThirdPartyTest(BaseCase):
    def root_with(self, records):
        root = self.tmproot()
        write(os.path.join(root, "data", "repos.jsonl"),
              "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n"
                      for r in records))
        return root

    @staticmethod
    def rows(root):
        with open(os.path.join(root, "data", "repos.jsonl"), encoding="utf-8") as fh:
            return [json.loads(l) for l in fh if l.strip()]

    def test_a_refreshed_markdown_description_does_not_break_the_build(self):
        """The real failure: JularDepick/Jev-Examiner's own GitHub text."""
        root = self.root_with([base_record()])
        gh = FakeGh(search=[], meta={"a/one": gh_meta(
            "a/one",
            description="An AI content moderation workflow powered by "
                        "the [TypeSafe/Jev model](https://typesafe.ai).")})
        update.run(root, runner=gh)
        rows = self.rows(root)
        self.assertNotIn("](", rows[0]["meta"]["description"])
        errors, _warnings = build.validate(rows)
        self.assertEqual(errors, [])

    def test_topics_language_and_license_are_cleaned_too(self):
        root = self.root_with([base_record()])
        gh = FakeGh(search=[], meta={"a/one": gh_meta(
            "a/one", topics=["jev", "[x](https://y)", "<b>b</b>", 3],
            language="<i>Python</i>", license={"spdx_id": "MIT](x"})})
        update.run(root, runner=gh)
        meta = self.rows(root)[0]["meta"]
        self.assertEqual(meta["topics"], ["jev", "x", "b"])
        self.assertEqual(meta["language"], "Python")
        self.assertNotIn("](", meta["license"])
        errors, _warnings = build.validate(self.rows(root))
        self.assertEqual(errors, [])

    def test_ham_meta_carries_the_clean_text_and_keeps_the_raw_one(self):
        root = self.root_with([base_record()])
        raw = "gate [see](https://typesafe.ai)"
        gh = FakeGh(search=["n/new"],
                    meta={"n/new": gh_meta("n/new", description=raw),
                          "a/one": gh_meta("a/one")})
        update.run(root, runner=gh)
        with open(os.path.join(root, "ham", "meta", "n@new.json"), encoding="utf-8") as fh:
            payload = json.load(fh)
        self.assertEqual(payload["description"], "gate see")
        self.assertEqual(payload["description_raw"], raw)

    def test_an_email_is_redacted_and_the_report_names_the_repository(self):
        root = self.root_with([base_record()])
        gh = FakeGh(search=[], meta={"a/one": gh_meta(
            "a/one", description="ask someone@example.com")})
        report = update.run(root, runner=gh)
        self.assertNotIn("someone@example.com", self.rows(root)[0]["meta"]["description"])
        self.assertTrue(any("a/one" in line and "e-posta" in line
                            for line in report["redacted"]), report["redacted"])
        self.assertEqual(report["invalid"], [])

    def test_a_repos_file_the_build_would_reject_is_never_written(self):
        root = self.root_with([base_record(total=12)])
        before = build.read_bytes(os.path.join(root, "data", "repos.jsonl"))
        gh = FakeGh(search=[], meta={"a/one": gh_meta("a/one")})
        report = update.run(root, runner=gh)
        self.assertTrue(report["invalid"])
        self.assertTrue(any("total" in e for e in report["invalid"]))
        self.assertEqual(build.read_bytes(os.path.join(root, "data", "repos.jsonl")), before)
        self.assertFalse(os.path.exists(os.path.join(root, "data", "repos.jsonl.tmp")))

    def test_an_invalid_result_exits_1(self):
        root = self.root_with([base_record(total=12)])
        gh = FakeGh(search=[], meta={"a/one": gh_meta("a/one")})
        self.assertEqual(update.main([], root=root, runner=gh), 1)

    def test_a_clean_run_still_writes_and_exits_0(self):
        root = self.root_with([base_record()])
        gh = FakeGh(search=[], meta={"a/one": gh_meta("a/one", stargazers_count=99)})
        self.assertEqual(update.main([], root=root, runner=gh), 0)
        self.assertEqual(self.rows(root)[0]["meta"]["stars"], 99)


if __name__ == "__main__":
    unittest.main()
