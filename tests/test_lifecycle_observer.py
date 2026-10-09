"""Test only the read-only lifecycle observation and its fail-closed boundary."""
import importlib.util
import pathlib
import unittest

p = pathlib.Path(__file__).resolve().parents[1] / "scripts/lifecycle_acceptance_observer.py"
spec = importlib.util.spec_from_file_location("lifecycle_observer", p)
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


class Fixture:
    def __init__(self, *, include_root_plan=False):
        self.calls = []
        self.include_root_plan = include_root_plan

    def get(self, endpoint):
        self.calls.append(endpoint)
        if endpoint == "":
            return {"full_name": M.TARGET, "private": True}
        if endpoint in ("/issues/1", "/issues/2", "/issues/3"):
            n = endpoint.split("/")[-1]
            return {"body": "Parent: #1" if n != "1" else "Owner seed SYNTHETIC",
                    "html_url": "https://github.com/" + M.TARGET + "/issues/" + n}
        raise AssertionError("unexpected fake endpoint " + endpoint)

    def all_pages(self, endpoint):
        self.calls.append(endpoint)
        if endpoint.startswith("/issues/"):
            if endpoint.startswith("/issues/1/") and self.include_root_plan:
                return [{"body": "IMPLEMENTATION_PLAN"}]
            return []
        if endpoint.startswith("/pulls?"):
            return [{"number": 5, "title": "Static infrastructure PR",
                     "head": {"sha": "a" * 40, "ref": "lab/t03r"},
                     "html_url": "https://github.com/" + M.TARGET + "/pull/5",
                     "draft": True}]
        raise AssertionError("unexpected fake collection " + endpoint)

    def text(self, path):
        self.calls.append(path)
        return {"docs/owner-intent.md": "Owner seed SYNTHETIC",
                ".relay/graph.yaml": "synthetic graph",
                ".relay/issue-map.json": "{}"}.get(path)


class LifecycleRedOracle(unittest.TestCase):
    def test_no_live_pipeline_never_qualifies(self):
        api = Fixture()
        model = M.inspect(api)
        self.assertEqual("RED_NOT_END_TO_END_QUALIFIED", model["status"])
        self.assertEqual("LAB_ONLY_PASS", model["results"]["L00"]["status"])
        self.assertEqual("MISSING", model["results"]["L01"]["status"])
        self.assertEqual("MISSING", model["results"]["L03"]["status"])
        self.assertEqual("HOLD_NO_APPROVED_GRAPH", model["results"]["L04"]["status"])
        self.assertEqual("MISSING", model["results"]["L05"]["status"])
        self.assertEqual("MISSING", model["results"]["L06"]["status"])
        self.assertEqual("MISSING", model["results"]["L07"]["status"])
        self.assertTrue(model["no_delp_progress_computed"])
        self.assertEqual(10, len(model["results"]))

    def test_root_plan_comment_never_certifies_decomposition(self):
        model = M.inspect(Fixture(include_root_plan=True))
        self.assertEqual("NEEDS_NATIVE_REPLAY", model["results"]["L01"]["status"])
        self.assertEqual("NEEDS_NATIVE_REPLAY", model["results"]["L02"]["status"])
        self.assertEqual("RED_NOT_END_TO_END_QUALIFIED", model["status"])

    def test_wrong_or_public_repository_rejected(self):
        for metadata in ({"full_name": "reallaksh19/Common", "private": True},
                         {"full_name": M.TARGET, "private": False}):
            class Wrong(Fixture):
                def get(self, endpoint):
                    if endpoint == "":
                        return metadata
                    return super().get(endpoint)
            with self.assertRaisesRegex(M.ProviderFailure, "wrong repository or public"):
                M.inspect(Wrong())

    def test_missing_provider_token_fail_closed(self):
        with self.assertRaisesRegex(M.ProviderFailure, "GITHUB_TOKEN is missing"):
            M.GitHubReadOnly("")


if __name__ == "__main__":
    unittest.main()
