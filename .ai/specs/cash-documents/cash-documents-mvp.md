---
status: verified
last_verified: 2026-04-24
related_paths:
  - README.md
  - backend/app/main.py
  - backend/app/db.py
  - backend/app/services/epp.py
  - backend/app/services/importers/saldeo.py
  - backend/app/services/importers/bank.py
  - frontend/app/import/page.tsx
  - frontend/app/documents/page.tsx
  - .ai/specs/cash-documents/cash-documents-mvp.md
---

# Cash Documents MVP

## Summary

MVP aplikacji służy do importu danych z Saldeo i wyciągów bankowych, przekształcenia ich do wspólnego modelu dokumentów kasowych `KP` i `KW`, ręcznej korekty rekordów wymagających uzupełnienia oraz eksportu pliku `.epp` zgodnego z EDI++ dla importu do Rewizora GT.

Priorytetem MVP jest poprawny eksport `.epp`. Import ma być tolerancyjny dla `CSV` i `XLSX`, ale nie jest celem samym w sobie. Ręczne dodawanie dokumentów poza importem nie wchodzi do zakresu MVP.

## Goals

- umożliwić import faktur z Saldeo opłaconych gotówką
- umożliwić import wyciągów bankowych i klasyfikację wpłat oraz wypłat z bankomatu
- utworzyć wspólny model dokumentów kasowych `KP` i `KW`
- umożliwić filtrowanie, przegląd i edycję rekordów przed eksportem
- wygenerować plik `.epp` zgodny z EDI++ dla dokumentów kasowych importowanych do Rewizora GT

## Non-Goals

- logowanie użytkowników
- obsługa wielu kas
- nadawanie finalnych numerów dokumentów kasowych
- ręczne dodawanie nowych dokumentów bez importu
- integracja online z Saldeo lub bankiem przez API
- automatyczne dekretowanie kont księgowych poza tym, co zapewnia schemat importu po stronie Rewizora

## Business Rules

### Saldeo

- faktura przychodowa z formą płatności gotówka tworzy dokument `KP`
- faktura kosztowa z formą płatności gotówka tworzy dokument `KW`
- rekordy bez płatności gotówkowej są pomijane
- rekordy bez możliwości ustalenia typu dokumentu lub z brakami krytycznymi otrzymują status `requires_review`

### Wyciąg bankowy

- rekord opisany jako wpłata do bankomatu, `deposit`, `atm wpłata` lub podobny tworzy dokument `KP`
- rekord opisany jako wypłata z bankomatu, `withdrawal`, `atm wypłata` lub podobny tworzy dokument `KW`
- pozostałe operacje są oznaczane jako `unsupported` i nie są eksportowane
- operacje bankomatowe używają stałego podmiotu bankowego skonfigurowanego w ustawieniach aplikacji
- operacje bankomatowe są eksportowane z typem odbiorcy zgodnym z EPP, jako kontrahent albo kontrahent jednorazowy

### Dokument kasowy

- aplikacja obsługuje tylko jedną kasę
- numer dokumentu w eksporcie pozostaje pusty albo tymczasowy, ponieważ finalny numer nadaje Rewizor GT
- użytkownik może edytować rekord po imporcie, ale nie może tworzyć nowego dokumentu od zera
- eksport obejmuje wyłącznie rekordy poprawne walidacyjnie i oznaczone jako gotowe

## User Flow

1. Użytkownik importuje plik Saldeo.
2. System zapisuje surowe wiersze, rozpoznaje dokumenty gotówkowe i buduje rekordy `KP` albo `KW`.
3. Użytkownik importuje wyciąg bankowy.
4. System klasyfikuje operacje bankomatowe i buduje dodatkowe rekordy `KP` albo `KW`.
5. Użytkownik przechodzi do listy dokumentów kasowych.
6. Użytkownik filtruje rekordy, poprawia braki w danych odbiorcy, tytułach, opisach lub statusie dokumentu.
7. System waliduje rekordy i pokazuje, które są gotowe do eksportu, a które są zablokowane.
8. Użytkownik pobiera plik `.epp`.
9. Użytkownik importuje plik do Rewizora GT przez `Narzędzia -> Import -> Plik komunikacji`.

## Screens

### Import

Widok zawiera dwa niezależne uploady:

- import Saldeo
- import wyciągu bankowego

Każdy import pokazuje:

- nazwę pliku
- liczbę wczytanych rekordów
- liczbę utworzonych dokumentów kasowych
- liczbę rekordów pominiętych
- liczbę rekordów wymagających ręcznej korekty

### Cash Documents

Tabela dokumentów kasowych zawiera:

