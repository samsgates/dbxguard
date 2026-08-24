from __future__ import annotations

# Query templates are intentionally read-only. They can be executed by an adapter that uses a
# SQL warehouse or statement execution API appropriate to the customer's Databricks environment.
BILLING_USAGE = """
SELECT workspace_id, sku_name, usage_start_time, usage_end_time, usage_quantity, usage_unit,
       usage_metadata, identity_metadata, custom_tags
FROM system.billing.usage
WHERE usage_start_time >= :start_time
""".strip()

LIST_PRICES = """
SELECT sku_name, cloud, currency_code, price_start_time, price_end_time, pricing
FROM system.billing.list_prices
WHERE price_start_time <= current_timestamp()
""".strip()

TABLE_LINEAGE = """
SELECT source_table_full_name, target_table_full_name, entity_type, entity_id, event_time
FROM system.access.table_lineage
WHERE event_time >= :start_time
""".strip()

COLUMN_LINEAGE = """
SELECT source_table_full_name, source_column_name, target_table_full_name, target_column_name,
       entity_type, entity_id, event_time
FROM system.access.column_lineage
WHERE event_time >= :start_time
""".strip()

AUDIT = """
SELECT event_time, service_name, action_name, user_identity, request_params, response, workspace_id
FROM system.access.audit
WHERE event_time >= :start_time
""".strip()

QUERY_HISTORY = """
SELECT statement_id, workspace_id, executed_by, statement_text, compute, total_duration_ms,
       execution_status, start_time, end_time
FROM system.query.history
WHERE start_time >= :start_time
""".strip()
