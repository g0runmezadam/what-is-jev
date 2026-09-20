"""Generated pages: determinism, language parity, links, stats, --check."""

import json
import os
import re
import subprocess
import sys
import unittest

from helpers import BaseCase, SOURCES, write, jsonl
from test_schema import base_record

import build


#: A markdown table cell ends at an UNESCAPED pipe. Splitting on every "|"
#: loses any row whose text contains one, which is exactly the row worth
#: checking.
CELL_SPLIT = re.compile(r"(?<!\\)\|")


def split_cells(line):
    return [c.strip() for c in CELL_SPLIT.split(line.strip().strip("|"))]


def sample_records():
    a = base_record()
    a.update(summary_en="Agent gate", summary_tr="Ajan kapisi",
             takeaway_en="Threshold band", takeaway_tr="Esik bandi",
             risk_en="none seen", risk_tr="gorulmedi",
             audited=True, audit_note_en="Confirmed by the second pass",
             audit_note_tr="Ikinci gecis dogruladi", scored_at="2026-09-19")
    b = base_record(repo="b/two", url="https://github.com/b/two",
                    evidence_url="https://github.com/b/two#readme",
                    category="code-review-hook", calls_jev="no",
                    question_types=[], total=5,
                    scores={"depth": 1, "relevance": 1, "novelty": 1,
                            "maturity": 1, "evidence": 1},
                    scored_at="2026-09-18")
    b["class"] = "C"
    c = base_record(repo="c/three", url="https://github.com/c/three",
                    evidence_url="https://github.com/c/three",
                    category="cli", calls_jev="unclear", total=5,
                    scores={"depth": 1, "relevance": 1, "novelty": 1,
                            "maturity": 1, "evidence": 1},
                    duplicate_of="a/one", scored_at="2026-09-17")
    c["class"] = "C"
    return [a, b, c]


