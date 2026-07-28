import sys
import os
import json
import base64
import textwrap
import threading
import traceback
from io import BytesIO
from dataclasses import dataclass, field
from typing import List, Optional, Dict
import webbrowser

if sys.platform == "win32":
    try:
        import ctypes
        hWnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hWnd != 0:
            ctypes.windll.user32.ShowWindow(hWnd, 0)
    except Exception:
        pass

try:
    import defusedxml.ElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

try:
    import requests
    from packaging import version
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    from reportlab.lib.colors import green, black, red, orange, blue, Color
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase import pdfmetrics
    import customtkinter as ctk
    from PIL import Image, ImageTk
except ImportError as e:
    print("\033[91mBŁĄD: Brakuje wymaganej biblioteki!\033[0m")
    print(f"Szczegóły: {e}\n")
    print("Zainstaluj pakiety poleceniem:")
    print("pip install reportlab defusedxml requests packaging customtkinter pillow\n")
    input("Naciśnij Enter, aby zamknąć...")
    sys.exit(1)

APP_VERSION = "2.1.3"
CONFIG_FILE = "epo_config.json"
MAX_FILENAME_LENGTH = 240

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

def get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

@dataclass
class ReportField:
    label: str
    value: str
    color: Color = black
    url: Optional[str] = None
    is_header: bool = False

@dataclass
class EPOReportData:
    source_filename: str
    file_path: str
    typ_raportu: str
    id_karty: str
    id_przesylki: str
    numer_nadania: str
    adresat_skrotony: str = ""
    data_glowna: str = ""
    status_opis: str = ""
    hex_color: str = "#2ecc71"
    fields: List[ReportField] = field(default_factory=list)
    podpis_base64: Optional[str] = None

def find_element(parent: ET.Element, xpath: str, namespaces: Dict[str, str] = None) -> Optional[ET.Element]:
    if parent is None:
        return None
    if namespaces:
        elem = parent.find(xpath, namespaces)
        if elem is not None:
            return elem
    tag_name = xpath.split(':')[-1] if ':' in xpath else xpath.split('/')[-1]
    for el in parent.iter():
        if el.tag.endswith(f"}}{tag_name}") or el.tag == tag_name:
            return el
    return None

def find_all_elements(parent: ET.Element, xpath: str, namespaces: Dict[str, str] = None) -> List[ET.Element]:
    if parent is None:
        return []
    if namespaces:
        elems = parent.findall(xpath, namespaces)
        if elems:
            return elems
    tag_name = xpath.split(':')[-1] if ':' in xpath else xpath.split('/')[-1]
    elems = []
    for el in parent.iter():
        if el.tag.endswith(f"}}{tag_name}") or el.tag == tag_name:
            elems.append(el)
    return elems

def get_xml_text(parent: ET.Element, xpath: str, namespaces: Dict[str, str] = None, default: str = "Brak danych") -> str:
    elem = find_element(parent, xpath, namespaces)
    return elem.text.strip() if elem is not None and elem.text else default

def get_xml_attr(parent: ET.Element, xpath: str, attr: str, namespaces: Dict[str, str] = None, default: str = "Brak danych") -> str:
    elem = find_element(parent, xpath, namespaces)
    return elem.attrib.get(attr, default) if elem is not None else default

def get_list_text(elements: List[ET.Element], index: int, default: str = "") -> str:
    if index < len(elements) and elements[index] is not None and elements[index].text:
        return elements[index].text.strip()
    return default

def format_address(nazwa: str, nazwa2: str, ulica: str, dom: str, lokal: str, kod: str, miasto: str, kraj: str = "") -> List[str]:
    lines = []
    full_name = f"{nazwa} {nazwa2}".strip()
    if full_name and full_name != "Brak danych":
        lines.append(full_name)
    ulica_dom = f"{ulica} {dom}".strip()
    if lokal and lokal not in ["Brak danych", "brak", "", "None"]:
        ulica_dom += f"/{lokal}"
    if ulica_dom and ulica_dom != "Brak danych":
        lines.append(ulica_dom)
    kod_miasto = f"{kod} {miasto}".strip()
    if kraj and kraj not in ["Brak danych", "", "None"]:
        kod_miasto += f", {kraj}"
    if kod_miasto and kod_miasto != "Brak danych":
        lines.append(kod_miasto)
    return lines

def parse_doreczenie(file_path: str, root: ET.Element) -> Optional[EPOReportData]:
    ns = {'mstns': 'KartaEPO/2018/07/15'}
    if get_xml_text(root, './/mstns:RodzajDoreczenie', ns, "") != "DORECZENIE":
        return None

    id_karty = get_xml_text(root, './/mstns:IdKartyEPO', ns)
    id_przesylki = get_xml_text(root, './/mstns:IdPrzesylki', ns)
    nr_nadania = get_xml_text(root, './/mstns:NumerNadania', ns)
    data_utw = get_xml_text(root, 'mstns:DataUtworzenia', ns)
    adresat_nazwa = get_xml_text(root, './/mstns:Adresat/mstns:Nazwa', ns)

    data = EPOReportData(
        source_filename=os.path.basename(file_path),
        file_path=file_path,
        typ_raportu="doreczenie",
        id_karty=id_karty,
        id_przesylki=id_przesylki,
        numer_nadania=nr_nadania,
        adresat_skrotony=adresat_nazwa,
        data_glowna=data_utw,
        status_opis="Doręczono",
        hex_color="#2ecc71",
        podpis_base64=get_xml_text(root, './/mstns:PodpisObraz', ns, None)
    )

    data.fields.append(ReportField("Data Utworzenia", f"{data_utw} (Data doręczenia)", green))
    data.fields.append(ReportField("Rodzaj Doręczenia", "DORECZENIE", green))
    
    podmiot = get_xml_text(root, './/mstns:PodmiotDoreczenia', ns, "")
    if podmiot and podmiot != "Brak danych":
        data.fields.append(ReportField("Podmiot Doręczenia", podmiot))
        
    adnotacja = get_xml_text(root, './/mstns:TrescAdnotacji', ns, "")
    if adnotacja and adnotacja != "Brak danych":
        data.fields.append(ReportField("Treść Adnotacji", adnotacja))

    tryb = get_xml_text(root, './/mstns:TrybDoreczenia', ns)
    do_rak = get_xml_attr(root, './/mstns:TrybDoreczenia', 'DoRakWlasnych', ns, 'false') == 'true'
    tryb_text = f"{tryb.capitalize()}{' (do rąk własnych)' if do_rak else ''}"
    data.fields.append(ReportField("Tryb doręczenia", tryb_text))

    adn = get_xml_text(root, './/mstns:Adnotacje', ns, "")
    if adn and adn != "Brak danych":
        data.fields.append(ReportField("Adnotacje", adn))

    data.fields.append(ReportField("Data Nadania", get_xml_text(root, './/mstns:DataNadania', ns)))
    data.fields.append(ReportField("Data Pisma", get_xml_text(root, './/mstns:DataPisma', ns)))
    data.fields.append(ReportField("Nr. przesyłki", nr_nadania, blue, url=f"https://sledzenie.poczta-polska.pl/?numer={nr_nadania}"))

    syg = get_xml_text(root, './/mstns:Sygnatura', ns, "")
    if syg and syg != "Brak danych":
        data.fields.append(ReportField("Sygnatura", syg))
        
    rodz = get_xml_text(root, './/mstns:Rodzaj', ns, "")
    if rodz and rodz != "Brak danych":
        data.fields.append(ReportField("Rodzaj", rodz))

    lokale = find_all_elements(root, './/mstns:NumerLokalu', ns)
    lokal_a = get_list_text(lokale, 0)
    lokal_n = get_list_text(lokale, 1)

    adresat_block = find_element(root, './/mstns:Adresat', ns)
    data.fields.append(ReportField("Adresat", "", is_header=True))
    for line in format_address(
        get_xml_text(adresat_block, 'mstns:Nazwa', ns), get_xml_text(adresat_block, 'mstns:Nazwa2', ns, ""),
        get_xml_text(adresat_block, 'mstns:Ulica', ns), get_xml_text(adresat_block, 'mstns:NumerDomu', ns),
        lokal_a, get_xml_text(adresat_block, 'mstns:KodPocztowy', ns), get_xml_text(adresat_block, 'mstns:Miejscowosc', ns)
    ):
        data.fields.append(ReportField("", line))

    nadawca_block = find_element(root, './/mstns:Nadawca', ns)
    data.fields.append(ReportField("Nadawca", "", is_header=True))
    for line in format_address(
        get_xml_text(nadawca_block, 'mstns:Nazwa', ns), get_xml_text(nadawca_block, 'mstns:Nazwa2', ns, ""),
        get_xml_text(nadawca_block, 'mstns:Ulica', ns), get_xml_text(nadawca_block, 'mstns:NumerDomu', ns),
        lokal_n, get_xml_text(nadawca_block, 'mstns:KodPocztowy', ns), get_xml_text(nadawca_block, 'mstns:Miejscowosc', ns)
    ):
        data.fields.append(ReportField("", line))

    return data

