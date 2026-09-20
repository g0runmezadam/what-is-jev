"""Record and source validation."""

import copy
import json
import os
import unittest

from helpers import BaseCase, SOURCES, make_legacy

import build


def base_record(**kw):
    rec = {
        "repo": "a/one",
        "url": "https://github.com/a/one",
        "source_set": "discord",
        "first_seen": "2026-09-19",
        "scored_at": "2026-09-19",
        "rubric_version": 1,
        "meta": {"description": None, "stars": None, "forks": None, "language": None,
                 "license": None, "created_at": None, "pushed_at": None,
                 "archived": None, "fork": None, "topics": []},
        "category": "agent-gate",
        "calls_jev": "yes",
        "question_types": ["choice"],
        "scores": {"depth": 3, "relevance": 3, "novelty": 2, "maturity": 2, "evidence": 1},
        "total": 11,
        "class": "A",
        "summary_en": "", "summary_tr": "ozet",
        "takeaway_en": "", "takeaway_tr": "fikir",
        "risk_en": "", "risk_tr": "gorulmedi",
        "evidence_url": "https://github.com/a/one#readme",
        "audited": False, "audit_note_en": "", "audit_note_tr": "",
        "duplicate_of": None, "status": "active",
    }
    rec.update(kw)
    return rec


