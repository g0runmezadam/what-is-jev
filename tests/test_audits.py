"""data/audits/*.jsonl carries an AUDIT result back into data/repos.jsonl.

The auditor reads a class A row and writes what the second pass concluded:
the five scores, a public note in both languages, whether the row turned out
to be a duplicate, and the day the reading happened. The auditor never writes
``total`` or ``class`` - those are the rubric's answer to the scores, so an
audit cannot contradict the scale.

Held to exactly the discipline ``data/incoming/`` is held to: one validation,
one bad line stops every file, a ledger entry so nothing is applied twice,
an atomic write, and ``--check`` that writes and moves nothing.
"""

import contextlib
import io
import json
import os
import unittest
from unittest import mock

from helpers import BaseCase, SOURCES, write, jsonl
from test_schema import base_record
from test_incoming import incoming_row

import build


def audit_row(repo="a/one", **kw):
    """One audit result, as the auditor writes it."""
    row = {
        "repo": repo,
        "scores": {"depth": 1, "relevance": 1, "novelty": 1,
                   "maturity": 1, "evidence": 1},
        "audit_note_en": "Maturity lowered: the repository is days old.",
        "audit_note_tr": "Olgunluk dusuruldu: repo birkac gunluk.",
        "duplicate_of": None,
        "audited_at": "2026-09-26",
        "score_batch": build.INITIAL_BATCH,
    }
    row.update(kw)
    return row


def ledger_entry(batch, name="batch-0.jsonl", applied_at="2026-09-19", kind=None):
    """A ledger line for a file whose sha256 starts with the id *batch*.

    The digest is padded out rather than computed: the file it describes was
    applied and archived in some earlier run, and only its first twelve
    digits are ever read back as a score identity.
    """
    entry = {"name": name, "sha256": batch + "0" * (64 - len(batch)),
             "applied_at": applied_at}
    if kind is not None:
        entry["kind"] = kind
    return entry


class AuditBase(BaseCase):
    def root_with(self, existing, audits=None, incoming=None, ledger=None):
        root = self.tmproot()
        write(os.path.join(root, "data", "repos.jsonl"), jsonl(existing))
        write(os.path.join(root, "data", "sources.jsonl"), jsonl(SOURCES))
        if ledger is not None:
            write(os.path.join(root, "data", "applied-batches.jsonl"), jsonl(ledger))
        for name, rows in (audits or {}).items():
            write(os.path.join(root, "data", "audits", name), jsonl(rows))
        for name, rows in (incoming or {}).items():
            write(os.path.join(root, "data", "incoming", name), jsonl(rows))
        return root

    def repos(self, root):
        path = os.path.join(root, "data", "repos.jsonl")
        with open(path, encoding="utf-8") as fh:
            return {r["repo"]: r for r in (json.loads(l) for l in fh if l.strip())}

    def ledger(self, root):
        path = os.path.join(root, "data", "applied-batches.jsonl")
        if not os.path.exists(path):
            return []
        with open(path, encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]

    def run_build(self, root, argv=()):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = build.main(list(argv), root=root)
        return code, out.getvalue()


