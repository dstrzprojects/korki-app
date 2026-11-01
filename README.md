# Lekcje — lokalny dziennik i konsola SQL

**Nowość: przełącznik danych rzeczywistych i testowych. Instrukcja: [START-DEMO.md](START-DEMO.md).**

Django 5.2 + PostgreSQL + Angular 21. Aplikacja dla jednej osoby, wyłącznie pod adresem **http://127.0.0.1:8765**. Wszystkie dane pozostają w Twoim PostgreSQL. Brak kont w chmurze, telemetrii, CDN i zewnętrznych fontów. Po zainstalowaniu zależności aplikacja działa bez internetu. Nie wystawiaj jej do sieci; nie ma logowania.

## 1. Wymagania — Windows 10/11

- Python **3.12 lub 3.13**, z Python Launcher (`py`).
- Node.js **24 LTS, co najmniej 24.0**, oraz npm. Angular 21 obsługuje tę linię Node.
- PostgreSQL **16 lub nowszy**, uruchomiony lokalnie. Instalator Windows: zapamiętaj hasło konta administracyjnego `postgres`.
- VS Code z Twoją wtyczką PostgreSQL.

Rozpakuj projekt do docelowego folderu, np. `C:\Projekty\Lekcje`. Nie przenoś folderu po utworzeniu środowiska `.venv` i skrótu; po przeniesieniu odtwórz je.

## 2. Instalacja zależności

Uruchom dwuklikiem `Zainstaluj.cmd`. Wymaga internetu. Instaluje zależności Pythona do `.venv`, zależności Angulara i kompiluje interfejs. Tworzy też `backend\.env`, jeśli plik nie istnieje. Nie konfiguruje ani nie nadpisuje danych PostgreSQL.

Możesz również wykonać ręcznie w terminalu PowerShell VS Code, w głównym folderze:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
Set-Location frontend
npm ci
npm run build
Set-Location ..
```

Plik `package-lock.json` utrwala wersje zależności frontendu. Gotowy build jest dołączony w `frontend/dist/browser`; nie potrzebujesz serwera Node podczas codziennego używania. Przy zmianach źródeł wykonaj ponownie `npm run build`.

## 3. Utworzenie bazy

W rozszerzeniu PostgreSQL VS Code utwórz połączenie:

- host: `127.0.0.1`
- port: `5432`
- użytkownik: `postgres`
- hasło: ustawione przy instalacji PostgreSQL
- baza: `postgres`

Otwórz `sql/01_database.sql`. **Zmień trzy przykładowe hasła** na własne. Uruchom polecenia pojedynczo, bez obejmowania całego skryptu transakcją — `CREATE DATABASE` nie działa wewnątrz transakcji.

To skrypt jednorazowy: tworzy bazę `lekcje` i trzy oddzielne role. Nie uruchamiaj go ponownie na istniejącej konfiguracji.

## 4. Konfiguracja połączeń

Edytuj `backend/.env`. Ustaw te same hasła, które wpisałeś w SQL:

```dotenv
DB_NAME=lekcje
DB_USER=lekcje_app
DB_PASSWORD=twoje_haslo_aplikacji
DB_HOST=127.0.0.1
DB_PORT=5432
SQL_READ_USER=lekcje_sql_read
SQL_READ_PASSWORD=twoje_haslo_odczytu
SQL_WRITE_USER=lekcje_sql_write
SQL_WRITE_PASSWORD=twoje_haslo_edycji
```

Dla haseł ze spacjami lub `#` użyj cudzysłowów zgodnych z formatem dotenv. `.env` jest plikiem prywatnym — nie udostępniaj go.

W terminalu VS Code, w głównym folderze projektu:

```powershell
.\.venv\Scripts\python.exe backend\manage.py migrate
.\.venv\Scripts\python.exe backend\manage.py check
```

Migracje tworzą prawdziwe tabele PostgreSQL z kluczami obcymi i ograniczeniami kwot.

**Dopiero teraz** przełącz połączenie administracyjne VS Code na bazę `lekcje` i uruchom `sql/02_permissions.sql` jako `postgres`.

- `lekcje_app` — konto Django, właściciel tabel i migracji.
- `lekcje_sql_read` — odczyt tabel danych; nie może ich modyfikować.
- `lekcje_sql_write` — odczyt i zmiana danych; własne tabele może tworzyć w schemacie `cwiczenia`. Nie może usuwać struktury tabel aplikacji ani zarządzać rolami.

Do ćwiczeń we wtyczce VS Code możesz dodać osobne połączenie na konto `lekcje_sql_read` lub `lekcje_sql_write`.

Po nadaniu uprawnień sprawdź wszystkie trzy połączenia bez zmieniania danych:

```powershell
.\.venv\Scripts\python.exe backend\manage.py verify_local
```

## 5. Start i skrót na pulpit

