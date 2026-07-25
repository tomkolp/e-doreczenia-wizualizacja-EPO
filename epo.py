import sys
import os
import base64
import textwrap
import traceback
from io import BytesIO
from dataclasses import dataclass, field
from typing import List, Optional, Dict
import webbrowser

# =====================================================================
# GLOBALNY PRZECHWYTYWACZ BŁĘDÓW (Zapobiega znikaniu okna .exe w Windows)
# =====================================================================
def global_exception_handler(exc_type, exc_value, exc_traceback):
    print("\033[91m\n========================================================")
    print("WYSTĄPIŁ BŁĄD KRYTYCZNY APLIKACJI:")
    print("========================================================\033[0m")
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    print("\n")
    try:
        input("Naciśnij klawisz Enter, aby zamknąć okno...")
    except Exception:
        pass
    sys.exit(1)

sys.excepthook = global_exception_handler

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
except ImportError as e:
    print("\033[91mBŁĄD: Brakuje wymaganej biblioteki!\033[0m")
    print(f"Szczegóły: {e}\n")
    print("Otwórz wiersz poleceń (cmd) i zainstaluj pakiety poleceniem:")
    print("pip install reportlab defusedxml requests packaging\n")
    input("Naciśnij Enter, aby zamknąć okno...")
    sys.exit(1)

APP_VERSION = "2.0.0"
MAX_FILENAME_LENGTH = 240

# =====================================================================
# MODEL DANYCH
# =====================================================================

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
    typ_raportu: str
    id_karty: str
    id_przesylki: str
    numer_nadania: str
    fields: List[ReportField] = field(default_factory=list)
    podpis_base64: Optional[str] = None

# =====================================================================
# NARZĘDZIA DO PARSOWANIA XML (Ignorujące Namespace URI)
# =====================================================================

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

# =====================================================================
# PARSERY DOKUMENTÓW EPO
# =====================================================================

