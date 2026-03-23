DROP TABLE IF EXISTS explanation_logs CASCADE;
DROP TABLE IF EXISTS model_registry CASCADE;
DROP TABLE IF EXISTS prediction_history CASCADE;
DROP TABLE IF EXISTS engineered_customers CASCADE;

\i database/migrations/000_engineered_customers.sql
\i database/migrations/001_prediction_history.sql
\i database/migrations/002_model_registry.sql
\i database/migrations/003_prediction_trigger.sql
\i database/migrations/004_explanation_logs.sql
\i database/migrations/005_portfolio_view.sql
\i database/migrations/006_constraints.sql
\i database/migrations/007_updated_timestamp.sql