def parse_zwrot_awizowany(file_path: str, root: ET.Element) -> Optional[EPOReportData]:
    ns = {'mstns': 'http://msepo.gov.pl/epo/XSD/KartaEPO.xsd'}
    przesylka = find_element(root, './/mstns:TabletPrzesylka', ns)
    if przesylka is None:
        return None

    try:
        status_val = int(get_xml_text(przesylka, './/mstns:StatusPrzesylki', ns, "0"))
    except ValueError:
        return None

    if status_val != 6:
        return None

    nr_nadania = get_xml_text(przesylka, './/mstns:NumerNadania', ns)
    sys_data = get_xml_text(przesylka, './/mstns:SystemowaDataOznaczenia', ns)
    adresat_nazwa = get_xml_text(przesylka, './/mstns:Adresat', ns)

    data = EPOReportData(
        source_filename=os.path.basename(file_path),
        file_path=file_path,
        typ_raportu="zwrot_awizowany",
        id_karty=get_xml_text(root, './/mstns:IDKartaEPO', ns),
        id_przesylki=get_xml_text(przesylka, './/mstns:IDPrzesylka', ns),
        numer_nadania=nr_nadania,
        adresat_skrotony=adresat_nazwa,
        data_glowna=sys_data,
        status_opis="Zwrot (po awizo)",
        hex_color="#f39c12"
    )

    data.fields.append(ReportField("Data Utworzenia", get_xml_text(root, './/mstns:CreationDate', ns)))
    data.fields.append(ReportField("Data Nadania", get_xml_text(przesylka, './/mstns:DataNadania', ns)))
    data.fields.append(ReportField("Status Przesyłki", "Zwrot (po awizo)", orange))
    data.fields.append(ReportField("Systemowa Data Oznaczenia", f"{sys_data} (Data zwrotu po awizacji)", orange))

    brak_map = {0: "adresat odmówił przyjęcia", 2: "Nie doręczona z innych przyczyn", 3: "Nie podjęto przesyłki z placówki pocztowej/Urzędu gminy"}
    try:
        brak_code = int(get_xml_text(przesylka, './/mstns:BrakDoreczenia', ns, "-1"))
        if brak_code in brak_map:
            data.fields.append(ReportField("Brak Doręczenia", brak_map[brak_code]))
    except ValueError:
        pass

    data.fields.append(ReportField("Data Awizo 1", get_xml_text(przesylka, './/mstns:DataAwizo1', ns), orange))
    data.fields.append(ReportField("Data Awizo 2", get_xml_text(przesylka, './/mstns:DataAwizo2', ns), orange))
    data.fields.append(ReportField("Nr. przesyłki", nr_nadania, blue, url=f"https://sledzenie.poczta-polska.pl/?numer={nr_nadania}"))

    if syg := get_xml_text(root, './/mstns:Sygnatura', ns, ""): data.fields.append(ReportField("Sygnatura", syg))
    if rodz := get_xml_text(root, './/mstns:Rodzaj', ns, ""): data.fields.append(ReportField("Rodzaj", rodz))

    kody = find_all_elements(przesylka, './/mstns:KodPocztowy', ns)
    ulice = find_all_elements(przesylka, './/mstns:Ulica', ns)
    domy = find_all_elements(przesylka, './/mstns:Dom', ns)
    lokale = find_all_elements(przesylka, './/mstns:Lokal', ns)

    data.fields.append(ReportField("Adresat", "", is_header=True))
    for line in format_address(
        adresat_nazwa, "",
        get_list_text(ulice, 0), get_list_text(domy, 0),
        get_list_text(lokale, 0), get_list_text(kody, 0),
        get_xml_text(przesylka, './/mstns:Miejscowosc', ns)
    ):
        data.fields.append(ReportField("", line))

    data.fields.append(ReportField("Nadawca", "", is_header=True))
    for line in format_address(
        get_xml_text(przesylka, './/mstns:NazwaJednostki', ns), "",
        get_list_text(ulice, 1), get_list_text(domy, 1),
        get_list_text(lokale, 1), get_list_text(kody, 1),
        get_xml_text(przesylka, './/mstns:Miasto', ns)
    ):
        data.fields.append(ReportField("", line))

    if wydz := get_xml_text(przesylka, './/mstns:Wydzial', ns, ""):
        data.fields.append(ReportField("Wydział", wydz))

    wyd = find_element(przesylka, './/mstns:Wydajacy', ns)
    if wyd is not None:
        data.fields.append(ReportField("Wydający zwróconą przesyłkę", "", is_header=True))
        data.fields.append(ReportField("Imię wydającego", wyd.attrib.get('Imie', 'Brak danych')))
        data.fields.append(ReportField("Nazwisko wydającego", wyd.attrib.get('Nazwisko', 'Brak danych')))
        data.fields.append(ReportField("ID wydającego", wyd.attrib.get('Id', 'Brak danych')))
        data.fields.append(ReportField("ID Placówki", wyd.attrib.get('IDPlacowka', 'Brak danych')))
        data.fields.append(ReportField("Nazwa Placówki", wyd.attrib.get('NazwaPlacowki', 'Brak danych')))
        data.fields.append(ReportField("Adres Placówki", wyd.attrib.get('AdresPlacowki', 'Brak danych')))
        data.fields.append(ReportField("PNI Placówki", wyd.attrib.get('PNIPlacowki', 'Brak danych')))

    return data