class AuditApplyTest(AuditBase):
    def test_an_audit_overwrites_the_scores_and_marks_the_row_audited(self):
        root = self.root_with([base_record()], {"2026-09-26.jsonl": [audit_row()]})
        self.assertEqual(self.run_build(root)[0], 0)
        rec = self.repos(root)["a/one"]
        self.assertEqual(rec["scores"], {"depth": 1, "relevance": 1, "novelty": 1,
                                         "maturity": 1, "evidence": 1})
        self.assertTrue(rec["audited"])
        self.assertEqual(rec["audited_at"], "2026-09-26")
        self.assertEqual(rec["audit_note_en"],
                         "Maturity lowered: the repository is days old.")
        self.assertEqual(rec["audit_note_tr"],
                         "Olgunluk dusuruldu: repo birkac gunluk.")

    def test_the_auditor_does_not_write_the_class_the_scale_does(self):
        """total and class are recomputed, so an audit cannot contradict them."""
        root = self.root_with([base_record()], {"a.jsonl": [audit_row(
            scores={"depth": 0, "relevance": 3, "novelty": 2,
                    "maturity": 0, "evidence": 0})]})
        self.assertEqual(self.run_build(root)[0], 0)
        rec = self.repos(root)["a/one"]
        self.assertEqual(rec["total"], 5)
        self.assertEqual(rec["class"], "A")   # relevance 3, novelty 2

        root = self.root_with([base_record()], {"a.jsonl": [audit_row()]})
        self.assertEqual(self.run_build(root)[0], 0)
        rec = self.repos(root)["a/one"]
        self.assertEqual(rec["total"], 5)
        self.assertEqual(rec["class"], "C")

    def test_a_class_written_by_the_auditor_is_a_field_the_schema_refuses(self):
        row = audit_row()
        row["class"] = "A"
        root = self.root_with([base_record()], {"a.jsonl": [row]})
        self.assertEqual(self.run_build(root)[0], 1)
        self.assertFalse(self.repos(root)["a/one"]["audited"])

    def test_an_audited_row_reaches_top(self):
        scores = {"depth": 3, "relevance": 3, "novelty": 3,
                  "maturity": 3, "evidence": 3}
        root = self.root_with([base_record()], {"a.jsonl": [audit_row(scores=scores)]})
        self.assertEqual(self.run_build(root)[0], 0)
        with open(os.path.join(root, "TOP.md"), encoding="utf-8") as fh:
            self.assertIn("a/one", fh.read())

    def test_a_duplicate_is_recorded_and_its_target_must_exist(self):
        other = base_record(repo="b/two", url="https://github.com/b/two",
                            evidence_url="https://github.com/b/two#readme")
        root = self.root_with([base_record(), other],
                              {"a.jsonl": [audit_row(duplicate_of="b/two")]})
        self.assertEqual(self.run_build(root)[0], 0)
        self.assertEqual(self.repos(root)["a/one"]["duplicate_of"], "b/two")

    def test_a_duplicate_of_a_repository_the_data_does_not_know_is_an_error(self):
        root = self.root_with([base_record()],
                              {"a.jsonl": [audit_row(duplicate_of="q/missing")]})
        self.assertEqual(self.run_build(root)[0], 1)
        self.assertFalse(self.repos(root)["a/one"]["audited"])

    def test_a_row_cannot_be_a_duplicate_of_itself(self):
        root = self.root_with([base_record()],
                              {"a.jsonl": [audit_row(duplicate_of="a/one")]})
        self.assertEqual(self.run_build(root)[0], 1)