Uruchom `Uruchom.cmd`. Otworzy przeglądarkę z aplikacją. Terminal pozostaje otwarty, ponieważ działa w nim serwer Waitress. Zamknij okno lub naciśnij Ctrl+C, aby zatrzymać aplikację. Zamknięcie samej karty przeglądarki nie zatrzymuje serwera. PostgreSQL działa jako osobna usługa Windows.

Kolejne uruchomienie wykryje działającą aplikację i otworzy stronę, bez uruchamiania drugiego serwera.

Aby utworzyć skrót na pulpicie, wykonaj **jednorazowo** w PowerShell w folderze projektu:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Utworz-skrot.ps1
```

Przełącznik dotyczy tylko tego uruchomienia skryptu, nie zmienia globalnej polityki PowerShell. Alternatywnie kliknij prawym na `Uruchom.cmd` → „Wyślij do” → „Pulpit (utwórz skrót)”.

## 6. Codzienna obsługa

1. W „Uczniowie” dodaj ucznia, stawkę godzinową oraz domyślny koszt dojazdu / dodatków.
2. Dodaj lekcję: data z godziną, czas w minutach, stawka i dodatki. Koszt = stawka × minuty / 60 + dodatki, zaokrąglony do groszy. Możesz zaznaczyć ręczne wpisanie ceny.
3. Stawka i koszt są zapisywane w lekcji. Zmiana domyślnej stawki ucznia nie zmienia historii.
4. Po zapisaniu lekcji kliknij „Wpłata” albo dodaj zbiorczą wpłatę w zakładce „Wpłaty”. Do wyboru BLIK, przelew, gotówka.
5. Pulpit pokazuje 8 ostatnich lekcji. Pełna historia ma wyszukiwanie, zakres dat, filtr ucznia i statusu rozliczenia. Historia dostępna jest też z kartoteki ucznia.
6. Wybierz miesiąc na pulpicie lub w historii, aby zobaczyć wpłaty, liczbę i wartość lekcji oraz zaległości za lekcje z tego miesiąca.
7. Jasny i ciemny motyw przełączysz w lewym panelu. Preferencja jest zapisana w tej przeglądarce.

Odwołanych lekcji po prostu nie wpisujesz. Kwoty są w PLN, daty lekcji w lokalnym czasie przeglądarki; Django domyślnie używa Europe/Warsaw.

### Jak działają rozliczenia

- Lekcje i wpłaty to oddzielne wpisy. Wpłata 300 zł może pokryć kilka lekcji.
- Automatyczne wpłaty są przetwarzane według daty i ID, a lekcje pokrywane od najstarszej daty i ID.
- Możesz wybrać konkretne lekcje; rozdział odbywa się w kolejności zaznaczenia.
- Nadwyżka automatycznej wpłaty pokryje również lekcje dodane później. Nadwyżka wpłaty z ręczną listą jest zarezerwowana dla tych lekcji; aby użyć jej na inne spotkania, edytuj wpłatę i dodaj lekcje lub przełącz rozliczenie na automatyczne.
- Saldo do rozliczenia = koszt wszystkich lekcji − suma wszystkich wpłat. Wartość ujemna oznacza nadpłatę. Przy ręcznym przypisaniu może równocześnie istnieć zaległość i niewykorzystana nadpłata.
- Przydziały są obliczane na bieżąco, nie utrwalane w dodatkowej tabeli. Edycja daty, ceny lub wpłaty może zmienić przydziały historyczne. Daty nie ograniczają rozdziału — zaliczka może pokryć późniejszą lekcję.
- Usunięcie lekcji usuwa ją z ręcznych list wpłat; jeżeli lista staje się pusta, wpłata przechodzi na automat. Wpłata pozostaje w rejestrze.
- Nie można usunąć ucznia, który ma lekcje albo wpłaty. Najpierw trzeba usunąć powiązane wpisy.

## 7. Konsola SQL

To konsola połączona z rzeczywistym PostgreSQL, bez sztucznych wyników. Domyślnie działa na odrębnym koncie odczytu i w transakcji READ ONLY.

Wykonuj jedno polecenie na raz (przycisk lub Ctrl+Enter). Limit zapytania to 5 s, blokady 1,5 s, wynik do 1000 wierszy. Eksport wyniku CSV obejmuje widoczne, maksymalnie 1000 wierszy. Eksport lekcji obejmuje całą historię, niezależnie od filtrów ekranu.

Po osobnym włączeniu edycji możesz używać `INSERT`, `UPDATE`, `DELETE`, a także tworzyć tabele w `cwiczenia`, np.:

```sql
CREATE TABLE cwiczenia.proby (id integer, opis text);
```

Udane polecenie zostaje zatwierdzone; błąd wycofuje transakcję. Nie używaj ręcznie BEGIN/COMMIT ani poleceń wymagających autocommit, np. VACUUM. Konsola nie jest pełnym odpowiednikiem psql i nie obsługuje komend `\d`, `\copy` itp.

Ćwiczenia znajdziesz w `sql/cwiczenia.sql`. Nazwy tabel są polskie, kolumny angielskie. Struktura dostępna jest w konsoli pod „Struktura tabel”.

Bezpośredni SQL omija walidację formularzy Django. Zachowuj poprawną metodę płatności, dodatnie kwoty i prawidłowy JSON `lesson_ids` (lista ID lekcji tego samego ucznia). Nie zmieniaj ręcznie ID istniejących wpisów. Rób kopie przed eksperymentami.

## 8. Kopie i odtwarzanie

„Dane i kopie” → „Kopia bazy” pobiera pełny dump PostgreSQL. Wymaga `pg_dump` w PATH albo ustawienia w `backend/.env`:

```dotenv
PG_DUMP=C:\Program Files\PostgreSQL\18\bin\pg_dump.exe
```

Dopasuj wersję ścieżki do zainstalowanego PostgreSQL. Wersja pg_dump nie może być starsza niż serwer. Kopia nie zawiera haseł i ról globalnych PostgreSQL ani pliku `.env`; zachowaj konfigurację oddzielnie.

Aby bezpiecznie sprawdzić kopię, zatrzymaj aplikację i odtwórz ją najpierw do **nowej pustej bazy**, np. `lekcje_odtworzone`, utworzonej przez postgres z właścicielem `lekcje_app`:

```sql
CREATE DATABASE lekcje_odtworzone OWNER lekcje_app;
```

W PowerShell (dopasuj ścieżkę i nazwę dump):

```powershell
& 'C:\Program Files\PostgreSQL\18\bin\pg_restore.exe' -h 127.0.0.1 -U lekcje_app -d lekcje_odtworzone --no-owner --no-privileges 'C:\Kopie\lekcje-backup.dump'
```

Program zapyta o hasło. Wykonaj `sql/02_permissions.sql` na odtworzonej bazie (pomiń CREATE SCHEMA, jeśli schemat cwiczenia już istnieje). Nadaj kontom SQL prawo CONNECT do nowej bazy. W `.env` ustaw `DB_NAME=lekcje_odtworzone`. Oryginalna baza pozostanie bez zmian. Dump odtworzony jako lekcje_app może przejąć własność tabel ćwiczeniowych — do tworzenia nowych tabel konto SQL nadal używa cwiczenia.

CSV jest eksportem do analizy, nie pełną kopią zapasową. Pola tekstowe są zabezpieczone przed interpretacją jako formuły arkusza.

## 9. Rozwiązywanie problemów

- **Brak połączenia z bazą:** sprawdź usługę PostgreSQL w `services.msc`, port, hasła i nazwę bazy w `.env`.
- **Błąd konta SQL / permission denied:** uruchom skrypt 02 po migracjach, na właściwej bazie i jako postgres.
- **Brak pg_dump:** ustaw pełną ścieżkę jak wyżej.
- **Port 8765 zajęty:** zamknij poprzedni terminal aplikacji lub program używający portu.
- **Błąd npm/Node:** użyj Node 24 LTS, potem ponownie uruchom instalację.
- **Puste dane:** nowa instalacja celowo nie zawiera fikcyjnych uczniów ani płatności.
- **Modyfikacja interfejsu:** edytuj `frontend/src/main.ts` i `styles.css`, potem `npm run build` w frontend i odśwież stronę.

## 10. Testy i ograniczenia

```powershell
.\.venv\Scripts\python.exe backend\manage.py check
```

Testy logiki na tymczasowej bazie SQLite, bez zmieniania Twojej bazy PostgreSQL:

```powershell
$env:TEST_SQLITE='1'
.\.venv\Scripts\python.exe backend\manage.py test core
Remove-Item Env:TEST_SQLITE
```

Testy obejmują cenę i zaokrąglenia, stawkę historyczną, wpłaty częściowe i zbiorcze, nadpłaty, ręczny rozdział, usuwanie, walidację, CSRF i CSV. Konsola SQL jest dostępna tylko z PostgreSQL.

To aplikacja jednoosobowa, bez logowania, synchronizacji, faktur ani rozliczeń podatkowych. Nie udostępniaj portu w sieci. Serwer nasłuchuje wyłącznie na 127.0.0.1, sprawdza adres klienta i źródło żądań oraz stosuje ochronę CSRF.

### Zakres weryfikacji wydania

Potwierdzono: kompilację Angulara, kontrolę konfiguracji Django, dziesięć testów logiki i izolacji dwóch baz na SQLite oraz test przeglądarkowy dodania lekcji i częściowej wpłaty, historii ucznia, motywu i układu mobilnego (bez błędów JavaScript). Dane testowe nie są dołączone do aplikacji. Nie uruchomiono tu serwera PostgreSQL ani skryptów Windows; ich sprawdzenie wykonasz po konfiguracji przez `verify_local` i `Uruchom.cmd`.