def parse_doreczenie_po_awizo(file_path: str, root: ET.Element) -> Optional[EPOReportData]:
    ns = {'mstns': 'http://msepo.gov.pl/epo/XSD/KartaEPO.xsd'}
    przesylka = find_element(root, './/mstns:TabletPrzesylki', ns)
    if przesylka is None:
        return None

    try:
        status_val = int(get_xml_text(przesylka, './/mstns:StatusPrzesylki', ns, "0"))
    except ValueError:
        return None

    if status_val != 5:
        return None

    nr_nadania = get_xml_text(przesylka, './/mstns:NumerNadania', ns)
    sys_data = get_xml_text(przesylka, './/mstns:SystemowaDataOznaczenia', ns)
    adresat_nazwa = get_xml_text(przesylka, './/mstns:Adresat', ns)

    data = EPOReportData(
        source_filename=os.path.basename(file_path),
        file_path=file_path,
        typ_raportu="doreczenie_po_awizo",
        id_karty=get_xml_text(root, './/mstns:IDKartaEPO', ns),
        id_przesylki=get_xml_text(przesylka, './/mstns:IDPrzesylka', ns),
        numer_nadania=nr_nadania,
        adresat_skrotony=adresat_nazwa,
        data_glowna=sys_data,
        status_opis="Wydana (po awizo)",
        hex_color="#2ecc71",
        podpis_base64=get_xml_text(przesylka, './/mstns:Podpis', ns, None)
    )

    data.fields.append(ReportField("Data Utworzenia", get_xml_text(root, './/mstns:CreationDate', ns)))
    data.fields.append(ReportField("Status", "Wydana (po awizo)", green))

    odb_map = {0: "Adresat", 1: "Upoważniony Pracownik", 2: "Osoba uprawniona do reprezentacji", 3: "Pełnomocnik pocztowy", 4: "Przedstawiciel ustawowy adresata"}
    try:
        odb_code = int(get_xml_text(przesylka, './/mstns:OdbiorcaPrzesylki', ns, "-1"))
        if odb_code in odb_map:
            data.fields.append(ReportField("Odbiorca Przesyłki", odb_map[odb_code]))
    except ValueError:
        pass

    data.fields.append(ReportField("Imię i Nazwisko Odbiorcy", get_xml_text(przesylka, './/mstns:ImieINazwiskoOdbiorcy', ns)))
    data.fields.append(ReportField("Systemowa Data Oznaczenia", f"{sys_data} (Data odbioru przesyłki)", green))
    data.fields.append(ReportField("Data Nadania", get_xml_text(przesylka, './/mstns:DataNadania', ns)))

    zaw_map = {0: "Skrzynka Oddawcza", 1: "Drzwi", 2: "Skrytka Pocztowa", 3: "Inne widoczne miejsce", 4: "Biuro", 5: "Inne pomieszczenie", 6: "Inne widoczne miejsce przy wejściu na posesję"}
    try:
        zaw_code = int(get_xml_text(przesylka, './/mstns:AwizoMiejsceZawiadomienia', ns, "-1"))
        if zaw_code in zaw_map:
            data.fields.append(ReportField("Awizo Miejsce Zawiadomienia", zaw_map[zaw_code]))
    except ValueError:
        pass

    data.fields.append(ReportField("Data Awizo 1", get_xml_text(przesylka, './/mstns:DataAwizo1', ns), orange))
    data.fields.append(ReportField("Data Awizo 2", get_xml_text(przesylka, './/mstns:DataAwizo2', ns), orange))
    
    miejsc_map = {0: "placówka pocztowa", 1: "urząd gminy"}
    try:
        m_code = int(get_xml_text(przesylka, './/mstns:AwizoMiejscePrzesylki', ns, "-1"))
        if m_code in miejsc_map:
            data.fields.append(ReportField("Miejsce Przechowywania Przesyłki", miejsc_map[m_code]))
    except ValueError:
        pass

    data.fields.append(ReportField("Nr. przesyłki", nr_nadania, blue, url=f"https://sledzenie.poczta-polska.pl/?numer={nr_nadania}"))
    if syg := get_xml_text(root, './/mstns:Sygnatura', ns, ""): data.fields.append(ReportField("Sygnatura", syg))
    if rodz := get_xml_text(root, './/mstns:Rodzaj', ns, ""): data.fields.append(ReportField("Rodzaj", rodz))

    kody = find_all_elements(przesylka, './/mstns:KodPocztowy', ns)
    ulice = find_all_elements(przesylka, './/mstns:Ulica', ns)
    domy = find_all_elements(przesylka, './/mstns:Dom', ns)
    lokale = find_all_elements(przesylka, './/mstns:Lokal', ns)

    data.fields.append(ReportField("Adresat", "", is_header=True))
    for line in format_address(
        adresat_nazwa, "",
        get_list_text(ulice, 0), get_list_text(domy, 0),
        get_list_text(lokale, 0), get_list_text(kody, 0),
        get_xml_text(przesylka, './/mstns:Miejscowosc', ns)
    ):
        data.fields.append(ReportField("", line))

    jedn = find_element(przesylka, './/mstns:TabletJednostkaMS', ns)
    data.fields.append(ReportField("Nadawca", "", is_header=True))
    for line in format_address(
        get_xml_text(jedn, './/mstns:NazwaJednostki', ns) if jedn is not None else "Brak danych", "",
        get_list_text(ulice, 1), get_list_text(domy, 1),
        get_list_text(lokale, 1), get_list_text(kody, 1),
        get_xml_text(jedn, './/mstns:Miasto', ns) if jedn is not None else ""
    ):
        data.fields.append(ReportField("", line))

    if jedn is not None and (wydz := get_xml_text(jedn, './/mstns:Wydzial', ns, "")):
        data.fields.append(ReportField("Wydział", wydz))

    data.fields.append(ReportField("Wydający przesyłkę", "", is_header=True))
    bio = find_element(przesylka, './/mstns:DaneBiometryczne', ns)
    if bio is not None:
        data.fields.append(ReportField("Data Podpisu", get_xml_text(bio, './/mstns:DataPodpisu', ns)))
        data.fields.append(ReportField("Data Zapisu", get_xml_text(bio, './/mstns:DataZapisu', ns)))
        data.fields.append(ReportField("ID Operatora", get_xml_text(bio, './/mstns:IdOperatora', ns)))
        data.fields.append(ReportField("ID Urządzenia", get_xml_text(bio, './/mstns:IdUrzadzenia', ns)))

    wyd = find_element(przesylka, './/mstns:Wydajacy', ns)
    if wyd is not None:
        data.fields.append(ReportField("Imię Wydającego", wyd.attrib.get('Imie', 'Brak danych')))
        data.fields.append(ReportField("Nazwisko Wydającego", wyd.attrib.get('Nazwisko', 'Brak danych')))
        data.fields.append(ReportField("ID Wydającego", wyd.attrib.get('Id', 'Brak danych')))
        data.fields.append(ReportField("ID Placówki", wyd.attrib.get('IDPlacowka', 'Brak danych')))
        data.fields.append(ReportField("Nazwa Placówki", wyd.attrib.get('NazwaPlacowki', 'Brak danych')))
        data.fields.append(ReportField("Adres Placówki", wyd.attrib.get('AdresPlacowki', 'Brak danych')))
        data.fields.append(ReportField("PNI Placówki", wyd.attrib.get('PNIPlacowki', 'Brak danych')))

    return data

