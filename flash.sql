\echo 'Delete and recreate flash db?'
\prompt 'Return for yes or control-C to cancel > ' foo

DROP DATABASE flash;
CREATE DATABASE flash;
\connect flash

\i flash-schema.sql
\i flash-seed.sql