"""update.py: discovery and metadata refresh against a fake gh runner."""

import json
import os
import unittest

from helpers import BaseCase, write, jsonl
from test_schema import base_record

import update


def gh_meta(repo, **kw):
    owner, name = repo.split("/")
    payload = {
        "full_name": repo, "html_url": "https://github.com/" + repo,
        "description": "d-" + name, "stargazers_count": 7, "forks_count": 1,
        "language": "Python", "license": {"spdx_id": "MIT"},
        "created_at": "2026-01-01T00:00:00Z", "pushed_at": "2026-09-01T00:00:00Z",
        "archived": False, "fork": False, "topics": ["jev"],
    }
    payload.update(kw)
    return payload


class FakeGh:
    """Records every call; answers from a canned table. Never touches the network."""

    def __init__(self, search=(), meta=None, readme=None, missing=()):
        self.search = list(search)
        self.meta = meta or {}
        self.readme = readme or {}
        self.missing = set(missing)
        self.calls = []

    def __call__(self, args):
        self.calls.append(list(args))
        joined = " ".join(args)
        if "search/repositories" in joined:
            return 0, json.dumps({"items": [gh_meta(r) for r in self.search]}), ""
        for repo in list(self.meta) + list(self.missing) + list(self.readme):
            if "repos/" + repo in joined:
                if repo in self.missing:
                    return 1, "", "gh: Not Found (HTTP 404)"
                if joined.rstrip().endswith("/readme") or "/readme" in joined:
                    return 0, self.readme.get(repo, "# " + repo), ""
                return 0, json.dumps(self.meta[repo]), ""
        return 1, "", "gh: Not Found (HTTP 404)"


class FailingGh:
    """A gh that answers the search with an error. Records every call."""

    def __init__(self, code=1, err="gh: API rate limit exceeded (HTTP 403)",
                 succeed_after=None):
        self.code = code
        self.err = err
        self.succeed_after = succeed_after
        self.calls = []

    def __call__(self, args):
        self.calls.append(list(args))
        joined = " ".join(args)
        if "search/repositories" in joined:
            searches = sum(1 for c in self.calls if "search/repositories" in " ".join(c))
            if self.succeed_after is not None and searches > self.succeed_after:
                return 0, json.dumps({"items": []}), ""
            return self.code, "", self.err
        return 1, "", "gh: Not Found (HTTP 404)"


class NameSafetyTest(BaseCase):
    def test_a_traversal_name_is_not_a_repository_name(self):
        for bad in ("..\\..\\data\\pwn", "../../data/pwn", "a/../../x",
                    "a\\b", "/etc/passwd", "a/one extra", "a//one",
                    "-a/one", "a/one\n", ""):
            self.assertFalse(update.valid_repo_name(bad), bad)

    def test_ordinary_names_are_accepted(self):
        for good in ("a/one", "AkashPriyadarshii/jev-scout", "0xNatoshi/jev.codex_router",
                     "24601/Augustus"):
            self.assertTrue(update.valid_repo_name(good), good)

    def test_a_path_outside_ham_is_refused_even_if_a_name_slips_through(self):
        root = self.tmproot()
        with self.assertRaises(ValueError):
            update.ham_path(root, "meta", "..\\..\\data\\pwn" + ".json")
        inside = update.ham_path(root, "meta", "a@one.json")
        self.assertTrue(os.path.realpath(inside).startswith(
            os.path.realpath(os.path.join(root, "ham")) + os.sep))