def parse_zwrot(file_path: str, root: ET.Element) -> Optional[EPOReportData]:
    ns = {'mstns': 'KartaEPO/2018/07/15'}
    if get_xml_text(root, './/mstns:RodzajZwrot', ns, "") != "ZWROT":
        return None

    nr_nadania = get_xml_text(root, './/mstns:NumerNadania', ns)
    sys_data = get_xml_text(root, './/mstns:SystemowaDataOznaczenia', ns)
    adresat_block = find_element(root, './/mstns:Adresat', ns)
    adresat_nazwa = get_xml_text(adresat_block, 'mstns:Nazwa', ns) if adresat_block is not None else "Brak danych"

    data = EPOReportData(
        source_filename=os.path.basename(file_path),
        file_path=file_path,
        typ_raportu="zwrot",
        id_karty=get_xml_text(root, './/mstns:IdKartyEPO', ns),
        id_przesylki=get_xml_text(root, './/mstns:IdPrzesylki', ns),
        numer_nadania=nr_nadania,
        adresat_skrotony=adresat_nazwa,
        data_glowna=sys_data,
        status_opis="ZWROT (Nie podjęto)",
        hex_color="#e74c3c"
    )

    data.fields.append(ReportField("Data Utworzenia", get_xml_text(root, './/mstns:DataUtworzenia', ns)))
    data.fields.append(ReportField("Treść Adnotacji", get_xml_text(root, './/mstns:TrescAdnotacji', ns), red))
    data.fields.append(ReportField("Systemowa Data Oznaczenia", f"{sys_data} (Data zwrotu)", red))
    data.fields.append(ReportField("Nr. przesyłki", nr_nadania, blue, url=f"https://sledzenie.poczta-polska.pl/?numer={nr_nadania}"))

    if syg := get_xml_text(root, './/mstns:Sygnatura', ns, ""): data.fields.append(ReportField("Sygnatura", syg))
    if rodz := get_xml_text(root, './/mstns:Rodzaj', ns, ""): data.fields.append(ReportField("Rodzaj", rodz))
    data.fields.append(ReportField("Data Nadania", get_xml_text(root, './/mstns:DataNadania', ns)))

    lokale = find_all_elements(root, './/mstns:NumerLokalu', ns)
    lokal_a = get_list_text(lokale, 0)
    lokal_n = get_list_text(lokale, 1)

    data.fields.append(ReportField("Adresat", "", is_header=True))
    for line in format_address(
        adresat_nazwa, get_xml_text(adresat_block, 'mstns:Nazwa2', ns, "") if adresat_block is not None else "",
        get_xml_text(adresat_block, 'mstns:Ulica', ns) if adresat_block is not None else "", get_xml_text(adresat_block, 'mstns:NumerDomu', ns) if adresat_block is not None else "",
        lokal_a, get_xml_text(adresat_block, 'mstns:KodPocztowy', ns) if adresat_block is not None else "", get_xml_text(adresat_block, 'mstns:Miejscowosc', ns) if adresat_block is not None else ""
    ):
        data.fields.append(ReportField("", line))

    nadawca_block = find_element(root, './/mstns:Nadawca', ns)
    data.fields.append(ReportField("Nadawca", "", is_header=True))
    for line in format_address(
        get_xml_text(nadawca_block, 'mstns:Nazwa', ns) if nadawca_block is not None else "", get_xml_text(nadawca_block, 'mstns:Nazwa2', ns, "") if nadawca_block is not None else "",
        get_xml_text(nadawca_block, 'mstns:Ulica', ns) if nadawca_block is not None else "", get_xml_text(nadawca_block, 'mstns:NumerDomu', ns) if nadawca_block is not None else "",
        lokal_n, get_xml_text(nadawca_block, 'mstns:KodPocztowy', ns) if nadawca_block is not None else "", get_xml_text(nadawca_block, 'mstns:Miejscowosc', ns) if nadawca_block is not None else ""
    ):
        data.fields.append(ReportField("", line))

    tryb = get_xml_text(root, './/mstns:TrybDoreczenia', ns)
    do_rak = get_xml_attr(root, './/mstns:TrybDoreczenia', 'DoRakWlasnych', ns, 'false') == 'true'
    data.fields.append(ReportField("Tryb Doręczenia", tryb))
    data.fields.append(ReportField("Do Rąk Własnych", 'Tak' if do_rak else 'Nie'))
    data.fields.append(ReportField("Data Adnotacji", get_xml_text(root, './/mstns:DataAdnotacji', ns)))
    data.fields.append(ReportField("Data Zdarzenia", get_xml_text(root, './/mstns:DataZdarzenia', ns)))

    operator_block = find_element(root, './/mstns:Operator', ns)
    data.fields.append(ReportField("Operator", "", is_header=True))
    data.fields.append(ReportField("Imię", get_xml_text(operator_block, 'mstns:Imie', ns) if operator_block is not None else ""))
    data.fields.append(ReportField("Nazwisko", get_xml_text(operator_block, 'mstns:Nazwisko', ns) if operator_block is not None else ""))
    data.fields.append(ReportField("ID Operatora", get_xml_text(operator_block, 'mstns:IdOperatora', ns) if operator_block is not None else ""))

    placowka_block = find_element(root, './/mstns:AdresPlacowkiPocztowej', ns)
    data.fields.append(ReportField("Placówka Pocztowa", "", is_header=True))
    for line in format_address(
        get_xml_text(placowka_block, 'mstns:Nazwa', ns) if placowka_block is not None else "", "",
        get_xml_text(placowka_block, 'mstns:Ulica', ns) if placowka_block is not None else "", get_xml_text(placowka_block, 'mstns:NumerDomu', ns) if placowka_block is not None else "",
        "", get_xml_text(placowka_block, 'mstns:KodPocztowy', ns) if placowka_block is not None else "",
        get_xml_text(placowka_block, 'mstns:Miejscowosc', ns) if placowka_block is not None else "", get_xml_text(placowka_block, 'mstns:Kraj', ns, "") if placowka_block is not None else ""
    ):
        data.fields.append(ReportField("", line))

    data.fields.append(ReportField("Powód Zwrotu", get_xml_text(root, './/mstns:PowodZwrotu', ns)))
    return data

