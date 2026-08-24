ALTER TABLE finance.transactions
ALTER COLUMN customer_id TYPE BIGINT;

ALTER TABLE finance.transactions
DROP COLUMN legacy_segment;
