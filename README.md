# E-doręczenia Wizualizacja Potwierdzeń EPO dla Przesyłek PUH

## Autor
Tomasz Rekusz

## Opis
Program generuje wizualiację Elektronicznego Potwierdzenia Odbioru (EPO) w formacie xml dla przesyłek Poczty Polskiej (PUH - Publiczna Usługa Hybrydowa).

## Instrukcja
1. Pobierz EPO.exe https://github.com/tomkolp/e-doreczenia-wizualizacja-EPO/releases
2. Umieść i uruchom program w katalogu, gdzie znajdują się pliki XML EPO.
3. Program generuje plik PDF dla nastepujących roadzajów EPO:
   - Doręczenie
   - Odbiór po awizowaniu
   - Zwrot awizowany
   - Zwrot z innych przyczyn

## Przyszłe Wersje
- Poprawki błędów i optymalizacja

## Wymagania do samodzielnego skompilowania
- Python 3.x
- Biblioteki: PyPDF2, ReportLab

## Instalacja
Aby zainstalować wymagane biblioteki, użyj poniższego polecenia:
```bash
pip install PyPDF2 ReportLab
