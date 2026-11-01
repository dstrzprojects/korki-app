# Testowanie bez ruszania prawdziwych danych

## Pierwsze uruchomienie demo

1. Rozpakuj nową wersję do osobnego folderu. Jeśli masz już skonfigurowane połączenie, skopiuj do niej swój `backend/.env`. Jeśli nie, Zainstaluj.cmd utworzy przykładowy plik — do samego demo wystarczy poprawny lokalny host i port PostgreSQL. Nie kopiuj katalogu `.venv` — utwórz go przez `Zainstaluj.cmd`.
2. Uruchom **Zainstaluj.cmd** (jeśli ten folder nie ma jeszcze zainstalowanych zależności).
3. Uruchom **Przygotuj-demo.cmd**. Wpisz lokalnie hasło administratora `postgres`. Program utworzy osobną bazę `lekcje_demo`, nada uprawnienia i wypełni ją fikcyjnymi danymi. Hasło administratora nie jest zapisywane; hasła trzech kont demo są generowane automatycznie w `.env`.
4. Zamknij stary terminal aplikacji i uruchom **Uruchom.cmd** z nowego folderu.
5. U góry strony wybierz **Dane testowe (demo)**.

Nie musisz sam tworzyć tabel ani wykonywać dodatkowych SQL. Skrypt tworzy tylko bazę demonstracyjną; baza rzeczywista pozostaje bez zmian. Po zmianie folderu utwórz ponownie skrót na pulpicie, aby wskazywał nową wersję.

## Co zawiera zestaw

- 8 fikcyjnych uczniów, 64 lekcje i 18 wpłat.
- Lekcje 45, 60, 90 i 120 minut, różne stawki, dojazd, ręczne ceny.
- Pełne płatności, częściowe wpłaty, brak płatności, nadpłata i zbiorcza wpłata za kilka spotkań.
- BLIK, przelew, gotówka oraz ręczne wskazanie lekcji do opłacenia.
- Daty z ostatnich około ośmiu tygodni, liczone od dnia wygenerowania.

## Przełączanie i reset

Przełącznik zmienia jednocześnie formularze, historię, konsolę SQL, CSV i kopię zapasową. Pomarańczowy pasek oznacza demo. Każda karta przeglądarki ma swój tryb; nowo otwarta lub odświeżona karta domyślnie pokazuje dane rzeczywiste.

**Przywróć dane testowe** usuwa uczniów, lekcje i wpłaty wyłącznie z bazy demo i generuje zestaw od nowa. Reset nie usuwa własnych tabel w schemacie `cwiczenia`, nie cofa zmian struktury bazy i nie dotyka bazy rzeczywistej. Identyfikatory po resecie mogą być inne.

Ponowne uruchomienie Przygotuj-demo.cmd zachowuje już istniejące wpisy demonstracyjne. Nie resetuje ich bez pytania.

## Dlaczego osobna baza

Nie trzeba tworzyć dodatkowych tabel w bazie rzeczywistej ani dodawać znacznika `is_test` do każdego rekordu. Baza demo ma jednak własne kopie tych samych tabel — bez tabel nie można przechowywać niezależnych danych.

Obie bazy działają w tym samym zainstalowanym serwerze PostgreSQL, więc nie instalujesz drugiego serwera. Oddzielne konta demo oraz wybór bazy przy każdym żądaniu ograniczają ryzyko przypadkowej edycji rzeczywistych danych podczas ćwiczeń SQL. Nie dodawaj demo kontom uprawnień do bazy rzeczywistej ani rozszerzeń łączących bazy.

## Opcja ręczna dla zaawansowanych

Po utworzeniu bazy, kont i zmiennych DEMO_* migracje wykonuje się przez:

```powershell
.\.venv\Scripts\python.exe backend\manage.py migrate --database=demo
.\.venv\Scripts\python.exe backend\manage.py seed_demo
```

`seed_demo --reset` resetuje dane wyłącznie w skonfigurowanej, odrębnej bazie demo. Nigdy nie wykonuj `loaddata` danych testowych na domyślnym połączeniu produkcyjnym.

## Weryfikacja aktualizacji

Przeszło 10 testów automatycznych na dwóch oddzielnych bazach SQLite oraz test przeglądarkowy: przełączenie na demo, zapis lekcji wyłącznie w demo, reset, eksport CSV, powrót do danych rzeczywistych i układ mobilny. Dobór konta PostgreSQL w konsoli sprawdzono testem z podstawionym połączeniem. Instalator bazy demo na Windows i rzeczywiste połączenia PostgreSQL wymagają sprawdzenia lokalnie.