class AuditValidationTest(AuditBase):
    def assert_refused(self, row, existing=None):
        root = self.root_with(existing or [base_record()], {"a.jsonl": [row]})
        code, _out = self.run_build(root)
        self.assertEqual(code, 1)
        self.assertFalse(self.repos(root)["a/one"]["audited"])
        # nothing was applied and nothing was filed away
        self.assertTrue(os.path.exists(
            os.path.join(root, "data", "audits", "a.jsonl")))
        return root

    def test_an_audit_for_a_repository_the_data_does_not_know_is_an_error(self):
        self.assert_refused(audit_row(repo="q/missing"))

    def test_a_missing_field_is_an_error(self):
        row = audit_row()
        del row["audit_note_tr"]
        self.assert_refused(row)

    def test_an_unknown_field_is_an_error(self):
        row = audit_row()
        row["gerekce"] = "sisirilmis puan"
        self.assert_refused(row)

    def test_an_empty_note_is_an_error_in_either_language(self):
        self.assert_refused(audit_row(audit_note_en="  "))
        self.assert_refused(audit_row(audit_note_tr=""))

    def test_a_note_carrying_markup_is_an_error(self):
        self.assert_refused(audit_row(audit_note_en="bak [buraya](http://x.invalid)"))
        self.assert_refused(audit_row(audit_note_tr="<script>alert(1)</script>"))

    def test_a_note_carrying_a_private_detail_is_an_error(self):
        self.assert_refused(audit_row(audit_note_tr="yaz: someone@example.com"))
        self.assert_refused(audit_row(audit_note_en="see 192.168.0.10"))

    def test_a_score_outside_the_scale_is_an_error(self):
        self.assert_refused(audit_row(scores={"depth": 4, "relevance": 1,
                                              "novelty": 1, "maturity": 1,
                                              "evidence": 1}))

    def test_a_missing_score_axis_is_an_error(self):
        self.assert_refused(audit_row(scores={"depth": 1, "relevance": 1,
                                              "novelty": 1, "maturity": 1}))

    def test_an_audited_at_that_is_not_a_calendar_day_is_an_error(self):
        self.assert_refused(audit_row(audited_at="2026-02-30"))

    def test_a_half_written_audit_line_fails_the_build(self):
        root = self.root_with([base_record()])
        write(os.path.join(root, "data", "audits", "a.jsonl"), '{"repo":"a/one",\n')
        self.assertEqual(self.run_build(root)[0], 1)

    def test_one_bad_audit_file_stops_the_good_one_too(self):
        other = base_record(repo="b/two", url="https://github.com/b/two",
                            evidence_url="https://github.com/b/two#readme")
        root = self.root_with([base_record(), other], {
            "a.jsonl": [audit_row()],
            "b.jsonl": [audit_row(repo="b/two", audit_note_en="")],
        })
        self.assertEqual(self.run_build(root)[0], 1)
        self.assertFalse(self.repos(root)["a/one"]["audited"])

    def test_a_bad_incoming_row_stops_the_audit_too(self):
        root = self.root_with([base_record()],
                              audits={"a.jsonl": [audit_row()]},
                              incoming={"batch-1.jsonl": [incoming_row(calls_jev="evet")]})
        self.assertEqual(self.run_build(root)[0], 1)
        self.assertFalse(self.repos(root)["a/one"]["audited"])


class AuditOrderTest(AuditBase):
    def test_an_audit_older_than_the_score_is_not_applied_and_is_reported(self):
        """An old audit cannot confirm a score written after it."""
        root = self.root_with([base_record(scored_at="2026-09-20")],
                              {"a.jsonl": [audit_row(audited_at="2026-09-10")]})
        code, out = self.run_build(root)
        self.assertEqual(code, 0)
        rec = self.repos(root)["a/one"]
        self.assertFalse(rec["audited"])
        self.assertEqual(rec["total"], 11)
        self.assertIn("2026-09-10", out)
        self.assertIn("a/one", out)

    def test_incoming_is_applied_before_the_audit_in_the_same_run(self):
        """The auditor read the new score, so the audit must land on top of it."""
        new = incoming_row(repo="a/one", url="https://github.com/a/one",
                           evidence_url="https://github.com/a/one#readme",
                           scored_at="2026-09-25", summary_tr="yeni ozet",
                           category="cli", total=5,
                           scores={"depth": 1, "relevance": 1, "novelty": 1,
                                   "maturity": 1, "evidence": 1})
        new["class"] = "C"
        root = self.root_with([base_record()], incoming={"batch-1.jsonl": [new]})
        # the auditor read the score this batch is bringing, and says so
        batch = build.batch_id(build.sha256_of(
            os.path.join(root, "data", "incoming", "batch-1.jsonl")))
        write(os.path.join(root, "data", "audits", "a.jsonl"),
              jsonl([audit_row(audited_at="2026-09-26", score_batch=batch)]))
        self.assertEqual(self.run_build(root)[0], 0)
        rec = self.repos(root)["a/one"]
        self.assertEqual(rec["summary_tr"], "yeni ozet")   # incoming landed
        self.assertTrue(rec["audited"])                    # audit landed after it
        self.assertEqual(rec["audited_at"], "2026-09-26")

    def test_an_audit_of_a_repository_added_by_incoming_in_the_same_run(self):
        root = self.root_with([base_record()],
                              incoming={"batch-1.jsonl": [incoming_row()]})
        batch = build.batch_id(build.sha256_of(
            os.path.join(root, "data", "incoming", "batch-1.jsonl")))
        write(os.path.join(root, "data", "audits", "a.jsonl"),
              jsonl([audit_row(repo="n/new", score_batch=batch)]))
        self.assertEqual(self.run_build(root)[0], 0)
        self.assertTrue(self.repos(root)["n/new"]["audited"])

    def test_a_new_score_leaves_the_audit_date_where_it_was(self):
        """Re-scoring clears audited; the date of the last reading is kept."""
        root = self.root_with([base_record()], {"a.jsonl": [audit_row()]})
        self.assertEqual(self.run_build(root)[0], 0)
        write(os.path.join(root, "data", "incoming", "batch-1.jsonl"), jsonl([
            incoming_row(repo="a/one", url="https://github.com/a/one",
                         evidence_url="https://github.com/a/one#readme",
                         scored_at="2026-09-27")]))
        self.assertEqual(self.run_build(root)[0], 0)
        rec = self.repos(root)["a/one"]
        self.assertFalse(rec["audited"])
        self.assertEqual(rec["audited_at"], "2026-09-26")

    def test_a_scorer_cannot_hand_itself_an_audit_date(self):
        row = incoming_row()
        row["audited_at"] = "2026-09-26"
        root = self.root_with([base_record()], incoming={"batch-1.jsonl": [row]})
        self.assertEqual(self.run_build(root)[0], 0)
        self.assertNotIn("audited_at", self.repos(root)["n/new"])


