# Bank Import Feedback Design

## Goal

Naprawić import realnych CSV z mBanku oraz pokazać w UI importu, co system robi podczas przetwarzania pliku i z jakim wynikiem kończy operację.

## Problem

- Realny plik `84442804_260301_260331.csv` kończy import HTTP 200, ale tworzy `0` dokumentów i oznacza wszystkie wiersze jako `unsupported`.
- Frontend pokazuje tylko pojedynczy tekst statusu, bez rozróżnienia na `processing`, `success`, `warning` i `error`.
- Użytkownik nie dostaje informacji, czy kliknięcie zadziałało, czy backend przetwarza plik, ani czy wynik wymaga ręcznej reakcji.

## Design

### Backend

- Ulepszyć `read_tabular_bytes()` dla CSV:
  - obsłużyć fallback dekodowania `cp1250`
  - wykrywać właściwy wiersz nagłówka zamiast zakładać, że pierwsza linia pliku jest nagłówkiem
- Ulepszyć parser bankowy:
  - rozpoznawać `#Opis operacji`
  - klasyfikować realne operacje bankomatowe z mBank, w tym `BLIK WYPŁATA ATM` i `WYPŁATA W BANKOMACIE`
  - porównywać tekst po normalizacji bez polskich znaków

### Frontend

- W `ImportPanel` dodać jawny model stanu importu:
  - `idle`
  - `processing`
  - `success`
  - `warning`
  - `error`
- Pokazać kartę statusu z:
  - ikoną stanu
  - krótkim tytułem
  - opisem akcji
  - podsumowaniem wyników importu
- Zablokować przycisk podczas przetwarzania i pokazać prosty spinner.

## Verification

- Test backendowy na CSV mBank z preambułą i kodowaniem `cp1250`
- Test endpointu `/api/imports/bank` na danych odpowiadających realnemu plikowi
- `python3 -m pytest tests`
- `npm run build`
- Ręczne sprawdzenie importu pliku `84442804_260301_260331.csv`
