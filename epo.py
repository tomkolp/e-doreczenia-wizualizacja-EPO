import os
import base64
import xml.etree.ElementTree as ET
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import green, black
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from io import BytesIO

def parse_xml_file(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Błąd parsowania pliku XML: {e}")
        return "Brak danych", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""

    # Namespace
    ns = {
        'mstns': 'KartaEPO/2018/07/15',
        'ds': 'http://www.w3.org/2000/09/xmldsig#',
        'xmime': 'http://www.w3.org/2005/05/xmlmime',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    # Extract RodzajDoreczenie
    rodzaj_doreczenie_elem = root.find('.//mstns:RodzajDoreczenie', ns)
    rodzaj_doreczenie = rodzaj_doreczenie_elem.text.strip() if rodzaj_doreczenie_elem is not None and rodzaj_doreczenie_elem.text is not None else ""

    # Check if rodzaj_doreczenie is "DORECZENIE"
    if rodzaj_doreczenie != "DORECZENIE":
        return "Brak danych", "", rodzaj_doreczenie, "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""

    # Extract IdKartyEPO
    id_karty_epo_elem = root.find('.//mstns:IdKartyEPO', ns)
    id_karty_epo = id_karty_epo_elem.text.strip() if id_karty_epo_elem is not None and id_karty_epo_elem.text is not None else "Brak danych"

    # Extract IdPrzesylki
    id_przesylki_elem = root.find('.//mstns:IdPrzesylki', ns)
    id_przesylki = id_przesylki_elem.text.strip() if id_przesylki_elem is not None and id_przesylki_elem.text is not None else "Brak danych"

    # Extract DataUtworzenia
    data_utworzenia_elem = root.find('mstns:DataUtworzenia', ns)
    data_utworzenia = data_utworzenia_elem.text if data_utworzenia_elem is not None else "Brak danych"

    # Extract PodpisObraz
    podpis_obraz_elem = root.find('.//mstns:PodpisObraz', ns)
    podpis_obraz = podpis_obraz_elem.text.strip() if podpis_obraz_elem is not None and podpis_obraz_elem.text is not None else ""

    # Extract DataNadania
    data_nadania_elem = root.find('.//mstns:DataNadania', ns)
    data_nadania = data_nadania_elem.text if data_nadania_elem is not None else "Brak danych"

    # Extract DataPisma
    data_pisma_elem = root.find('.//mstns:DataPisma', ns)
    data_pisma = data_pisma_elem.text if data_pisma_elem is not None else "Brak danych"

    # Extract NumerNadania
    numer_nadania_elem = root.find('.//mstns:NumerNadania', ns)
    numer_nadania = numer_nadania_elem.text if numer_nadania_elem is not None else "Brak danych"

    # Extract Adresat
    adresat_nazwa_elem = root.find('.//mstns:Adresat/mstns:Nazwa', ns)
    adresat_nazwa = adresat_nazwa_elem.text if adresat_nazwa_elem is not None else "Brak danych"
    adresat_ulica_elem = root.find('.//mstns:Adresat/mstns:Ulica', ns)
    adresat_ulica = adresat_ulica_elem.text if adresat_ulica_elem is not None else "Brak danych"
    adresat_numer_domu_elem = root.find('.//mstns:Adresat/mstns:NumerDomu', ns)
    adresat_numer_domu = adresat_numer_domu_elem.text if adresat_numer_domu_elem is not None else "Brak danych"
    adresat_miejscowosc_elem = root.find('.//mstns:Adresat/mstns:Miejscowosc', ns)
    adresat_miejscowosc = adresat_miejscowosc_elem.text if adresat_miejscowosc_elem is not None else "Brak danych"
    adresat_kod_pocztowy_elem = root.find('.//mstns:Adresat/mstns:KodPocztowy', ns)
    adresat_kod_pocztowy = adresat_kod_pocztowy_elem.text if adresat_kod_pocztowy_elem is not None else "Brak danych"

    # Extract Nadawca
    nadawca_nazwa_elem = root.find('.//mstns:Nadawca/mstns:Nazwa', ns)
    nadawca_nazwa = nadawca_nazwa_elem.text if nadawca_nazwa_elem is not None else "Brak danych"
    nadawca_nazwa2_elem = root.find('.//mstns:Nadawca/mstns:Nazwa2', ns)
    nadawca_nazwa2 = nadawca_nazwa2_elem.text if nadawca_nazwa2_elem is not None else ""
    nadawca_ulica_elem = root.find('.//mstns:Nadawca/mstns:Ulica', ns)
    nadawca_ulica = nadawca_ulica_elem.text if nadawca_ulica_elem is not None else "Brak danych"
    nadawca_numer_domu_elem = root.find('.//mstns:Nadawca/mstns:NumerDomu', ns)
    nadawca_numer_domu = nadawca_numer_domu_elem.text if nadawca_numer_domu_elem is not None else "Brak danych"
    nadawca_miejscowosc_elem = root.find('.//mstns:Nadawca/mstns:Miejscowosc', ns)
    nadawca_miejscowosc = nadawca_miejscowosc_elem.text if nadawca_miejscowosc_elem is not None else "Brak danych"
    nadawca_kod_pocztowy_elem = root.find('.//mstns:Nadawca/mstns:KodPocztowy', ns)
    nadawca_kod_pocztowy = nadawca_kod_pocztowy_elem.text if nadawca_kod_pocztowy_elem is not None else "Brak danych"

    # Extract TrybDoreczenia and DoRakWlasnych
    tryb_doreczenia_elem = root.find('.//mstns:TrybDoreczenia', ns)
    tryb_doreczenia = tryb_doreczenia_elem.text.strip() if tryb_doreczenia_elem is not None and tryb_doreczenia_elem.text is not None else "Brak danych"
    do_rak_wlasnych = tryb_doreczenia_elem.attrib.get('DoRakWlasnych', 'false') == 'true' if tryb_doreczenia_elem is not None else False

    # Extract Sygnatura, Rodzaj, Adnotacje
    sygnatura_elem = root.find('.//mstns:Sygnatura', ns)
    sygnatura = sygnatura_elem.text.strip() if sygnatura_elem is not None and sygnatura_elem.text is not None else ""
    rodzaj_elem = root.find('.//mstns:Rodzaj', ns)
    rodzaj = rodzaj_elem.text.strip() if rodzaj_elem is not None and rodzaj_elem.text is not None else ""
    adnotacje_elem = root.find('.//mstns:Adnotacje', ns)
    adnotacje = adnotacje_elem.text.strip() if adnotacje_elem is not None and adnotacje_elem.text is not None else ""

    # Extract PodmiotDoreczenia and TrescAdnotacji
    podmiot_doreczenia_elem = root.find('.//mstns:PodmiotDoreczenia', ns)
    podmiot_doreczenia = podmiot_doreczenia_elem.text.strip() if podmiot_doreczenia_elem is not None and podmiot_doreczenia_elem.text is not None else ""
    tresc_adnotacji_elem = root.find('.//mstns:TrescAdnotacji', ns)
    tresc_adnotacji = tresc_adnotacji_elem.text.strip() if tresc_adnotacji_elem is not None and tresc_adnotacji_elem.text is not None else ""

    return data_utworzenia, podpis_obraz, rodzaj_doreczenie, data_nadania, data_pisma, numer_nadania, adresat_nazwa, adresat_ulica, adresat_numer_domu, adresat_miejscowosc, adresat_kod_pocztowy, nadawca_nazwa, nadawca_nazwa2, nadawca_ulica, nadawca_numer_domu, nadawca_miejscowosc, nadawca_kod_pocztowy, id_karty_epo, id_przesylki, tryb_doreczenia, do_rak_wlasnych, sygnatura, rodzaj, adnotacje, podmiot_doreczenia, tresc_adnotacji

def doreczenie_save_to_pdf(data_utworzenia, podpis_obraz, rodzaj_doreczenie, data_nadania, data_pisma, numer_nadania, adresat_nazwa, adresat_ulica, adresat_numer_domu, adresat_miejscowosc, adresat_kod_pocztowy, nadawca_nazwa, nadawca_nazwa2, nadawca_ulica, nadawca_numer_domu, nadawca_miejscowosc, nadawca_kod_pocztowy, id_karty_epo, id_przesylki, tryb_doreczenia, do_rak_wlasnych, sygnatura, rodzaj, adnotacje, podmiot_doreczenia, tresc_adnotacji, output_file, source_file):
    c = canvas.Canvas(output_file, pagesize=A4)
    width, height = A4

    # Rejestracja i ustawienie czcionki Arial
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
    c.setFont("Arial", 11)

    # Dodanie nazwy pliku źródłowego, IdKartyEPO i IdPrzesylki do PDF w trzech liniach
    source_file_name = os.path.basename(source_file)
    text1 = f"Raport z pliku: {source_file_name}"
    text2 = f"IdKartyEPO: {id_karty_epo}"
    text3 = f"IdPrzesylki: {id_przesylki}"

    y_position = height - 30

    for line in [text1, text2, text3]:
        c.drawString(50, y_position, line)
        y_position -= 20  # Dostosuj odstępy między liniami w razie potrzeby

    # Dostosowanie y_position dla następnej sekcji
    y_position -= 20

    # Dodanie DataUtworzenia do PDF
    c.drawString(50, y_position, f"Data Utworzenia: {data_utworzenia} (Data doręczenia)")
    y_position -= 20

    # Dodanie RodzajDoreczenie do PDF
    if rodzaj_doreczenie == "DORECZENIE":
        c.setFillColor(green)
        c.rect(45, y_position - 10, 200, 20, fill=True, stroke=False)
        c.setFillColor(black)
    c.drawString(50, y_position, f"Rodzaj Doreczenie: {rodzaj_doreczenie}")
    y_position -= 20

    # Dodanie PodmiotDoreczenia do PDF
    if podmiot_doreczenia:
        c.drawString(50, y_position, f"Podmiot Doreczenia: {podmiot_doreczenia}")
        y_position -= 20

    # Dodanie TrescAdnotacji do PDF
    if tresc_adnotacji:
        c.drawString(50, y_position, f"Tresc Adnotacji: {tresc_adnotacji}")
        y_position -= 20

    # Dodanie TrybDoreczenia do PDF
    tryb_doreczenia_text = f"Tryb doręczenia: {tryb_doreczenia.capitalize()}"
    if do_rak_wlasnych:
        tryb_doreczenia_text += " (do rąk własnych)"
    c.drawString(50, y_position, tryb_doreczenia_text)
    y_position -= 20

    # Dodanie Sygnatura do PDF
    if sygnatura:
        c.drawString(50, y_position, f"Sygnatura: {sygnatura}")
        y_position -= 20

    # Dodanie Rodzaj do PDF
    if rodzaj:
        c.drawString(50, y_position, f"Rodzaj: {rodzaj}")
        y_position -= 20

    # Dodanie Adnotacje do PDF
    if adnotacje:
        c.drawString(50, y_position, f"Adnotacje: {adnotacje}")
        y_position -= 20

    # Dodanie DataNadania do PDF
    c.drawString(50, y_position, f"Data Nadania: {data_nadania}")
    y_position -= 20

    # Dodanie DataPisma do PDF
    c.drawString(50, y_position, f"Data Pisma: {data_pisma}")
    y_position -= 20

    # Dodanie NumerNadania jako klikalny link do PDF
    tracking_url = f"https://sledzenie.poczta-polska.pl/?numer={numer_nadania}"
    c.drawString(50, y_position, "Nr. przesyłki: ")
    c.setFillColorRGB(0, 0, 1)  # Ustawienie koloru na niebieski
    c.drawString(150, y_position, tracking_url)
    c.linkURL(tracking_url, (150, y_position, 450, y_position + 15), relative=1, thickness=0, color=None)
    c.setFillColor(black)  # Powrót do domyślnego koloru
    y_position -= 20

    # Dodanie Adresat do PDF
    c.drawString(50, y_position, "Adresat:")
    c.line(50, y_position - 2, 100, y_position - 2)  # Podkreślenie tekstu
    y_position -= 20
    c.drawString(50, y_position, f"{adresat_nazwa}")
    y_position -= 20
    c.drawString(50, y_position, f"Ulica: {adresat_ulica} {adresat_numer_domu}")
    y_position -= 20
    c.drawString(50, y_position, f"Miejscowość: {adresat_miejscowosc}")
    y_position -= 20
    c.drawString(50, y_position, f"Kod Pocztowy: {adresat_kod_pocztowy}")
    y_position -= 20

    # Dodanie Nadawca do PDF
    c.drawString(50, y_position, "Nadawca:")
    c.line(50, y_position - 2, 100, y_position - 2)  # Podkreślenie tekstu
    y_position -= 20
    c.drawString(50, y_position, f"{nadawca_nazwa}")
    y_position -= 20
    c.drawString(50, y_position, f"Nadawca cd.: {nadawca_nazwa2}")
    y_position -= 20
    c.drawString(50, y_position, f"Ulica: {nadawca_ulica} {nadawca_numer_domu}")
    y_position -= 20
    c.drawString(50, y_position, f"Miejscowość: {nadawca_miejscowosc}")
    y_position -= 20
    c.drawString(50, y_position, f"Kod Pocztowy: {nadawca_kod_pocztowy}")
    y_position -= 20

    # Dodanie nowej strony dla obrazu
    c.showPage()

    # Dekodowanie i dodanie PodpisObraz do PDF
    if podpis_obraz:
        try:
            podpis_obraz_data = base64.b64decode(podpis_obraz)
            image = ImageReader(BytesIO(podpis_obraz_data))
            c.drawImage(image, 100, height - 400, width=width - 200, height=400)
        except Exception as e:
            print(f"Błąd dekodowania obrazu: {e}")

    c.save()

def process_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".xml"):
            file_path = os.path.join(folder_path, filename)
            data_utworzenia, podpis_obraz, rodzaj_doreczenie, data_nadania, data_pisma, numer_nadania, adresat_nazwa, adresat_ulica, adresat_numer_domu, adresat_miejscowosc, adresat_kod_pocztowy, nadawca_nazwa, nadawca_nazwa2, nadawca_ulica, nadawca_numer_domu, nadawca_miejscowosc, nadawca_kod_pocztowy, id_karty_epo, id_przesylki, tryb_doreczenia, do_rak_wlasnych, sygnatura, rodzaj, adnotacje, podmiot_doreczenia, tresc_adnotacji = parse_xml_file(file_path)
            if rodzaj_doreczenie == "DORECZENIE":
                pdf_output_file = os.path.join(folder_path, f"{os.path.splitext(filename)[0]}.pdf")
                doreczenie_save_to_pdf(data_utworzenia, podpis_obraz, rodzaj_doreczenie, data_nadania, data_pisma, numer_nadania, adresat_nazwa, adresat_ulica, adresat_numer_domu, adresat_miejscowosc, adresat_kod_pocztowy, nadawca_nazwa, nadawca_nazwa2, nadawca_ulica, nadawca_numer_domu, nadawca_miejscowosc, nadawca_kod_pocztowy, id_karty_epo, id_przesylki, tryb_doreczenia, do_rak_wlasnych, sygnatura, rodzaj, adnotacje, podmiot_doreczenia, tresc_adnotacji, pdf_output_file, file_path)

if __name__ == "__main__":
    folder_path = os.path.abspath(os.getcwd())
    process_folder(folder_path)
    input("Naciśnij Enter, aby zakończyć...")