class SchemaTest(BaseCase):
    def test_clean_record_passes(self):
        errors, _ = build.validate([base_record()], SOURCES)
        self.assertEqual(errors, [])

    def test_missing_url_is_an_error(self):
        rec = base_record()
        del rec["url"]
        errors, _ = build.validate([rec], SOURCES)
        self.assertTrue(any("url" in e for e in errors))

    def test_non_http_url_is_an_error(self):
        errors, _ = build.validate([base_record(url="github.com/a/one")], SOURCES)
        self.assertTrue(any("url" in e for e in errors))

    def test_missing_evidence_url_is_an_error(self):
        errors, _ = build.validate([base_record(evidence_url="")], SOURCES)
        self.assertTrue(any("evidence_url" in e for e in errors))

    def test_duplicate_repo_case_insensitive_is_an_error(self):
        a = base_record()
        b = base_record(repo="A/One", url="https://github.com/A/One")
        errors, _ = build.validate([a, b], SOURCES)
        self.assertTrue(any("a/one" in e.lower() for e in errors))

    def test_total_must_equal_sum_of_scores(self):
        errors, _ = build.validate([base_record(total=12)], SOURCES)
        self.assertTrue(any("total" in e for e in errors))

    def test_score_out_of_range_is_an_error(self):
        rec = base_record()
        rec["scores"] = dict(rec["scores"], depth=4)
        rec["total"] = 12
        errors, _ = build.validate([rec], SOURCES)
        self.assertTrue(any("depth" in e for e in errors))

    def test_bad_enum_values_are_errors(self):
        errors, _ = build.validate([base_record(calls_jev="evet")], SOURCES)
        self.assertTrue(any("calls_jev" in e for e in errors))
        errors, _ = build.validate([base_record(category="ajan-kapisi")], SOURCES)
        self.assertTrue(any("category" in e for e in errors))

    def test_class_rule_mismatch_on_an_unaudited_row_is_an_error(self):
        """Nobody has looked at this row, so the rubric is all it has."""
        rec = base_record(**{"class": "C"})
        errors, warnings = build.validate([rec], SOURCES)
        self.assertTrue(any("class" in e for e in errors), errors)
        self.assertEqual([w for w in warnings if "class" in w], [])

    def test_auditor_class_wins_on_audited_rows(self):
        rec = base_record(audited=True, audit_note="denetlendi")
        rec["class"] = "C"
        errors, warnings = build.validate([rec], SOURCES)
        self.assertEqual(errors, [])
        self.assertEqual([w for w in warnings if "class" in w], [])

    def test_expected_class_rule(self):
        self.assertEqual(build.expected_class(11, 1, 0), "A")
        self.assertEqual(build.expected_class(8, 3, 2), "A")   # relevance=3, novelty>=2
        self.assertEqual(build.expected_class(8, 2, 2), "B")
        self.assertEqual(build.expected_class(6, 1, 1), "C")

    def test_source_needs_http_url(self):
        bad = dict(SOURCES[0], url="ftp://x")
        errors, _ = build.validate([base_record()], [bad])
        self.assertTrue(any("url" in e for e in errors))

    def test_source_enums_and_unique_id(self):
        bad_type = dict(SOURCES[0], type="blogpost")
        errors, _ = build.validate([base_record()], [bad_type])
        self.assertTrue(any("type" in e for e in errors))
        errors, _ = build.validate([base_record()], [SOURCES[0], dict(SOURCES[1], id=SOURCES[0]["id"])])
        self.assertTrue(any("id" in e for e in errors))

    def test_a_date_that_is_not_a_date_is_an_error(self):
        errors, _ = build.validate([base_record(scored_at="not-a-date")], SOURCES)
        self.assertTrue(any("scored_at" in e for e in errors), errors)

    def test_an_impossible_calendar_date_is_an_error(self):
        """2026-02-30 matches YYYY-MM-DD and is still not a day."""
        errors, _ = build.validate([base_record(first_seen="2026-02-30")], SOURCES)
        self.assertTrue(any("first_seen" in e for e in errors), errors)

    def test_an_unknown_rubric_version_is_an_error(self):
        errors, _ = build.validate([base_record(rubric_version="banana")], SOURCES)
        self.assertTrue(any("rubric_version" in e for e in errors), errors)
        errors, _ = build.validate([base_record(rubric_version=99)], SOURCES)
        self.assertTrue(any("rubric_version" in e for e in errors), errors)

    def test_a_meta_without_its_fields_is_an_error(self):
        errors, _ = build.validate([base_record(meta={})], SOURCES)
        self.assertTrue(any("meta" in e for e in errors), errors)

    def test_a_meta_field_of_the_wrong_type_is_an_error(self):
        rec = base_record()
        rec["meta"] = dict(rec["meta"], stars="12")
        errors, _ = build.validate([rec], SOURCES)
        self.assertTrue(any("meta.stars" in e for e in errors), errors)
        rec["meta"] = dict(base_record()["meta"], topics="jev")
        errors, _ = build.validate([rec], SOURCES)
        self.assertTrue(any("meta.topics" in e for e in errors), errors)

    def test_a_repo_name_that_is_not_owner_slash_name_is_an_error(self):
        errors, _ = build.validate([base_record(repo="a b/one")], SOURCES)
        self.assertTrue(any("repo" in e for e in errors), errors)

    def test_question_types_must_be_a_list_without_repeats(self):
        errors, _ = build.validate([base_record(question_types="choice")], SOURCES)
        self.assertTrue(any("question_types" in e for e in errors), errors)
        errors, _ = build.validate(
            [base_record(question_types=["choice", "choice"])], SOURCES)
        self.assertTrue(any("question_types" in e for e in errors), errors)

    def test_audited_must_be_a_boolean_and_texts_must_be_strings(self):
        errors, _ = build.validate([base_record(audited="yes")], SOURCES)
        self.assertTrue(any("audited" in e for e in errors), errors)
        errors, _ = build.validate([base_record(summary_tr=12)], SOURCES)
        self.assertTrue(any("summary_tr" in e for e in errors), errors)

    def test_schema_and_code_agree_on_the_field_set_and_the_constraints(self):
        """data/schema/repo.schema.json describes what validate() enforces."""
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(root, "data", "schema", "repo.schema.json"),
                  encoding="utf-8") as fh:
            schema = json.load(fh)
        props = schema["properties"]
        self.assertEqual(set(props), set(build.RECORD_FIELDS))
        self.assertEqual(set(schema["required"]), set(build.RECORD_FIELDS))
        self.assertEqual(set(props["category"]["enum"]), set(build.CATEGORY_TITLES))
        self.assertEqual(set(props["class"]["enum"]), set(build.CLASSES))
        self.assertEqual(set(props["question_types"]["items"]["enum"]),
                         set(build.QUESTION_TYPES))
        self.assertEqual(props["rubric_version"]["enum"],
                         sorted(build.RUBRIC_VERSIONS))
        self.assertEqual(set(props["meta"]["required"]),
                         set(build.META_FIELD_TYPES))
        self.assertEqual(set(props["meta"]["properties"]),
                         set(build.META_FIELD_TYPES))
        self.assertEqual({name for name, _legacy in build.META_KEYS},
                         set(build.META_FIELD_TYPES))
        self.assertEqual(set(props["scores"]["properties"]),
                         {name for name, _l, _s in build.SCORE_KEYS})
        for field in ("first_seen", "scored_at"):
            self.assertEqual(props[field]["pattern"], "^\\d{4}-\\d{2}-\\d{2}$")

    def test_schema_files_describe_the_real_fields(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(root, "data", "schema", "repo.schema.json"),
                  encoding="utf-8") as fh:
            schema = json.load(fh)
        for field in base_record():
            self.assertIn(field, schema["properties"], field)
        with open(os.path.join(root, "data", "schema", "source.schema.json"),
                  encoding="utf-8") as fh:
            src = json.load(fh)
        for field in SOURCES[0]:
            self.assertIn(field, src["properties"], field)


if __name__ == "__main__":
    unittest.main()
