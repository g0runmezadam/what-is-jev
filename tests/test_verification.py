"""The re-run pipeline: sampling, statistics, verdicts, resume, key hygiene.

Nothing here touches the network. Every call goes through a fake transport, so
the suite runs on a machine with no API key at all.
"""

import hashlib
import json
import os
import sys
import unittest

from helpers import BaseCase, write

VERIFICATION = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "verification")
if VERIFICATION not in sys.path:
    sys.path.insert(0, VERIFICATION)

import client
import sampling
import stats
import runner


# --------------------------------------------------------------------------
# sampling

class SamplingTest(unittest.TestCase):
    def items(self, n=200):
        return [{"id": "row-%d" % i, "stratum": "a" if i % 3 else "b"}
                for i in range(n)]

    def test_the_same_seed_gives_the_same_sample(self):
        first = sampling.sample(self.items(), 20, seed=20260920)
        second = sampling.sample(self.items(), 20, seed=20260920)
        self.assertEqual([r["id"] for r in first], [r["id"] for r in second])
        self.assertEqual(len(first), 20)

    def test_a_different_seed_gives_a_different_sample(self):
        first = sampling.sample(self.items(), 20, seed=1)
        second = sampling.sample(self.items(), 20, seed=2)
        self.assertNotEqual([r["id"] for r in first], [r["id"] for r in second])

    def test_the_sample_does_not_depend_on_the_input_order(self):
        forward = sampling.sample(self.items(), 20, seed=7)
        backward = sampling.sample(list(reversed(self.items())), 20, seed=7)
        self.assertEqual(sorted(r["id"] for r in forward),
                         sorted(r["id"] for r in backward))

    def test_the_sample_does_not_depend_on_the_process_hash_seed(self):
        """The order comes from a digest, never from Python's own hashing."""
        ids = [r["id"] for r in sampling.sample(self.items(), 5, seed=3)]
        self.assertEqual(ids, sampling.deterministic_order(
            self.items(), seed=3)[:5] and
            [r["id"] for r in sampling.sample(self.items(), 5, seed=3)])

    def test_asking_for_more_than_there_is_returns_everything(self):
        self.assertEqual(len(sampling.sample(self.items(10), 99, seed=1)), 10)

    def test_a_stratified_sample_keeps_every_stratum(self):
        out = sampling.sample(self.items(90), 30, seed=5, stratum="stratum")
        seen = {r["stratum"] for r in out}
        self.assertEqual(seen, {"a", "b"})
        self.assertEqual(len(out), 30)

    def test_a_stratified_sample_is_also_deterministic(self):
        a = sampling.sample(self.items(90), 30, seed=5, stratum="stratum")
        b = sampling.sample(self.items(90), 30, seed=5, stratum="stratum")
        self.assertEqual([r["id"] for r in a], [r["id"] for r in b])


# --------------------------------------------------------------------------
# statistics

class WilsonTest(unittest.TestCase):
    def test_a_known_interval(self):
        lo, hi = stats.wilson(639, 662)
        self.assertAlmostEqual(lo, 0.950, places=2)
        self.assertAlmostEqual(hi, 0.977, places=2)

    def test_the_interval_brackets_the_observed_share(self):
        lo, hi = stats.wilson(50, 100)
        self.assertLess(lo, 0.5)
        self.assertGreater(hi, 0.5)

    def test_an_empty_sample_has_no_interval(self):
        self.assertEqual(stats.wilson(0, 0), (0.0, 1.0))

    def test_a_perfect_sample_still_has_a_lower_bound_below_one(self):
        lo, hi = stats.wilson(72, 72)
        self.assertLess(lo, 1.0)
        self.assertEqual(hi, 1.0)


