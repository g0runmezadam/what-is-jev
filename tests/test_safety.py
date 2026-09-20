"""The repository is public: nothing hostile and nothing private may escape.

Two separate promises are tested here.

1. Text that came from somebody else's README appears on the generated page as
   PLAIN TEXT. No HTML tag, no markdown image or link, no tracking pixel.
   ``validate()`` refuses such text outright so the data file stays clean too.
2. No local path, private address or e-mail address reaches the data file, a
   generated page, or a handwritten document.
"""

import hashlib
import os
import re
import subprocess
import unittest

from helpers import BaseCase, SOURCES, write, jsonl
from test_schema import base_record

import build


# The auditor's own payloads, verbatim.
HOSTILE_SUMMARY = ("<script>alert(1)</script> ![](http://tracker.invalid/p) "
                   "[x](javascript:alert(1))")
HOSTILE_URL = "https://github.com/a/one) [x](javascript:alert(1))"
HOSTILE_EVIDENCE = "https://example.invalid/a\nBROKEN"


class EscapeTest(BaseCase):
    def test_active_markup_is_neutralised_in_a_table_cell(self):
        out = build._esc(HOSTILE_SUMMARY)
        self.assertNotIn("<script>", out)
        self.assertNotIn("![](", out)
        self.assertNotIn("](", out)
        for ch in ("[", "]", "(", ")"):
            self.assertNotIn(ch + "", out.replace("\\" + ch, ""))
        # information is escaped, never deleted
        self.assertIn("alert", out)
        self.assertIn("tracker.invalid/p", out)

    def test_pipes_newlines_and_backslashes_cannot_break_the_table(self):
        out = build._esc("a | b\nc\r\nd \\ e")
        self.assertNotIn("\n", out)
        self.assertNotIn("\r", out)
        # no pipe survives unescaped, so the cell stays one cell
        self.assertIsNone(re.search(r"(?<!\\)\|", out), out)
        self.assertIn("\\|", out)
        self.assertIn("\\\\", out)

    def test_backticks_survive(self):
        self.assertIn("`code`", build._esc("uses `code` here"))

    def test_angle_brackets_become_entities(self):
        out = build._esc("a <b> c")
        self.assertNotIn("<b>", out)
        self.assertIn("&lt;", out)
        self.assertIn("&gt;", out)

    def test_a_hostile_summary_reaches_the_page_inert(self):
        rec = base_record(summary_en=HOSTILE_SUMMARY, summary_tr=HOSTILE_SUMMARY,
                          takeaway_en=HOSTILE_SUMMARY, takeaway_tr=HOSTILE_SUMMARY,
                          audited=True)
        for name, text in build.render_all([rec], SOURCES).items():
            self.assertNotIn("<script>", text, name)
            # no unescaped link or image syntax survives anywhere in the page
            self.assertIsNone(re.search(r"!\[[^\]]*\]\(", text), name)
            self.assertIsNone(re.search(r"(?<!\\)\(javascript:", text), name)
            self.assertIsNone(re.search(r"(?<!\\)\(http://tracker\.invalid", text),
                              name)


class TextValidationTest(BaseCase):
    def _errors(self, **kw):
        errors, _ = build.validate([base_record(**kw)], SOURCES)
        return errors

    def test_html_tag_in_a_text_field_is_an_error(self):
        self.assertTrue(any("summary_en" in e for e in
                            self._errors(summary_en="<script>alert(1)</script>")))

    def test_markdown_link_syntax_in_a_text_field_is_an_error(self):
        self.assertTrue(any("takeaway_tr" in e for e in
                            self._errors(takeaway_tr="bak [buraya](http://x.invalid)")))

    def test_javascript_and_data_urls_in_a_text_field_are_errors(self):
        self.assertTrue(any("risk_en" in e for e in
                            self._errors(risk_en="javascript:alert(1)")))
        self.assertTrue(any("audit_note_en" in e for e in
                            self._errors(audit_note_en="data:text/html;base64,AAAA")))

    def test_both_audit_notes_are_validated(self):
        self.assertTrue(any("audit_note_tr" in e for e in
                            self._errors(audit_note_tr="bak [buraya](http://x.invalid)")))
        self.assertTrue(any("audit_note_en" in e for e in
                            self._errors(audit_note_en="<b>hi</b>")))

    def test_description_is_checked_too(self):
        rec = base_record()
        rec["meta"] = dict(rec["meta"], description="<img src=x onerror=1>")
        errors, _ = build.validate([rec], SOURCES)
        self.assertTrue(any("description" in e for e in errors))

    def test_clean_text_still_passes(self):
        self.assertEqual(self._errors(summary_en="A gate that uses `jev` for triage."),
                         [])


