from __future__ import annotations

import re
from pathlib import Path
from dbxguard_core.models import Change, ChangeOperation, Evidence, ResourceType

_RESOURCE=re.compile(r'resource\s+"(databricks_[^"]+)"\s+"([^"]+)"\s*\{',re.I)
_NUMERIC=re.compile(r"^\s*(num_workers|max_workers|min_workers)\s*=\s*(\d+)",re.M)


def parse_terraform(text:str,source_file:str|None=None)->list[Change]:
    changes=[]; resources=list(_RESOURCE.finditer(text))
    for i,m in enumerate(resources):
        start=m.end(); end=resources[i+1].start() if i+1<len(resources) else len(text); block=text[start:end]
        resource_type,name=m.groups(); resource=f"{resource_type}.{name}"
        for num in _NUMERIC.finditer(block):
            prop,value=num.groups(); changes.append(Change(resource=resource,resource_type=ResourceType.UNKNOWN,operation=ChangeOperation.COMPUTE_CHANGE,property=prop,before=None,after=int(value),source_file=source_file,evidence=[Evidence(source="terraform",description=f"{prop}={value}",confidence=0.9)]))
    return changes


def parse_terraform_file(path:str|Path)->list[Change]:
    p=Path(path); return parse_terraform(p.read_text(),str(p))
