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

    # Extract DataUtworzenia
    data_utworzenia_elem = root.find('mstns:DataUtworzenia', ns)
    data_utworzenia = data_utworzenia_elem.text if data_utworzenia_elem is not None else "Brak danych"

    # Extract PodpisObraz
    podpis_obraz_elem = root.find('.//mstns:PodpisObraz', ns)
    podpis_obraz = podpis_obraz_elem.text.strip() if podpis_obraz_elem is not None else ""

    # Extract RodzajDoreczenie
    rodzaj_doreczenie_elem = root.find('.//mstns:RodzajDoreczenie', ns)
    rodzaj_doreczenie = rodzaj_doreczenie_elem.text.strip() if rodzaj_doreczenie_elem is not None else ""

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

def save_to_pdf(data_utworzenia, podpis_obraz, rodzaj_doreczenie, data_nadania, data_pisma, numer_nadania, adresat_nazwa, adresat_ulica, adresat_numer_domu, adresat_miejscowosc, adresat_kod_pocztowy, adresat_kraj, nadawca_nazwa, nadawca_nazwa2, nadawca_ulica, nadawca_numer_domu, nadawca_miejscowosc, nadawca_kod_pocztowy, nadawca_kraj, output_file):
    c = canvas.Canvas(output_file, pagesize=A4)
    width, height = A4

    # Register and set font to Arial
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
    c.setFont("Arial", 12)

    # Add DataUtworzenia to PDF
    c.drawString(100, height - 100, f"Data Utworzenia: {data_utworzenia}")

    # Add RodzajDoreczenie to PDF
    if rodzaj_doreczenie == "DORECZENIE":
        c.setFillColor(green)
        c.rect(95, height - 130, 200, 20, fill=True, stroke=False)
        c.setFillColorRGB(0, 0, 0)
    c.drawString(100, height - 125, f"Rodzaj Doreczenie: {rodzaj_doreczenie}")

    # Add DataNadania to PDF
    c.drawString(100, height - 150, f"Data Nadania: {data_nadania}")

    # Add DataPisma to PDF
    c.drawString(100, height - 175, f"Data Pisma: {data_pisma}")

    # Add NumerNadania as clickable link to PDF
    tracking_url = f"https://sledzenie.poczta-polska.pl/?numer={numer_nadania}"
    c.drawString(100, height - 200, "Numer Nadania: ")
    c.linkURL(tracking_url, (200, height - 200, 500, height - 185), relative=1, thickness=1, color=green)
    c.drawString(200, height - 200, numer_nadania)

    # Add Adresat to PDF
    c.drawString(100, height - 225, "Adresat:")
    c.drawString(100, height - 250, f"{adresat_nazwa}")
    c.drawString(100, height - 275, f"Ulica: {adresat_ulica} {adresat_numer_domu}")
    c.drawString(100, height - 300, f"Miejscowość: {adresat_miejscowosc}")
    c.drawString(100, height - 325, f"Kod Pocztowy: {adresat_kod_pocztowy}")
    c.drawString(100, height - 350, f"Kraj: {adresat_kraj}")

    # Add Nadawca to PDF
    c.drawString(100, height - 375, "Nadawca:")
    c.drawString(100, height - 400, f"{nadawca_nazwa} {nadawca_nazwa2}")
    c.drawString(100, height - 425, f"Ulica: {nadawca_ulica} {nadawca_numer_domu}")
    c.drawString(100, height - 450, f"Miejscowość: {nadawca_miejscowosc}")
    c.drawString(100, height - 475, f"Kod Pocztowy: {nadawca_kod_pocztowy}")
    c.drawString(100, height - 500, f"Kraj: {nadawca_kraj}")

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
            pdf_output_file = os.path.join(folder_path, f"{os.path.splitext(filename)[0]}.pdf")
            save_to_pdf(data_utworzenia, podpis_obraz, rodzaj_doreczenie, data_nadania, data_pisma, numer_nadania, adresat_nazwa, adresat_ulica, adresat_numer_domu, adresat_miejscowosc, adresat_kod_pocztowy, adresat_kraj, nadawca_nazwa, nadawca_nazwa2, nadawca_ulica, nadawca_numer_domu, nadawca_miejscowosc, nadawca_kod_pocztowy, nadawca_kraj, pdf_output_file)

if __name__ == "__main__":
    folder_path = os.path.abspath(os.getcwd())
    process_folder(folder_path)
    input("Naciśnij Enter, aby zakończyć...")