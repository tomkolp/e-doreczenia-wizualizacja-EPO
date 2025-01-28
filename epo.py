import os
import base64
import textwrap
import xml.etree.ElementTree as ET
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import green, black, red, orange
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from io import BytesIO
import requests
import webbrowser
from packaging import version

def doreczenie_parse_xml_file(file_path):
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


def zwrot_awizowany_parse_xml_file(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Błąd parsowania pliku XML: {e}")
        return "Brak danych", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""

    ns = {
        'mstns': 'http://msepo.gov.pl/epo/XSD/KartaEPO.xsd',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    status_przesylki = 0

    creation_date_elem = root.find('.//mstns:CreationDate', ns)
    creation_date = creation_date_elem.text if creation_date_elem is not None else "Brak danych"

    id_karta_epo_elem = root.find('.//mstns:IDKartaEPO', ns)
    id_karta_epo = id_karta_epo_elem.text if id_karta_epo_elem is not None else "Brak danych"

    przesylka_elem = root.find('.//mstns:TabletPrzesylka', ns)
    if przesylka_elem is not None:
        status_przesylki_elem = przesylka_elem.find('.//mstns:StatusPrzesylki', ns)
        status_przesylki = int(status_przesylki_elem.text) if status_przesylki_elem is not None else 0

        if status_przesylki != 6:
            return "Brak danych", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""

        id_przesylka_elem = przesylka_elem.find('.//mstns:IDPrzesylka', ns)
        id_przesylka = id_przesylka_elem.text if id_przesylka_elem is not None else "Brak danych"

        numer_nadania_elem = przesylka_elem.find('.//mstns:NumerNadania', ns)
        numer_nadania = numer_nadania_elem.text if numer_nadania_elem is not None else "Brak danych"

        data_nadania_elem = przesylka_elem.find('.//mstns:DataNadania', ns)
        data_nadania = data_nadania_elem.text if data_nadania_elem is not None else "Brak danych"

        adresat_elem = przesylka_elem.find('.//mstns:Adresat', ns)
        adresat = adresat_elem.text if adresat_elem is not None else "Brak danych"

        kod_pocztowy_elems = przesylka_elem.findall('.//mstns:KodPocztowy', ns)
        kod_pocztowy_adresat = kod_pocztowy_elems[0].text if len(kod_pocztowy_elems) > 0 else "Brak danych"
        kod_pocztowy_nadawca = kod_pocztowy_elems[1].text if len(kod_pocztowy_elems) > 1 else "Brak danych"

        ulica_elems = przesylka_elem.findall('.//mstns:Ulica', ns)
        ulica_adresat = ulica_elems[0].text if len(ulica_elems) > 0 else "Brak danych"
        ulica_nadawca = ulica_elems[1].text if len(ulica_elems) > 1 else "Brak danych"

        dom_elems = przesylka_elem.findall('.//mstns:Dom', ns)
        dom_adresat = dom_elems[0].text if len(dom_elems) > 0 else "Brak danych"
        dom_nadawca = dom_elems[1].text if len(dom_elems) > 1 else "Brak danych"

        lokal_elems = przesylka_elem.findall('.//mstns:Lokal', ns)
        lokal_adresat = lokal_elems[0].text if len(lokal_elems) > 0 else "Brak danych"
        lokal_nadawca = lokal_elems[1].text if len(lokal_elems) > 1 else "Brak danych"

        miejscowosc_elem = przesylka_elem.find('.//mstns:Miejscowosc', ns)
        adresat_miejscowosc = miejscowosc_elem.text if miejscowosc_elem is not None else "Brak danych"

        systemowa_data_elem = przesylka_elem.find('.//mstns:SystemowaDataOznaczenia', ns)
        systemowa_data = systemowa_data_elem.text if systemowa_data_elem is not None else "Brak danych"

        brak_doreczenia_elem = przesylka_elem.find('.//mstns:BrakDoreczenia', ns)
        brak_doreczenia = brak_doreczenia_elem.text if brak_doreczenia_elem is not None else "Brak danych"

        data_awizo1_elem = przesylka_elem.find('.//mstns:DataAwizo1', ns)
        data_awizo1 = data_awizo1_elem.text if data_awizo1_elem is not None else "Brak danych"

        data_awizo2_elem = przesylka_elem.find('.//mstns:DataAwizo2', ns)
        data_awizo2 = data_awizo2_elem.text if data_awizo2_elem is not None else "Brak danych"

        nadawca_nazwa_elem = przesylka_elem.find('.//mstns:NazwaJednostki', ns)
        nadawca_nazwa = nadawca_nazwa_elem.text if nadawca_nazwa_elem is not None else "Brak danych"
        nadawca_wydzial_elem = przesylka_elem.find('.//mstns:Wydzial', ns)
        nadawca_wydzial = nadawca_wydzial_elem.text if nadawca_wydzial_elem is not None else ""
        nadawca_miasto_elem = przesylka_elem.find('.//mstns:Miasto', ns)
        nadawca_miasto = nadawca_miasto_elem.text if nadawca_miasto_elem is not None else "Brak danych"
        nadawca_kod_pocztowy = kod_pocztowy_nadawca
        nadawca_ulica = ulica_nadawca
        nadawca_dom = dom_nadawca
        nadawca_lokal = lokal_nadawca
    else:
        id_przesylka = numer_nadania = data_nadania = adresat = kod_pocztowy_adresat = kod_pocztowy_nadawca = ulica_adresat = ulica_nadawca = dom_adresat = dom_nadawca = lokal_adresat = lokal_nadawca = adresat_miejscowosc = systemowa_data = brak_doreczenia = data_awizo1 = data_awizo2 = nadawca_nazwa = nadawca_wydzial = nadawca_miasto = nadawca_kod_pocztowy = nadawca_ulica = nadawca_dom = nadawca_lokal = "Brak danych"

    return creation_date, id_karta_epo, id_przesylka, numer_nadania, data_nadania, adresat, kod_pocztowy_adresat, ulica_adresat, dom_adresat, lokal_adresat, adresat_miejscowosc, status_przesylki, systemowa_data, brak_doreczenia, data_awizo1, data_awizo2, nadawca_nazwa, nadawca_wydzial, nadawca_miasto, nadawca_kod_pocztowy, nadawca_ulica, nadawca_dom, nadawca_lokal

def zwrot_parse_xml_file(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Błąd parsowania pliku XML: {e}")
        return "Brak danych", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""

    ns = {
        'mstns': 'KartaEPO/2018/07/15',
        'ds': 'http://www.w3.org/2000/09/xmldsig#',
        'xmime': 'http://www.w3.org/2005/05/xmlmime',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    rodzaj_zwrot_elem = root.find('.//mstns:RodzajZwrot', ns)
    rodzaj_zwrot = rodzaj_zwrot_elem.text if rodzaj_zwrot_elem is not None else ""

    if rodzaj_zwrot != "ZWROT":
        return "Brak danych", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""

    data_utworzenia_elem = root.find('.//mstns:DataUtworzenia', ns)
    data_utworzenia = data_utworzenia_elem.text if data_utworzenia_elem is not None else "Brak danych"

    id_karty_epo_elem = root.find('.//mstns:IdKartyEPO', ns)
    id_karty_epo = id_karty_epo_elem.text if id_karty_epo_elem is not None else "Brak danych"

    id_przesylki_elem = root.find('.//mstns:IdPrzesylki', ns)
    id_przesylki = id_przesylki_elem.text if id_przesylki_elem is not None else "Brak danych"

    numer_nadania_elem = root.find('.//mstns:NumerNadania', ns)
    numer_nadania = numer_nadania_elem.text if numer_nadania_elem is not None else "Brak danych"

    data_nadania_elem = root.find('.//mstns:DataNadania', ns)
    data_nadania = data_nadania_elem.text if data_nadania_elem is not None else "Brak danych"

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

    tryb_doreczenia_elem = root.find('.//mstns:TrybDoreczenia', ns)
    tryb_doreczenia = tryb_doreczenia_elem.text if tryb_doreczenia_elem is not None else "Brak danych"
    do_rak_wlasnych = tryb_doreczenia_elem.attrib.get('DoRakWlasnych', 'false') == 'true' if tryb_doreczenia_elem is not None else False

    systemowa_data_elem = root.find('.//mstns:SystemowaDataOznaczenia', ns)
    systemowa_data = systemowa_data_elem.text if systemowa_data_elem is not None else "Brak danych"

    data_adnotacji_elem = root.find('.//mstns:DataAdnotacji', ns)
    data_adnotacji = data_adnotacji_elem.text if data_adnotacji_elem is not None else "Brak danych"

    data_zdarzenia_elem = root.find('.//mstns:DataZdarzenia', ns)
    data_zdarzenia = data_zdarzenia_elem.text if data_zdarzenia_elem is not None else "Brak danych"

    operator_imie_elem = root.find('.//mstns:Operator/mstns:Imie', ns)
    operator_imie = operator_imie_elem.text if operator_imie_elem is not None else "Brak danych"
    operator_nazwisko_elem = root.find('.//mstns:Operator/mstns:Nazwisko', ns)
    operator_nazwisko = operator_nazwisko_elem.text if operator_nazwisko_elem is not None else "Brak danych"
    operator_id_elem = root.find('.//mstns:Operator/mstns:IdOperatora', ns)
    operator_id = operator_id_elem.text if operator_id_elem is not None else "Brak danych"

    placowka_nazwa_elem = root.find('.//mstns:PlacowkaPocztowa/mstns:AdresPlacowkiPocztowej/mstns:Nazwa', ns)
    placowka_nazwa = placowka_nazwa_elem.text if placowka_nazwa_elem is not None else "Brak danych"
    placowka_ulica_elem = root.find('.//mstns:PlacowkaPocztowa/mstns:AdresPlacowkiPocztowej/mstns:Ulica', ns)
    placowka_ulica = placowka_ulica_elem.text if placowka_ulica_elem is not None else "Brak danych"
    placowka_numer_domu_elem = root.find('.//mstns:PlacowkaPocztowa/mstns:AdresPlacowkiPocztowej/mstns:NumerDomu', ns)
    placowka_numer_domu = placowka_numer_domu_elem.text if placowka_numer_domu_elem is not None else "Brak danych"
    placowka_miejscowosc_elem = root.find('.//mstns:PlacowkaPocztowa/mstns:AdresPlacowkiPocztowej/mstns:Miejscowosc', ns)
    placowka_miejscowosc = placowka_miejscowosc_elem.text if placowka_miejscowosc_elem is not None else "Brak danych"
    placowka_kod_pocztowy_elem = root.find('.//mstns:PlacowkaPocztowa/mstns:AdresPlacowkiPocztowej/mstns:KodPocztowy', ns)
    placowka_kod_pocztowy = placowka_kod_pocztowy_elem.text if placowka_kod_pocztowy_elem is not None else "Brak danych"
    placowka_kraj_elem = root.find('.//mstns:PlacowkaPocztowa/mstns:AdresPlacowkiPocztowej/mstns:Kraj', ns)
    placowka_kraj = placowka_kraj_elem.text if placowka_kraj_elem is not None else "Brak danych"

    powod_zwrotu_elem = root.find('.//mstns:PowodZwrotu', ns)
    powod_zwrotu = powod_zwrotu_elem.text if powod_zwrotu_elem is not None else "Brak danych"

    tresc_adnotacji_elem = root.find('.//mstns:TrescAdnotacji', ns)
    tresc_adnotacji = tresc_adnotacji_elem.text if tresc_adnotacji_elem is not None else "Brak danych"

    return (data_utworzenia, id_karty_epo, id_przesylki, numer_nadania, data_nadania, adresat_nazwa, adresat_ulica, adresat_numer_domu, adresat_miejscowosc, adresat_kod_pocztowy, nadawca_nazwa, nadawca_nazwa2, nadawca_ulica, nadawca_numer_domu, nadawca_miejscowosc, nadawca_kod_pocztowy, tryb_doreczenia, do_rak_wlasnych, systemowa_data, data_adnotacji, data_zdarzenia, operator_imie, operator_nazwisko, operator_id, placowka_nazwa, placowka_ulica, placowka_numer_domu, placowka_miejscowosc, placowka_kod_pocztowy, placowka_kraj, powod_zwrotu, tresc_adnotacji, rodzaj_zwrot)

def doreczenie_po_awizo_parse_xml_file(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Błąd parsowania pliku XML: {e}")
        return tuple(["Brak danych"] * 40)

    ns = {
        'mstns': 'http://msepo.gov.pl/epo/XSD/KartaEPO.xsd',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    status_przesylki = 0

    creation_date_elem = root.find('.//mstns:CreationDate', ns)
    creation_date = creation_date_elem.text if creation_date_elem is not None else "Brak danych"

    id_karta_epo_elem = root.find('.//mstns:IDKartaEPO', ns)
    id_karta_epo = id_karta_epo_elem.text if id_karta_epo_elem is not None else "Brak danych"

    przesylka_elem = root.find('.//mstns:TabletPrzesylki', ns)
    if przesylka_elem is not None:
        status_przesylki_elem = przesylka_elem.find('.//mstns:StatusPrzesylki', ns)
        status_przesylki = int(status_przesylki_elem.text) if status_przesylki_elem is not None else 0

        if status_przesylki != 5:
            return tuple(["Brak danych"] * 40)

        id_przesylka_elem = przesylka_elem.find('.//mstns:IDPrzesylka', ns)
        id_przesylka = id_przesylka_elem.text if id_przesylka_elem is not None else "Brak danych"

        numer_nadania_elem = przesylka_elem.find('.//mstns:NumerNadania', ns)
        numer_nadania = numer_nadania_elem.text if numer_nadania_elem is not None else "Brak danych"

        data_nadania_elem = przesylka_elem.find('.//mstns:DataNadania', ns)
        data_nadania = data_nadania_elem.text if data_nadania_elem is not None else "Brak danych"

        adresat_elem = przesylka_elem.find('.//mstns:Adresat', ns)
        adresat = adresat_elem.text if adresat_elem is not None else "Brak danych"

        kod_pocztowy_elems = przesylka_elem.findall('.//mstns:KodPocztowy', ns)
        kod_pocztowy_adresat = kod_pocztowy_elems[0].text if len(kod_pocztowy_elems) > 0 else "Brak danych"
        kod_pocztowy_nadawca = kod_pocztowy_elems[1].text if len(kod_pocztowy_elems) > 1 else "Brak danych"

        ulica_elems = przesylka_elem.findall('.//mstns:Ulica', ns)
        ulica_adresat = ulica_elems[0].text if len(ulica_elems) > 0 else "Brak danych"
        ulica_nadawca = ulica_elems[1].text if len(ulica_elems) > 1 else "Brak danych"

        dom_elems = przesylka_elem.findall('.//mstns:Dom', ns)
        dom_adresat = dom_elems[0].text if len(dom_elems) > 0 else "Brak danych"
        dom_nadawca = dom_elems[1].text if len(dom_elems) > 1 else "Brak danych"

        lokal_elems = przesylka_elem.findall('.//mstns:Lokal', ns)
        lokal_adresat = lokal_elems[0].text if len(lokal_elems) > 0 else "Brak danych"
        lokal_nadawca = lokal_elems[1].text if len(lokal_elems) > 1 else "Brak danych"

        miejscowosc_elem = przesylka_elem.find('.//mstns:Miejscowosc', ns)
        miejscowosc = miejscowosc_elem.text if miejscowosc_elem is not None else "Brak danych"

        systemowa_data_elem = przesylka_elem.find('.//mstns:SystemowaDataOznaczenia', ns)
        systemowa_data = systemowa_data_elem.text if systemowa_data_elem is not None else "Brak danych"

        odbiorca_przesylki_elem = przesylka_elem.find('.//mstns:OdbiorcaPrzesylki', ns)
        odbiorca_przesylki = odbiorca_przesylki_elem.text if odbiorca_przesylki_elem is not None else "Brak danych"

        imie_nazwisko_odbiorcy_elem = przesylka_elem.find('.//mstns:ImieINazwiskoOdbiorcy', ns)
        imie_nazwisko_odbiorcy = imie_nazwisko_odbiorcy_elem.text if imie_nazwisko_odbiorcy_elem is not None else "Brak danych"

        podpis_elem = przesylka_elem.find('.//mstns:Podpis', ns)
        podpis = podpis_elem.text if podpis_elem is not None else "Brak danych"

        brak_doreczenia_elem = przesylka_elem.find('.//mstns:BrakDoreczenia', ns)
        brak_doreczenia = brak_doreczenia_elem.text if brak_doreczenia_elem is not None else "Brak danych"

        awizo_miejsce_przesylki_elem = przesylka_elem.find('.//mstns:AwizoMiejscePrzesylki', ns)
        awizo_miejsce_przesylki = awizo_miejsce_przesylki_elem.text if awizo_miejsce_przesylki_elem is not None else "Brak danych"

        awizo_miejsce_zawiadomienia_elem = przesylka_elem.find('.//mstns:AwizoMiejsceZawiadomienia', ns)
        awizo_miejsce_zawiadomienia = awizo_miejsce_zawiadomienia_elem.text if awizo_miejsce_zawiadomienia_elem is not None else "Brak danych"

        data_awizo1_elem = przesylka_elem.find('.//mstns:DataAwizo1', ns)
        data_awizo1 = data_awizo1_elem.text if data_awizo1_elem is not None else "Brak danych"

        #data_awizo2_elem = przesylka_elem.find('.//mstns:DataAwizo2', ns)
        #data_awizo2 = data_awizo2_elem.text if data_awizo2_elem is not None else "Brak danych"

        jednostka_ms_elem = przesylka_elem.find('.//mstns:TabletJednostkaMS', ns)
        id_jednostka_ms_elem = jednostka_ms_elem.find('.//mstns:IDJednostkaMS', ns)
        id_jednostka_ms = id_jednostka_ms_elem.text if id_jednostka_ms_elem is not None else "Brak danych"

        nazwa_jednostki_elem = jednostka_ms_elem.find('.//mstns:NazwaJednostki', ns)
        nazwa_jednostki = nazwa_jednostki_elem.text if nazwa_jednostki_elem is not None else "Brak danych"

        wydzial_elem = jednostka_ms_elem.find('.//mstns:Wydzial', ns)
        wydzial = wydzial_elem.text if wydzial_elem is not None else "Brak danych"

        miasto_elem = jednostka_ms_elem.find('.//mstns:Miasto', ns)
        miasto = miasto_elem.text if miasto_elem is not None else "Brak danych"

        #kod_pocztowy_jednostki_elem = jednostka_ms_elem.find('.//mstns:KodPocztowy', ns)
        #kod_pocztowy_jednostki = kod_pocztowy_jednostki_elem.text if kod_pocztowy_jednostki_elem is not None else "Brak danych"

        #ulica_jednostki_elem = jednostka_ms_elem.find('.//mstns:Ulica', ns)
        #ulica_jednostki = ulica_jednostki_elem.text if ulica_jednostki_elem is not None else "Brak danych"

        #dom_jednostki_elem = jednostka_ms_elem.find('.//mstns:Dom', ns)
        #dom_jednostki = dom_jednostki_elem.text if dom_jednostki_elem is not None else "Brak danych"

        #lokal_jednostki_elem = jednostka_ms_elem.find('.//mstns:Lokal', ns)
        #lokal_jednostki = lokal_jednostki_elem.text if lokal_jednostki_elem is not None else "Brak danych"

        dane_biometryczne_elem = przesylka_elem.find('.//mstns:DaneBiometryczne', ns)
        data_podpisu_elem = dane_biometryczne_elem.find('.//mstns:DataPodpisu', ns)
        data_podpisu = data_podpisu_elem.text if data_podpisu_elem is not None else "Brak danych"

        data_zapisu_elem = dane_biometryczne_elem.find('.//mstns:DataZapisu', ns)
        data_zapisu = data_zapisu_elem.text if data_zapisu_elem is not None else "Brak danych"

        id_operatora_elem = dane_biometryczne_elem.find('.//mstns:IdOperatora', ns)
        id_operatora = id_operatora_elem.text if id_operatora_elem is not None else "Brak danych"

        id_urzadzenia_elem = dane_biometryczne_elem.find('.//mstns:IdUrzadzenia', ns)
        id_urzadzenia = id_urzadzenia_elem.text if id_urzadzenia_elem is not None else "Brak danych"

        #czas_nacisk_elem = dane_biometryczne_elem.find('.//mstns:CzasNacisk', ns)
        #czas_elem = czas_nacisk_elem.find('.//mstns:Czas', ns)
        #czas = czas_elem.text if czas_elem is not None else "Brak danych"

        wydajacy_elem = przesylka_elem.find('.//mstns:Wydajacy', ns)
        imie_wydajacego = wydajacy_elem.attrib.get('Imie', 'Brak danych')
        nazwisko_wydajacego = wydajacy_elem.attrib.get('Nazwisko', 'Brak danych')
        id_wydajacego = wydajacy_elem.attrib.get('Id', 'Brak danych')
        id_placowka = wydajacy_elem.attrib.get('IDPlacowka', 'Brak danych')
        nazwa_placowki = wydajacy_elem.attrib.get('NazwaPlacowki', 'Brak danych')
        adres_placowki = wydajacy_elem.attrib.get('AdresPlacowki', 'Brak danych')
        pni_placowki = wydajacy_elem.attrib.get('PNIPlacowki', 'Brak danych')

    else:
        return tuple(["Brak danych"] * 40)

    return (creation_date, id_karta_epo, id_przesylka, numer_nadania, data_nadania, adresat, kod_pocztowy_adresat, kod_pocztowy_nadawca, ulica_adresat, ulica_nadawca, dom_adresat, dom_nadawca, lokal_adresat, lokal_nadawca, miejscowosc, status_przesylki, systemowa_data, odbiorca_przesylki, imie_nazwisko_odbiorcy, podpis, brak_doreczenia, awizo_miejsce_przesylki, awizo_miejsce_zawiadomienia, data_awizo1, id_jednostka_ms, nazwa_jednostki, wydzial, miasto, data_podpisu, data_zapisu, id_operatora, id_urzadzenia, imie_wydajacego, nazwisko_wydajacego, id_wydajacego, id_placowka, nazwa_placowki, adres_placowki, pni_placowki, "brak")

def doreczenie_save_to_pdf(data_utworzenia, podpis_obraz, rodzaj_doreczenie, data_nadania, data_pisma, numer_nadania, adresat_nazwa, adresat_ulica, adresat_numer_domu, adresat_miejscowosc, adresat_kod_pocztowy, nadawca_nazwa, nadawca_nazwa2, nadawca_ulica, nadawca_numer_domu, nadawca_miejscowosc, nadawca_kod_pocztowy, id_karty_epo, id_przesylki, tryb_doreczenia, do_rak_wlasnych, sygnatura, rodzaj, adnotacje, podmiot_doreczenia, tresc_adnotacji, output_file, source_file):
    if rodzaj_doreczenie != "DORECZENIE":
        return
    try:
        c = canvas.Canvas(output_file, pagesize=A4)
        width, height = A4

        # Rejestracja i ustawienie czcionki Arial
        pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
        c.setFont("Arial", 11)

        # Zawijanie nazwy pliku
        text_wrap_width = 90  # Maksymalna liczba znaków dla nazwy pliku

        source_file_name = os.path.basename(source_file)
        wrapped_file_name = textwrap.wrap(source_file_name, width=text_wrap_width)

        y_position = height - 30

        c.drawString(48.2, y_position, "Raport z pliku: ")
        y_position -= 20

        for line in wrapped_file_name:
            c.drawString(48.2, y_position, line)
            y_position -= 20

        # Dodanie pozostałych informacji do PDF
        c.drawString(48.2, y_position, f"IdKartyEPO: {id_karty_epo}")
        y_position -= 20
        c.drawString(48.2, y_position, f"IdPrzesylki: {id_przesylki}")
        y_position -= 20

        # Dodanie DataUtworzenia do PDF
        c.setFillColor(green)
        c.drawString(50, y_position, f"Data Utworzenia: {data_utworzenia} (Data doręczenia)")
        c.setFillColor(black)
        y_position -= 20

        # Dodanie RodzajDoreczenie do PDF
        if rodzaj_doreczenie == "DORECZENIE":
            c.setFillColor(green)
        c.drawString(50, y_position, f"Rodzaj Doręczenia: {rodzaj_doreczenie}")
        c.setFillColor(black)  # Powrót do domyślnego koloru
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
    except PermissionError:
        print(f"Błąd: Nie można zapisać pliku PDF '{output_file}'. Upewnij się, że plik nie jest otwarty w innym programie.")

def zwrot_awizowany_save_to_pdf(creation_date, id_karta_epo, id_przesylka, numer_nadania, data_nadania, adresat, kod_pocztowy_adresat, ulica_adresat, dom_adresat, lokal_adresat, adresat_miejscowosc, status_przesylki, systemowa_data, brak_doreczenia, data_awizo1, data_awizo2, nadawca_nazwa, nadawca_wydzial, nadawca_miasto, nadawca_kod_pocztowy, nadawca_ulica, nadawca_dom, nadawca_lokal, output_file, source_file):
    if status_przesylki != 6:
        return

    try:
        c = canvas.Canvas(output_file, pagesize=A4)
        width, height = A4

        # Rejestracja i ustawienie czcionki Arial
        pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
        c.setFont("Arial", 11)

        # Zawijanie nazwy pliku
        text_wrap_width = 80  # Maksymalna liczba znaków dla nazwy pliku

        source_file_name = os.path.basename(source_file)
        wrapped_file_name = textwrap.wrap(source_file_name, width=text_wrap_width)

        y_position = height - 30

        c.drawString(48.2, y_position, "Raport z pliku: ")
        y_position -= 20

        for line in wrapped_file_name:
            c.drawString(48.2, y_position, line)
            y_position -= 20

        # Dodanie pozostałych informacji do PDF
        c.drawString(48.2, y_position, f"IdKartyEPO: {id_karta_epo}")
        y_position -= 20
        c.drawString(48.2, y_position, f"IdPrzesylki: {id_przesylka}")
        y_position -= 20

        c.drawString(50, y_position, f"Data Utworzenia: {creation_date}")
        y_position -= 20

        c.drawString(50, y_position, f"Data Nadania: {data_nadania}")
        y_position -= 20

        c.drawString(50, y_position, f"Status Przesyłki: {status_przesylki}")
        y_position -= 20

        c.setFillColor(orange)
        c.drawString(50, y_position, f"Systemowa Data Oznaczenia: {systemowa_data} (Data zwrotu po awizacji)")
        c.setFillColor(black)
        y_position -= 20

        c.drawString(50, y_position, f"Brak Doręczenia: {brak_doreczenia}")
        y_position -= 20

        c.setFillColor(orange)
        c.drawString(50, y_position, f"Data Awizo 1: {data_awizo1}")
        c.setFillColor(black)
        y_position -= 20

       # c.drawString(50, y_position, f"Data Awizo 2: {data_awizo2}")
        #y_position -= 20

        tracking_url = f"https://sledzenie.poczta-polska.pl/?numer={numer_nadania}"
        c.drawString(50, y_position, "Nr. przesyłki: ")
        c.setFillColorRGB(0, 0, 1)
        c.drawString(150, y_position, tracking_url)
        c.linkURL(tracking_url, (150, y_position, 450, y_position + 15), relative=1, thickness=0, color=None)
        c.setFillColor(black)
        y_position -= 20

        c.drawString(50, y_position, "Adresat:")
        c.line(50, y_position - 2, 100, y_position - 2)
        y_position -= 20
        c.drawString(50, y_position, f"{adresat}")
        y_position -= 20
        c.drawString(50, y_position, f"Ulica: {ulica_adresat} {dom_adresat}")
        if lokal_adresat:
            c.drawString(50, y_position, f"Lokal: {lokal_adresat}")
            y_position -= 20
        y_position -= 20
        c.drawString(50, y_position, f"Miejscowość: {adresat_miejscowosc}")
        y_position -= 20
        c.drawString(50, y_position, f"Kod Pocztowy: {kod_pocztowy_adresat}")
        y_position -= 20

        c.drawString(50, y_position, "Nadawca:")
        c.line(50, y_position - 2, 100, y_position - 2)
        y_position -= 20
        c.drawString(50, y_position, f"{nadawca_nazwa}")
        y_position -= 20
        c.drawString(50, y_position, f"Wydział: {nadawca_wydzial}")
        y_position -= 20
        c.drawString(50, y_position, f"Miasto: {nadawca_miasto}")
        y_position -= 20
        c.drawString(50, y_position, f"Ulica: {nadawca_ulica} {nadawca_dom}")
        if nadawca_lokal:
            c.drawString(50, y_position, f"Lokal: {nadawca_lokal}")
            y_position -= 20
        y_position -= 20
        c.drawString(50, y_position, f"Kod Pocztowy: {nadawca_kod_pocztowy}")
        y_position -= 20

        c.save()
    except PermissionError:
        print(f"Błąd: Nie można zapisać pliku PDF '{output_file}'. Upewnij się, że plik nie jest otwarty w innym programie.")

def zwrot_save_to_pdf(data_utworzenia, id_karty_epo, id_przesylki, numer_nadania, data_nadania, adresat_nazwa, adresat_ulica, adresat_numer_domu, adresat_miejscowosc, adresat_kod_pocztowy, nadawca_nazwa, nadawca_nazwa2, nadawca_ulica, nadawca_numer_domu, nadawca_miejscowosc, nadawca_kod_pocztowy, tryb_doreczenia, do_rak_wlasnych, systemowa_data, data_adnotacji, data_zdarzenia, operator_imie, operator_nazwisko, operator_id, placowka_nazwa, placowka_ulica, placowka_numer_domu, placowka_miejscowosc, placowka_kod_pocztowy, placowka_kraj, powod_zwrotu, tresc_adnotacji, rodzaj_zwrot, output_file):

    try:
        c = canvas.Canvas(output_file, pagesize=A4)
        width, height = A4

        pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
        c.setFont("Arial", 11)

        margin = 48.2
        available_width = width - 2 * margin

        y_position = height - 50
        c.drawString(50, y_position, f"Data Utworzenia: {data_utworzenia}")
        y_position -= 20
        c.setFillColor(red)
        c.drawString(50, y_position, f"Systemowa Data Oznaczenia: {systemowa_data} (Data zwrotu)")
        c.setFillColor(black)
        y_position -= 20

        # Dodanie NumerNadania jako klikalny link do PDF
        tracking_url = f"https://sledzenie.poczta-polska.pl/?numer={numer_nadania}"
        c.drawString(50, y_position, "Nr. przesyłki: ")
        c.setFillColorRGB(0, 0, 1)  # Ustawienie koloru na niebieski
        c.drawString(150, y_position, tracking_url)
        c.linkURL(tracking_url, (150, y_position, 450, y_position + 15), relative=1, thickness=0, color=None)
        c.setFillColor(black)  # Powrót do domyślnego koloru
        y_position -= 20

        c.drawString(50, y_position, f"Data Nadania: {data_nadania}")
        y_position -= 20

        c.drawString(50, y_position, "Adresat:")
        c.line(50, y_position - 2, 100, y_position - 2)
        y_position -= 20
        c.drawString(50, y_position, f"Nazwa: {adresat_nazwa}")
        y_position -= 20
        c.drawString(50, y_position, f"Ulica: {adresat_ulica} {adresat_numer_domu}")
        y_position -= 20
        c.drawString(50, y_position, f"Miejscowość: {adresat_miejscowosc}")
        y_position -= 20
        c.drawString(50, y_position, f"Kod Pocztowy: {adresat_kod_pocztowy}")
        y_position -= 20

        c.drawString(50, y_position, "Nadawca:")
        c.line(50, y_position - 2, 100, y_position - 2)
        y_position -= 20
        c.drawString(50, y_position, f"Nazwa: {nadawca_nazwa}")
        y_position -= 20
        c.drawString(50, y_position, f"Nazwa cd.: {nadawca_nazwa2}")
        y_position -= 20
        c.drawString(50, y_position, f"Ulica: {nadawca_ulica} {nadawca_numer_domu}")
        y_position -= 20
        c.drawString(50, y_position, f"Miejscowość: {nadawca_miejscowosc}")
        y_position -= 20
        c.drawString(50, y_position, f"Kod Pocztowy: {nadawca_kod_pocztowy}")
        y_position -= 20

        c.drawString(50, y_position, f"Tryb Doręczenia: {tryb_doreczenia}")
        y_position -= 20
        c.drawString(50, y_position, f"Do Rąk Własnych: {'Tak' if do_rak_wlasnych else 'Nie'}")
        y_position -= 20
        y_position -= 20
        c.drawString(50, y_position, f"Data Adnotacji: {data_adnotacji}")
        y_position -= 20
        c.drawString(50, y_position, f"Data Zdarzenia: {data_zdarzenia}")
        y_position -= 20

        c.drawString(50, y_position, "Operator:")
        c.line(50, y_position - 2, 100, y_position - 2)
        y_position -= 20
        c.drawString(50, y_position, f"Imię: {operator_imie}")
        y_position -= 20
        c.drawString(50, y_position, f"Nazwisko: {operator_nazwisko}")
        y_position -= 20
        c.drawString(50, y_position, f"ID Operatora: {operator_id}")
        y_position -= 20

        c.drawString(50, y_position, "Placówka Pocztowa:")
        c.line(50, y_position - 2, 150, y_position - 2)
        y_position -= 20
        c.drawString(50, y_position, f"Nazwa: {placowka_nazwa}")
        y_position -= 20
        c.drawString(50, y_position, f"Ulica: {placowka_ulica} {placowka_numer_domu}")
        y_position -= 20
        c.drawString(50, y_position, f"Miejscowość: {placowka_miejscowosc}")
        y_position -= 20
        c.drawString(50, y_position, f"Kod Pocztowy: {placowka_kod_pocztowy}")
        y_position -= 20
        c.drawString(50, y_position, f"Kraj: {placowka_kraj}")
        y_position -= 20

        c.drawString(50, y_position, f"Powód Zwrotu: {powod_zwrotu}")
        y_position -= 20

        c.setFillColor(red)
        c.drawString(50, y_position, f"Treść Adnotacji: {tresc_adnotacji}")
        c.setFillColor(black)
        y_position -= 20

        c.save()
    except PermissionError:
        print(f"Błąd: Nie można zapisać pliku PDF '{output_file}'. Upewnij się, że plik nie jest otwarty w innym programie.")

def doreczenie_po_awizo_save_to_pdf(creation_date, id_karta_epo, id_przesylka, numer_nadania, data_nadania, adresat, kod_pocztowy_adresat, kod_pocztowy_nadawca, ulica_adresat, ulica_nadawca, dom_adresat, dom_nadawca, lokal_adresat, lokal_nadawca, miejscowosc, status_przesylki, systemowa_data, odbiorca_przesylki, imie_nazwisko_odbiorcy, podpis, brak_doreczenia, awizo_miejsce_przesylki, awizo_miejsce_zawiadomienia, data_awizo1, id_jednostka_ms, nazwa_jednostki, wydzial, miasto, data_podpisu, data_zapisu, id_operatora, id_urzadzenia, imie_wydajacego, nazwisko_wydajacego, id_wydajacego, id_placowka, nazwa_placowki, adres_placowki, pni_placowki, output_file, podpis_obraz_base64, source_file):

    try:
        c = canvas.Canvas(output_file, pagesize=A4)
        width, height = A4

        pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
        c.setFont("Arial", 11)

        # Zawijanie nazwy pliku
        text_wrap_width = 90  # Maksymalna liczba znaków dla nazwy pliku

        source_file_name = os.path.basename(source_file)
        wrapped_file_name = textwrap.wrap(source_file_name, width=text_wrap_width)

        y_position = height - 30

        c.drawString(48.2, y_position, "Raport z pliku: ")
        y_position -= 20

        for line in wrapped_file_name:
            c.drawString(48.2, y_position, line)
            y_position -= 20

        # Dodanie pozostałych informacji do PDF
        c.drawString(48.2, y_position, f"IdKartyEPO: {id_karta_epo}")
        y_position -= 20
        c.drawString(48.2, y_position, f"IdPrzesylki: {id_przesylka}")
        y_position -= 20

        c.drawString(50, y_position, f"Data Utworzenia: {creation_date} ")
        y_position -= 20

        if status_przesylki == 5:
            c.setFillColor(green)
            c.drawString(50, y_position, "Wydana (po awizo)")
            c.setFillColor(black)
            y_position -= 20
        else:
            c.drawString(50, y_position, f"Status Przesyłki: {status_przesylki}")
            y_position -= 20


        odbiorca_przesylki_map = {
            0: "Adresat",
            1: "Upoważniony Pracownik",
            2: "Osoba uprawniona do reprezentacji",
            3: "Pełnomocnik pocztowy",
            4: "Przedstawiciel ustawowy adresata"
        }

        odbiorca_przesylki = int(odbiorca_przesylki)

        if 0 <= odbiorca_przesylki <= 4:
            odbiorca_przesylki_text = odbiorca_przesylki_map[odbiorca_przesylki]
            c.drawString(50, y_position, f"Odbiorca Przesyłki: {odbiorca_przesylki_text}")
            y_position -= 20


        c.drawString(50, y_position, f"Imię i Nazwisko Odbiorcy: {imie_nazwisko_odbiorcy}")
        y_position -= 20

        c.setFillColor(green)
        c.drawString(50, y_position, f"Systemowa Data Oznaczenia: {systemowa_data} (Data odbioru przesyłki)")
        c.setFillColor(black)
        y_position -= 20

        c.drawString(50, y_position, f"Data Nadania: {data_nadania}")
        y_position -= 20

        #c.drawString(50, y_position, f"Brak Doręczenia: {brak_doreczenia}")
        #y_position -= 20

        awizo_miejsce_zawiadomienia_map = {
            0: "Skrzynka Oddawcza",
            1: "Drzwi",
            2: "Skrytka Pocztowa",
            3: "Inne widoczne miejsce",
            4: "Biuro",
            5: "Inne pomieszczenie",
            6: "Inne widoczne miejsce przy wejściu na posesję"
        }

        awizo_miejsce_zawiadomienia = int(awizo_miejsce_zawiadomienia)

        if 0 <= awizo_miejsce_zawiadomienia <= 6:
            awizo_miejsce_zawiadomienia_text = awizo_miejsce_zawiadomienia_map[awizo_miejsce_zawiadomienia]
            c.drawString(50, y_position, f"Awizo Miejsce Zawiadomienia: {awizo_miejsce_zawiadomienia_text}")
            y_position -= 20
        c.setFillColor(orange)
        c.drawString(50, y_position, f"Data Awizo 1: {data_awizo1}")
        c.setFillColor(black)
        y_position -= 20

        awizo_miejsce_przesylki_map = {
            0: "placówka pocztowa",
            1: "urząd gminy"
        }
        awizo_miejsce_przesylki = int(awizo_miejsce_przesylki)
        if 0 <= awizo_miejsce_przesylki <= 1:
            awizo_miejsce_przesylki_text = awizo_miejsce_przesylki_map[awizo_miejsce_przesylki]
            c.drawString(50, y_position, f"Miejsce Przechowywania Przesyłki: {awizo_miejsce_przesylki_text}")
            y_position -= 20

        tracking_url = f"https://sledzenie.poczta-polska.pl/?numer={numer_nadania}"
        c.drawString(50, y_position, "Nr. przesyłki: ")
        c.setFillColorRGB(0, 0, 1)
        c.drawString(150, y_position, tracking_url)
        c.linkURL(tracking_url, (150, y_position, 450, y_position + 15), relative=1, thickness=0, color=None)
        c.setFillColor(black)
        y_position -= 20

        c.drawString(50, y_position, "Adresat:")
        c.line(50, y_position - 2, 100, y_position - 2)
        y_position -= 20
        c.drawString(50, y_position, f"{adresat}")
        y_position -= 20
        c.drawString(50, y_position, f"{ulica_adresat} {dom_adresat}")
        y_position -= 20
        if lokal_adresat:
            c.drawString(50, y_position, f"Lokal: {lokal_adresat}")
            y_position -= 20
        c.drawString(50, y_position, f"{kod_pocztowy_adresat} {miejscowosc}")
        y_position -= 20
        c.drawString(50, y_position, "Nadawca:")
        c.line(50, y_position - 2, 100, y_position - 2)
        y_position -= 20
        c.drawString(50, y_position, f"{nazwa_jednostki}")
        y_position -= 20
        c.drawString(50, y_position, f"{ulica_nadawca} {dom_nadawca}")
        y_position -= 20
        if lokal_adresat:
            c.drawString(50, y_position, f"Lokal: {lokal_nadawca}")
            y_position -= 20
        if wydzial:
            c.drawString(50, y_position, f"Wydział: {wydzial}")
            y_position -= 20
        if kod_pocztowy_nadawca:
            c.drawString(50, y_position, f"{kod_pocztowy_nadawca} {miasto}")
        else:
            c.drawString(50, y_position, f"{miasto}")
        y_position -= 20

        c.drawString(50, y_position, "Wydający przesyłkę:")
        c.line(50, y_position - 2, 150, y_position - 2)
        y_position -= 20
        # Dodanie nowych wartości do PDF
        c.drawString(50, y_position, f"Data Podpisu: {data_podpisu}")
        y_position -= 20

        c.drawString(50, y_position, f"Data Zapisu: {data_zapisu}")
        y_position -= 20

        c.drawString(50, y_position, f"ID Operatora: {id_operatora}")
        y_position -= 20

        c.drawString(50, y_position, f"ID Urządzenia: {id_urzadzenia}")
        y_position -= 20

        c.drawString(50, y_position, f"Imię Wydającego: {imie_wydajacego}")
        y_position -= 20

        c.drawString(50, y_position, f"Nazwisko Wydającego: {nazwisko_wydajacego}")
        y_position -= 20

        c.drawString(50, y_position, f"ID Wydającego: {id_wydajacego}")
        y_position -= 20

        c.drawString(50, y_position, f"ID Placówki: {id_placowka}")
        y_position -= 20

        c.drawString(50, y_position, f"Nazwa Placówki: {nazwa_placowki}")
        y_position -= 20

        c.drawString(50, y_position, f"Adres Placówki: {adres_placowki}")
        y_position -= 20

        c.drawString(50, y_position, f"PNI Placówki: {pni_placowki}")
        y_position -= 20

        # Dodanie nowej strony dla obrazu
        c.showPage()
        # Dekodowanie i dodanie podpisu do PDF
        if podpis:
            try:
                podpis_obraz = base64.b64decode(podpis)
                image = ImageReader(BytesIO(podpis_obraz))
                c.drawImage(image, 100, height - 450, width=width - 200, height=350)
            except Exception as e:
                print(f"Błąd dodawania podpisu do PDF: {e}")
        else:
            print("Brak podpisu do dodania do PDF.")
        c.save()
    except PermissionError:
        print(f"Błąd: Nie można zapisać pliku PDF '{output_file}'. Upewnij się, że plik nie jest otwarty w innym programie.")
        
def process_folder(folder_path):
    MAX_FILENAME_LENGTH = 240

    doreczenia_count = 0
    zwrot_awizowany_count = 0
    zwrot_count = 0
    doreczenia_po_zwrocie_count = 0

    for filename in os.listdir(folder_path):
        if filename.endswith(".xml"):
            file_path = os.path.join(folder_path, filename)

            # Obsługa doreczenia
            data_utworzenia, podpis_obraz, rodzaj_doreczenie, data_nadania, data_pisma, numer_nadania, adresat_nazwa, adresat_ulica, adresat_numer_domu, adresat_miejscowosc, adresat_kod_pocztowy, nadawca_nazwa, nadawca_nazwa2, nadawca_ulica, nadawca_numer_domu, nadawca_miejscowosc, nadawca_kod_pocztowy, id_karty_epo, id_przesylki, tryb_doreczenia, do_rak_wlasnych, sygnatura, rodzaj, adnotacje, podmiot_doreczenia, tresc_adnotacji = doreczenie_parse_xml_file(file_path)
            if rodzaj_doreczenie == "DORECZENIE":
                doreczenia_count += 1
                pdf_output_file = os.path.join(folder_path, f"{os.path.splitext(filename)[0]}_doreczenie.pdf")
                if len(pdf_output_file) > MAX_FILENAME_LENGTH:
                    input()
                    return
                doreczenie_save_to_pdf(data_utworzenia, podpis_obraz, rodzaj_doreczenie, data_nadania, data_pisma, numer_nadania, adresat_nazwa, adresat_ulica, adresat_numer_domu, adresat_miejscowosc, adresat_kod_pocztowy, nadawca_nazwa, nadawca_nazwa2, nadawca_ulica, nadawca_numer_domu, nadawca_miejscowosc, nadawca_kod_pocztowy, id_karty_epo, id_przesylki, tryb_doreczenia, do_rak_wlasnych, sygnatura, rodzaj, adnotacje, podmiot_doreczenia, tresc_adnotacji, pdf_output_file, file_path)

            # Obsługa zwrotu awizowanego
            creation_date, id_karta_epo, id_przesylka, numer_nadania, data_nadania, adresat, kod_pocztowy_adresat, ulica_adresat, dom_adresat, lokal_adresat, adresat_miejscowosc, status_przesylki, systemowa_data, brak_doreczenia, data_awizo1, data_awizo2, nadawca_nazwa, nadawca_wydzial, nadawca_miasto, nadawca_kod_pocztowy, nadawca_ulica, nadawca_dom, nadawca_lokal = zwrot_awizowany_parse_xml_file(file_path)
            if status_przesylki == 6:
                zwrot_awizowany_count += 1
                pdf_output_file = os.path.join(folder_path, f"{os.path.splitext(filename)[0]}_zwrot_awizowany.pdf")
                if len(pdf_output_file) > MAX_FILENAME_LENGTH:
                    input()
                    return
                zwrot_awizowany_save_to_pdf(creation_date, id_karta_epo, id_przesylka, numer_nadania, data_nadania, adresat, kod_pocztowy_adresat, ulica_adresat, dom_adresat, lokal_adresat, adresat_miejscowosc, status_przesylki, systemowa_data, brak_doreczenia, data_awizo1, data_awizo2, nadawca_nazwa, nadawca_wydzial, nadawca_miasto, nadawca_kod_pocztowy, nadawca_ulica, nadawca_dom, nadawca_lokal, pdf_output_file, file_path)


           # Obsługa doreczenia po awizo
            creation_date, id_karta_epo, id_przesylka, numer_nadania, data_nadania, adresat, kod_pocztowy_adresat, kod_pocztowy_nadawca, ulica_adresat, ulica_nadawca, dom_adresat, dom_nadawca, lokal_adresat, lokal_nadawca, miejscowosc, status_przesylki, systemowa_data, odbiorca_przesylki, imie_nazwisko_odbiorcy, podpis, brak_doreczenia, awizo_miejsce_przesylki, awizo_miejsce_zawiadomienia, data_awizo1, id_jednostka_ms, nazwa_jednostki, wydzial, miasto, data_podpisu, data_zapisu, id_operatora, id_urzadzenia, imie_wydajacego, nazwisko_wydajacego, id_wydajacego, id_placowka, nazwa_placowki, adres_placowki, pni_placowki, podpis_obraz_base64 = doreczenie_po_awizo_parse_xml_file(file_path)
            if status_przesylki == 5:
                doreczenia_po_zwrocie_count += 1
                pdf_output_file = os.path.join(folder_path, f"{os.path.splitext(filename)[0]}_doreczenie_po_awizo.pdf")
                if len(pdf_output_file) > MAX_FILENAME_LENGTH:
                    input()
                    return
                doreczenie_po_awizo_save_to_pdf(creation_date, id_karta_epo, id_przesylka, numer_nadania, data_nadania, adresat, kod_pocztowy_adresat, kod_pocztowy_nadawca, ulica_adresat, ulica_nadawca, dom_adresat, dom_nadawca, lokal_adresat, lokal_nadawca, miejscowosc, status_przesylki, systemowa_data, odbiorca_przesylki, imie_nazwisko_odbiorcy, podpis, brak_doreczenia, awizo_miejsce_przesylki, awizo_miejsce_zawiadomienia, data_awizo1, id_jednostka_ms, nazwa_jednostki, wydzial, miasto, data_podpisu, data_zapisu, id_operatora, id_urzadzenia, imie_wydajacego, nazwisko_wydajacego, id_wydajacego, id_placowka, nazwa_placowki, adres_placowki, pni_placowki, pdf_output_file, podpis_obraz_base64, file_path)

            # Obsługa zwrotu
            data_utworzenia, id_karty_epo, id_przesylki, numer_nadania, data_nadania, adresat_nazwa, adresat_ulica, adresat_numer_domu, adresat_miejscowosc, adresat_kod_pocztowy, nadawca_nazwa, nadawca_nazwa2, nadawca_ulica, nadawca_numer_domu, nadawca_miejscowosc, nadawca_kod_pocztowy, tryb_doreczenia, do_rak_wlasnych, systemowa_data, data_adnotacji, data_zdarzenia, operator_imie, operator_nazwisko, operator_id, placowka_nazwa, placowka_ulica, placowka_numer_domu, placowka_miejscowosc, placowka_kod_pocztowy, placowka_kraj, powod_zwrotu, tresc_adnotacji, rodzaj_zwrot = zwrot_parse_xml_file(file_path)
            if rodzaj_zwrot == "ZWROT":
                zwrot_count += 1
                pdf_output_file = os.path.join(folder_path, f"{os.path.splitext(filename)[0]}_zwrot.pdf")
                if len(pdf_output_file) > MAX_FILENAME_LENGTH:
                    input()
                    return
                zwrot_save_to_pdf(data_utworzenia, id_karty_epo, id_przesylki, numer_nadania, data_nadania, adresat_nazwa, adresat_ulica, adresat_numer_domu, adresat_miejscowosc, adresat_kod_pocztowy, nadawca_nazwa, nadawca_nazwa2, nadawca_ulica, nadawca_numer_domu, nadawca_miejscowosc, nadawca_kod_pocztowy, tryb_doreczenia, do_rak_wlasnych, systemowa_data, data_adnotacji, data_zdarzenia, operator_imie, operator_nazwisko, operator_id, placowka_nazwa, placowka_ulica, placowka_numer_domu, placowka_miejscowosc, placowka_kod_pocztowy, placowka_kraj, powod_zwrotu, tresc_adnotacji, rodzaj_zwrot, pdf_output_file)

    print(f"Doreczenia: {doreczenia_count}")
    print(f"Zwrot awizowany: {zwrot_awizowany_count}")
    print(f"Doreczenia po awizo: {doreczenia_po_zwrocie_count}")
    if zwrot_count > 0:
        print(f"\033[91mZwrot: {zwrot_count} (błędny adres, adresat nie mieszka pod wskazanym adresem lub inne)\033[0m")

def check_latest_release(owner, repo, current_version):
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Sprawdza, czy odpowiedź HTTP zawiera błąd
        latest_release = response.json()
        latest_version = latest_release['tag_name']
        if version.parse(latest_version) > version.parse(current_version):
            print(f"Nowa wersja dostępna: {latest_version}. Obecna wersja: {current_version}.")
            user_input = input("Czy chcesz pobrać najnowszą wersję? Naciśnij 'T' lub 'N': ")
            if user_input.lower() == 't':
                webbrowser.open(f"https://github.com/{owner}/{repo}/releases")
    except requests.exceptions.SSLError as e:
        print("Błąd weryfikacji certyfikatu SSL: nie udało się zweryfikować certyfikatu. Sprawdź swoje połączenie internetowe lub ustawienia certyfikatów.")
    except requests.exceptions.RequestException as e:
        print(f"Nie udało się pobrać informacji o najnowszej wersji: {e}")

if __name__ == "__main__":
    print("EPO wersja 1.0.11 Autor: Tomasz Rekusz")
    print()

    # Przetwarzanie plików
    folder_path = os.path.abspath(os.getcwd())
    process_folder(folder_path)

    # Sprawdzanie najnowszej wersji
    owner = "tomkolp"
    repo = "e-doreczenia-wizualizacja-EPO"
    current_version = "1.0.11"
    check_latest_release(owner, repo, current_version)

    print()
    input("Naciśnij Enter, aby zakończyć...")
