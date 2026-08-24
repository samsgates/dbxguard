from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml
from dbxguard_core.models import Change, Decision, Finding, PolicyResult

_PRIORITY={Decision.ALLOW:0,Decision.WARN:1,Decision.REQUIRE_APPROVAL:2,Decision.BLOCK:3}


class PolicyEngine:
    def __init__(self,policies:list[dict[str,Any]])->None: self.policies=policies

    @classmethod
    def from_directory(cls,directory:str|Path)->"PolicyEngine":
        policies=[]
        for path in sorted(Path(directory).glob("**/*.y*ml")):
            data=yaml.safe_load(path.read_text())
            if data: data["__file__"]=str(path); policies.append(data)
        return cls(policies)

    def evaluate(self,changes:list[Change],findings:list[Finding],environment:str,risk_score:float)->list[PolicyResult]:
        results=[]
        for policy in self.policies:
            name=policy.get("metadata",{}).get("name",policy.get("__file__","unnamed")); spec=policy.get("spec",{}); match=spec.get("match",{})
            if match.get("environment") not in (None,environment): continue
            for idx,rule in enumerate(spec.get("rules",[]),1):
                cond=rule.get("condition",{}); matched=list(changes)
                if "operation" in cond: matched=[c for c in matched if c.operation.value==str(cond["operation"])]
                if "resourceType" in cond: matched=[c for c in matched if c.resource_type.value==str(cond["resourceType"])]
                if "risk_score_gte" in cond and risk_score<float(cond["risk_score_gte"]): matched=[]
                if matched:
                    ids={c.id for c in matched}; results.append(PolicyResult(policy=f"{name}#{idx}",action=Decision(str(rule.get("action","WARN"))),matched=True,reason=f"Matched policy condition {cond}",finding_ids=[f.id for f in findings if f.change_id in ids]))
        return results

    def final_decision(self,results:list[PolicyResult],risk_score:float)->Decision:
        if results: return max((r.action for r in results),key=lambda x:_PRIORITY[x])
        if risk_score>=80: return Decision.BLOCK
        if risk_score>=60: return Decision.REQUIRE_APPROVAL
        if risk_score>=40: return Decision.WARN
        return Decision.ALLOW