def parse_doreczenie(file_path: str, root: ET.Element) -> Optional[EPOReportData]:
    ns = {'mstns': 'KartaEPO/2018/07/15'}
    if get_xml_text(root, './/mstns:RodzajDoreczenie', ns, "") != "DORECZENIE":
        return None

    id_karty = get_xml_text(root, './/mstns:IdKartyEPO', ns)
    id_przesylki = get_xml_text(root, './/mstns:IdPrzesylki', ns)
    nr_nadania = get_xml_text(root, './/mstns:NumerNadania', ns)

    data = EPOReportData(
        source_filename=os.path.basename(file_path),
        typ_raportu="doreczenie",
        id_karty=id_karty,
        id_przesylki=id_przesylki,
        numer_nadania=nr_nadania,
        podpis_base64=get_xml_text(root, './/mstns:PodpisObraz', ns, None)
    )

    data.fields.append(ReportField("Data Utworzenia", f"{get_xml_text(root, 'mstns:DataUtworzenia', ns)} (Data doręczenia)", green))
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
    adresat_lines = format_address(
        get_xml_text(adresat_block, 'mstns:Nazwa', ns), get_xml_text(adresat_block, 'mstns:Nazwa2', ns, ""),
        get_xml_text(adresat_block, 'mstns:Ulica', ns), get_xml_text(adresat_block, 'mstns:NumerDomu', ns),
        lokal_a, get_xml_text(adresat_block, 'mstns:KodPocztowy', ns), get_xml_text(adresat_block, 'mstns:Miejscowosc', ns)
    )
    for line in adresat_lines:
        data.fields.append(ReportField("", line))

    nadawca_block = find_element(root, './/mstns:Nadawca', ns)
    data.fields.append(ReportField("Nadawca", "", is_header=True))
    nadawca_lines = format_address(
        get_xml_text(nadawca_block, 'mstns:Nazwa', ns), get_xml_text(nadawca_block, 'mstns:Nazwa2', ns, ""),
        get_xml_text(nadawca_block, 'mstns:Ulica', ns), get_xml_text(nadawca_block, 'mstns:NumerDomu', ns),
        lokal_n, get_xml_text(nadawca_block, 'mstns:KodPocztowy', ns), get_xml_text(nadawca_block, 'mstns:Miejscowosc', ns)
    )
    for line in nadawca_lines:
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
    data = EPOReportData(
        source_filename=os.path.basename(file_path),
        typ_raportu="zwrot_awizowany",
        id_karty=get_xml_text(root, './/mstns:IDKartaEPO', ns),
        id_przesylki=get_xml_text(przesylka, './/mstns:IDPrzesylka', ns),
        numer_nadania=nr_nadania
    )

    data.fields.append(ReportField("Data Utworzenia", get_xml_text(root, './/mstns:CreationDate', ns)))
    data.fields.append(ReportField("Data Nadania", get_xml_text(przesylka, './/mstns:DataNadania', ns)))
    data.fields.append(ReportField("Status Przesyłki", "Zwrot (po awizo)", orange))
    data.fields.append(ReportField("Systemowa Data Oznaczenia", f"{get_xml_text(przesylka, './/mstns:SystemowaDataOznaczenia', ns)} (Data zwrotu po awizacji)", orange))

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

    syg = get_xml_text(root, './/mstns:Sygnatura', ns, "")
    if syg and syg != "Brak danych":
        data.fields.append(ReportField("Sygnatura", syg))
    rodz = get_xml_text(root, './/mstns:Rodzaj', ns, "")
    if rodz and rodz != "Brak danych":
        data.fields.append(ReportField("Rodzaj", rodz))

    kody = find_all_elements(przesylka, './/mstns:KodPocztowy', ns)
    ulice = find_all_elements(przesylka, './/mstns:Ulica', ns)
    domy = find_all_elements(przesylka, './/mstns:Dom', ns)
    lokale = find_all_elements(przesylka, './/mstns:Lokal', ns)

    data.fields.append(ReportField("Adresat", "", is_header=True))
    adresat_lines = format_address(
        get_xml_text(przesylka, './/mstns:Adresat', ns), "",
        get_list_text(ulice, 0), get_list_text(domy, 0),
        get_list_text(lokale, 0), get_list_text(kody, 0),
        get_xml_text(przesylka, './/mstns:Miejscowosc', ns)
    )
    for line in adresat_lines:
        data.fields.append(ReportField("", line))

    data.fields.append(ReportField("Nadawca", "", is_header=True))
    nadawca_lines = format_address(
        get_xml_text(przesylka, './/mstns:NazwaJednostki', ns), "",
        get_list_text(ulice, 1), get_list_text(domy, 1),
        get_list_text(lokale, 1), get_list_text(kody, 1),
        get_xml_text(przesylka, './/mstns:Miasto', ns)
    )
    for line in nadawca_lines:
        data.fields.append(ReportField("", line))

    wydz = get_xml_text(przesylka, './/mstns:Wydzial', ns, "")
    if wydz and wydz != "Brak danych":
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
    data = EPOReportData(
        source_filename=os.path.basename(file_path),
        typ_raportu="doreczenie_po_awizo",
        id_karty=get_xml_text(root, './/mstns:IDKartaEPO', ns),
        id_przesylki=get_xml_text(przesylka, './/mstns:IDPrzesylka', ns),
        numer_nadania=nr_nadania,
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
    data.fields.append(ReportField("Systemowa Data Oznaczenia", f"{get_xml_text(przesylka, './/mstns:SystemowaDataOznaczenia', ns)} (Data odbioru przesyłki)", green))
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
    syg = get_xml_text(root, './/mstns:Sygnatura', ns, "")
    if syg and syg != "Brak danych":
        data.fields.append(ReportField("Sygnatura", syg))
    rodz = get_xml_text(root, './/mstns:Rodzaj', ns, "")
    if rodz and rodz != "Brak danych":
        data.fields.append(ReportField("Rodzaj", rodz))

    kody = find_all_elements(przesylka, './/mstns:KodPocztowy', ns)
    ulice = find_all_elements(przesylka, './/mstns:Ulica', ns)
    domy = find_all_elements(przesylka, './/mstns:Dom', ns)
    lokale = find_all_elements(przesylka, './/mstns:Lokal', ns)

    data.fields.append(ReportField("Adresat", "", is_header=True))
    adresat_lines = format_address(
        get_xml_text(przesylka, './/mstns:Adresat', ns), "",
        get_list_text(ulice, 0), get_list_text(domy, 0),
        get_list_text(lokale, 0), get_list_text(kody, 0),
        get_xml_text(przesylka, './/mstns:Miejscowosc', ns)
    )
    for line in adresat_lines:
        data.fields.append(ReportField("", line))

    jedn = find_element(przesylka, './/mstns:TabletJednostkaMS', ns)
    data.fields.append(ReportField("Nadawca", "", is_header=True))
    nadawca_lines = format_address(
        get_xml_text(jedn, './/mstns:NazwaJednostki', ns) if jedn is not None else "Brak danych", "",
        get_list_text(ulice, 1), get_list_text(domy, 1),
        get_list_text(lokale, 1), get_list_text(kody, 1),
        get_xml_text(jedn, './/mstns:Miasto', ns) if jedn is not None else ""
    )
    for line in nadawca_lines:
        data.fields.append(ReportField("", line))

    if jedn is not None:
        wydz = get_xml_text(jedn, './/mstns:Wydzial', ns, "")
        if wydz and wydz != "Brak danych":
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
    data = EPOReportData(
        source_filename=os.path.basename(file_path),
        typ_raportu="zwrot",
        id_karty=get_xml_text(root, './/mstns:IdKartyEPO', ns),
        id_przesylki=get_xml_text(root, './/mstns:IdPrzesylki', ns),
        numer_nadania=nr_nadania
    )

    data.fields.append(ReportField("Data Utworzenia", get_xml_text(root, './/mstns:DataUtworzenia', ns)))
    data.fields.append(ReportField("Treść Adnotacji", get_xml_text(root, './/mstns:TrescAdnotacji', ns), red))
    data.fields.append(ReportField("Systemowa Data Oznaczenia", f"{get_xml_text(root, './/mstns:SystemowaDataOznaczenia', ns)} (Data zwrotu)", red))
    data.fields.append(ReportField("Nr. przesyłki", nr_nadania, blue, url=f"https://sledzenie.poczta-polska.pl/?numer={nr_nadania}"))

    syg = get_xml_text(root, './/mstns:Sygnatura', ns, "")
    if syg and syg != "Brak danych":
        data.fields.append(ReportField("Sygnatura", syg))
    rodz = get_xml_text(root, './/mstns:Rodzaj', ns, "")
    if rodz and rodz != "Brak danych":
        data.fields.append(ReportField("Rodzaj", rodz))
    data.fields.append(ReportField("Data Nadania", get_xml_text(root, './/mstns:DataNadania', ns)))

    lokale = find_all_elements(root, './/mstns:NumerLokalu', ns)
    lokal_a = get_list_text(lokale, 0)
    lokal_n = get_list_text(lokale, 1)

    adresat_block = find_element(root, './/mstns:Adresat', ns)
    data.fields.append(ReportField("Adresat", "", is_header=True))
    adresat_lines = format_address(
        get_xml_text(adresat_block, 'mstns:Nazwa', ns), get_xml_text(adresat_block, 'mstns:Nazwa2', ns, ""),
        get_xml_text(adresat_block, 'mstns:Ulica', ns), get_xml_text(adresat_block, 'mstns:NumerDomu', ns),
        lokal_a, get_xml_text(adresat_block, 'mstns:KodPocztowy', ns), get_xml_text(adresat_block, 'mstns:Miejscowosc', ns)
    )
    for line in adresat_lines:
        data.fields.append(ReportField("", line))

    nadawca_block = find_element(root, './/mstns:Nadawca', ns)
    data.fields.append(ReportField("Nadawca", "", is_header=True))
    nadawca_lines = format_address(
        get_xml_text(nadawca_block, 'mstns:Nazwa', ns), get_xml_text(nadawca_block, 'mstns:Nazwa2', ns, ""),
        get_xml_text(nadawca_block, 'mstns:Ulica', ns), get_xml_text(nadawca_block, 'mstns:NumerDomu', ns),
        lokal_n, get_xml_text(nadawca_block, 'mstns:KodPocztowy', ns), get_xml_text(nadawca_block, 'mstns:Miejscowosc', ns)
    )
    for line in nadawca_lines:
        data.fields.append(ReportField("", line))

    tryb = get_xml_text(root, './/mstns:TrybDoreczenia', ns)
    do_rak = get_xml_attr(root, './/mstns:TrybDoreczenia', 'DoRakWlasnych', ns, 'false') == 'true'
    data.fields.append(ReportField("Tryb Doręczenia", tryb))
    data.fields.append(ReportField("Do Rąk Własnych", 'Tak' if do_rak else 'Nie'))
    data.fields.append(ReportField("Data Adnotacji", get_xml_text(root, './/mstns:DataAdnotacji', ns)))
    data.fields.append(ReportField("Data Zdarzenia", get_xml_text(root, './/mstns:DataZdarzenia', ns)))

    operator_block = find_element(root, './/mstns:Operator', ns)
    data.fields.append(ReportField("Operator", "", is_header=True))
    data.fields.append(ReportField("Imię", get_xml_text(operator_block, 'mstns:Imie', ns)))
    data.fields.append(ReportField("Nazwisko", get_xml_text(operator_block, 'mstns:Nazwisko', ns)))
    data.fields.append(ReportField("ID Operatora", get_xml_text(operator_block, 'mstns:IdOperatora', ns)))

    placowka_block = find_element(root, './/mstns:AdresPlacowkiPocztowej', ns)
    data.fields.append(ReportField("Placówka Pocztowa", "", is_header=True))
    placowka_lines = format_address(
        get_xml_text(placowka_block, 'mstns:Nazwa', ns), "",
        get_xml_text(placowka_block, 'mstns:Ulica', ns), get_xml_text(placowka_block, 'mstns:NumerDomu', ns),
        "", get_xml_text(placowka_block, 'mstns:KodPocztowy', ns),
        get_xml_text(placowka_block, 'mstns:Miejscowosc', ns), get_xml_text(placowka_block, 'mstns:Kraj', ns, "")
    )
    for line in placowka_lines:
        data.fields.append(ReportField("", line))

    data.fields.append(ReportField("Powód Zwrotu", get_xml_text(root, './/mstns:PowodZwrotu', ns)))
    return data

# =====================================================================
# GENERATOR PDF
# =====================================================================

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
            font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Arial.ttf')
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
        try:
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
        except PermissionError:
            print(f"Błąd: Nie można zapisać pliku '{self.output_path}'. Upewnij się, że nie jest otwarty w innym programie.")

# =====================================================================
# GŁÓWNA LOGIKA APLIKACJI
# =====================================================================

def process_folder(folder_path: str):
    stats = {"doreczenie": 0, "zwrot_awizowany": 0, "doreczenie_po_awizo": 0, "zwrot": 0}
    
    parsers = [
        parse_doreczenie,
        parse_zwrot_awizowany,
        parse_doreczenie_po_awizo,
        parse_zwrot
    ]

    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(".xml"):
            continue
            
        file_path = os.path.join(folder_path, filename)
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except Exception:
            continue

        for parse_func in parsers:
            data = parse_func(file_path, root)
            if data:
                stats[data.typ_raportu] += 1
                pdf_output = os.path.join(folder_path, f"{os.path.splitext(filename)[0]}_{data.typ_raportu}.pdf")
                
                if len(pdf_output) <= MAX_FILENAME_LENGTH:
                    generator = PDFReportGenerator(pdf_output)
                    generator.generate(data)
                break

    print(f"Doreczenia: {stats['doreczenie']}\n")
    print(f"Zwrot awizowany: {stats['zwrot_awizowany']}\n")
    print(f"Doreczenia po awizo: {stats['doreczenie_po_awizo']}\n")
    if stats['zwrot'] > 0:
        print(f"\033[91mZwrot: {stats['zwrot']} (błędny adres, adresat nie mieszka pod wskazanym adresem lub inne)\033[0m")

def check_latest_release(owner: str, repo: str, current_version: str):
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    try:
        # Rozwiązanie problemu zawieszania w Windows .exe (wyłączenie proxy systemowego)
        # oraz krótki timeout: 1.5s na połączenie, 3s na odczyt API
        response = requests.get(
            url, 
            timeout=(1.5, 3.0), 
            proxies={"http": None, "https": None}
        )
        response.raise_for_status()
        latest_version = response.json().get('tag_name', '')
        if latest_version and version.parse(latest_version) > version.parse(current_version):
            print(f"\nNowa wersja dostępna: {latest_version} (obecna: {current_version}).")
            if input("Czy chcesz otworzyć stronę pobierania? (T/N): ").strip().lower() == 't':
                webbrowser.open(f"https://github.com/{owner}/{repo}/releases")
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print("\033[93m\nBrak połączenia z internetem – pominięto sprawdzanie aktualizacji.\033[0m")
    except Exception:
        pass

if __name__ == "__main__":
    print(f"EPO wersja {APP_VERSION} | Refaktoryzacja architektoniczna")
    print("Autor oryginału: Tomasz Rekusz https://github.com/tomkolp/e-doreczenia-wizualizacja-EPO\n")

    folder_path = os.path.dirname(os.path.abspath(__file__))
    process_folder(folder_path)

    check_latest_release("tomkolp", "e-doreczenia-wizualizacja-EPO", APP_VERSION)

    print()
    input("Naciśnij Enter, aby zakończyć...")