class UrlValidationTest(BaseCase):
    def _errors(self, **kw):
        errors, _ = build.validate([base_record(**kw)], SOURCES)
        return errors

    def test_url_with_a_markdown_tail_is_an_error(self):
        self.assertTrue(any("url" in e for e in self._errors(url=HOSTILE_URL)))

    def test_evidence_url_with_a_newline_is_an_error(self):
        self.assertTrue(any("evidence_url" in e for e in
                            self._errors(evidence_url=HOSTILE_EVIDENCE)))

    def test_url_must_be_exactly_a_github_repository(self):
        for bad in ("https://github.com/a/one/tree/main",
                    "https://github.com/a",
                    "https://gitlab.com/a/one",
                    "https://github.com/a/one?x=1"):
            self.assertTrue(any("url" in e for e in self._errors(url=bad)), bad)
        self.assertEqual(self._errors(url="https://github.com/a/one"), [])

    def test_evidence_url_may_be_any_strict_http_url(self):
        self.assertEqual(
            self._errors(evidence_url="https://example.org/a/b?c=d#readme"), [])

    def test_source_url_is_strict_too(self):
        bad = dict(SOURCES[0], url="https://x.invalid/a b")
        errors, _ = build.validate([base_record()], [bad])
        self.assertTrue(any("url" in e for e in errors))

    def test_a_url_is_percent_encoded_on_the_page(self):
        self.assertEqual(build._url("https://example.org/a b"),
                         "https://example.org/a%20b")
        self.assertEqual(build._url("https://example.org/a(b)"),
                         "https://example.org/a%28b%29")
        # an already encoded url is not encoded twice
        self.assertEqual(build._url("https://example.org/a%20b"),
                         "https://example.org/a%20b")

    def test_import_drops_a_tail_it_can_clean_and_falls_back_otherwise(self):
        self.assertEqual(
            build.normalize_evidence_url("https://example.org/a (docs/X.md)",
                                         "https://github.com/a/one"),
            "https://example.org/a")
        # a tail that cannot be cleaned away: fall back to the repository url
        self.assertEqual(
            build.normalize_evidence_url(HOSTILE_URL, "https://github.com/a/one"),
            "https://github.com/a/one")


class PrivacyPatternTest(BaseCase):
    def test_every_pattern_catches_its_leak(self):
        for leak in (r"C:\Projects\notes", "C:/Users/alice", "../ham/readme/a@b.md",
                     "ham/readme/a@b.md", "/home/alice/x", "/mnt/d/notes",
                     "10.0.0.5", "172.16.0.4", "192.168.0.10",
                     "someone@example.com", "noreply@example.net"):
            self.assertTrue(build.privacy_hits(leak), leak)

    def test_clean_text_is_left_alone(self):
        for clean in ("https://github.com/a/one#readme", "http://x.dev/ham",
                      "[Türkçe](tr/REPOS.md)", "chamber of things",
                      "8.8.8.8", "172.15.0.1", "ham/  (git-ignored)",
                      "the @mention of a user"):
            self.assertEqual(build.privacy_hits(clean), [], clean)


