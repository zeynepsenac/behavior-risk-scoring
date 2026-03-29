\echo '=== RUNNING ALL MIGRATIONS ==='

\i /database/migrations/000_engineered_customers.sql
\i /database/migrations/001_prediction_history.sql
\i /database/migrations/002_model_registry.sql
\i /database/migrations/003_prediction_trigger.sql
\i /database/migrations/004_explanation_logs.sql
\i /database/migrations/005_portfolio_view.sql
\i /database/migrations/006_constraints.sql
\i /database/migrations/007_updated_timestamp.sql
\i /database/migrations/008_trigger_use_model_registry.sql

\echo '=== SEEDING ACTIVE MODEL ==='
\i /database/migrations/009_seed_active_model.sql

\i /database/migrations/010_customers.sql
\i /database/migrations/011_raw_events.sql
\i /database/migrations/012_engineered_features.sql
\i /database/migrations/013_staging_tables.sql
\i /database/migrations/014_dataset_alias.sql
\i /database/migrations/015_audit_enum_and_index.sql

\i /database/migrations/016__add_data_lineage.sql
\i /database/migrations/017_add_not_null_risk_score.sql
\i /database/migrations/018_mlops_monitoring.sql

\i database/seeds/001_sync_customers.sql
\echo '=== MIGRATIONS FINISHED ==='