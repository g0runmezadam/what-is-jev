"""data/incoming/*.jsonl is folded into data/repos.jsonl, then filed away."""

import contextlib
import io
import json
import os
import unittest
from unittest import mock

from helpers import BaseCase, SOURCES, write, jsonl
from test_schema import base_record

import build


def incoming_row(repo="n/new", **kw):
    """A complete repository row, in English field names, as an agent writes it."""
    row = base_record(repo=repo, url="https://github.com/" + repo,
                      evidence_url="https://github.com/" + repo + "#readme",
                      first_seen="2026-09-25", scored_at="2026-09-25",
                      summary_en="New summary", summary_tr="Yeni ozet",
                      takeaway_en="New takeaway", takeaway_tr="Yeni fikir")
    row.update(kw)
    return row


class IncomingTest(BaseCase):
    def root_with(self, existing, batches):
        root = self.tmproot()
        write(os.path.join(root, "data", "repos.jsonl"), jsonl(existing))
        write(os.path.join(root, "data", "sources.jsonl"), jsonl(SOURCES))
        for name, rows in batches.items():
            write(os.path.join(root, "data", "incoming", name), jsonl(rows))
        return root

    def repos(self, root):
        path = os.path.join(root, "data", "repos.jsonl")
        with open(path, encoding="utf-8") as fh:
            return {r["repo"]: r for r in (json.loads(l) for l in fh if l.strip())}

    def test_an_unknown_repository_is_added_with_first_seen_from_the_row(self):
        root = self.root_with([base_record()], {"batch-1.jsonl": [incoming_row()]})
        self.assertEqual(build.main([], root=root), 0)
        rows = self.repos(root)
        self.assertIn("n/new", rows)
        self.assertEqual(rows["n/new"]["first_seen"], "2026-09-25")
        self.assertEqual(rows["n/new"]["summary_en"], "New summary")

    def test_a_known_repository_has_its_score_and_text_overwritten(self):
        old = base_record(audited=True, audit_note_en="Auditor said so",
                          audit_note_tr="Denetci boyle dedi",
                          duplicate_of="b/two", first_seen="2026-09-19")
        new = incoming_row(repo="a/one", url="https://github.com/a/one",
                           evidence_url="https://github.com/a/one#readme",
                           category="cli", calls_jev="no", total=5,
                           scores={"depth": 1, "relevance": 1, "novelty": 1,
                                   "maturity": 1, "evidence": 1})
        new["class"] = "C"
        root = self.root_with([old], {"batch-1.jsonl": [new]})
        self.assertEqual(build.main([], root=root), 0)
        rec = self.repos(root)["a/one"]
        self.assertEqual(rec["total"], 5)
        self.assertEqual(rec["class"], "C")
        self.assertEqual(rec["category"], "cli")
        self.assertEqual(rec["calls_jev"], "no")
        self.assertEqual(rec["summary_en"], "New summary")
        self.assertEqual(rec["scored_at"], "2026-09-25")

    def test_the_merge_keeps_what_the_scorer_did_not_earn(self):
        """first_seen, the audit note and duplicate_of survive; audited does not."""
        old = base_record(audited=True, audit_note_en="Auditor said so",
                          audit_note_tr="Denetci boyle dedi",
                          duplicate_of="b/two", first_seen="2026-09-19")
        root = self.root_with([old], {"batch-1.jsonl": [
            incoming_row(repo="a/one", url="https://github.com/a/one",
                         evidence_url="https://github.com/a/one#readme",
                         audited=True, audit_note_en="", audit_note_tr="",
                         duplicate_of=None)]})
        self.assertEqual(build.main([], root=root), 0)
        rec = self.repos(root)["a/one"]
        self.assertEqual(rec["first_seen"], "2026-09-19")
        self.assertEqual(rec["audit_note_en"], "Auditor said so")
        self.assertEqual(rec["audit_note_tr"], "Denetci boyle dedi")
        self.assertEqual(rec["duplicate_of"], "b/two")
        # the new score has not been audited, whatever the row claims
        self.assertFalse(rec["audited"])

    def test_a_new_row_cannot_declare_itself_audited(self):
        """The auditor's marks are the auditor's to give, on a new row too."""
        root = self.root_with([base_record()], {"batch-1.jsonl": [
            incoming_row(audited=True, audit_note_en="Scored it myself",
                         audit_note_tr="Kendim puanladim",
                         duplicate_of="a/one")]})
        self.assertEqual(build.main([], root=root), 0)
        rec = self.repos(root)["n/new"]
        self.assertFalse(rec["audited"])
        self.assertEqual(rec["audit_note_en"], "")
        self.assertEqual(rec["audit_note_tr"], "")
        self.assertIsNone(rec["duplicate_of"])
        # TOP lists audited rows only, so the row must not have reached it
        with open(os.path.join(root, "TOP.md"), encoding="utf-8") as fh:
            self.assertNotIn("n/new", fh.read())

    def test_a_row_missing_a_field_is_an_error_and_nothing_is_applied(self):
        row = incoming_row()
        del row["category"]
        root = self.root_with([base_record()], {"batch-1.jsonl": [row]})
        self.assertEqual(build.main([], root=root), 1)
        self.assertNotIn("n/new", self.repos(root))
        self.assertTrue(os.path.exists(
            os.path.join(root, "data", "incoming", "batch-1.jsonl")))

    def test_a_row_with_a_bad_value_is_an_error(self):
        root = self.root_with([base_record()],
                              {"batch-1.jsonl": [incoming_row(calls_jev="evet")]})
        self.assertEqual(build.main([], root=root), 1)

    def test_a_turkish_field_name_is_an_error(self):
        row = incoming_row()
        row["kategori"] = "diger"
        root = self.root_with([base_record()], {"batch-1.jsonl": [row]})
        self.assertEqual(build.main([], root=root), 1)

    def test_one_bad_file_stops_the_other_one_too(self):
        root = self.root_with([base_record()], {
            "batch-1.jsonl": [incoming_row()],
            "batch-2.jsonl": [incoming_row(repo="o/other", calls_jev="evet")],
        })
        self.assertEqual(build.main([], root=root), 1)
        self.assertNotIn("n/new", self.repos(root))

    def test_a_merged_file_moves_under_applied(self):
        root = self.root_with([base_record()], {"batch-1.jsonl": [incoming_row()]})
        self.assertEqual(build.main([], root=root), 0)
        self.assertFalse(os.path.exists(
            os.path.join(root, "data", "incoming", "batch-1.jsonl")))
        self.assertTrue(os.path.exists(
            os.path.join(root, "data", "incoming", "applied", "batch-1.jsonl")))

    def test_an_applied_file_is_not_merged_again(self):
        root = self.root_with([base_record()], {"batch-1.jsonl": [incoming_row()]})
        build.main([], root=root)
        before = self.repos(root)
        self.assertEqual(build.main([], root=root), 0)
        self.assertEqual(self.repos(root), before)

    def test_check_moves_nothing_and_writes_nothing(self):
        root = self.root_with([base_record()], {"batch-1.jsonl": [incoming_row()]})
        build.main([], root=root)           # bring the pages up to date first
        write(os.path.join(root, "data", "incoming", "batch-2.jsonl"),
              jsonl([incoming_row(repo="o/other", url="https://github.com/o/other",
                                  evidence_url="https://github.com/o/other")]))
        before = self.repos(root)
        self.assertEqual(build.main(["--check"], root=root), 1)
        self.assertEqual(self.repos(root), before)
        self.assertTrue(os.path.exists(
            os.path.join(root, "data", "incoming", "batch-2.jsonl")))
        self.assertFalse(os.path.exists(
            os.path.join(root, "data", "incoming", "applied", "batch-2.jsonl")))

    def test_an_incoming_row_is_checked_against_the_real_schema(self):
        """A full field list is not a valid row: the values have to hold up."""
        root = self.root_with([base_record()], {"batch-1.jsonl": [
            incoming_row(scored_at="not-a-date", rubric_version="banana", meta={})]})
        self.assertEqual(build.main([], root=root), 1)
        self.assertNotIn("n/new", self.repos(root))

    def test_a_row_older_than_the_stored_score_is_not_applied(self):
        """An old score cannot overwrite a newer one, and the run says so."""
        old = base_record(scored_at="2026-09-19", summary_tr="yeni ozet")
        root = self.root_with([old], {"batch-1.jsonl": [
            incoming_row(repo="a/one", url="https://github.com/a/one",
                         evidence_url="https://github.com/a/one#readme",
                         scored_at="2026-09-10", summary_tr="eski ozet")]})
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(build.main([], root=root), 0)
        rec = self.repos(root)["a/one"]
        self.assertEqual(rec["summary_tr"], "yeni ozet")
        self.assertEqual(rec["scored_at"], "2026-09-19")
        self.assertIn("2026-09-10", out.getvalue())

    def test_the_merged_file_stays_sorted_by_repository(self):
        root = self.root_with([base_record()], {"batch-1.jsonl": [
            incoming_row(repo="A/zed", url="https://github.com/A/zed",
                         evidence_url="https://github.com/A/zed"),
            incoming_row(repo="n/new")]})
        self.assertEqual(build.main([], root=root), 0)
        with open(os.path.join(root, "data", "repos.jsonl"), encoding="utf-8") as fh:
            names = [json.loads(line)["repo"] for line in fh if line.strip()]
        self.assertEqual(names, sorted(names, key=str.lower))