class MetricsTest(unittest.TestCase):
    def test_roc_auc_on_a_perfect_ranking(self):
        self.assertEqual(stats.roc_auc([0.9, 0.8, 0.2, 0.1], [1, 1, 0, 0]), 1.0)

    def test_roc_auc_on_a_reversed_ranking(self):
        self.assertEqual(stats.roc_auc([0.1, 0.2, 0.8, 0.9], [1, 1, 0, 0]), 0.0)

    def test_roc_auc_counts_a_tie_as_half(self):
        self.assertEqual(stats.roc_auc([0.5, 0.5], [1, 0]), 0.5)

    def test_roc_auc_without_both_classes_is_undefined(self):
        self.assertIsNone(stats.roc_auc([0.1, 0.9], [1, 1]))

    def test_confusion_at_a_threshold(self):
        got = stats.confusion([0.9, 0.6, 0.4, 0.1], [1, 0, 1, 0], 0.5)
        self.assertEqual((got["tp"], got["fp"], got["fn"], got["tn"]), (1, 1, 1, 1))
        self.assertAlmostEqual(got["accuracy"], 0.5)
        self.assertAlmostEqual(got["precision"], 0.5)
        self.assertAlmostEqual(got["recall"], 0.5)

    def test_ece_is_zero_for_a_perfectly_calibrated_run(self):
        probs = [0.0] * 10 + [1.0] * 10
        labels = [0] * 10 + [1] * 10
        self.assertAlmostEqual(stats.ece(probs, labels, 10), 0.0)

    def test_ece_is_one_when_every_claim_is_backwards(self):
        probs = [1.0] * 10
        labels = [0] * 10
        self.assertAlmostEqual(stats.ece(probs, labels, 10), 1.0)


class VerdictTest(unittest.TestCase):
    """The acceptance rule, fixed in the job file before any live call."""

    def test_a_reported_share_inside_our_interval_is_reproduced(self):
        got = stats.judge_proportion(reported=0.965, k=639, n=662, tolerance=0.02)
        self.assertEqual(got["verdict"], "reproduced")

    def test_a_reported_share_just_outside_is_partially_reproduced(self):
        got = stats.judge_proportion(reported=0.99, k=639, n=662, tolerance=0.05)
        self.assertEqual(got["verdict"], "partially reproduced")

    def test_a_reported_share_far_outside_is_not_reproduced(self):
        got = stats.judge_proportion(reported=0.60, k=639, n=662, tolerance=0.05)
        self.assertEqual(got["verdict"], "not reproduced")

    def test_the_judgement_carries_the_numbers_it_used(self):
        got = stats.judge_proportion(reported=0.965, k=639, n=662, tolerance=0.02)
        self.assertEqual(got["n"], 662)
        self.assertAlmostEqual(got["observed"], 639 / 662)
        self.assertEqual(len(got["ci95"]), 2)

    def test_an_absolute_metric_uses_its_own_tolerance(self):
        self.assertEqual(
            stats.judge_absolute(reported=0.9927, observed=0.9900,
                                 tolerance=0.01, partial=0.05)["verdict"],
            "reproduced")
        self.assertEqual(
            stats.judge_absolute(reported=0.9927, observed=0.96,
                                 tolerance=0.01, partial=0.05)["verdict"],
            "partially reproduced")
        self.assertEqual(
            stats.judge_absolute(reported=0.9927, observed=0.5,
                                 tolerance=0.01, partial=0.05)["verdict"],
            "not reproduced")

    def test_a_hard_gate_admits_no_tolerance(self):
        self.assertEqual(stats.judge_gate(reported=0, observed=0)["verdict"],
                         "reproduced")
        self.assertEqual(stats.judge_gate(reported=0, observed=1)["verdict"],
                         "not reproduced")

    def test_a_missing_observation_is_not_a_pass(self):
        self.assertEqual(stats.judge_proportion(reported=0.9, k=0, n=0,
                                                tolerance=0.02)["verdict"],
                         "not run")


# --------------------------------------------------------------------------
# key handling

class FakeRegistry(dict):
    pass


