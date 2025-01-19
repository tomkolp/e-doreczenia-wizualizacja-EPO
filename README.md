# Wizualizacja Potwierdzeń EPO dla Przesyłek PUH

## Autor
Tomasz Rekusz

## Opis
To jest wstępna wersja wizualizacji potwierdzeń Elektronicznego Potwierdzenia Odbioru (EPO) dla przesyłek Poczty Polskiej (PUH - Publiczna Usługa Hybrydowa). Na tę chwilę możliwa jest wizualizacja EPO dla przesyłek doręczonych. W następnych wersjach pojawi się wizualizacja dla zwrotów, informacje o awizowaniu itd.

## Instrukcja
1. Pobierz EPO.exe https://github.com/tomkolp/e-doreczenia-wizualizacja-EPO/releases
2. Umieść program w katalogu, gdzie znajdują się pliki XML EPO.
3. Program generuje plik PDF z następującymi informacjami:
   - Data nadania
   - Adresat
   - Odbiorca
   - Klikalny link do śledzenia przesyłki
   - Na drugiej stronie PDF-a znajduje się wizualizacja podpisu z tabletu listonosza.

## Przyszłe Wersje
- Wizualizacja dla zwrotów
- Informacje o awizowaniu
- Dodatkowe funkcje i usprawnienia

## Wymagania do samodzielnego skompilowania
- Python 3.x
- Biblioteki: PyPDF2, ReportLab

## Instalacja
Aby zainstalować wymagane biblioteki, użyj poniższego polecenia:
```bash
pip install PyPDF2 ReportLab