class PageTest(BaseCase):
    def pages(self):
        return build.render_all(sample_records(), SOURCES)

    def test_expected_page_set(self):
        pages = self.pages()
        for name in ("SOURCES.md", "REPOS.md", "TOP.md",
                     "categories/agent-gate.md", "categories/code-review-hook.md",
                     "categories/cli.md"):
            self.assertIn(name, pages)
            self.assertIn("tr/" + name, pages)

    def test_language_parity(self):
        self.assertEqual(build.check_language_parity(self.pages()), [])

    def test_missing_translation_page_breaks_parity(self):
        pages = self.pages()
        del pages["tr/TOP.md"]
        self.assertTrue(build.check_language_parity(pages))

    def test_generated_banner_and_language_links(self):
        pages = self.pages()
        self.assertTrue(pages["REPOS.md"].startswith(
            "<!-- GENERATED — do not edit; run tools/build.py -->"))
        self.assertIn("tr/REPOS.md", pages["REPOS.md"].splitlines()[1])
        self.assertIn("../REPOS.md", pages["tr/REPOS.md"].splitlines()[1])
        self.assertIn("../tr/categories/cli.md",
                      pages["categories/cli.md"].splitlines()[1])
        self.assertIn("../../categories/cli.md",
                      pages["tr/categories/cli.md"].splitlines()[1])

    def test_every_repo_row_carries_repo_and_evidence_links(self):
        page = self.pages()["categories/agent-gate.md"]
        self.assertIn("[a/one](https://github.com/a/one)", page)
        self.assertIn("[evidence](https://github.com/a/one#readme)", page)
        self.assertIn("A", page)
        self.assertIn("11", page)
        self.assertIn("yes", page)

    def _assert_every_row_is_linked(self, pages):
        rows = 0
        for name, text in pages.items():
            for line in text.splitlines():
                cells = split_cells(line)
                is_repo_row = (line.startswith("| [") and len(cells) == 7
                               and cells[1] in ("A", "B", "C"))
                if is_repo_row:
                    rows += 1
                    self.assertIn("](https://", line, name + ": " + line)
                    self.assertTrue("[evidence](" in line or "[kanıt](" in line,
                                    name + ": " + line)
                elif line.startswith("| [") or line.startswith("- ["):
                    self.assertIn("](", line, name + ": " + line)
        return rows

    def test_no_row_without_a_link(self):
        """A repository row always carries its repo link and its evidence link."""
        self.assertTrue(self._assert_every_row_is_linked(self.pages()))

    def test_a_summary_containing_a_pipe_is_still_a_recognisable_row(self):
        """The escaped pipe must not make the row look like something else."""
        records = sample_records()
        records[0]["summary_en"] = "routes a | b | c through the gate"
        records[0]["summary_tr"] = "a | b | c yonlendirir"
        pages = build.render_all(records, SOURCES)
        rows = self._assert_every_row_is_linked(pages)
        self.assertEqual(rows, 12)  # 3 repos x (REPOS + category) x 2 languages
        self.assertIn("a \\| b \\| c", pages["categories/agent-gate.md"])

    def test_duplicate_is_out_of_the_counts_but_still_listed(self):
        pages = self.pages()
        self.assertIn("duplicate of [a/one]", pages["categories/cli.md"])
        self.assertIn("duplicate of [a/one]", pages["tr/categories/cli.md"])
        stats = build.stats(sample_records(), SOURCES)
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["duplicates"], 1)

    def test_top_page_lists_only_audited_a_class(self):
        top = self.pages()["TOP.md"]
        self.assertIn("a/one", top)
        self.assertNotIn("b/two", top)

    def test_each_language_shows_its_own_audit_note(self):
        pages = self.pages()
        self.assertIn("Confirmed by the second pass", pages["TOP.md"])
        self.assertNotIn("Ikinci gecis dogruladi", pages["TOP.md"])
        self.assertIn("Ikinci gecis dogruladi", pages["tr/TOP.md"])
        self.assertNotIn("Confirmed by the second pass", pages["tr/TOP.md"])

    def test_sources_page_links_every_source(self):
        page = self.pages()["SOURCES.md"]
        for src in SOURCES:
            self.assertIn("](" + src["url"] + ")", page)

    def test_no_local_path_leaks_into_any_page(self):
        for name, text in self.pages().items():
            self.assertEqual(build.privacy_hits(text), [], name)

    def test_rendering_does_not_depend_on_the_input_order(self):
        """Not "the same call twice": a different order must give the same page."""
        forward = build.render_all(sample_records(), SOURCES)
        backward = build.render_all(list(reversed(sample_records())),
                                    list(reversed(SOURCES)))
        self.assertEqual(sorted(forward), sorted(backward))
        for name in forward:
            self.assertEqual(forward[name], backward[name], name)

    def test_the_untranslated_row_is_hidden_when_nothing_is_untranslated(self):
        records = sample_records()
        for rec in records:
            rec["summary_en"] = rec["summary_en"] or "translated"
        st = build.stats(records, SOURCES)
        self.assertEqual(st["missing_translation"], 0)
        self.assertNotIn("Rows still untranslated", build.stats_block(st, "en"))
        self.assertNotIn("Çevirisi eksik satır", build.stats_block(st, "tr"))

    def test_the_untranslated_row_is_shown_when_a_row_is_untranslated(self):
        records = sample_records()
        records[1]["summary_en"] = ""
        st = build.stats(records, SOURCES)
        self.assertEqual(st["missing_translation"], 1)
        self.assertIn("Rows still untranslated | 1", build.stats_block(st, "en"))
        self.assertIn("Çevirisi eksik satır | 1", build.stats_block(st, "tr"))

    def test_pages_use_lf_endings_and_no_clock(self):
        for name, text in self.pages().items():
            self.assertNotIn("\r", name + text)
        self.assertIn("2026-09-19", self.pages()["REPOS.md"])  # newest scored_at

    def test_stats_numbers(self):
        st = build.stats(sample_records(), SOURCES)
        self.assertEqual(st["calls_jev"], {"yes": 1, "no": 1, "unclear": 0})
        self.assertEqual(st["classes"], {"A": 1, "B": 0, "C": 1})
        self.assertEqual(st["sources"], 2)
        self.assertEqual(st["generated_at"], "2026-09-19")


