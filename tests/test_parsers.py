from dbxguard_core.models import ChangeOperation
from dbxguard_parsers.bundle import diff_bundle
from dbxguard_parsers.sql import parse_sql
from dbxguard_parsers.terraform import parse_terraform

def test_sql_parser():
    changes=parse_sql("ALTER TABLE finance.t DROP COLUMN old_col;"); assert changes[0].operation==ChangeOperation.DROP_COLUMN; assert changes[0].resource=="finance.t.old_col"
def test_bundle_compute_change():
    before={"resources":{"jobs":{"j":{"job_clusters":[{"new_cluster":{"num_workers":2}}]}}}}; after={"resources":{"jobs":{"j":{"job_clusters":[{"new_cluster":{"num_workers":10}}]}}}}; changes=diff_bundle(before,after); assert any(c.operation==ChangeOperation.COMPUTE_CHANGE for c in changes)
def test_terraform_parser():
    tf='resource "databricks_cluster" "etl" {\n  num_workers = 8\n}\n'; changes=parse_terraform(tf); assert changes[0].operation==ChangeOperation.COMPUTE_CHANGE