class KeyTest(unittest.TestCase):
    SECRET = "sk-verification-test-0123456789"

    def setUp(self):
        client.forget_secrets()
        self.addCleanup(client.forget_secrets)

    def test_the_process_environment_wins(self):
        os.environ["JEV_TEST_KEY"] = self.SECRET
        self.addCleanup(os.environ.pop, "JEV_TEST_KEY", None)
        self.assertEqual(client.read_key("JEV_TEST_KEY"), self.SECRET)

    def test_a_missing_key_raises_without_naming_a_value(self):
        os.environ.pop("JEV_ABSENT_KEY", None)
        with self.assertRaises(client.KeyMissing) as caught:
            client.read_key("JEV_ABSENT_KEY", registry_reader=lambda name: None)
        self.assertIn("JEV_ABSENT_KEY", str(caught.exception))
        self.assertNotIn(self.SECRET, str(caught.exception))

    def test_a_remembered_secret_is_masked_everywhere(self):
        client.remember(self.SECRET)
        text = "Authorization: Bearer %s failed" % self.SECRET
        self.assertNotIn(self.SECRET, client.mask(text))
        self.assertIn("[redacted]", client.mask(text))

    def test_masking_also_catches_a_bearer_token_we_never_saw(self):
        blob = "Bearer sk-someone-elses-key-value-here"
        self.assertNotIn("sk-someone-elses-key-value-here", client.mask(blob))

    def test_the_error_of_a_failed_call_carries_no_key(self):
        client.remember(self.SECRET)

        def transport(url, headers, body, timeout):
            raise OSError("connect failed for Bearer " + self.SECRET)

        out = client.call({"a": "b"}, {"q": {"type": "boolean",
                                             "instructions": "i",
                                             "criteria": {"true": "t", "false": "f"}}},
                          transport=transport,
                          key_reader=lambda: self.SECRET)
        self.assertFalse(out["ok"])
        self.assertNotIn(self.SECRET, json.dumps(out))

    def test_the_request_body_renames_boolean_to_the_endpoint_spelling(self):
        body = client.build_body({"s": 1}, {"q": {"type": "boolean",
                                                 "instructions": "i",
                                                 "criteria": {"true": "t", "false": "f"}}})
        self.assertEqual(body["questions"]["q"]["type"], "noul")
        self.assertEqual(body["model"], client.MODEL)
        self.assertEqual(body["state"], {"s": 1})


class RetryTest(unittest.TestCase):
    QUESTIONS = {"q": {"type": "boolean", "instructions": "i",
                       "criteria": {"true": "t", "false": "f"}}}

    def ok_payload(self):
        return json.dumps({"model": "jev-1.13.0",
                           "answers": {"q": {"noul": 0.9, "confidence": 0.8}}})

    def test_an_overloaded_endpoint_is_retried_with_growing_waits(self):
        seen = []
        waits = []

        def transport(url, headers, body, timeout):
            seen.append(1)
            if len(seen) < 3:
                return 429, "busy"
            return 200, self.ok_payload()

        out = client.call({}, self.QUESTIONS, transport=transport,
                          key_reader=lambda: "k", sleep=waits.append)
        self.assertTrue(out["ok"])
        self.assertEqual(len(seen), 3)
        self.assertEqual(len(waits), 2)
        self.assertGreater(waits[1], waits[0])

    def test_retries_stop_and_the_failure_is_reported(self):
        def transport(url, headers, body, timeout):
            return 529, "still busy"

        out = client.call({}, self.QUESTIONS, transport=transport,
                          key_reader=lambda: "k", sleep=lambda s: None,
                          max_attempts=3)
        self.assertFalse(out["ok"])
        self.assertEqual(out["status"], 529)

    def test_a_plain_error_is_not_retried(self):
        seen = []

        def transport(url, headers, body, timeout):
            seen.append(1)
            return 400, "bad request"

        out = client.call({}, self.QUESTIONS, transport=transport,
                          key_reader=lambda: "k", sleep=lambda s: None)
        self.assertFalse(out["ok"])
        self.assertEqual(len(seen), 1)

    def test_a_good_answer_comes_back_with_its_model_version(self):
        out = client.call({}, self.QUESTIONS,
                          transport=lambda *a: (200, self.ok_payload()),
                          key_reader=lambda: "k")
        self.assertTrue(out["ok"])
        self.assertEqual(out["model"], "jev-1.13.0")
        self.assertEqual(out["answers"]["q"]["noul"], 0.9)


