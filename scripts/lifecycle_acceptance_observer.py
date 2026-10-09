#!/usr/bin/env python3
"""Non-authorizing provider observation oracle for V3.5 LC0.

This is deliberately NOT a DELP progress calculator, GitHub writer, or
substitute for native V3.2 C6 / V3.5 cold successor verification.
Only a native live test can promote NEEDS_NATIVE_REPLAY to PASS.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

TARGET = "reallaksh19/relay-v35-e2e-lab"
UA = "v35-lifecycle-observer/1.0"
ROOT = "https://api.github.com/repos/" + TARGET
GATES = ("L00", "L01", "L02", "L03", "L04", "L05", "L06", "L07", "L08", "L09")


class ProviderFailure(RuntimeError):
    pass


class GitHubReadOnly:
    def __init__(self, token: str):
        if not token:
            raise ProviderFailure("GITHUB_TOKEN is missing; provider is UNKNOWN, never zero")
        self.token = token
        self.requests = []

    def get(self, endpoint: str):
        url = ROOT + endpoint
        req = urllib.request.Request(
            url, headers={
                "Authorization": "Bearer " + self.token,
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": UA,
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=25) as response:
                raw = response.read()
                self.requests.append({"url": url, "status": response.status,
                                      "sha256": hashlib.sha256(raw).hexdigest()})
                return json.loads(raw)
        except urllib.error.HTTPError as exc:
            if exc.code == 404 and endpoint.startswith("/contents/"):
                self.requests.append({"url": url, "status": 404})
                return None
            raise ProviderFailure("provider HTTP {0} at {1}".format(exc.code, endpoint)) from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ProviderFailure("provider UNOBSERVED at {0}: {1}".format(endpoint, exc)) from exc

    def all_pages(self, endpoint: str):
        # GitHub REST uses page numbers here. Never call a truncated first page COMPLETE.
        output = []
        for page in range(1, 21):
            separator = "&" if "?" in endpoint else "?"
            batch = self.get(endpoint + separator + "per_page=100&page=" + str(page))
            if not isinstance(batch, list):
                raise ProviderFailure("provider list not returned at " + endpoint)
            output.extend(batch)
            if len(batch) < 100:
                return output
        raise ProviderFailure("provider pagination exceeded bound: " + endpoint)

    def text(self, path: str):
        value = self.get("/contents/" + urllib.parse.quote(path, safe="/"))
        if value is None:
            return None
        if not isinstance(value, dict) or value.get("encoding") != "base64":
            raise ProviderFailure("unverifiable content representation for " + path)
        try:
            return base64.b64decode(value["content"]).decode("utf-8")
        except (ValueError, UnicodeDecodeError, KeyError) as exc:
            raise ProviderFailure("invalid provider content " + path) from exc


def _sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def inspect(api):
    identity = api.get("")
    if identity.get("full_name") != TARGET or not identity.get("private"):
        raise ProviderFailure("wrong repository or public lab, refuse audit")
    issues = {i: api.get("/issues/" + str(i)) for i in (1, 2, 3)}
    comments = {i: api.all_pages("/issues/" + str(i) + "/comments") for i in issues}
    pull_requests = api.all_pages("/pulls?state=all")
    owner_source = api.text("docs/owner-intent.md")
    graph_source = api.text(".relay/graph.yaml")
    issue_map_source = api.text(".relay/issue-map.json")
    index_source = api.text("relay/SESSION_INDEX_V1.jsonl")
    handover_source = api.text(".relay/handover.json")

    results = {}
    def gate(name, state, why, refs=None):
        results[name] = {"status": state, "reason": why, "source_refs": refs or []}

    owner = (issues[1].get("body") or "")
    seed_equal = owner_source is not None and owner_source == owner
    gate("L00", "LAB_ONLY_PASS" if seed_equal and "SYNTHETIC" in owner else "FAIL",
         "Exact source mirror checked; SYNTHETIC_LAB_ONLY is not authenticated original chat"
         if seed_equal else "Owner issue body and source file not byte-identical",
         [issues[1].get("html_url"), "docs/owner-intent.md"])
    root_comments = "\n".join(c.get("body") or "" for c in comments[1])
    implementation = "IMPLEMENTATION_PLAN" in root_comments
    gate("L01", "NEEDS_NATIVE_REPLAY" if implementation else "MISSING",
         "Root must carry typed, source-bound implementation-plan publication",
         [issues[1].get("html_url")])
    graph_declared = graph_source is not None and issue_map_source is not None
    linked = all("#1" in (issues[i].get("body") or "") for i in (2, 3))
    gate("L02", "NEEDS_NATIVE_REPLAY" if graph_declared and linked and implementation
         else "MISSING",
         "Generated graph and child descriptions alone do not prove native decomposition publication",
         [issues[2].get("html_url"), issues[3].get("html_url"), ".relay/graph.yaml"])
    facts = {i: [c for c in comments[i]
                  if "TASK_EVIDENCE" in (c.get("body") or "")
                  and "CHECKPOINT_FACTS_V1" in (c.get("body") or "")]
             for i in (2, 3)}
    gate("L03", "NEEDS_NATIVE_REPLAY" if all(facts[i] for i in facts) else "MISSING",
         "Both child issues require material-current machine facts; external Common #875 comments are not substitutes",
         [issues[2].get("html_url"), issues[3].get("html_url")])
    approved = "V35_GRAPH_SELECTION_APPROVAL_V1_BEGIN" in root_comments
    gate("L04", "NEEDS_NATIVE_REPLAY" if approved else "HOLD_NO_APPROVED_GRAPH",
         "Graph presence does not imply provider-approved native DELP/source authority",
         [issues[1].get("html_url"), ".relay/graph.yaml"])
    issue_views = all(
        "LIVE_STATUS_V1" in "\n".join(c.get("body") or "" for c in comments[i])
        for i in (1, 2, 3))
    feature_prs = [p for p in pull_requests
                   if "lab/parser" in (p.get("head") or {}).get("ref", "")
                   or "lab/report" in (p.get("head") or {}).get("ref", "")]
    gate("L05", "NEEDS_NATIVE_REPLAY" if issue_views and feature_prs else "MISSING",
         "Need common DELP snapshot digest and real managed issue AND feature-PR GET/readbacks; never infer P/E from title",
         [issues[1].get("html_url")] + [p.get("html_url") for p in feature_prs])
    gate("L06", "NEEDS_NATIVE_REPLAY" if index_source else "MISSING",
         "Proposed index path absent; native repo-wise session/Owner-revision integration must be selected by approved protocol",
         ["relay/SESSION_INDEX_V1.jsonl", "docs/owner-intent.md"])
    handover_comment = any(
        "HANDOVER_CONTEXT" in (c.get("body") or "")
        for rows in comments.values() for c in rows)
    gate("L07", "NEEDS_NATIVE_REPLAY" if handover_comment and handover_source else "MISSING",
         "Current-source C6 successor handover not observed; do not accept copied prompt",
         [".relay/handover.json", issues[1].get("html_url")])
    gate("L08", "NOT_RUN", "Four genuine clean cold successors and separate reviewer principals not observed")
    gate("L09", "NOT_RUN", "Adversarial currentness, graph-drift and dual-writer stress not observed")
    if set(results) != set(GATES):
        raise ProviderFailure("oracle gate definitions incomplete")

    material = {
        "schema": "V35_LC0_READ_ONLY_OBSERVATION_V1",
        "repository": TARGET,
        "private": True,
        "owner_source_grade": "SYNTHETIC_LAB_ONLY",
        "authority": "NON_AUTHORIZING_PROVIDER_OBSERVATION_ONLY",
        "no_delp_progress_computed": True,
        "issue_ids": [1, 2, 3],
        "comment_counts": {str(i): len(comments[i]) for i in comments},
        "all_prs_observed": [{"number": p["number"], "title": p["title"],
                             "head": p["head"]["sha"], "draft": p["draft"]}
                            for p in pull_requests],
        "features_prs_observed": [p["number"] for p in feature_prs],
        "results": results,
        "status": "RED_NOT_END_TO_END_QUALIFIED",
        "missing_or_unproven": [g for g in GATES if results[g]["status"] not in ("PASS",)],
        "provider_requests": api.requests,
    }
    material["observation_sha256_not_delp_snapshot"] = _sha(material)
    return material


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", default=TARGET)
    parser.add_argument("--output", default="LIFECYCLE_ACCEPTANCE.json")
    args = parser.parse_args()
    if args.repository != TARGET:
        print("REFUSED: repository must equal private laboratory", file=sys.stderr)
        return 2
    try:
        report = inspect(GitHubReadOnly(os.environ.get("GITHUB_TOKEN", "")))
    except ProviderFailure as exc:
        print("NOT_OBSERVED: " + str(exc), file=sys.stderr)
        return 2
    pathlib.Path(args.output).write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8")
    for key in GATES:
        print("{0}: {1}: {2}".format(
            key, report["results"][key]["status"], report["results"][key]["reason"]))
    print("Native V3.5 acceptance: RED. Provider-observation digest (NOT DELP): "
          + report["observation_sha256_not_delp_snapshot"])
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
