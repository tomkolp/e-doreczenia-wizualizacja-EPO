import os
import base64
import xml.etree.ElementTree as ET
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import green
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from io import BytesIO

def parse_xml_file(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Błąd parsowania pliku XML: {e}")
        return "Brak danych", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""

    # Namespace
    ns = {
        'mstns': 'KartaEPO/2018/07/15',
        'ds': 'http://www.w3.org/2000/09/xmldsig#',
        'xmime': 'http://www.w3.org/2005/05/xmlmime',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    # Extract RodzajDoreczenie
    rodzaj_doreczenie_elem = root.find('.//mstns:RodzajDoreczenie', ns)
    rodzaj_doreczenie = rodzaj_doreczenie_elem.text.strip() if rodzaj_doreczenie_elem is not None else ""

    # Check if rodzaj_doreczenie is "DORECZENIE"
    if rodzaj_doreczenie != "DORECZENIE":
        return "Brak danych", "", rodzaj_doreczenie, "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""

    # Extract DataUtworzenia
    data_utworzenia_elem = root.find('mstns:DataUtworzenia', ns)
    data_utworzenia = data_utworzenia_elem.text if data_utworzenia_elem is not None else "Brak danych"

    # Extract PodpisObraz
    podpis_obraz_elem = root.find('.//mstns:PodpisObraz', ns)
    podpis_obraz = podpis_obraz_elem.text.strip() if podpis_obraz_elem is not None else ""

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
    adresat_kraj_elem = root.find('.//mstns:Adresat/mstns:Kraj', ns)
    adresat_kraj = adresat_kraj_elem.text if adresat_kraj_elem is not None else "Brak danych"

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
    nadawca_kraj_elem = root.find('.//mstns:Nadawca/mstns:Kraj', ns)
    nadawca_kraj = nadawca_kraj_elem.text if nadawca_kraj_elem is not None else "Brak danych"

    return data_utworzenia, podpis_obraz, rodzaj_doreczenie, data_nadania, data_pisma, numer_nadania, adresat_nazwa, adresat_ulica, adresat_numer_domu, adresat_miejscowosc, adresat_kod_pocztowy, adresat_kraj, nadawca_nazwa, nadawca_nazwa2, nadawca_ulica, nadawca_numer_domu, nadawca_miejscowosc, nadawca_kod_pocztowy, nadawca_kraj

def doreczenie_save_to_pdf(data_utworzenia, podpis_obraz, rodzaj_doreczenie, data_nadania, data_pisma, numer_nadania, adresat_nazwa, adresat_ulica, adresat_numer_domu, adresat_miejscowosc, adresat_kod_pocztowy, adresat_kraj, nadawca_nazwa, nadawca_nazwa2, nadawca_ulica, nadawca_numer_domu, nadawca_miejscowosc, nadawca_kod_pocztowy, nadawca_kraj, output_file):
    c = canvas.Canvas(output_file, pagesize=A4)
    width, height = A4

    # Register and set font to Arial
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
    c.setFont("Arial", 11)

    # Add DataUtworzenia to PDF
    c.drawString(50, height - 50, f"Data Utworzenia: {data_utworzenia}")

    # Add RodzajDoreczenie to PDF
    if rodzaj_doreczenie == "DORECZENIE":
        c.setFillColor(green)
        c.rect(45, height - 80, 200, 20, fill=True, stroke=False)
        c.setFillColorRGB(0, 0, 0)
    c.drawString(50, height - 75, f"Rodzaj Doreczenie: {rodzaj_doreczenie}")

    # Add DataNadania to PDF
    c.drawString(50, height - 95, f"Data Nadania: {data_nadania}")

    # Add DataPisma to PDF
    c.drawString(50, height - 115, f"Data Pisma: {data_pisma}")

    # Add NumerNadania as clickable link to PDF
    tracking_url = f"https://sledzenie.poczta-polska.pl/?numer={numer_nadania}"
    c.drawString(50, height - 135, "Nr. przesyłki: ")
    c.setFillColorRGB(0, 0, 1)  # Ustawienie koloru na niebieski
    c.drawString(150, height - 135, tracking_url)
    c.linkURL(tracking_url, (150, height - 135, 450, height - 120), relative=1, thickness=0, color=None)
    c.setFillColorRGB(0, 0, 0)  # Powrót do domyślnego koloru

    # Add Adresat to PDF
    c.drawString(50, height - 155, "Adresat:")
    c.line(50, height - 157, 100, height - 157)  # Podkreślenie tekstu
    c.drawString(50, height - 175, f"{adresat_nazwa}")
    c.drawString(50, height - 195, f"Ulica: {adresat_ulica} {adresat_numer_domu}")
    c.drawString(50, height - 215, f"Miejscowość: {adresat_miejscowosc}")
    c.drawString(50, height - 235, f"Kod Pocztowy: {adresat_kod_pocztowy}")
    c.drawString(50, height - 255, f"Kraj: {adresat_kraj}")

    # Add Nadawca to PDF
    c.drawString(50, height - 275, "Nadawca:")
    c.line(50, height - 277, 100, height - 277)  # Podkreślenie tekstu
    c.drawString(50, height - 295, f"{nadawca_nazwa}")
    c.drawString(50, height - 315, f"Nadawca cd.: {nadawca_nazwa2}")
    c.drawString(50, height - 335, f"Ulica: {nadawca_ulica} {nadawca_numer_domu}")
    c.drawString(50, height - 355, f"Miejscowość: {nadawca_miejscowosc}")
    c.drawString(50, height - 375, f"Kod Pocztowy: {nadawca_kod_pocztowy}")
    c.drawString(50, height - 395, f"Kraj: {nadawca_kraj}")

    # Add a new page for the image
    c.showPage()

    # Decode and add PodpisObraz to PDF
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
            data_utworzenia, podpis_obraz, rodzaj_doreczenie, data_nadania, data_pisma, numer_nadania, adresat_nazwa, adresat_ulica, adresat_numer_domu, adresat_miejscowosc, adresat_kod_pocztowy, adresat_kraj, nadawca_nazwa, nadawca_nazwa2, nadawca_ulica, nadawca_numer_domu, nadawca_miejscowosc, nadawca_kod_pocztowy, nadawca_kraj = parse_xml_file(file_path)
            if rodzaj_doreczenie == "DORECZENIE":
                pdf_output_file = os.path.join(folder_path, f"{os.path.splitext(filename)[0]}.pdf")
                doreczenie_save_to_pdf(data_utworzenia, podpis_obraz, rodzaj_doreczenie, data_nadania, data_pisma, numer_nadania, adresat_nazwa, adresat_ulica, adresat_numer_domu, adresat_miejscowosc, adresat_kod_pocztowy, adresat_kraj, nadawca_nazwa, nadawca_nazwa2, nadawca_ulica, nadawca_numer_domu, nadawca_miejscowosc, nadawca_kod_pocztowy, nadawca_kraj, pdf_output_file)

if __name__ == "__main__":
    folder_path = os.path.abspath(os.getcwd())
    process_folder(folder_path)
    input("Naciśnij Enter, aby zakończyć...")