- typ dokumentu `KP` albo `KW`
- datę wystawienia
- kwotę
- źródło danych
- kontrahenta albo podmiot bankowy
- status dokumentu
- status walidacji
- flagę gotowości do eksportu

Filtry:

- typ `KP` albo `KW`
- zakres dat
- zakres kwot
- źródło `saldeo` albo `bank`
- status walidacji
- tekstowe wyszukiwanie po tytule, numerze faktury lub nazwie odbiorcy

### Cash Document Edit

Edycja pojedynczego dokumentu pozwala zmienić:

- status dokumentu `odłożony` albo `wykonany`
- tytuł
- opis
- typ odbiorcy
- dane odbiorcy
- flagę gotowości do eksportu

Edycja nie pozwala zmieniać źródła rekordu ani ręcznie podmieniać typu dokumentu bez uzasadnionej reguły biznesowej.

### Export

Widok eksportu pokazuje:

- liczbę dokumentów gotowych do eksportu
- liczbę dokumentów z błędami
- listę najczęstszych blokad walidacyjnych
- przycisk pobrania `.epp`
- krótką instrukcję importu do Rewizora GT

### Settings

Ustawienia podstawowe obejmują:

- dane firmy
- dane kasy
- stały podmiot bankowy używany dla operacji bankomatowych

## Data Model

### `import_session`

Służy do śledzenia pojedynczego importu.

Przykładowe pola:

- `id`
- `source_type` (`saldeo`, `bank`)
- `filename`
- `imported_at`
- `status`
- `row_count`
- `created_documents_count`
- `ignored_rows_count`
- `review_required_count`

### `import_row_raw`

Przechowuje oryginalny wiersz z importu i wynik jego przetworzenia.

Przykładowe pola:

- `id`
- `import_session_id`
- `row_index`
- `raw_payload`
- `classification`
- `processing_status` (`created`, `ignored`, `unsupported`, `requires_review`)
- `cash_document_id`
- `error_reason`

### `cash_document`

Wspólny model domenowy dla eksportu EPP.

Przykładowe pola:

- `id`
- `source_type` (`saldeo`, `bank`)
- `source_reference` (np. numer faktury albo identyfikator operacji)
- `document_type` (`KP`, `KW`)
- `document_status` (`stored`, `executed`)
- `issue_date`
- `amount`
- `title`
- `description`
- `recipient_type` (`contractor`, `employee`, `office`, `one_time_contractor`)
- `recipient_name_short`
- `recipient_name_full`
- `recipient_address_line`
- `recipient_postal_code`
- `recipient_city`
- `recipient_tax_id`
- `recipient_pesel`
- `validation_status` (`valid`, `invalid`, `requires_review`)
- `validation_errors`
- `ready_for_export`
- `import_session_id`
- `created_at`
- `updated_at`

### `counterparty`

Lokalna kartoteka kontrahentów do dopasowania i uzupełniania braków.

Przykładowe pola:

- `id`
- `name_short`
- `name_full`
- `address_line`
- `postal_code`
- `city`
- `tax_id`

### `employee`

Lokalna kartoteka pracowników. W MVP może istnieć na poziomie modelu i API bez rozbudowanego interfejsu.

### `app_settings`

Przechowuje ustawienia globalne potrzebne do eksportu.

Przykładowe pola:

- `company_name`
- `cash_register_name`
- `cash_register_symbol`
- `bank_party_name_short`
- `bank_party_name_full`
- `bank_party_address_line`
- `bank_party_postal_code`
- `bank_party_city`
- `bank_party_tax_id`

## Import Mapping

### Saldeo Input

Obsługiwane formaty: `CSV`, `XLSX`

Wymagane pola robocze po mapowaniu:

- numer faktury
- data dokumentu albo data płatności
- kontrahent
- kwota brutto
- forma płatności
- typ dokumentu przychodowy albo kosztowy

Mapowanie:

- przychód gotówkowy -> `KP`
- koszt gotówkowy -> `KW`

Generowanie tytułu:

- `KP`: `wpłata za fakturę {numer_faktury}`
- `KW`: `zapłata za fakturę {numer_faktury}`

### Bank Input

Obsługiwane formaty: `CSV`, `XLSX`

Wymagane pola robocze po mapowaniu:

- data operacji
- opis operacji
- kwota

Klasyfikacja odbywa się po znormalizowanym opisie operacji.

Przykładowe słowa dla `KP`:

- `wpłata`
- `wpłata do bankomatu`
- `deposit`
- `atm wpłata`

Przykładowe słowa dla `KW`:

- `wypłata`
- `wypłata z bankomatu`
- `withdrawal`
- `atm wypłata`

Generowanie tytułu:

- `KP`: `wpłata do bankomatu z dnia {dd-mm-yyyy}`
- `KW`: `wypłata z bankomatu z dnia {dd-mm-yyyy}`

