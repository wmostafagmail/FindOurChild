-- Schema-version/checksum metadata contains no case data. Both trusted runtime
-- processes compare this ledger with their immutable bundled SQL before any
-- synthetic workflow operation; missing or mismatched metadata fails closed.
GRANT SELECT ON platform.migrations TO foc_api, foc_worker;