def top_records():
    """Two rows over the measured bar, two class A rows under it, one duplicate."""
    def a_row(repo, total, scores, category="agent-gate", **kw):
        rec = base_record(repo=repo, url="https://github.com/" + repo,
                          evidence_url="https://github.com/" + repo + "#readme",
                          category=category, scores=scores, total=total,
                          audited=kw.pop("audited", True),
                          summary_en=repo + " summary", summary_tr=repo + " ozet",
                          takeaway_en=repo + " takeaway", takeaway_tr=repo + " fikir",
                          audit_note_en=repo + " note", audit_note_tr=repo + " not",
                          **kw)
        rec["class"] = "A"
        return rec
    full = {"depth": 3, "relevance": 3, "novelty": 3, "maturity": 3, "evidence": 3}
    return [
        # same total as z/core: the tie is broken by the repository name
        a_row("z/core", 14, dict(full, evidence=2)),
        a_row("a/core", 14, dict(full, evidence=2), category="cli"),
        a_row("m/top", 15, full, category="cli"),
        # class A through the second gate (relevance 3, novelty 2), total 8
        a_row("b/wide", 8, {"depth": 0, "relevance": 3, "novelty": 2,
                            "maturity": 2, "evidence": 1}),
        a_row("c/wide", 12, {"depth": 3, "relevance": 3, "novelty": 3,
                             "maturity": 2, "evidence": 1}, category="cli"),
        # audited, class A, over the bar - but a duplicate, so nowhere
        a_row("d/dupe", 14, dict(full, evidence=2), duplicate_of="m/top"),
        # class A but never audited
        a_row("e/raw", 14, dict(full, evidence=2), audited=False),
    ]


class TopPageTest(BaseCase):
    def pages(self):
        return build.render_all(top_records(), SOURCES)

    def core_lines(self, page):
        """The bullet lines of the first section, in page order."""
        out, inside = [], False
        for line in page.splitlines():
            if line.startswith("## "):
                inside = ("Measured core" in line
                          or "Ölçümle desteklenen çekirdek" in line)
            elif inside and line.startswith("- ["):
                out.append(line)
        return out

    def other_lines(self, page):
        out, inside = [], False
        for line in page.splitlines():
            if line.startswith("## "):
                inside = "Other class A" in line or "Diğer A sınıfı" in line
            elif line.startswith("### "):
                pass
            elif inside and line.startswith("- ["):
                out.append(line)
        return out

    def test_the_core_holds_only_audited_class_a_at_thirteen_or_more(self):
        lines = "\n".join(self.core_lines(self.pages()["TOP.md"]))
        for repo in ("m/top", "z/core", "a/core"):
            self.assertIn("[%s]" % repo, lines)
        for repo in ("b/wide", "c/wide", "d/dupe", "e/raw"):
            self.assertNotIn("[%s]" % repo, lines)

    def test_the_core_is_sorted_by_total_then_repository_name(self):
        lines = self.core_lines(self.pages()["TOP.md"])
        self.assertEqual([line.split("]")[0][3:] for line in lines],
                         ["m/top", "a/core", "z/core"])

    def test_the_other_section_holds_the_remaining_audited_class_a(self):
        page = self.pages()["TOP.md"]
        lines = "\n".join(self.other_lines(page))
        for repo in ("b/wide", "c/wide"):
            self.assertIn("[%s]" % repo, lines)
        for repo in ("m/top", "a/core", "z/core", "d/dupe", "e/raw"):
            self.assertNotIn("[%s]" % repo, lines)

    def test_the_other_section_is_grouped_by_category(self):
        page = self.pages()["TOP.md"]
        tail = page[page.index("## Other class A"):]
        self.assertIn("### Agent gates", tail)
        self.assertIn("### Command line tools", tail)
        tr = self.pages()["tr/TOP.md"]
        self.assertIn("### Ajan kapıları", tr[tr.index("## Diğer A sınıfı"):])

    def test_the_page_says_why_the_core_is_kept_apart(self):
        page = self.pages()["TOP.md"]
        self.assertIn("relevance", page)
        self.assertIn("11", page)
        self.assertIn("novelty", page)
        tr = self.pages()["tr/TOP.md"]
        self.assertIn("iki kapı", tr)

    def test_a_row_carries_the_scores_summary_takeaway_note_and_evidence(self):
        line = self.core_lines(self.pages()["TOP.md"])[0]
        self.assertIn("[m/top](https://github.com/m/top)", line)
        self.assertIn("15/15", line)
        self.assertIn("D3 R3 N3 M3 E3", line)
        self.assertIn("m/top summary", line)
        self.assertIn("m/top takeaway", line)
        self.assertIn("m/top note", line)
        self.assertIn("[evidence](https://github.com/m/top#readme)", line)

    def test_the_turkish_row_is_turkish(self):
        line = self.core_lines(self.pages()["tr/TOP.md"])[0]
        self.assertIn("m/top ozet", line)
        self.assertIn("m/top fikir", line)
        self.assertIn("m/top not", line)
        self.assertIn("D3 R3 N3 M3 E3", line)
        self.assertIn("[kanıt](", line)