class AuditScoreBatchTest(AuditBase):
    """An audit says which version of the score it read.

    The auditor's trigger: a new incoming score and an older audit, both
    dated ``2026-09-20``. The day comparison could not separate them, so the
    stale audit reset the fresh scores and marked the row audited. The audit
    now carries the row's ``score_batch``; a different one means the auditor
    read a score that is no longer there.
    """

    def test_an_audit_without_a_score_batch_is_an_error(self):
        row = audit_row()
        del row["score_batch"]
        root = self.root_with([base_record()], {"a.jsonl": [row]})
        code, out = self.run_build(root)
        self.assertEqual(code, 1)
        self.assertIn("score_batch", out)
        self.assertFalse(self.repos(root)["a/one"]["audited"])

    def test_a_score_batch_that_is_not_a_batch_id_is_an_error(self):
        for bad in ("", "INITIAL", "zzzzzzzzzzzz", 12, True, None):
            root = self.root_with([base_record()],
                                  {"a.jsonl": [audit_row(score_batch=bad)]})
            code, out = self.run_build(root)
            self.assertEqual(code, 1, bad)
            self.assertIn("score_batch", out)

    def test_an_audit_of_the_score_the_row_carries_is_applied(self):
        root = self.root_with([base_record(score_batch="6aeebbf643f8")],
                              {"a.jsonl": [audit_row(score_batch="6aeebbf643f8")]},
                              ledger=[ledger_entry("6aeebbf643f8")])
        self.assertEqual(self.run_build(root)[0], 0)
        self.assertTrue(self.repos(root)["a/one"]["audited"])

    def test_an_audit_of_another_score_is_not_applied_and_is_reported(self):
        root = self.root_with([base_record(score_batch="6aeebbf643f8")],
                              {"a.jsonl": [audit_row(score_batch="initial")]},
                              ledger=[ledger_entry("6aeebbf643f8")])
        code, out = self.run_build(root)
        self.assertEqual(code, 0)
        rec = self.repos(root)["a/one"]
        self.assertFalse(rec["audited"])
        self.assertEqual(rec["total"], 11)          # the new score stands
        self.assertIn("a/one", out)
        self.assertIn("initial", out)
        self.assertIn("6aeebbf643f8", out)

    def test_the_same_day_stale_audit_no_longer_confirms_a_fresh_score(self):
        """Both dated 2026-09-20: only the batch id tells them apart."""
        new = incoming_row(repo="a/one", url="https://github.com/a/one",
                           evidence_url="https://github.com/a/one#readme",
                           scored_at="2026-09-20", summary_tr="yeni ozet")
        root = self.root_with(
            [base_record(scored_at="2026-09-20", score_batch="initial")],
            audits={"a.jsonl": [audit_row(audited_at="2026-09-20",
                                          score_batch="initial",
                                          scores={"depth": 0, "relevance": 0,
                                                  "novelty": 0, "maturity": 0,
                                                  "evidence": 0})]},
            incoming={"batch-1.jsonl": [new]})
        code, out = self.run_build(root)
        self.assertEqual(code, 0, out)
        rec = self.repos(root)["a/one"]
        self.assertEqual(rec["summary_tr"], "yeni ozet")
        self.assertFalse(rec["audited"])
        self.assertEqual(rec["class"], "A")
        self.assertEqual(rec["total"], 11)

    def test_an_audit_of_a_score_applied_in_the_same_run_is_applied(self):
        """The auditor read the batch that is landing right now."""
        root = self.root_with([base_record()],
                              incoming={"batch-1.jsonl": [incoming_row()]})
        digest = build.sha256_of(
            os.path.join(root, "data", "incoming", "batch-1.jsonl"))
        write(os.path.join(root, "data", "audits", "a.jsonl"),
              jsonl([audit_row(repo="n/new", score_batch=digest[:12])]))
        self.assertEqual(self.run_build(root)[0], 0)
        self.assertTrue(self.repos(root)["n/new"]["audited"])

    def test_an_audit_never_changes_the_batch_the_score_came_from(self):
        root = self.root_with([base_record(score_batch="6aeebbf643f8")],
                              {"a.jsonl": [audit_row(score_batch="6aeebbf643f8")]},
                              ledger=[ledger_entry("6aeebbf643f8")])
        self.assertEqual(self.run_build(root)[0], 0)
        self.assertEqual(self.repos(root)["a/one"]["score_batch"], "6aeebbf643f8")

    def test_the_date_check_still_catches_an_audit_older_than_the_score(self):
        root = self.root_with([base_record(scored_at="2026-09-20")],
                              {"a.jsonl": [audit_row(audited_at="2026-09-10")]})
        code, out = self.run_build(root)
        self.assertEqual(code, 0)
        self.assertFalse(self.repos(root)["a/one"]["audited"])
        self.assertIn("2026-09-10", out)