## Validation Rules

Dokument jest gotowy do eksportu tylko wtedy, gdy ma:

- poprawny typ dokumentu `KP` albo `KW`
- ustawiony status dokumentu
- datę wystawienia
- kwotę większą od zera
- niepusty tytuł
- poprawny typ odbiorcy
- komplet danych odbiorcy wymaganych przez eksport

Dodatkowe zasady:

- opis jest opcjonalny i ograniczony do 255 znaków
- status dokumentu mapuje się do EPP jako `0` dla `stored` i `1` dla `executed`
- typ odbiorcy mapuje się do EPP jako `1` kontrahent, `2` pracownik, `3` urząd, `4` kontrahent jednorazowy
- rekord oznaczony jako `unsupported` nigdy nie trafia do eksportu
- rekord z brakami danych pozostaje widoczny do korekty, ale nie jest eksportowany

## EPP Export

Eksport generuje tekstowy plik `.epp` zgodny z EDI++ dla dokumentów kasowych importowanych do Rewizora GT.

Założenia eksportu:

- eksportujemy wyłącznie dokumenty `KP` i `KW`
- każdy dokument jest generowany jako osobny blok z sekcją `[NAGLOWEK]`
- pola są oddzielone przecinkami
- pola opcjonalne pozostają puste zgodnie z wymaganiami schematu importu
- pole numeru dokumentu pozostaje puste albo tymczasowe
- pola dekretacji prostej mogą pozostać niewypełnione, jeśli nie są używane w importach ewidencji kasowej

Generator musi mapować wewnętrzny model `cash_document` do pól nagłówka dokumentu kasowego EDI++ na podstawie specyfikacji InsERT.

## API Scope

Planowany backend powinien udostępnić minimum:

- endpoint do importu pliku Saldeo
- endpoint do importu wyciągu bankowego
- endpoint listowania dokumentów kasowych z filtrami
- endpoint pobrania pojedynczego dokumentu
- endpoint aktualizacji dokumentu
- endpoint listowania błędów walidacyjnych
- endpoint wygenerowania i pobrania `.epp`
- endpoint odczytu i zapisu ustawień podstawowych

## Edge Cases

- plik ma nieznane lub brakujące kolumny
- plik ma wiersze puste albo zduplikowane
- forma płatności nie jest jednoznacznie gotówkowa
- dokument Saldeo nie ma rozpoznawalnego typu przychodowy albo kosztowy
- kontrahent nie istnieje w lokalnej kartotece
- opis operacji bankowej zawiera podobne frazy, ale nie oznacza wpłaty albo wypłaty z bankomatu
- kwota jest ujemna albo równa zero
- tytuł po automatycznym wygenerowaniu wymaga skrócenia albo ręcznej korekty
- użytkownik próbuje eksportować rekordy z błędami walidacji

## Architecture Direction

Rekomendowany stack MVP:

- `frontend`: Next.js
- `backend`: FastAPI
- `database`: SQLite

Podejście architektoniczne:

- importery są adapterami danych wejściowych
- wspólny model `cash_document` jest rdzeniem domeny
- walidacja i generator `.epp` są logiką centralną systemu
- frontend służy przede wszystkim do kontroli jakości danych przed eksportem

## Testing Scope

Minimalny zakres testów:

- parser Saldeo dla przychodu gotówkowego
- parser Saldeo dla kosztu gotówkowego
- parser wyciągu bankowego dla wpłaty bankomatowej
- parser wyciągu bankowego dla wypłaty bankomatowej
- parser wyciągu bankowego dla operacji nieobsługiwanej
- walidacja dokumentu z kompletnymi danymi
- walidacja dokumentu z brakami blokującymi eksport
- generator `.epp` dla przykładowego `KP`
- generator `.epp` dla przykładowego `KW`
- test przepływu import -> edycja -> eksport

## Implementation Notes

- formaty importu powinny być tolerancyjne i umożliwiać mapowanie kolumn po nagłówkach
- należy zachować surowe dane wejściowe do diagnostyki importu
- generator `.epp` powinien być testowany na stabilnych fixture'ach tekstowych
- brak numeracji dokumentów po stronie aplikacji nie może blokować eksportu
- dane podmiotu bankowego powinny być konfigurowalne, a nie zaszyte na stałe

## Changelog

- 2026-04-24: utworzono spec MVP dla importu Saldeo, importu wyciągów bankowych, modelu dokumentów kasowych i eksportu `.epp`
- 2026-04-24: status zmieniono na `verified` po implementacji backendu FastAPI, generatora `.epp`, importerow CSV/XLSX i szkieletu frontendu Next.js