class PrivacyScanTest(BaseCase):
    def root_with(self, records):
        root = self.tmproot()
        write(os.path.join(root, "data", "repos.jsonl"), jsonl(records))
        write(os.path.join(root, "data", "sources.jsonl"), jsonl(SOURCES))
        return root

    def test_a_local_path_in_the_data_file_stops_the_build(self):
        root = self.root_with([base_record(takeaway_tr=r"C:\Projects dizinine bak")])
        self.assertEqual(build.main([], root=root), 1)
        self.assertFalse(os.path.exists(os.path.join(root, "REPOS.md")))

    def test_the_error_names_the_repository_and_the_field(self):
        root = self.root_with([base_record(takeaway_tr=r"C:\Projects dizinine bak")])
        problems = build.scan_privacy(root, build.read_jsonl(
            os.path.join(root, "data", "repos.jsonl"))[0], {})
        self.assertTrue(any("a/one" in p and "takeaway_tr" in p for p in problems),
                        problems)

    def test_a_local_path_in_either_audit_note_stops_the_build(self):
        for field in ("audit_note_tr", "audit_note_en"):
            root = self.root_with([base_record(**{field: r"bak C:\Projects\notes"})])
            self.assertEqual(build.main([], root=root), 1, field)

    def test_an_e_mail_address_in_the_data_file_stops_the_build(self):
        root = self.root_with([base_record(summary_tr="yaz: someone@example.com")])
        self.assertEqual(build.main([], root=root), 1)

    def test_a_handwritten_document_is_scanned_and_named(self):
        root = self.root_with([base_record()])
        write(os.path.join(root, "FINDINGS.md"), "bak /mnt/d/notes/dizin\n")
        problems = build.scan_privacy(root, [], {})
        self.assertTrue(any("FINDINGS.md:1" in p for p in problems), problems)

    def test_a_generated_page_is_scanned(self):
        problems = build.scan_privacy(self.root_with([base_record()]), [],
                                      {"REPOS.md": "x\nsee C:/Users/alice\n"})
        self.assertTrue(any("REPOS.md:2" in p for p in problems), problems)

    def test_the_clean_tree_has_no_finding(self):
        root = self.root_with([base_record()])
        self.assertEqual(build.main([], root=root), 0)


#: Tokens that must never appear in a tracked file; stored as digests so the
#: list itself reveals nothing. A file is split into words and every word is
#: hashed twice, as written and lower-cased; a hit is a hash found in this set.
#: So a token is matched as a whole word only, a longer word that merely
#: contains it passes, an entry stored lower-cased matches any casing, and an
#: entry stored with a capital matches that casing alone - which is how a token
#: that doubles as an ordinary word is kept apart from the ordinary word. For an
#: IPv4 address the first three octets are hashed as well, which catches a /24
#: prefix without the list naming it.
FORBIDDEN_DIGESTS = frozenset([
    "00fc4690c4173e95f1fd45f5131f0bfd5a9a3f2a457f6bead8eda6eb9467cf19",
    "b40b7dca347bc75e04be1ff95b78ae2ea2f4a799429b2d133596c42ab5b9bca1",
    "b8bd87578a2f82ed8ad7077357e905b8474c25a6b42fa350e96954365eeb51d9",
    "178e3b1a9a65e317e5f8a02a4c0e59cfe62ff60c6e751cd40e5b174c337a8a06",
    "170436c304cbae8b6990fda1205074891a0883a47fc64c128e326bfd8e9a5a8d",
    "261b835b5c5f0e9613532de868f6308dff9060aeebf19f8ed0173fd46191502b",
])

WORD = re.compile(r"[A-Za-z0-9]+")
IPV4 = re.compile(r"(?<![0-9.])([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\.[0-9]{1,3}(?![0-9.])")


