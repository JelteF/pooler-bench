CREATE USER postgres WITH SUPERUSER PASSWORD 'test';
CREATE USER test WITH PASSWORD 'test';
CREATE DATABASE test WITH OWNER test;
CREATE DATABASE test_2 WITH OWNER test;

CREATE USER npgsql_tests PASSWORD 'npgsql_tests' SUPERUSER;
CREATE DATABASE npgsql_tests OWNER npgsql_tests;

CREATE DATABASE auth_db;
CREATE SCHEMA _supavisor;