class BatchIdLedgerTest(AuditBase):
    """A score identity is the ledger's to hand out, not a line's to claim.

    ``score_batch`` was checked for shape and for row-audit agreement only,
    so twelve hex digits nobody had ever applied passed both: an audit
    quoting an invented id landed on the row and marked it audited. The
    valid set is what ``data/applied-batches.jsonl`` accounts for - the
    first data set plus every incoming batch really applied.
    """

    BOGUS = "deadbeefdead"

    def repos_text(self, root):
        with open(os.path.join(root, "data", "repos.jsonl"), encoding="utf-8") as fh:
            return fh.read()

    def test_an_audit_quoting_a_batch_no_ledger_knows_is_refused(self):
        """The trigger: row and audit agree on an id nothing ever applied."""
        root = self.root_with([base_record(score_batch=self.BOGUS)],
                              {"a.jsonl": [audit_row(score_batch=self.BOGUS)]})
        code, out = self.run_build(root)
        self.assertEqual(code, 1)
        self.assertIn(self.BOGUS, out)
        self.assertFalse(self.repos(root)["a/one"]["audited"])
        self.assertEqual(self.ledger(root), [])

    def test_an_unknown_id_in_the_audit_alone_stops_every_file(self):
        """Not a stale audit to skip: an invented one, so nothing is applied."""
        root = self.root_with([base_record()],
                              {"a.jsonl": [audit_row(score_batch=self.BOGUS)]})
        code, out = self.run_build(root)
        self.assertEqual(code, 1)
        self.assertIn("data/audits/a.jsonl:1", out)
        self.assertIn(self.BOGUS, out)
        self.assertFalse(self.repos(root)["a/one"]["audited"])

    def test_a_row_whose_batch_no_ledger_knows_stops_the_build(self):
        root = self.root_with([base_record(score_batch=self.BOGUS)])
        code, out = self.run_build(root)
        self.assertEqual(code, 1)
        self.assertIn("a/one", out)
        self.assertIn("score_batch", out)

    def test_the_ledger_entry_for_that_batch_makes_the_row_and_audit_valid(self):
        root = self.root_with([base_record(score_batch="6aeebbf643f8")],
                              {"a.jsonl": [audit_row(score_batch="6aeebbf643f8")]},
                              ledger=[ledger_entry("6aeebbf643f8")])
        code, out = self.run_build(root)
        self.assertEqual(code, 0, out)
        self.assertTrue(self.repos(root)["a/one"]["audited"])

    def test_initial_is_the_only_identity_an_empty_ledger_hands_out(self):
        root = self.root_with([base_record()], {"a.jsonl": [audit_row()]})
        self.assertEqual(self.ledger(root), [])
        code, out = self.run_build(root)
        self.assertEqual(code, 0, out)
        self.assertTrue(self.repos(root)["a/one"]["audited"])

    def test_a_batch_applied_in_the_same_run_counts_for_the_audit_after_it(self):
        """incoming lands first, so its id is already the ledger's when the
        audit quoting it is read."""
        root = self.root_with([base_record()],
                              incoming={"batch-1.jsonl": [incoming_row()]})
        digest = build.sha256_of(
            os.path.join(root, "data", "incoming", "batch-1.jsonl"))
        write(os.path.join(root, "data", "audits", "a.jsonl"),
              jsonl([audit_row(repo="n/new", score_batch=digest[:12])]))
        code, out = self.run_build(root)
        self.assertEqual(code, 0, out)
        self.assertTrue(self.repos(root)["n/new"]["audited"])
        self.assertEqual(self.repos(root)["n/new"]["score_batch"], digest[:12])

    def test_an_audit_files_own_sha256_is_not_a_score_identity(self):
        """An audit carries scores back; it does not produce them."""
        root = self.root_with(
            [base_record(score_batch="6aeebbf643f8")],
            ledger=[ledger_entry("6aeebbf643f8", name="2026-09-26.jsonl",
                                 kind="audit")])
        code, out = self.run_build(root)
        self.assertEqual(code, 1)
        self.assertIn("6aeebbf643f8", out)

    def test_check_refuses_the_unknown_batch_and_writes_nothing(self):
        root = self.root_with([base_record(score_batch=self.BOGUS)],
                              {"a.jsonl": [audit_row(score_batch=self.BOGUS)]})
        before = self.repos_text(root)
        code, _out = self.run_build(root, ["--check"])
        self.assertEqual(code, 1)
        self.assertEqual(self.repos_text(root), before)
        self.assertFalse(os.path.exists(
            os.path.join(root, "data", "applied-batches.jsonl")))
        self.assertTrue(os.path.exists(
            os.path.join(root, "data", "audits", "a.jsonl")))


