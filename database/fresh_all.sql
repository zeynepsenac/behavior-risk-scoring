\echo '=== RESET DATABASE ==='

DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;

\echo '=== RUNNING MIGRATIONS ==='

\i /database/run_all.sql

\echo '=== DATABASE READY ==='