class StatsBlockTest(BaseCase):
    def test_block_is_filled_between_the_markers(self):
        text = "# T\n\n<!-- STATS:START -->\nold\n<!-- STATS:END -->\n\ntail\n"
        out, changed, found = build.fill_stats(text, "new line")
        self.assertTrue(found)
        self.assertTrue(changed)
        self.assertIn("<!-- STATS:START -->\nnew line\n<!-- STATS:END -->", out)
        self.assertTrue(out.endswith("tail\n"))
        self.assertNotIn("old", out)

    def test_second_fill_is_a_no_op(self):
        text = "<!-- STATS:START -->\nold\n<!-- STATS:END -->\n"
        once, _, _ = build.fill_stats(text, "new line")
        twice, changed, _ = build.fill_stats(once, "new line")
        self.assertEqual(once, twice)
        self.assertFalse(changed)

    def test_missing_markers_leave_the_file_alone(self):
        text = "# handwritten readme\n"
        out, changed, found = build.fill_stats(text, "new line")
        self.assertFalse(found)
        self.assertFalse(changed)
        self.assertEqual(out, text)


class MainTest(BaseCase):
    def root_with_data(self):
        root = self.tmproot()
        write(os.path.join(root, "data", "repos.jsonl"),
              "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n"
                      for r in sample_records()))
        write(os.path.join(root, "data", "sources.jsonl"), jsonl(SOURCES))
        return root

    def test_build_writes_pages_then_check_is_clean(self):
        root = self.root_with_data()
        self.assertEqual(build.main([], root=root), 0)
        self.assertTrue(os.path.exists(os.path.join(root, "REPOS.md")))
        self.assertTrue(os.path.exists(os.path.join(root, "tr", "categories", "cli.md")))
        self.assertEqual(build.main(["--check"], root=root), 0)

    def test_check_fails_and_writes_nothing_when_out_of_sync(self):
        root = self.root_with_data()
        build.main([], root=root)
        path = os.path.join(root, "REPOS.md")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("tampered\n")
        self.assertEqual(build.main(["--check"], root=root), 1)
        with open(path, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "tampered\n")

    def test_check_reports_a_page_that_should_no_longer_exist(self):
        root = self.root_with_data()
        build.main([], root=root)
        stale = os.path.join(root, "categories", "eski.md")
        write(stale, build.BANNER + "\nEnglish | [Türkçe](../tr/categories/eski.md)\n")
        self.assertEqual(build.main(["--check"], root=root), 1)
        # --check writes nothing, so the file is still there afterwards
        self.assertTrue(os.path.exists(stale))

    def test_check_reports_a_turkish_page_whose_english_twin_is_gone(self):
        root = self.root_with_data()
        build.main([], root=root)
        write(os.path.join(root, "tr", "categories", "eski.md"),
              build.BANNER + "\n[English](../../categories/eski.md) | Türkçe\n")
        self.assertEqual(build.main(["--check"], root=root), 1)

    def test_build_deletes_a_page_the_data_no_longer_asks_for(self):
        root = self.root_with_data()
        build.main([], root=root)
        stale = os.path.join(root, "categories", "eski.md")
        write(stale, build.BANNER + "\nold\n")
        self.assertEqual(build.main([], root=root), 0)
        self.assertFalse(os.path.exists(stale))
        self.assertEqual(build.main(["--check"], root=root), 0)

    def test_build_never_deletes_a_file_it_did_not_generate(self):
        root = self.root_with_data()
        build.main([], root=root)
        handwritten = os.path.join(root, "categories", "NOTES.md")
        write(handwritten, "# my own notes\n")
        self.assertEqual(build.main([], root=root), 0)
        self.assertTrue(os.path.exists(handwritten))

    def test_check_counts_a_crlf_only_difference(self):
        root = self.root_with_data()
        build.main([], root=root)
        path = os.path.join(root, "REPOS.md")
        with open(path, encoding="utf-8", newline="") as fh:
            text = fh.read()
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text.replace("\n", "\r\n"))
        self.assertEqual(build.main(["--check"], root=root), 1)

    def test_rebuild_is_byte_identical(self):
        root = self.root_with_data()
        build.main([], root=root)
        with open(os.path.join(root, "REPOS.md"), "rb") as fh:
            first = fh.read()
        build.main([], root=root)
        with open(os.path.join(root, "REPOS.md"), "rb") as fh:
            self.assertEqual(fh.read(), first)
        self.assertNotIn(b"\r\n", first)

    def test_a_separate_process_writes_the_same_bytes(self):
        """Determinism across processes, with the hash seed deliberately moved."""
        root = self.root_with_data()
        first = self._run_build_in_a_subprocess(root, "0")
        second = self._run_build_in_a_subprocess(root, "12345")
        self.assertTrue(first)
        self.assertEqual(first, second)

    def _run_build_in_a_subprocess(self, root, hashseed):
        script = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "tools", "build.py")
        env = dict(os.environ, PYTHONHASHSEED=hashseed)
        proc = subprocess.run([sys.executable, script, "--root", root],
                              env=env, capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        blobs = {}
        for name in sorted(build.discover_generated(root)):
            with open(os.path.join(root, *name.split("/")), "rb") as fh:
                blobs[name] = fh.read()
        return blobs

    def test_readme_stats_marker_is_filled_when_present(self):
        root = self.root_with_data()
        write(os.path.join(root, "README.md"),
              "# R\n\n<!-- STATS:START -->\n<!-- STATS:END -->\n")
        build.main([], root=root)
        with open(os.path.join(root, "README.md"), encoding="utf-8") as fh:
            text = fh.read()
        self.assertIn("2", text)
        self.assertNotIn("<!-- STATS:START -->\n<!-- STATS:END -->", text)

    def test_readme_without_marker_is_untouched(self):
        root = self.root_with_data()
        readme = os.path.join(root, "README.md")
        write(readme, "# handwritten\n")
        build.main([], root=root)
        with open(readme, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "# handwritten\n")

    def test_import_legacy_flag_writes_repos_jsonl(self):
        from helpers import make_legacy
        root = self.tmproot()
        make_legacy(root)
        write(os.path.join(root, "data", "sources.jsonl"), jsonl(SOURCES))
        self.assertEqual(build.main(["--import-legacy"], root=root), 0)
        path = os.path.join(root, "data", "repos.jsonl")
        with open(path, encoding="utf-8") as fh:
            rows = [json.loads(line) for line in fh if line.strip()]
        self.assertEqual(len(rows), 5)

    def test_a_half_written_incoming_file_fails_the_build(self):
        root = self.root_with_data()
        write(os.path.join(root, "data", "incoming", "batch-1.jsonl"),
              '{"repo":"n/new",\n')
        self.assertEqual(build.main([], root=root), 1)

    def test_strict_fails_on_missing_translations(self):
        from helpers import make_legacy
        root = self.tmproot()
        make_legacy(root)
        write(os.path.join(root, "data", "sources.jsonl"), jsonl(SOURCES))
        self.assertEqual(build.main(["--import-legacy", "--strict"], root=root), 1)


if __name__ == "__main__":
    unittest.main()