class AuditLedgerTest(AuditBase):
    def test_an_applied_audit_file_is_recorded_with_kind_audit(self):
        root = self.root_with([base_record()], {"2026-09-26.jsonl": [audit_row()]})
        self.assertEqual(self.run_build(root)[0], 0)
        entries = self.ledger(root)
        self.assertEqual(len(entries), 1, entries)
        self.assertEqual(entries[0]["name"], "2026-09-26.jsonl")
        self.assertEqual(entries[0]["kind"], "audit")
        self.assertEqual(entries[0]["applied_at"], "2026-09-26")
        self.assertEqual(len(entries[0]["sha256"]), 64)

    def test_an_incoming_entry_without_kind_counts_as_incoming(self):
        """The ledger written before audits existed still means what it meant."""
        root = self.root_with([base_record()], {"a.jsonl": [audit_row()]})
        digest = build.sha256_of(os.path.join(root, "data", "audits", "a.jsonl"))
        write(os.path.join(root, "data", "applied-batches.jsonl"),
              jsonl([{"name": "a.jsonl", "sha256": digest,
                      "applied_at": "2026-09-26"}]))
        self.assertEqual(self.run_build(root)[0], 0)
        # the old entry is an incoming one, so the audit file is still new work
        self.assertTrue(self.repos(root)["a/one"]["audited"])
        kinds = [e.get("kind") for e in self.ledger(root)]
        self.assertEqual(kinds, [None, "audit"])

    def test_the_same_audit_file_is_not_applied_twice(self):
        root = self.root_with([base_record()], {"a.jsonl": [audit_row()]})
        self.assertEqual(self.run_build(root)[0], 0)
        before = self.repos(root)
        write(os.path.join(root, "data", "audits", "a.jsonl"), jsonl([audit_row()]))
        code, out = self.run_build(root)
        self.assertEqual(code, 0)
        self.assertEqual(self.repos(root), before)
        self.assertIn("ZATEN UYGULANMIŞ", out)
        self.assertEqual(len(self.ledger(root)), 1)

    def test_the_same_name_with_new_content_is_a_new_audit(self):
        root = self.root_with([base_record()], {"a.jsonl": [audit_row()]})
        self.assertEqual(self.run_build(root)[0], 0)
        write(os.path.join(root, "data", "audits", "a.jsonl"),
              jsonl([audit_row(audited_at="2026-09-27",
                               audit_note_en="Read again, score kept.",
                               audit_note_tr="Yeniden okundu, puan korundu.")]))
        self.assertEqual(self.run_build(root)[0], 0)
        self.assertEqual(self.repos(root)["a/one"]["audited_at"], "2026-09-27")
        self.assertEqual(len(self.ledger(root)), 2)


