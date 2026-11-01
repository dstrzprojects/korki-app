-- Uruchom jako postgres, poza transakcją, na bazie postgres.
-- ZMIEŃ trzy przykładowe hasła, te same wpisz w backend/.env.
CREATE ROLE lekcje_app LOGIN PASSWORD 'haslo_do_aplikacji' NOSUPERUSER NOCREATEDB NOCREATEROLE;
CREATE ROLE lekcje_sql_read LOGIN PASSWORD 'haslo_do_odczytu' NOSUPERUSER NOCREATEDB NOCREATEROLE;
CREATE ROLE lekcje_sql_write LOGIN PASSWORD 'haslo_do_edycji' NOSUPERUSER NOCREATEDB NOCREATEROLE;
CREATE DATABASE lekcje OWNER lekcje_app;
REVOKE ALL ON DATABASE lekcje FROM PUBLIC;
GRANT CONNECT ON DATABASE lekcje TO lekcje_sql_read,lekcje_sql_write;