class PDFReportGenerator:
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.width, self.height = A4
        self.margin = 50
        self.y = self.height - 30
        self.c = canvas.Canvas(output_path, pagesize=A4)
        self.setup_font()

    def setup_font(self):
        try:
            font_path = os.path.join(get_app_dir(), 'Arial.ttf')
            if not os.path.exists(font_path):
                font_path = 'Arial.ttf'
            pdfmetrics.registerFont(TTFont('Arial', font_path))
            self.c.setFont("Arial", 11)
        except Exception:
            self.c.setFont("Helvetica", 11)

    def check_page_break(self, required_space: int = 40):
        if self.y < required_space:
            self.c.showPage()
            self.setup_font()
            self.y = self.height - 50

    def draw_line_text(self, text: str, x: float = 50, color: Color = black):
        self.check_page_break()
        self.c.setFillColor(color)
        self.c.drawString(x, self.y, text)
        self.c.setFillColor(black)
        self.y -= 20

    def generate(self, data: EPOReportData):
        self.draw_line_text("Raport z pliku: ", x=48.2)
        for line in textwrap.wrap(data.source_filename, width=80):
            self.draw_line_text(line, x=48.2)
        
        if data.id_karty and data.id_karty != "Brak danych":
            self.draw_line_text(f"IdKartyEPO: {data.id_karty}", x=48.2)
        if data.id_przesylki and data.id_przesylki != "Brak danych":
            self.draw_line_text(f"IdPrzesylki: {data.id_przesylki}", x=48.2)

        for field in data.fields:
            if field.is_header:
                self.check_page_break(50)
                self.c.drawString(self.margin, self.y, f"{field.label}:")
                self.c.line(self.margin, self.y - 2, self.margin + 150, self.y - 2)
                self.y -= 20
            elif field.label == "":
                self.draw_line_text(field.value)
            else:
                text = f"{field.label}: {field.value}" if field.value else field.label
                if field.url:
                    self.check_page_break()
                    self.c.drawString(self.margin, self.y, f"{field.label}: ")
                    self.c.setFillColor(field.color)
                    self.c.drawString(self.margin + 100, self.y, field.url)
                    self.c.linkURL(field.url, (self.margin + 100, self.y, self.margin + 400, self.y + 15), relative=1, thickness=0)
                    self.c.setFillColor(black)
                    self.y -= 20
                else:
                    self.draw_line_text(text, color=field.color)

        if data.podpis_base64 and data.podpis_base64 not in ["Brak danych", ""]:
            self.c.showPage()
            self.setup_font()
            try:
                img_data = base64.b64decode(data.podpis_base64)
                image = ImageReader(BytesIO(img_data))
                self.c.drawImage(image, 100, self.height - 450, width=self.width - 200, height=350, preserveAspectRatio=True)
            except Exception:
                pass

        self.c.save()

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.id = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(300, self.showtip)

    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def showtip(self, event=None):
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 20
        self.tip_window = tw = ctk.CTkToplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)
        
        lbl = ctk.CTkLabel(tw, text=self.text, font=("Arial", 11), fg_color="#c0392b", text_color="white", corner_radius=6, padx=10, pady=6)
        lbl.pack()

    def hidetip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

class EPOGuiApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"EPO - Wizualizator e-Doręczeń [v{APP_VERSION}]")
        
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        win_w = min(int(screen_w * 0.85), 1400)
        win_h = min(int(screen_h * 0.85), 900)
        pos_x = int((screen_w - win_w) / 2)
        pos_y = int((screen_h - win_h) / 2)
        self.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.minsize(900, 550)

        self.loaded_data: Dict[str, EPOReportData] = {}
        self.checkboxes: Dict[str, ctk.CTkCheckBox] = {}
        self.row_frames: Dict[str, ctk.CTkFrame] = {}
        self.selected_file_path: Optional[str] = None
        self.current_folder: str = ""
        self.update_info_text = ""

        self.load_config()
        self.build_ui()
        self.load_folder(self.current_folder)

        threading.Thread(target=self.check_latest_release_background, daemon=True).start()
        self.after(300, self.update_gen_button)

    def load_config(self):
        default_dir = get_app_dir()
        self.current_folder = default_dir
        self.remember_var = ctk.BooleanVar(value=False)
        
        config_path = os.path.join(default_dir, CONFIG_FILE)
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    if cfg.get("remember", False) and os.path.isdir(cfg.get("folder", "")):
                        self.current_folder = cfg["folder"]
                        self.remember_var.set(True)
            except Exception:
                pass

    def save_config(self):
        try:
            config_path = os.path.join(get_app_dir(), CONFIG_FILE)
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump({
                    "folder": self.current_folder,
                    "remember": self.remember_var.get()
                }, f)
        except Exception:
            pass

    def build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top_frame = ctk.CTkFrame(self, corner_radius=0)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        top_frame.grid_columnconfigure(1, weight=1)

        title_box = ctk.CTkFrame(top_frame, fg_color="transparent")
        title_box.grid(row=0, column=0, columnspan=5, sticky="w", padx=10, pady=(2, 0))
        
        self.lbl_update_pulse = ctk.CTkLabel(title_box, text="", font=("Arial", 11, "bold"), text_color="#f39c12", cursor="hand2")
        self.lbl_update_pulse.pack(side="left")
        self.lbl_update_pulse.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/tomkolp/e-doreczenia-wizualizacja-EPO/releases"))

        ctk.CTkLabel(top_frame, text="Katalog XML:", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=10, pady=10)
        self.folder_entry = ctk.CTkEntry(top_frame)
        self.folder_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=10)
        self.folder_entry.insert(0, self.current_folder)

        ctk.CTkButton(top_frame, text="Zmień...", width=80, command=self.browse_folder).grid(row=1, column=2, padx=5, pady=10)
        ctk.CTkButton(top_frame, text="Odśwież", width=80, command=lambda: self.load_folder(self.folder_entry.get())).grid(row=1, column=3, padx=5, pady=10)
        ctk.CTkCheckBox(top_frame, text="Zapamiętaj folder", variable=self.remember_var, command=self.save_config).grid(row=1, column=4, padx=10, pady=10)

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        main_frame.grid_columnconfigure(0, weight=5)
        main_frame.grid_columnconfigure(1, weight=6)
        main_frame.grid_rowconfigure(0, weight=1)

        left_frame = ctk.CTkFrame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(2, weight=1)

        filter_box = ctk.CTkFrame(left_frame, fg_color="transparent")
        filter_box.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        filter_box.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(filter_box, placeholder_text="Szukaj (plik, adresat, nr nadania)...")
        self.search_entry.grid(row=0, column=0, sticky="ew", pady=5)
        self.search_entry.bind("<KeyRelease>", self.filter_file_list)

        btn_box = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_box.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        ctk.CTkButton(btn_box, text="Zaznacz wszystkie", width=120, height=24, command=lambda: self.toggle_all(True)).pack(side="left", padx=(0, 5))
        ctk.CTkButton(btn_box, text="Odznacz wszystkie", width=120, height=24, command=lambda: self.toggle_all(False)).pack(side="left")

        self.scroll_list = ctk.CTkScrollableFrame(left_frame, label_text="Znalezione pliki EPO")
        self.scroll_list.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.scroll_list.grid_columnconfigure(0, weight=1)

        self.gen_btn = ctk.CTkButton(left_frame, text="Generuj PDF dla zaznaczonych (0)", height=40, font=("Arial", 14, "bold"), fg_color="#27ae60", hover_color="#2ecc71", command=self.start_pdf_generation)
        self.gen_btn.grid(row=3, column=0, sticky="ew", padx=10, pady=10)

        right_frame = ctk.CTkFrame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(right_frame, text="Szybki podgląd pliku (zaznacz i skopiuj tekst Ctrl+C)", font=("Arial", 14, "bold")).grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        
        self.preview_scroll = ctk.CTkScrollableFrame(right_frame, fg_color="transparent")
        self.preview_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.preview_scroll.grid_columnconfigure(0, weight=1)

        self.lbl_preview_info = ctk.CTkLabel(self.preview_scroll, text="Wybierz plik z listy po lewej stronie, aby zobaczyć podgląd.", text_color="gray", font=("Arial", 13))
        self.lbl_preview_info.grid(row=0, column=0, pady=50)

        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        bottom_frame.grid_columnconfigure(0, weight=1)

        self.stats_label = ctk.CTkLabel(bottom_frame, text="Gotowy. Wczytanych plików: 0", font=("Arial", 12, "bold"))
        self.stats_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        ctk.CTkButton(bottom_frame, text="Pokaż folder w Eksploratorze Windows", width=220, height=24, command=self.open_system_folder).grid(row=0, column=1, padx=10, pady=5)

        self.log_box = ctk.CTkTextbox(bottom_frame, height=80, font=("Consolas", 11))
        self.log_box.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 5))
        
        footer_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        footer_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 5))
        
        ctk.CTkLabel(footer_frame, text="Autor oryginału: Tomasz Rekusz", font=("Arial", 11)).pack(side="left")
        repo_link = ctk.CTkLabel(footer_frame, text="GitHub: tomkolp/e-doreczenia-wizualizacja-EPO", font=("Arial", 11, "underline"), text_color="#3498db", cursor="hand2")
        repo_link.pack(side="right")
        repo_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/tomkolp/e-doreczenia-wizualizacja-EPO"))

        self.log("Aplikacja EPO z interfejsem graficznym gotowa do pracy.")
        self.log(f"Katalog roboczy: {self.current_folder}")

    def bind_mouse_scroll(self, widget):
        def _on_mousewheel(event):
            move = int(-1 * (event.delta / 10))
            self.preview_scroll._parent_canvas.yview_scroll(move, "units")
        def _on_linux_scroll_up(event):
            self.preview_scroll._parent_canvas.yview_scroll(-5, "units")
        def _on_linux_scroll_down(event):
            self.preview_scroll._parent_canvas.yview_scroll(5, "units")

        widget.bind("<MouseWheel>", _on_mousewheel, add="+")
        widget.bind("<Button-4>", _on_linux_scroll_up, add="+")
        widget.bind("<Button-5>", _on_linux_scroll_down, add="+")

    def log(self, message: str):
        self.log_box.insert("end", f"{message}\n")
        self.log_box.see("end")

    def browse_folder(self):
        folder = ctk.filedialog.askdirectory(initialdir=self.current_folder)
        if folder:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)
            self.load_folder(folder)

    def open_system_folder(self):
        if os.path.exists(self.current_folder):
            webbrowser.open(self.current_folder)

    def load_folder(self, folder_path: str):
        if not os.path.isdir(folder_path):
            self.log(f"Błąd: Katalog '{folder_path}' nie istnieje.")
            return

        self.current_folder = folder_path
        self.save_config()
        self.loaded_data.clear()
        self.selected_file_path = None

        for child in self.scroll_list.winfo_children():
            child.destroy()
        for child in self.preview_scroll.winfo_children():
            child.destroy()
        self.lbl_preview_info = ctk.CTkLabel(self.preview_scroll, text="Wybierz plik z listy po lewej stronie, aby zobaczyć podgląd.", text_color="gray", font=("Arial", 13))
        self.lbl_preview_info.grid(row=0, column=0, pady=50)

        parsers = [parse_doreczenie, parse_zwrot_awizowany, parse_doreczenie_po_awizo, parse_zwrot]
        counts = {"doreczenie": 0, "zwrot_awizowany": 0, "doreczenie_po_awizo": 0, "zwrot": 0}

        files = [f for f in os.listdir(folder_path) if f.lower().endswith(".xml")]
        
        for filename in sorted(files):
            file_path = os.path.join(folder_path, filename)
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                for parse_func in parsers:
                    data = parse_func(file_path, root)
                    if data:
                        self.loaded_data[file_path] = data
                        counts[data.typ_raportu] += 1
                        break
            except Exception:
                pass

        self.checkboxes.clear()
        self.row_frames.clear()

        for idx, (fpath, data) in enumerate(self.loaded_data.items()):
            row_bg = ("gray85", "gray17") if idx % 2 == 0 else "transparent"
            row = ctk.CTkFrame(self.scroll_list, fg_color=row_bg, corner_radius=6)
            row.grid(row=idx, column=0, sticky="ew", pady=2, padx=2)
            row.grid_columnconfigure(3, weight=1)
            self.row_frames[fpath] = row

            chk = ctk.CTkCheckBox(row, text="", width=24, command=self.update_gen_button)
            chk.grid(row=0, column=0, padx=(10, 0), pady=8)
            chk.select()
            self.checkboxes[fpath] = chk

            badge = ctk.CTkLabel(row, text=data.status_opis, font=("Arial", 11, "bold"), fg_color=data.hex_color, text_color="white", corner_radius=4, padx=6, pady=2)
            badge.grid(row=0, column=1, sticky="w", padx=10, pady=6)

            expected_pdf = os.path.join(folder_path, f"{os.path.splitext(data.source_filename)[0]}_{data.typ_raportu}.pdf")
            if len(expected_pdf) > MAX_FILENAME_LENGTH:
                warn_lbl = ctk.CTkLabel(row, text=" [!] ", font=("Arial", 10, "bold"), fg_color="#c0392b", text_color="white", corner_radius=3, cursor="hand2")
                warn_lbl.grid(row=0, column=2, padx=(0, 5), pady=6)
                Tooltip(warn_lbl, "⚠️ Za długa nazwa pliku lub ścieżka!\nZmień nazwę pliku na krótszą lub przenieś go do folderu z krótszą ścieżką.")

            info_text = f"{data.source_filename}\nAdresat: {data.adresat_skrotony} | {data.data_glowna}"
            lbl = ctk.CTkLabel(row, text=info_text, font=("Arial", 11), justify="left", anchor="w", text_color=("gray10", "gray90"))
            lbl.grid(row=0, column=3, sticky="ew", padx=(0, 10), pady=6)
            
            for widget in (row, badge, lbl):
                widget.bind("<Button-1>", lambda e, p=fpath: self.show_preview(p))
                widget.configure(cursor="hand2")

        total = len(self.loaded_data)
        self.stats_label.configure(text=f"Wczytano: {total} | Doręczenia: {counts['doreczenie'] + counts['doreczenie_po_awizo']} | Zwroty: {counts['zwrot'] + counts['zwrot_awizowany']}")
        self.log(f"Pomyślnie wczytano i rozpoznano {total} plików XML.")
        
        self.update_gen_button()

    def filter_file_list(self, event=None):
        query = self.search_entry.get().lower()
        for fpath, data in self.loaded_data.items():
            frame = self.row_frames.get(fpath)
            if not frame: continue
            search_content = f"{data.source_filename} {data.adresat_skrotony} {data.numer_nadania} {data.status_opis}".lower()
            if query in search_content:
                frame.grid()
            else:
                frame.grid_remove()
        self.update_gen_button()

    def toggle_all(self, state: bool):
        for chk in self.checkboxes.values():
            if chk.winfo_viewable():
                if state: chk.select()
                else: chk.deselect()
        self.update_gen_button()

    def update_gen_button(self):
        selected_count = sum(1 for fpath, chk in self.checkboxes.items() if chk.get() and self.row_frames[fpath].winfo_ismapped())
        self.gen_btn.configure(text=f"Generuj PDF dla zaznaczonych ({selected_count})")

    def show_preview(self, file_path: str):
        self.selected_file_path = file_path
        data = self.loaded_data.get(file_path)
        if not data: return

        for p, frame in self.row_frames.items():
            frame.configure(border_width=2 if p == file_path else 0, border_color="#3498db" if p == file_path else "")

        for child in self.preview_scroll.winfo_children():
            child.destroy()

        self.preview_scroll.grid_columnconfigure(0, weight=1)
        row_idx = 0

        title_box = ctk.CTkFrame(self.preview_scroll, fg_color=data.hex_color, corner_radius=6)
        title_box.grid(row=row_idx, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(title_box, text=f"{data.status_opis.upper()}", font=("Arial", 14, "bold"), text_color="white").pack(side="left", padx=15, pady=6)
        
        expected_pdf_path = os.path.join(self.current_folder, f"{os.path.splitext(data.source_filename)[0]}_{data.typ_raportu}.pdf")
        if len(expected_pdf_path) > MAX_FILENAME_LENGTH:
            warn_icon = ctk.CTkLabel(title_box, text=" [!] ", font=("Arial", 11, "bold"), fg_color="#c0392b", text_color="white", corner_radius=3, cursor="hand2")
            warn_icon.pack(side="right", padx=10, pady=6)
            Tooltip(warn_icon, "⚠️ Za długa nazwa pliku lub ścieżka!\nZmień nazwę pliku na krótszą lub przenieś go do folderu z krótszą ścieżką.")

        row_idx += 1

        if data.numer_nadania and data.numer_nadania != "Brak danych":
            url = f"https://sledzenie.poczta-polska.pl/?numer={data.numer_nadania}"
            track_btn = ctk.CTkButton(self.preview_scroll, text=f"Śledź przesyłkę: {data.numer_nadania}", font=("Arial", 12, "bold"), fg_color="#2980b9", hover_color="#3498db", command=lambda u=url: webbrowser.open(u))
            track_btn.grid(row=row_idx, column=0, sticky="ew", pady=(0, 10))
            self.bind_mouse_scroll(track_btn)
            row_idx += 1

        preview_text_lines = []
        for field in data.fields:
            if field.is_header:
                preview_text_lines.append(f"\n--- {field.label.upper()} ---")
            elif field.label == "":
                preview_text_lines.append(f"   {field.value}")
            else:
                preview_text_lines.append(f"{field.label}: {field.value}")
        
        full_preview_str = "\n".join(preview_text_lines).strip()
        num_lines = len(preview_text_lines)
        box_height = max(180, min(num_lines * 18 + 20, 500))

        txt_box = ctk.CTkTextbox(self.preview_scroll, height=box_height, font=("Consolas", 12), fg_color=("gray90", "gray14"), border_width=1, border_color=("gray70", "gray25"))
        txt_box.grid(row=row_idx, column=0, sticky="ew", pady=(0, 10))
        txt_box.insert("1.0", full_preview_str)
        txt_box.configure(state="disabled")
        self.bind_mouse_scroll(txt_box)
        row_idx += 1

        if data.podpis_base64 and data.podpis_base64 not in ["Brak danych", ""]:
            lbl_p = ctk.CTkLabel(self.preview_scroll, text="PODPIS ODBIORCY / GRAPHIC (Kliknij, aby powiększyć):", font=("Arial", 12, "bold"), text_color="#3498db")
            lbl_p.grid(row=row_idx, column=0, sticky="w", pady=(5, 5))
            self.bind_mouse_scroll(lbl_p)
            row_idx += 1
            try:
                img_data = base64.b64decode(data.podpis_base64)
                pil_img = Image.open(BytesIO(img_data))
                
                max_w, max_h = 350, 150
                pil_img_thumb = pil_img.copy()
                pil_img_thumb.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
                
                ctk_img = ctk.CTkImage(light_image=pil_img_thumb, dark_image=pil_img_thumb, size=pil_img_thumb.size)
                
                img_btn = ctk.CTkButton(self.preview_scroll, image=ctk_img, text="", fg_color="white", hover_color="gray90", corner_radius=6, command=lambda img=pil_img: self.show_signature_modal(img))
                img_btn.grid(row=row_idx, column=0, pady=5, sticky="w")
                self.bind_mouse_scroll(img_btn)
                row_idx += 1
                
                zoom_btn = ctk.CTkButton(self.preview_scroll, text="🔍 Powiększ podpis", width=150, height=24, fg_color="#34495e", hover_color="#2c3e50", command=lambda img=pil_img: self.show_signature_modal(img))
                zoom_btn.grid(row=row_idx, column=0, sticky="w", pady=(0, 15))
                self.bind_mouse_scroll(zoom_btn)
                row_idx += 1
            except Exception:
                pass

    def show_signature_modal(self, pil_img: Image.Image):
        modal = ctk.CTkToplevel(self)
        modal.title("Powiększony widok podpisu")
        modal.geometry("850x650")
        modal.minsize(500, 400)
        modal.transient(self)
        modal.grab_set()
        
        large_img = pil_img.copy()
        large_img.thumbnail((800, 550), Image.Resampling.LANCZOS)
        ctk_large = ctk.CTkImage(light_image=large_img, dark_image=large_img, size=large_img.size)
        
        lbl = ctk.CTkLabel(modal, image=ctk_large, text="", fg_color="white", corner_radius=8)
        lbl.pack(expand=True, fill="both", padx=20, pady=20)
        
        ctk.CTkButton(modal, text="Zamknij", width=120, command=modal.destroy).pack(pady=(0, 15))

    def start_pdf_generation(self):
        selected_files = [fpath for fpath, chk in self.checkboxes.items() if chk.get() and self.row_frames[fpath].winfo_ismapped()]
        if not selected_files:
            self.log("Ostrzeżenie: Nie zaznaczono żadnych plików do wygenerowania.")
            return

        self.gen_btn.configure(state="disabled", text="Generowanie w tle...")
        self.log(f"Rozpoczynam generowanie {len(selected_files)} raportów PDF...")
        thread = threading.Thread(target=self._generate_thread, args=(selected_files,), daemon=True)
        thread.start()

    def _generate_thread(self, file_paths: List[str]):
        success_count = 0
        for fpath in file_paths:
            data = self.loaded_data.get(fpath)
            if not data: continue

            pdf_output = os.path.join(self.current_folder, f"{os.path.splitext(data.source_filename)[0]}_{data.typ_raportu}.pdf")
            if len(pdf_output) > MAX_FILENAME_LENGTH:
                self.after(0, lambda f=data.source_filename: self.log(f"Pominięto (zbyt długa ścieżka): {f}"))
                continue

            try:
                gen = PDFReportGenerator(pdf_output)
                gen.generate(data)
                success_count += 1
                self.after(0, lambda f=os.path.basename(pdf_output): self.log(f" -> Zapisano: {f}"))
            except Exception as e:
                self.after(0, lambda err=str(e): self.log(f"Błąd generowania PDF: {err}"))

        self.after(0, lambda: self._generation_finished(success_count, len(file_paths)))

    def _generation_finished(self, success: int, total: int):
        self.log(f"Zakończono! Pomyślnie wygenerowano {success} z {total} plików PDF.")
        self.update_gen_button()
        self.gen_btn.configure(state="normal")

    def check_latest_release_background(self):
        url = "https://api.github.com/repos/tomkolp/e-doreczenia-wizualizacja-EPO/releases/latest"
        try:
            response = requests.get(url, timeout=(1.5, 3.0), proxies={"http": None, "https": None})
            response.raise_for_status()
            latest_version = response.json().get('tag_name', '')
            if latest_version and version.parse(latest_version) > version.parse(APP_VERSION):
                self.update_info_text = f"🚀 (Dostępna nowa wersja: {latest_version}!)"
                self.after(0, self.start_pulse_animation)
        except Exception as e:
            self.after(0, lambda: self.log(f"Info aktualizacji: Nie udało się połączyć z GitHubem ({e})"))

    def start_pulse_animation(self):
        self.pulse_state = True
        self.pulse_loop()

    def pulse_loop(self):
        if self.update_info_text:
            color = "#f39c12" if self.pulse_state else "#e74c3c"
            self.lbl_update_pulse.configure(text=self.update_info_text, text_color=color)
            self.pulse_state = not self.pulse_state
            self.after(700, self.pulse_loop)

def run_cli_mode(folder_path: str):
    """Funkcja obsługująca generowanie PDF z poziomu wiersza poleceń (Headless/CLI)."""
    if not os.path.isdir(folder_path):
        print(f"[BŁĄD] Wskazany katalog nie istnieje: {folder_path}")
        sys.exit(1)

    print(f"[*] Rozpoczynam przetwarzanie folderu w trybie konsolowym: {folder_path}")
    parsers = [parse_doreczenie, parse_zwrot_awizowany, parse_doreczenie_po_awizo, parse_zwrot]
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(".xml")]
    
    success_count = 0
    total_found = 0

    for filename in sorted(files):
        file_path = os.path.join(folder_path, filename)
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            data = None
            for parse_func in parsers:
                data = parse_func(file_path, root)
                if data:
                    break
            
            if data:
                total_found += 1
                pdf_output = os.path.join(folder_path, f"{os.path.splitext(data.source_filename)[0]}_{data.typ_raportu}.pdf")
                if len(pdf_output) > MAX_FILENAME_LENGTH:
                    print(f"[POMINIĘTO] Zbyt długa ścieżka dla pliku: {data.source_filename}")
                    continue
                
                gen = PDFReportGenerator(pdf_output)
                gen.generate(data)
                success_count += 1
                print(f" [OK] Wygenerowano: {os.path.basename(pdf_output)}")
        except Exception as e:
            print(f"[BŁĄD] Nie udało się przetworzyć pliku {filename}: {e}")

    print(f"[*] Zakończono! Przetworzono poprawnie {success_count} z {total_found} znalezionych plików EPO.")

if __name__ == "__main__":
    # Sprawdzenie, czy podano ścieżkę jako argument konsolowy (np. EPO.exe ścieżka)
    if len(sys.argv) > 1:
        target_folder = sys.argv[1]
        run_cli_mode(target_folder)
    else:
        app = EPOGuiApp()
        app.mainloop()