class AuditFilingTest(AuditBase):
    def applied(self, root, name):
        return os.path.join(root, "data", "audits", "applied", name)

    def test_an_applied_audit_file_moves_under_applied(self):
        root = self.root_with([base_record()], {"a.jsonl": [audit_row()]})
        self.assertEqual(self.run_build(root)[0], 0)
        self.assertFalse(os.path.exists(
            os.path.join(root, "data", "audits", "a.jsonl")))
        self.assertTrue(os.path.exists(self.applied(root, "a.jsonl")))

    def test_a_second_file_of_the_same_name_is_filed_beside_the_first(self):
        root = self.root_with([base_record()], {"a.jsonl": [audit_row()]})
        self.assertEqual(self.run_build(root)[0], 0)
        write(os.path.join(root, "data", "audits", "a.jsonl"),
              jsonl([audit_row(audited_at="2026-09-27")]))
        self.assertEqual(self.run_build(root)[0], 0)
        self.assertTrue(os.path.exists(self.applied(root, "a.jsonl")))
        self.assertTrue(os.path.exists(self.applied(root, "a-2.jsonl")))

    def test_an_audit_that_cannot_be_filed_away_is_named_and_the_build_fails(self):
        root = self.root_with([base_record()], {"a.jsonl": [audit_row()]})
        real = os.replace
        archive = os.path.join("audits", "applied") + os.sep

        def no_archiving(src, dst):
            if archive in str(dst):
                raise OSError("arsivleme basarisiz")
            return real(src, dst)

        with mock.patch.object(build.os, "replace", side_effect=no_archiving):
            code, out = self.run_build(root)
        self.assertEqual(code, 1)
        self.assertIn("a.jsonl", out)
        # the audit landed in the data, and the ledger says so
        self.assertTrue(self.repos(root)["a/one"]["audited"])
        self.assertEqual(len(self.ledger(root)), 1)

        # the next run only retries the move; nothing is applied again
        self.assertEqual(self.run_build(root)[0], 0)
        self.assertTrue(os.path.exists(self.applied(root, "a.jsonl")))

    def test_check_writes_nothing_and_moves_nothing(self):
        root = self.root_with([base_record()])
        self.assertEqual(self.run_build(root)[0], 0)
        write(os.path.join(root, "data", "audits", "a.jsonl"), jsonl([audit_row()]))
        before = self.repos(root)
        self.assertEqual(self.run_build(root, ["--check"])[0], 1)
        self.assertEqual(self.repos(root), before)
        self.assertTrue(os.path.exists(
            os.path.join(root, "data", "audits", "a.jsonl")))
        self.assertFalse(os.path.exists(self.applied(root, "a.jsonl")))

    def test_an_empty_audits_directory_changes_nothing(self):
        root = self.root_with([base_record()])
        os.makedirs(os.path.join(root, "data", "audits"), exist_ok=True)
        self.assertEqual(self.run_build(root)[0], 0)
        self.assertEqual(self.run_build(root, ["--check"])[0], 0)