class UpdateTest(BaseCase):
    def root_with(self, records):
        root = self.tmproot()
        write(os.path.join(root, "data", "repos.jsonl"),
              "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n"
                      for r in records))
        return root

    def test_only_unknown_repos_land_in_pending(self):
        root = self.root_with([base_record()])
        gh = FakeGh(search=["a/one", "n/new"], meta={"n/new": gh_meta("n/new"),
                                                     "a/one": gh_meta("a/one")})
        report = update.run(root, runner=gh)
        with open(os.path.join(root, "data", "pending.txt"), encoding="utf-8") as fh:
            pending = [l.strip() for l in fh if l.strip()]
        self.assertEqual(pending, ["n/new"])
        self.assertEqual(report["new"], ["n/new"])

    def test_known_repo_match_is_case_insensitive(self):
        root = self.root_with([base_record()])
        gh = FakeGh(search=["A/ONE"], meta={"A/ONE": gh_meta("A/ONE")})
        report = update.run(root, runner=gh)
        self.assertEqual(report["new"], [])

    def test_manual_list_is_merged_and_comments_ignored(self):
        root = self.root_with([base_record()])
        write(os.path.join(root, "data", "manual.txt"),
              "# elle eklenenler\n\nm/one\nm/two\n")
        gh = FakeGh(search=[], meta={"m/one": gh_meta("m/one"),
                                     "m/two": gh_meta("m/two")})
        report = update.run(root, runner=gh)
        self.assertEqual(report["new"], ["m/one", "m/two"])

    def test_new_repo_readme_is_written_under_ham_only(self):
        root = self.root_with([base_record()])
        gh = FakeGh(search=["n/new"], meta={"n/new": gh_meta("n/new")},
                    readme={"n/new": "# new repo\n" + "x" * 20000})
        update.run(root, runner=gh)
        path = os.path.join(root, "ham", "readme", "n@new.md")
        self.assertTrue(os.path.exists(path))
        with open(path, encoding="utf-8") as fh:
            body = fh.read()
        self.assertLessEqual(len(body), update.README_LIMIT)
        self.assertFalse(os.path.exists(os.path.join(root, "data", "readme")))

    def test_existing_metadata_is_refreshed(self):
        rec = base_record()
        rec["meta"]["stars"] = 0
        root = self.root_with([rec])
        gh = FakeGh(search=[], meta={"a/one": gh_meta("a/one", stargazers_count=99)})
        update.run(root, runner=gh)
        with open(os.path.join(root, "data", "repos.jsonl"), encoding="utf-8") as fh:
            rows = [json.loads(l) for l in fh if l.strip()]
        self.assertEqual(rows[0]["meta"]["stars"], 99)
        self.assertEqual(rows[0]["meta"]["license"], "MIT")

    def test_404_marks_gone_and_keeps_the_row(self):
        root = self.root_with([base_record()])
        gh = FakeGh(search=[], missing=["a/one"])
        report = update.run(root, runner=gh)
        with open(os.path.join(root, "data", "repos.jsonl"), encoding="utf-8") as fh:
            rows = [json.loads(l) for l in fh if l.strip()]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "gone")
        self.assertEqual(report["gone"], ["a/one"])

    def test_a_repo_that_came_back_is_active_again(self):
        rec = base_record(status="gone")
        root = self.root_with([rec])
        gh = FakeGh(search=[], meta={"a/one": gh_meta("a/one")})
        update.run(root, runner=gh)
        with open(os.path.join(root, "data", "repos.jsonl"), encoding="utf-8") as fh:
            rows = [json.loads(l) for l in fh if l.strip()]
        self.assertEqual(rows[0]["status"], "active")

    def test_update_never_scores_and_never_calls_a_model(self):
        root = self.root_with([base_record()])
        gh = FakeGh(search=["n/new"], meta={"n/new": gh_meta("n/new")})
        update.run(root, runner=gh)
        for call in gh.calls:
            joined = " ".join(call).lower()
            for banned in ("claude", "openai", "anthropic", "typesafe", "systemone"):
                self.assertNotIn(banned, joined)

    def test_a_hostile_manual_entry_writes_nothing_outside_ham(self):
        root = self.root_with([base_record()])
        write(os.path.join(root, "data", "manual.txt"),
              "..\\..\\data\\pwn\na/../../x\nm/ok\n")
        gh = FakeGh(search=[], meta={"m/ok": gh_meta("m/ok")})
        report = update.run(root, runner=gh)
        self.assertEqual(report["new"], ["m/ok"])
        self.assertEqual(len(report["rejected"]), 2)
        self.assertFalse(os.path.exists(os.path.join(root, "data", "pwn.json")))
        self.assertFalse(os.path.exists(os.path.join(root, "data", "pwn")))

    def test_a_hostile_search_result_is_rejected_too(self):
        root = self.root_with([base_record()])
        gh = FakeGh(search=["../pwn"])
        report = update.run(root, runner=gh)
        self.assertEqual(report["new"], [])
        self.assertTrue(report["rejected"])

    def test_a_failed_search_leaves_pending_alone_and_reports(self):
        root = self.root_with([base_record()])
        write(os.path.join(root, "data", "pending.txt"), "keep/me\n")
        report = update.run(root, runner=FailingGh(), sleep=lambda s: None)
        self.assertTrue(report["search_failed"])
        with open(os.path.join(root, "data", "pending.txt"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "keep/me\n")

    def test_a_failed_search_exits_1(self):
        root = self.root_with([base_record()])
        self.assertEqual(
            update.main([], root=root, runner=FailingGh(), sleep=lambda s: None), 1)

    def test_a_rate_limited_search_is_retried_with_the_injected_wait(self):
        root = self.root_with([base_record()])
        waits = []
        gh = FailingGh(succeed_after=2)
        report = update.run(root, runner=gh, sleep=waits.append)
        self.assertFalse(report["search_failed"])
        self.assertEqual(len(waits), 2)
        self.assertTrue(all(w > 0 for w in waits), waits)

    def test_a_search_that_keeps_failing_gives_up_after_the_retries(self):
        root = self.root_with([base_record()])
        waits = []
        gh = FailingGh()
        report = update.run(root, runner=gh, sleep=waits.append)
        self.assertTrue(report["search_failed"])
        searches = [c for c in gh.calls if "search/repositories" in " ".join(c)]
        self.assertEqual(len(searches), update.SEARCH_RETRIES + 1)

    def test_a_non_rate_limit_search_error_is_not_retried(self):
        root = self.root_with([base_record()])
        waits = []
        gh = FailingGh(err="gh: Bad credentials (HTTP 401)")
        report = update.run(root, runner=gh, sleep=waits.append)
        self.assertTrue(report["search_failed"])
        self.assertEqual(waits, [])

    def test_the_runner_is_injectable_so_tests_stay_offline(self):
        gh = FakeGh(search=[])
        root = self.root_with([base_record()])
        update.run(root, runner=gh)
        self.assertTrue(gh.calls)
        self.assertTrue(all(call[0] == "api" or call[0] == "search" for call in gh.calls),
                        gh.calls)


if __name__ == "__main__":
    unittest.main()
