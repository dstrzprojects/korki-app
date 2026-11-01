-- Tabele rzeczywiste: uczniowie, lekcje, wplaty.
SELECT * FROM lekcje ORDER BY date DESC LIMIT 20;
SELECT u.name, COUNT(l.id) AS liczba_lekcji, COALESCE(SUM(l.price),0) AS wartosc
FROM uczniowie u LEFT JOIN lekcje l ON l.student_id=u.id GROUP BY u.id ORDER BY wartosc DESC;
-- Oddzielne agregacje zapobiegają mnożeniu kwot przez JOIN.
SELECT u.name,
 COALESCE((SELECT SUM(price) FROM lekcje WHERE student_id=u.id),0) AS koszt,
 COALESCE((SELECT SUM(amount) FROM wplaty WHERE student_id=u.id),0) AS wplaty,
 COALESCE((SELECT SUM(price) FROM lekcje WHERE student_id=u.id),0)-COALESCE((SELECT SUM(amount) FROM wplaty WHERE student_id=u.id),0) AS saldo
FROM uczniowie u;
-- Tryb edycji: własne tabele twórz w schemacie cwiczenia.
-- CREATE TABLE cwiczenia.proby (id integer, opis text);
