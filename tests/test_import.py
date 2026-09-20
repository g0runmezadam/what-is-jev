"""Legacy import: last file wins, broken lines, mappings, audit, translations."""

import os
import unittest

from helpers import (BaseCase, LOST_LINE, add_audit, add_audit_notes, add_notr,
                     add_translations, break_last_line, make_legacy, write,
                     jsonl, legacy_row)

import build


class ImportTest(BaseCase):
    def imported(self, with_audit=False, with_tr=False, with_notr=False,
                 with_notes=False):
        root = self.tmproot()
        make_legacy(root)
        if with_audit:
            add_audit(root)
        if with_notes:
            add_audit_notes(root)
        if with_tr:
            add_translations(root)
        if with_notr:
            add_notr(root)
        records, report = build.import_legacy(root)
        return root, {r["repo"]: r for r in records}, report

    def test_last_file_wins(self):
        _, by_repo, _ = self.imported()
        self.assertEqual(by_repo["a/one"]["total"], 9)
        self.assertEqual(by_repo["a/one"]["class"], "B")

    def test_broken_legacy_line_is_tolerated_when_the_repo_is_sound_elsewhere(self):
        _, by_repo, report = self.imported()
        self.assertEqual(report["skipped"], 1)
        self.assertTrue(any("sonuc-00.jsonl" in d for d in report["skipped_detail"]))
        # the repository itself is not lost: the other file carries it
        self.assertIn("x/broken", by_repo)
        self.assertEqual(report["fatal"], [])

    def test_broken_legacy_line_is_fatal_when_the_repo_is_lost(self):
        root = self.tmproot()
        make_legacy(root)
        path = os.path.join(root, "repo-analizi", "sonuc-02.jsonl")
        write(path, LOST_LINE)
        records, report = build.import_legacy(root)
        self.assertNotIn("z/lost", {r["repo"] for r in records})
        self.assertTrue(any("z/lost" in f for f in report["fatal"]), report["fatal"])

    def test_a_broken_line_without_a_readable_repo_is_fatal(self):
        root = self.tmproot()
        make_legacy(root)
        write(os.path.join(root, "repo-analizi", "sonuc-02.jsonl"), "{oops\n")
        _records, report = build.import_legacy(root)
        self.assertTrue(any("sonuc-02.jsonl" in f for f in report["fatal"]),
                        report["fatal"])

    def test_a_half_written_audit_file_is_fatal(self):
        root = self.tmproot()
        make_legacy(root)
        add_audit(root)
        break_last_line(os.path.join(root, "repo-analizi", "A-denetim.jsonl"))
        _records, report = build.import_legacy(root)
        self.assertTrue(any("A-denetim.jsonl" in f for f in report["fatal"]),
                        report["fatal"])

    def test_a_half_written_translation_file_is_fatal(self):
        root = self.tmproot()
        make_legacy(root)
        add_translations(root)
        break_last_line(os.path.join(root, "repo-analizi", "ceviri-0.jsonl"))
        _records, report = build.import_legacy(root)
        self.assertTrue(any("ceviri-0.jsonl" in f for f in report["fatal"]),
                        report["fatal"])

    def test_a_half_written_notr_file_is_fatal(self):
        root = self.tmproot()
        make_legacy(root)
        add_notr(root)
        break_last_line(os.path.join(root, "repo-analizi", "notr-en.jsonl"))
        _records, report = build.import_legacy(root)
        self.assertTrue(any("notr-en.jsonl" in f for f in report["fatal"]),
                        report["fatal"])

    def test_a_fatal_import_line_fails_the_build(self):
        from helpers import SOURCES
        root = self.tmproot()
        make_legacy(root)
        write(os.path.join(root, "data", "sources.jsonl"), jsonl(SOURCES))
        write(os.path.join(root, "repo-analizi", "sonuc-02.jsonl"), LOST_LINE)
        self.assertEqual(build.main(["--import-legacy"], root=root), 1)

    def test_category_and_value_mapping(self):
        _, by_repo, _ = self.imported()
        self.assertEqual(by_repo["a/one"]["category"], "agent-gate")
        self.assertEqual(by_repo["b/two"]["category"], "code-review-hook")
        self.assertEqual(by_repo["a/one"]["calls_jev"], "yes")
        self.assertEqual(by_repo["b/two"]["calls_jev"], "no")
        self.assertEqual(by_repo["c/three"]["calls_jev"], "unclear")

    def test_scores_renamed(self):
        _, by_repo, _ = self.imported()
        s = by_repo["a/one"]["scores"]
        self.assertEqual(
            s, {"depth": 2, "relevance": 2, "novelty": 2, "maturity": 2, "evidence": 1})

    def test_evidence_url_readme_becomes_github_anchor(self):
        _, by_repo, _ = self.imported()
        self.assertEqual(by_repo["a/one"]["evidence_url"],
                         "https://github.com/a/one#readme")

    def test_evidence_url_dotdot_ham_path_with_note(self):
        _, by_repo, _ = self.imported()
        self.assertEqual(by_repo["b/two"]["evidence_url"],
                         "https://github.com/b/two#readme")

    def test_evidence_url_non_http_falls_back_to_repo_url(self):
        _, by_repo, _ = self.imported()
        self.assertEqual(by_repo["c/three"]["evidence_url"],
                         "https://github.com/c/three")

    def test_evidence_url_http_note_is_trimmed(self):
        _, by_repo, _ = self.imported()
        self.assertEqual(by_repo["d/four"]["evidence_url"],
                         "https://github.com/d/four")

    def test_every_record_has_http_evidence_url(self):
        _, by_repo, _ = self.imported()
        for rec in by_repo.values():
            self.assertTrue(rec["evidence_url"].startswith("https://"), rec["repo"])

    def test_source_set(self):
        _, by_repo, _ = self.imported()
        self.assertEqual(by_repo["a/one"]["source_set"], "discord")
        self.assertEqual(by_repo["c/three"]["source_set"], "topic")
        self.assertEqual(by_repo["d/four"]["source_set"], "manual")

    def test_meta_field_names_are_translated(self):
        _, by_repo, _ = self.imported()
        meta = by_repo["a/one"]["meta"]
        self.assertEqual(meta["description"], "Gate")
        self.assertEqual(meta["language"], "Python")
        self.assertEqual(meta["created_at"], "2026-01-01T00:00:00Z")
        self.assertEqual(meta["pushed_at"], "2026-09-01T00:00:00Z")
        self.assertEqual(meta["stars"], 12)
        # repo without metadata still gets the full (empty) meta shape
        self.assertIsNone(by_repo["d/four"]["meta"]["description"])

    def test_audit_overrides_scores_and_marks_duplicate(self):
        _, by_repo, report = self.imported(with_audit=True)
        a = by_repo["a/one"]
        self.assertEqual(a["total"], 5)
        self.assertEqual(a["class"], "C")
        self.assertTrue(a["audited"])
        self.assertEqual(by_repo["b/two"]["duplicate_of"], "a/one")
        self.assertEqual(report["audited"], 2)

    def test_the_note_file_fills_both_languages(self):
        _, by_repo, report = self.imported(with_audit=True, with_notes=True)
        a = by_repo["a/one"]
        self.assertEqual(a["audit_note_tr"], "Sisirilmis uygunluk puani")
        self.assertEqual(a["audit_note_en"], "Inflated relevance score")
        self.assertEqual(report["audit_notes"], 2)

    def test_the_raw_gerekce_is_never_written_to_the_data(self):
        """A-denetim's ``gerekce`` is written for us, not for a public page."""
        _, by_repo, _ = self.imported(with_audit=True, with_notes=True)
        for rec in by_repo.values():
            self.assertNotIn("audit_note", rec)
            self.assertNotIn("Sisirilmis P2", rec["audit_note_tr"])
            self.assertNotIn("Sisirilmis P2", rec["audit_note_en"])

    def test_without_the_note_file_both_fields_stay_empty_and_the_build_warns(self):
        _, by_repo, report = self.imported(with_audit=True)
        self.assertEqual(by_repo["a/one"]["audit_note_tr"], "")
        self.assertEqual(by_repo["a/one"]["audit_note_en"], "")
        self.assertTrue(any("denetim-notlari" in w for w in report["warnings"]),
                        report["warnings"])
        self.assertEqual(report["fatal"], [])

    def test_a_half_written_note_file_is_fatal(self):
        root = self.tmproot()
        make_legacy(root)
        add_audit_notes(root)
        break_last_line(os.path.join(root, "repo-analizi", "denetim-notlari.jsonl"))
        _records, report = build.import_legacy(root)
        self.assertTrue(any("denetim-notlari.jsonl" in f for f in report["fatal"]),
                        report["fatal"])

    def penalised(self, hardware_penalty=True, eski=None):
        """a/one: the auditor cut relevance for hardware nobody else has."""
        root = self.tmproot()
        make_legacy(root)
        write(os.path.join(root, "repo-analizi", "A-denetim.jsonl"), jsonl([
            {"repo": "a/one",
             "eski": eski if eski is not None else
             {"P1": 0, "P2": 3, "P3": 3, "P4": 2, "P5": 3,
              "toplam": 11, "sinif": "A"},
             "yeni": {"P1": 0, "P2": 2, "P3": 3, "P4": 2, "P5": 3,
                      "toplam": 10, "sinif": "B"},
             "degisti": True, "readme_acildi": True,
             "gerekce": "Yalniz Apple Silicon'da calisiyor", "mukerrer_of": None},
        ]))
        add_audit_notes(root, [
            {"repo": "a/one", "audit_note_tr": "Sizinti sinyali degerli",
             "audit_note_en": "The leak signal is valuable",
             "hardware_penalty": hardware_penalty},
        ])
        records, report = build.import_legacy(root)
        return {r["repo"]: r for r in records}, report

    def test_a_hardware_penalty_row_gets_its_relevance_back(self):
        """Our hardware is not the public's; that cut does not survive."""
        by_repo, report = self.penalised()
        a = by_repo["a/one"]
        self.assertEqual(a["scores"]["relevance"], 3)       # back to eski
        self.assertEqual(a["scores"], {"depth": 0, "relevance": 3, "novelty": 3,
                                       "maturity": 2, "evidence": 3})
        self.assertEqual(a["total"], 11)
        self.assertEqual(a["class"], "A")
        self.assertEqual(report["hardware_reverted"], 1)

    def test_the_hardware_penalty_leaves_the_note_alone(self):
        by_repo, _ = self.penalised()
        self.assertEqual(by_repo["a/one"]["audit_note_en"],
                         "The leak signal is valuable")
        self.assertTrue(by_repo["a/one"]["audited"])

    def test_without_the_flag_the_auditors_relevance_stands(self):
        by_repo, report = self.penalised(hardware_penalty=False)
        a = by_repo["a/one"]
        self.assertEqual(a["scores"]["relevance"], 2)
        self.assertEqual(a["total"], 10)
        self.assertEqual(a["class"], "B")
        self.assertEqual(report["hardware_reverted"], 0)

    def test_a_hardware_penalty_without_an_old_relevance_warns_and_changes_nothing(self):
        by_repo, report = self.penalised(eski={"P1": 0, "P3": 3})
        self.assertEqual(by_repo["a/one"]["scores"]["relevance"], 2)
        self.assertTrue(any("donanım" in w for w in report["warnings"]),
                        report["warnings"])
        self.assertEqual(report["hardware_reverted"], 0)

    def test_build_works_without_audit_file(self):
        _, by_repo, report = self.imported()
        self.assertFalse(by_repo["a/one"]["audited"])
        self.assertTrue(any("A-denetim" in w for w in report["warnings"]))

    def test_translations_merge_and_missing_counted(self):
        _, by_repo, report = self.imported(with_tr=True)
        self.assertEqual(by_repo["a/one"]["summary_en"], "Agent gate")
        self.assertEqual(by_repo["a/one"]["takeaway_en"], "Threshold band")
        self.assertEqual(by_repo["a/one"]["risk_en"], "none seen")
        self.assertEqual(by_repo["b/two"]["summary_en"], "")
        self.assertEqual(report["missing_translation"], 4)

    def test_translator_input_files_are_not_read_as_output(self):
        _, by_repo, _ = self.imported(with_tr=True)
        # ceviri-girdi-*.jsonl carries Turkish only; it must not blank or fill _en
        self.assertEqual(by_repo["a/one"]["summary_en"], "Agent gate")

    def test_turkish_fields_kept(self):
        _, by_repo, _ = self.imported()
        self.assertEqual(by_repo["a/one"]["takeaway_tr"], "Esik + belirsiz bandi")
        self.assertEqual(by_repo["b/two"]["risk_tr"], "gorulmedi")

    def test_fixed_import_stamps(self):
        _, by_repo, _ = self.imported()
        rec = by_repo["a/one"]
        self.assertEqual(rec["scored_at"], build.IMPORT_DATE)
        self.assertEqual(rec["first_seen"], build.IMPORT_DATE)
        self.assertEqual(rec["rubric_version"], build.RUBRIC_VERSION)
        self.assertEqual(rec["status"], "active")

    def test_import_is_deterministic_and_sorted(self):
        root = self.tmproot()
        make_legacy(root)
        first, _ = build.import_legacy(root)
        second, _ = build.import_legacy(root)
        self.assertEqual(first, second)
        self.assertEqual([r["repo"] for r in first],
                         sorted((r["repo"] for r in first), key=str.lower))

    def test_notr_rows_overwrite_the_imported_text(self):
        _, by_repo, report = self.imported(with_tr=True, with_notr=True)
        a = by_repo["a/one"]
        self.assertEqual(a["summary_tr"], "Notr ozet")
        self.assertEqual(a["takeaway_tr"], "Notr fikir")
        self.assertEqual(a["risk_tr"], "Notr risk")
        # the neutralisation pass runs last: it also beats the translation
        self.assertEqual(a["summary_en"], "Neutral summary")
        self.assertEqual(a["takeaway_en"], "Neutral takeaway")
        self.assertEqual(a["risk_en"], "Neutral risk")
        self.assertEqual(report["neutralised"], 2)

    def test_a_row_without_a_notr_line_keeps_its_text(self):
        _, by_repo, _ = self.imported(with_notr=True)
        self.assertEqual(by_repo["b/two"]["summary_tr"], "Bir sey yapiyor")

    def test_missing_notr_files_only_warn(self):
        _, _by_repo, report = self.imported()
        self.assertTrue(any("notr-" in w for w in report["warnings"]),
                        report["warnings"])
        self.assertEqual(report["fatal"], [])

    def test_unknown_category_falls_back_to_other_and_warns(self):
        root = self.tmproot()
        make_legacy(root)
        write(os.path.join(root, "repo-analizi", "sonuc-99.jsonl"),
              jsonl([legacy_row("e/five", kategori="uydurma-kategori")]))
        records, report = build.import_legacy(root)
        by_repo = {r["repo"]: r for r in records}
        self.assertEqual(by_repo["e/five"]["category"], "other")
        self.assertTrue(any("uydurma-kategori" in w for w in report["warnings"]))


if __name__ == "__main__":
    unittest.main()
