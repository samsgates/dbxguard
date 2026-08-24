from __future__ import annotations

import re
from pathlib import Path
try:
    import sqlglot
except ImportError:  # Allows offline/core-only validation. Full installs include sqlglot.
    sqlglot = None
from dbxguard_core.models import Change, ChangeOperation, Evidence, ResourceType

_DROP_COLUMN = re.compile(r"ALTER\s+TABLE\s+([\w.`]+)\s+DROP\s+COLUMN\s+([\w`]+)", re.I)
_ALTER_TYPE = re.compile(r"ALTER\s+TABLE\s+([\w.`]+)\s+ALTER\s+COLUMN\s+([\w`]+)\s+(?:TYPE|SET\s+DATA\s+TYPE)\s+([\w() ,]+)", re.I)
_DROP_TABLE = re.compile(r"DROP\s+TABLE\s+(?:IF\s+EXISTS\s+)?([\w.`]+)", re.I)
_GRANT = re.compile(r"\b(GRANT|REVOKE)\b.+?\bON\b\s+(?:CATALOG|SCHEMA|TABLE|VIEW)?\s*([\w.`]+)", re.I|re.S)


def _clean(name:str)->str: return name.replace("`","").strip()


def parse_sql(text:str, source_file:str|None=None, base_types:dict[str,str]|None=None)->list[Change]:
    changes=[]; base_types=base_types or {}
    def ev(desc:str): return [Evidence(source="sql",description=desc,confidence=0.97,metadata={"file":source_file})]
    for m in _DROP_COLUMN.finditer(text):
        table,column=map(_clean,m.groups()); changes.append(Change(resource=f"{table}.{column}",resource_type=ResourceType.COLUMN,operation=ChangeOperation.DROP_COLUMN,source_file=source_file,evidence=ev(m.group(0))))
    for m in _ALTER_TYPE.finditer(text):
        table,column,new_type=m.groups(); resource=f"{_clean(table)}.{_clean(column)}"
        changes.append(Change(resource=resource,resource_type=ResourceType.COLUMN,operation=ChangeOperation.TYPE_CHANGE,property="type",before=base_types.get(resource),after=new_type.strip().upper(),source_file=source_file,evidence=ev(m.group(0))))
    for m in _DROP_TABLE.finditer(text):
        table=_clean(m.group(1)); changes.append(Change(resource=table,resource_type=ResourceType.TABLE,operation=ChangeOperation.DELETE,source_file=source_file,evidence=ev(m.group(0))))
    for m in _GRANT.finditer(text):
        resource=_clean(m.group(2)); changes.append(Change(resource=resource,resource_type=ResourceType.UNKNOWN,operation=ChangeOperation.PERMISSION_CHANGE,source_file=source_file,evidence=ev(m.group(0))))
    if text.strip() and sqlglot is not None:
        sqlglot.parse(text, read="databricks", error_level="RAISE")
    return changes


def parse_sql_file(path:str|Path, base_types:dict[str,str]|None=None)->list[Change]:
    p=Path(path); return parse_sql(p.read_text(),str(p),base_types)