class ArchivingTest(BaseCase):
    """Filing a batch away must not lose one, and must not lie about it."""

    def root_with(self, existing, batches):
        root = self.tmproot()
        write(os.path.join(root, "data", "repos.jsonl"), jsonl(existing))
        write(os.path.join(root, "data", "sources.jsonl"), jsonl(SOURCES))
        for name, rows in batches.items():
            write(os.path.join(root, "data", "incoming", name), jsonl(rows))
        return root

    def repos(self, root):
        path = os.path.join(root, "data", "repos.jsonl")
        with open(path, encoding="utf-8") as fh:
            return {r["repo"]: r for r in (json.loads(l) for l in fh if l.strip())}

    def applied(self, root, name):
        return os.path.join(root, "data", "incoming", "applied", name)

    def test_a_second_batch_of_the_same_name_is_filed_beside_the_first(self):
        root = self.root_with([base_record()], {"batch-1.jsonl": [incoming_row()]})
        self.assertEqual(build.main([], root=root), 0)
        # the same file name, reused weeks later for different work
        write(os.path.join(root, "data", "incoming", "batch-1.jsonl"),
              jsonl([incoming_row(repo="o/other", url="https://github.com/o/other",
                                  evidence_url="https://github.com/o/other")]))
        self.assertEqual(build.main([], root=root), 0)

        self.assertTrue(os.path.exists(self.applied(root, "batch-1.jsonl")))
        self.assertTrue(os.path.exists(self.applied(root, "batch-1-2.jsonl")))
        with open(self.applied(root, "batch-1.jsonl"), encoding="utf-8") as fh:
            self.assertIn("n/new", fh.read())
        with open(self.applied(root, "batch-1-2.jsonl"), encoding="utf-8") as fh:
            self.assertIn("o/other", fh.read())
        # and neither repository was lost on the way
        self.assertIn("n/new", self.repos(root))
        self.assertIn("o/other", self.repos(root))

    ARCHIVE = os.path.join("incoming", "applied") + os.sep

    def _no_archiving(self):
        """os.replace fails, but only for a move into incoming/applied/."""
        real = os.replace

        def flaky(src, dst):
            if self.ARCHIVE in str(dst):
                raise OSError("arsivleme basarisiz")
            return real(src, dst)

        return mock.patch.object(build.os, "replace", side_effect=flaky)

    def test_a_batch_that_cannot_be_filed_away_is_named_and_the_build_fails(self):
        root = self.root_with([base_record()], {"batch-1.jsonl": [incoming_row()]})
        out = io.StringIO()
        with self._no_archiving(), contextlib.redirect_stdout(out):
            code = build.main([], root=root)
        self.assertEqual(code, 1)
        self.assertIn("batch-1.jsonl", out.getvalue())
        # the data landed and says so; the batch is still where it was
        self.assertIn("n/new", self.repos(root))
        self.assertTrue(os.path.exists(
            os.path.join(root, "data", "incoming", "batch-1.jsonl")))

    def test_the_stranded_batch_is_only_filed_away_on_the_next_run(self):
        """Its rows are in the ledger, so the next run does not re-apply them."""
        root = self.root_with([base_record()], {"batch-1.jsonl": [incoming_row()]})
        with self._no_archiving(), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(build.main([], root=root), 1)
        after_failure = self.repos(root)

        self.assertEqual(build.main([], root=root), 0)
        self.assertEqual(self.repos(root), after_failure)
        self.assertTrue(os.path.exists(self.applied(root, "batch-1.jsonl")))
        self.assertFalse(os.path.exists(
            os.path.join(root, "data", "incoming", "batch-1.jsonl")))

    def ledger(self, root):
        path = os.path.join(root, "data", "applied-batches.jsonl")
        if not os.path.exists(path):
            return []
        with open(path, encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]

    def test_an_applied_batch_is_recorded_in_the_ledger(self):
        root = self.root_with([base_record()], {"batch-1.jsonl": [incoming_row()]})
        self.assertEqual(build.main([], root=root), 0)
        entries = self.ledger(root)
        self.assertEqual(len(entries), 1, entries)
        self.assertEqual(entries[0]["name"], "batch-1.jsonl")
        self.assertEqual(len(entries[0]["sha256"]), 64)
        # the batch's own newest scored_at, never the wall clock
        self.assertEqual(entries[0]["applied_at"], "2026-09-25")

    def test_a_stranded_older_batch_cannot_undo_a_newer_one(self):
        """a.jsonl (old) stays behind, b.jsonl (new) is filed: b must survive."""
        rows = {
            "a.jsonl": [incoming_row(repo="a/one", url="https://github.com/a/one",
                                     evidence_url="https://github.com/a/one#readme",
                                     scored_at="2026-09-20", summary_tr="eski ozet")],
            "b.jsonl": [incoming_row(repo="a/one", url="https://github.com/a/one",
                                     evidence_url="https://github.com/a/one#readme",
                                     scored_at="2026-09-26", summary_tr="yeni ozet")],
        }
        root = self.root_with([base_record(scored_at="2026-09-19")], rows)
        real = os.replace

        def only_a_is_stranded(src, dst):
            if self.ARCHIVE in str(dst) and os.path.basename(str(src)) == "a.jsonl":
                raise OSError("arsivleme basarisiz")
            return real(src, dst)

        with mock.patch.object(build.os, "replace", side_effect=only_a_is_stranded), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(build.main([], root=root), 1)
        self.assertEqual(self.repos(root)["a/one"]["summary_tr"], "yeni ozet")

        # second run: a.jsonl is still in incoming/, and must not be re-applied
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(build.main([], root=root), 0)
        rec = self.repos(root)["a/one"]
        self.assertEqual(rec["summary_tr"], "yeni ozet")
        self.assertEqual(rec["scored_at"], "2026-09-26")
        self.assertTrue(os.path.exists(self.applied(root, "a.jsonl")))
        self.assertFalse(os.path.exists(
            os.path.join(root, "data", "incoming", "a.jsonl")))

    def test_the_same_name_with_new_content_is_a_new_batch(self):
        root = self.root_with([base_record()], {"batch-1.jsonl": [incoming_row()]})
        self.assertEqual(build.main([], root=root), 0)
        write(os.path.join(root, "data", "incoming", "batch-1.jsonl"),
              jsonl([incoming_row(repo="o/other", url="https://github.com/o/other",
                                  evidence_url="https://github.com/o/other")]))
        self.assertEqual(build.main([], root=root), 0)
        self.assertIn("o/other", self.repos(root))
        self.assertEqual(len(self.ledger(root)), 2)

    def test_an_interrupted_ledger_write_stops_the_next_run(self):
        """repos.jsonl landed, the record of it did not: say so, do not guess."""
        root = self.root_with([base_record()], {"batch-1.jsonl": [incoming_row()]})
        real = os.replace

        def no_ledger(src, dst):
            if str(dst).endswith("applied-batches.jsonl"):
                raise OSError("kayit yazilamadi")
            return real(src, dst)

        out = io.StringIO()
        with mock.patch.object(build.os, "replace", side_effect=no_ledger), \
                contextlib.redirect_stdout(out):
            self.assertEqual(build.main([], root=root), 1)
        self.assertTrue(os.path.exists(os.path.join(
            root, "data", "applied-batches.jsonl.tmp")))

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(build.main([], root=root), 1)
        self.assertIn("applied-batches.jsonl.tmp", out.getvalue())
        # nothing was applied a second time behind the operator's back
        self.assertEqual(len(self.repos(root)), 2)

    def test_the_data_file_is_replaced_atomically(self):
        """No reader ever sees data/repos.jsonl half written."""
        root = self.root_with([base_record()], {"batch-1.jsonl": [incoming_row()]})
        seen = []
        real = os.replace

        def watch(src, dst):
            if str(dst).endswith("repos.jsonl"):
                seen.append((src, dst))
            return real(src, dst)

        with mock.patch.object(build.os, "replace", side_effect=watch):
            self.assertEqual(build.main([], root=root), 0)
        self.assertEqual(len(seen), 1, seen)
        self.assertNotEqual(seen[0][0], seen[0][1])
        self.assertFalse(os.path.exists(seen[0][0]))


class LegacyIsNoLongerTheDefaultTest(BaseCase):
    def test_a_build_without_the_legacy_directory_says_nothing_about_it(self):
        root = self.tmproot()
        write(os.path.join(root, "data", "repos.jsonl"), jsonl([base_record()]))
        write(os.path.join(root, "data", "sources.jsonl"), jsonl(SOURCES))
        self.assertFalse(os.path.exists(os.path.join(root, "repo-analizi")))
        self.assertEqual(build.main([], root=root), 0)
        self.assertEqual(build.main(["--check"], root=root), 0)

    def test_import_legacy_without_the_directory_is_an_error(self):
        root = self.tmproot()
        write(os.path.join(root, "data", "repos.jsonl"), jsonl([base_record()]))
        write(os.path.join(root, "data", "sources.jsonl"), jsonl(SOURCES))
        self.assertEqual(build.main(["--import-legacy"], root=root), 1)
        # the one source of truth is left exactly as it was
        with open(os.path.join(root, "data", "repos.jsonl"), encoding="utf-8") as fh:
            self.assertIn("a/one", fh.read())


if __name__ == "__main__":
    unittest.main()