# --------------------------------------------------------------------------
# the runner

def tiny_job(**kw):
    job = {
        "id": "tiny",
        "source": {"repo": "e/f", "commit": "0" * 40,
                   "url": "https://github.com/e/f"},
        "seed": 1,
        "sample": {"n": 4},
        "max_calls": 100,
        "criteria": [{"metric": "accuracy", "kind": "proportion",
                      "reported": 0.5, "tolerance": 0.25}],
    }
    job.update(kw)
    return job


def tiny_items():
    return [{"id": "i-%d" % i, "label": i % 2,
             "state": {"text": "third party text %d" % i},
             "text_sha256": hashlib.sha256(("t%d" % i).encode()).hexdigest()}
            for i in range(4)]


class RunnerTest(BaseCase):
    QUESTIONS = {"q": {"type": "boolean", "instructions": "i",
                       "criteria": {"true": "t", "false": "f"}}}

    def responder(self, calls):
        def call(state, questions, **kw):
            calls.append(state)
            return {"ok": True, "status": 200, "model": "jev-1.13.0",
                    "latency_ms": 5,
                    "answers": {"q": {"noul": 0.9, "confidence": 0.7}}}
        return call

    def test_a_run_writes_one_raw_line_per_item(self):
        root = self.tmproot()
        calls = []
        runner.run_job(tiny_job(), tiny_items(), self.QUESTIONS, root,
                       caller=self.responder(calls))
        lines = self.raw(root)
        self.assertEqual(len(lines), 4)
        self.assertEqual(len(calls), 4)

    def raw(self, root, job_id="tiny"):
        path = os.path.join(root, "results", job_id, "raw.jsonl")
        with open(path, encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]

    def test_no_third_party_text_reaches_the_raw_record(self):
        root = self.tmproot()
        runner.run_job(tiny_job(), tiny_items(), self.QUESTIONS, root,
                       caller=self.responder([]))
        blob = json.dumps(self.raw(root))
        self.assertNotIn("third party text", blob)
        self.assertIn("i-0", blob)
        self.assertIn("request_sha256", self.raw(root)[0])

    def test_a_second_run_resumes_instead_of_paying_twice(self):
        root = self.tmproot()
        first, second = [], []
        runner.run_job(tiny_job(max_calls=2), tiny_items(), self.QUESTIONS, root,
                       caller=self.responder(first))
        self.assertEqual(len(first), 2)
        runner.run_job(tiny_job(), tiny_items(), self.QUESTIONS, root,
                       caller=self.responder(second))
        self.assertEqual(len(second), 2)
        self.assertEqual(len(self.raw(root)), 4)
        self.assertEqual(sorted(r["item"] for r in self.raw(root)),
                         ["i-0", "i-1", "i-2", "i-3"])

    def test_the_call_ceiling_is_hard(self):
        root = self.tmproot()
        calls = []
        runner.run_job(tiny_job(max_calls=1), tiny_items(), self.QUESTIONS, root,
                       caller=self.responder(calls))
        self.assertEqual(len(calls), 1)

    def test_a_half_written_raw_file_does_not_stop_the_resume(self):
        root = self.tmproot()
        runner.run_job(tiny_job(max_calls=2), tiny_items(), self.QUESTIONS, root,
                       caller=self.responder([]))
        path = os.path.join(root, "results", "tiny", "raw.jsonl")
        with open(path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write('{"item": "i-2", "answ')
        runner.run_job(tiny_job(), tiny_items(), self.QUESTIONS, root,
                       caller=self.responder([]))
        items = sorted(r["item"] for r in self.raw(root))
        self.assertEqual(items, ["i-0", "i-1", "i-2", "i-3"])

    def test_a_failed_call_is_recorded_and_not_counted_as_an_answer(self):
        root = self.tmproot()

        def failing(state, questions, **kw):
            return {"ok": False, "status": 500, "detail": "server said no",
                    "latency_ms": 1, "answers": {}, "model": None}

        summary = runner.run_job(tiny_job(), tiny_items(), self.QUESTIONS, root,
                                 caller=failing)
        self.assertEqual(summary["calls"], 4)
        self.assertEqual(summary["answered"], 0)
        self.assertEqual(summary["failed"], 4)

    def test_the_summary_carries_the_verdict_and_the_model_version(self):
        root = self.tmproot()
        summary = runner.run_job(tiny_job(), tiny_items(), self.QUESTIONS, root,
                                 caller=self.responder([]),
                                 scorer=lambda records, items: {"accuracy": 0.5})
        self.assertEqual(summary["model_versions"], ["jev-1.13.0"])
        verdicts = {c["metric"]: c["verdict"] for c in summary["criteria"]}
        self.assertEqual(verdicts["accuracy"], "reproduced")
        self.assertIn("verdict", summary)
        self.assertTrue(os.path.exists(
            os.path.join(root, "results", "tiny", "summary.json")))

    def test_the_overall_verdict_is_the_weakest_of_its_parts(self):
        self.assertEqual(runner.overall(["reproduced", "partially reproduced"]),
                         "partially reproduced")
        self.assertEqual(runner.overall(["reproduced", "reproduced"]),
                         "reproduced")
        self.assertEqual(runner.overall(["reproduced", "not reproduced"]),
                         "not reproduced")
        self.assertEqual(runner.overall([]), "not run")


# --------------------------------------------------------------------------
# job files and the documents around them

class JobFileTest(unittest.TestCase):
    ROOT = os.path.dirname(VERIFICATION)

    def job_files(self):
        folder = os.path.join(VERIFICATION, "jobs")
        if not os.path.isdir(folder):
            return []
        return [os.path.join(folder, n) for n in sorted(os.listdir(folder))
                if n.endswith(".json")]

    def test_there_is_at_least_one_job(self):
        self.assertTrue(self.job_files())

    def test_every_job_pins_a_commit_and_fixes_its_acceptance_rule(self):
        for path in self.job_files():
            with open(path, encoding="utf-8") as fh:
                job = json.load(fh)
            name = os.path.basename(path)
            self.assertEqual(len(job["source"]["commit"]), 40, name)
            self.assertTrue(job["criteria"], name)
            for crit in job["criteria"]:
                self.assertIn(crit["kind"],
                              ("proportion", "absolute", "gate"), name)
                self.assertIn("reported", crit)
                self.assertIn("reported_at", crit)
            self.assertIn(job["lang"], ("en", "de", "mixed"), name)
            self.assertIn("license", job["source"], name)

    def test_every_job_url_is_pinned_to_its_commit(self):
        for path in self.job_files():
            with open(path, encoding="utf-8") as fh:
                job = json.load(fh)
            for ref in job.get("files", []):
                self.assertIn(job["source"]["commit"], ref["url"],
                              os.path.basename(path))
                self.assertEqual(len(ref["sha256"]), 64)


class PrivacyTest(unittest.TestCase):
    """The published repository must not carry a local path or an address."""

    def documents(self):
        import build
        out = []
        for folder in (VERIFICATION, os.path.join(
                os.path.dirname(VERIFICATION), "tr", "verification")):
            for base, _dirs, names in os.walk(folder):
                for name in names:
                    if name.endswith((".md", ".json", ".py")):
                        out.append(os.path.join(base, name))
        return out, build

    def test_no_document_leaks_a_local_path_or_an_address(self):
        documents, build = self.documents()
        self.assertTrue(documents)
        for path in documents:
            with open(path, encoding="utf-8") as fh:
                for number, line in enumerate(fh, 1):
                    self.assertEqual(build.privacy_hits(line), [],
                                     "%s:%d" % (os.path.basename(path), number))

    def test_the_cache_folder_is_ignored(self):
        with open(os.path.join(os.path.dirname(VERIFICATION), ".gitignore"),
                  encoding="utf-8") as fh:
            self.assertIn("ham/", fh.read())


if __name__ == "__main__":
    unittest.main()
