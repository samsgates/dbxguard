from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml
from dbxguard_core.models import Change, ChangeOperation, Evidence, ResourceType


def _flatten(prefix:str,value:Any,out:dict[str,Any])->None:
    if isinstance(value,dict):
        for key,child in value.items(): _flatten(f"{prefix}.{key}" if prefix else str(key),child,out)
    elif isinstance(value,list):
        for idx,child in enumerate(value): _flatten(f"{prefix}.{idx}",child,out)
    else: out[prefix]=value


def diff_bundle(before:dict[str,Any],after:dict[str,Any],source_file:str="databricks.yml")->list[Change]:
    left={}; right={}; _flatten("",before,left); _flatten("",after,right); changes=[]
    for key in sorted(set(left)|set(right)):
        if left.get(key)==right.get(key): continue
        op=ChangeOperation.UPDATE
        if key.endswith("max_workers") or key.endswith("num_workers") or ("warehouse" in key and key.endswith("size")): op=ChangeOperation.COMPUTE_CHANGE
        elif ".permissions" in key: op=ChangeOperation.PERMISSION_CHANGE
        elif key.endswith("schedule") or ".schedule." in key: op=ChangeOperation.SCHEDULE_CHANGE
        resource=key.rsplit(".",1)[0] or key
        changes.append(Change(resource=resource,resource_type=ResourceType.UNKNOWN,operation=op,property=key.rsplit(".",1)[-1],before=left.get(key),after=right.get(key),source_file=source_file,evidence=[Evidence(source="bundle",description=f"Bundle property changed: {key}",confidence=0.98)]))
    return changes


def load_yaml(path:str|Path)->dict[str,Any]: return yaml.safe_load(Path(path).read_text()) or {}