class AuditedAtFieldTest(BaseCase):
    def test_a_row_without_audited_at_is_still_valid(self):
        errors, _ = build.validate([base_record()], SOURCES)
        self.assertEqual(errors, [])

    def test_audited_at_must_be_a_calendar_day_when_it_is_there(self):
        errors, _ = build.validate([base_record(audited_at="2026-02-30")], SOURCES)
        self.assertTrue(any("audited_at" in e for e in errors), errors)
        errors, _ = build.validate([base_record(audited_at=20260919)], SOURCES)
        self.assertTrue(any("audited_at" in e for e in errors), errors)
        errors, _ = build.validate([base_record(audited_at="2026-09-19")], SOURCES)
        self.assertEqual(errors, [])

    def test_the_json_schema_knows_the_field_and_does_not_require_it(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(root, "data", "schema", "repo.schema.json"),
                  encoding="utf-8") as fh:
            schema = json.load(fh)
        self.assertIn("audited_at", schema["properties"])
        self.assertNotIn("audited_at", schema["required"])
        self.assertEqual(schema["properties"]["audited_at"]["pattern"],
                         "^\\d{4}-\\d{2}-\\d{2}$")
        self.assertEqual(set(schema["properties"]) - set(build.RECORD_FIELDS),
                         set(build.OPTIONAL_FIELDS))


class AwaitingAuditTest(AuditBase):
    def records(self, waiting=1):
        rows = [base_record(repo="a/audited", url="https://github.com/a/audited",
                            evidence_url="https://github.com/a/audited#readme",
                            audited=True, audited_at="2026-09-19",
                            audit_note_en="Kept", audit_note_tr="Korundu")]
        for number in range(waiting):
            name = "w/wait%d" % number
            rows.append(base_record(repo=name, url="https://github.com/" + name,
                                    evidence_url="https://github.com/" + name))
        # a duplicate class A never counts
        rows.append(base_record(repo="d/dupe", url="https://github.com/d/dupe",
                                evidence_url="https://github.com/d/dupe",
                                duplicate_of="a/audited"))
        return rows

    def test_the_count_leaves_out_duplicates_and_audited_rows(self):
        st = build.stats(self.records(waiting=2), SOURCES)
        self.assertEqual(st["awaiting_audit"], 2)

    def test_the_stats_row_appears_in_both_languages(self):
        st = build.stats(self.records(waiting=2), SOURCES)
        self.assertIn("Class A awaiting audit | 2", build.stats_block(st, "en"))
        self.assertIn("Denetim bekleyen A sınıfı | 2", build.stats_block(st, "tr"))

    def test_the_stats_row_is_hidden_when_nothing_is_waiting(self):
        st = build.stats(self.records(waiting=0), SOURCES)
        self.assertEqual(st["awaiting_audit"], 0)
        self.assertNotIn("Class A awaiting audit", build.stats_block(st, "en"))
        self.assertNotIn("Denetim bekleyen A sınıfı", build.stats_block(st, "tr"))

    def test_top_says_how_many_are_waiting_and_where_they_are(self):
        pages = build.render_all(self.records(waiting=2), SOURCES)
        top = pages["TOP.md"]
        self.assertIn("2", top.split("## ")[0])
        self.assertIn("REPOS.md", top)
        self.assertIn("audited", top.lower())
        tr = pages["tr/TOP.md"]
        self.assertIn("REPOS.md", tr)
        self.assertIn("Denetim bekleyen", tr)

    def test_top_says_nothing_when_nothing_is_waiting(self):
        top = build.render_all(self.records(waiting=0), SOURCES)["TOP.md"]
        self.assertNotIn("awaiting audit", top)

    def test_the_repository_tables_show_whether_a_row_was_audited(self):
        pages = build.render_all(self.records(waiting=1), SOURCES)
        page = pages["REPOS.md"]
        self.assertIn("| Audited |", page)
        line = [l for l in page.splitlines() if l.startswith("| [w/wait0]")][0]
        self.assertTrue(line.rstrip().endswith("| no |"), line)
        line = [l for l in page.splitlines() if l.startswith("| [a/audited]")][0]
        self.assertTrue(line.rstrip().endswith("| yes |"), line)
        self.assertIn("| Denetlendi |", pages["tr/REPOS.md"])


if __name__ == "__main__":
    unittest.main()
