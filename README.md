# E-doręczenia wizualizacja potwierdzeń EPO dla przesyłek PUH

## Autor
Tomasz Rekusz
[☕ Wesprzyj mnie na BuyCoffee.to](https://buycoffee.to/tomkolp)
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
  
# Przykładowo wygenerowane EPO:

Poniżej znajdują się linki do pobrania dokumentów EPO w formacie PDF, z podziałem na strony.

## 📄 Podgląd dokumentów

### Raport EPO dla przesyłki doręczonej
#### Doręczenie
📥 **[Pobierz raport EPO - strona 1 (PDF)](pdf/doreczenie.pdf)**  
📥 **[Pobierz raport EPO - strona 2 (PDF)](pdf/doreczenie.pdf)**  

### Raport EPO dla przesyłki doręczonej po awizo
#### Doręczenie po awizo
📥 **[Pobierz raport EPO - strona 1 (PDF)](pdf/doreczenie_po_awizo.pdf)**  
📥 **[Pobierz raport EPO - strona 2 (PDF)](pdf/doreczenie_po_awizo.pdf)**  

### Raport EPO dla przesyłki zwróconej
#### Zwrot
📥 **[Pobierz raport EPO - strona 1 (PDF)](pdf/zwrot.pdf)**  

### Raport EPO dla przesyłki zwróconej po awizo
#### Zwrot awizowany
📥 **[Pobierz raport EPO - strona 1 (PDF)](pdf/zwrot_awizowany.pdf)**  

---

📌 **Uwaga:** Wszystkie pliki znajdują się w katalogu `pdf/` w repozytorium.



## Przyszłe Wersje
- Poprawki błędów i optymalizacja

## Wymagania do samodzielnego skompilowania
- Python 3.x

### Wbudowane biblioteki (w zestawie z Pythonem):
- `os`
- `base64`
- `textwrap`
- `xml.etree.ElementTree`
- `io`
- `webbrowser`

### Biblioteki zewnętrzne (instalowane przez PIP):
- `reportlab` (do generowania plików PDF)
- `requests` (do wykonywania żądań HTTP)
- `packaging` (do porównywania wersji)