def sha256_token(token):
    """The digest of one token, exactly as it is written."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def token_digests(token):
    """The digest of a token as written and of its lower-cased form."""
    return {sha256_token(token), sha256_token(token.lower())}


def line_tokens(line):
    """Every word of a line, plus the /24 prefix of every IPv4 address in it."""
    tokens = set(WORD.findall(line))
    tokens.update(IPV4.findall(line))
    return tokens


def scan_files(root, names, digests):
    """Report ``name:line`` for every file whose text carries a listed token.

    Binary files are skipped. The report names the digest, never the token, so
    a failing run still does not print the thing it protects.
    """
    found = []
    for name in names:
        path = os.path.join(root, *name.split("/"))
        if not os.path.isfile(path):
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                lines = fh.readlines()
        except (UnicodeDecodeError, OSError):
            continue
        for number, line in enumerate(lines, 1):
            for token in line_tokens(line):
                for digest in sorted(token_digests(token) & set(digests)):
                    found.append("%s:%d: yasaklı dizge (%s…)"
                                 % (name, number, digest[:8]))
    return found


class TokenScanTest(BaseCase):
    """The scanner is proved with a throw-away token, never with a real one."""

    SECRET = "examplesecret"
    PREFIX = "203.0.113"

    def digests(self, *tokens):
        return {sha256_token(t) for t in tokens}

    def write_tree(self, files):
        root = self.tmproot()
        for name, text in files.items():
            write(os.path.join(root, name), text)
        return root

    def test_a_forbidden_token_is_found_with_its_file_and_line(self):
        root = self.write_tree({"a.md": "clean line\nhere is EXAMPLESECRET in text\n"})
        hits = scan_files(root, ["a.md"], self.digests(self.SECRET))
        self.assertEqual(len(hits), 1, hits)
        self.assertIn("a.md:2", hits[0])
        # the report names the digest, never the token itself
        self.assertNotIn(self.SECRET, hits[0].lower())

    def test_a_token_glued_by_a_separator_is_still_found(self):
        root = self.write_tree({"b.md": "path/examplesecret_Dir/x-examplesecret.txt\n"})
        self.assertTrue(scan_files(root, ["b.md"], self.digests(self.SECRET)))

    def test_an_entry_stored_with_a_capital_matches_that_casing_alone(self):
        digests = self.digests("Examplesecret")
        root = self.write_tree({"h.md": "Examplesecret here\n",
                                "i.md": "examplesecret here\n"})
        self.assertTrue(scan_files(root, ["h.md"], digests))
        self.assertEqual(scan_files(root, ["i.md"], digests), [])

    def test_a_neutral_file_has_no_hit(self):
        root = self.write_tree({"c.md": "an ordinary sentence with examples and secrets\n"})
        self.assertEqual(scan_files(root, ["c.md"], self.digests(self.SECRET)), [])

    def test_a_longer_name_that_merely_starts_with_the_token_passes(self):
        root = self.write_tree({"d.md": "examplesecret123 is a different word\n"})
        self.assertEqual(scan_files(root, ["d.md"], self.digests(self.SECRET)), [])

    def test_the_slash_24_prefix_of_an_address_is_found(self):
        root = self.write_tree({"e.md": "reach it at 203.0.113.42 today\n"})
        hits = scan_files(root, ["e.md"], self.digests(self.PREFIX))
        self.assertTrue(hits, hits)
        self.assertIn("e.md:1", hits[0])

    def test_another_address_in_the_same_shape_passes(self):
        root = self.write_tree({"f.md": "reach it at 198.51.100.42 today\n"})
        self.assertEqual(scan_files(root, ["f.md"], self.digests(self.PREFIX)), [])

    def test_a_binary_file_is_skipped_instead_of_crashing(self):
        root = self.tmproot()
        path = os.path.join(root, "g.bin")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(b"\x00\xff\xfe binary \x00")
        self.assertEqual(scan_files(root, ["g.bin"], self.digests(self.SECRET)), [])


class TrackedTreeTest(BaseCase):
    """Not one tracked file may carry a name from the author's own estate."""

    def tracked(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        try:
            raw = subprocess.run(["git", "-C", root, "ls-files", "-z"],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.DEVNULL,
                                 check=True).stdout
        except (OSError, subprocess.SubprocessError):
            self.skipTest("git ls-files çalıştırılamadı")
        return root, [name for name in raw.decode("utf-8").split("\0") if name]

    def test_no_tracked_file_names_the_authors_own_machine(self):
        root, names = self.tracked()
        self.assertTrue(names, "izlenen dosya bulunamadı")
        found = scan_files(root, names, FORBIDDEN_DIGESTS)
        self.assertEqual(found, [], "\n".join(found))


if __name__ == "__main__":
    unittest.main()
