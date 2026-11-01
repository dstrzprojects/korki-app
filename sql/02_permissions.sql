-- Uruchom jako postgres NA BAZIE lekcje, PO migracjach Django.
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO lekcje_sql_read,lekcje_sql_write;
GRANT SELECT ON uczniowie,lekcje,wplaty TO lekcje_sql_read;
GRANT SELECT,INSERT,UPDATE,DELETE ON uczniowie,lekcje,wplaty TO lekcje_sql_write;
GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA public TO lekcje_sql_write;
CREATE SCHEMA cwiczenia AUTHORIZATION lekcje_sql_write;
GRANT USAGE ON SCHEMA cwiczenia TO lekcje_sql_read;
ALTER DEFAULT PRIVILEGES FOR ROLE lekcje_sql_write IN SCHEMA cwiczenia GRANT SELECT ON TABLES TO lekcje_sql_read;
ALTER ROLE lekcje_sql_read SET default_transaction_read_only=on;
ALTER ROLE lekcje_sql_read SET statement_timeout='5s';
ALTER ROLE lekcje_sql_write SET statement_timeout='5s';
ALTER ROLE lekcje_sql_read SET search_path=public,cwiczenia;
ALTER ROLE lekcje_sql_write SET search_path=public,cwiczenia;
