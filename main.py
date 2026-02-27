import json
import requests
import flet as ft
from flet import FontWeight
from fpdf import FPDF, XPos, YPos
import os
from datetime import datetime

# URL do pliku ze stawkami w sieci
STAWKI_URL = "https://raw.githubusercontent.com/RavMav/kalkulator_stawki/refs/heads/main/stawki.json"

class Formularz_glowny(ft.Column):
    def __init__(self):
        super().__init__()

        self.prog_przestepstwa = 4608 * 5
        self.wybrany_tryb = None
        self.dzisiaj = datetime.now().strftime("%d-%m-%Y")

        # W klasie Twojego formularza:
        self.stawki = self.zaladuj_stawki()

        # Logo
        self.logo = ft.Container(
            content=ft.Image(
                src="/assets/Kas_winieta.jpg",
                fit=ft.BoxFit.CONTAIN,
            ),
            width=300,
            height=300,
            alignment=ft.Alignment.CENTER,
            animate=ft.Animation(600, ft.AnimationCurve.EASE_IN_OUT),
        )

        self.logo_container = ft.Row([self.logo], alignment=ft.MainAxisAlignment.CENTER)

        # 1. Tworzymy pola na formularzu
        self.pole_towar = ft.Text("", size=20, weight=ft.FontWeight.BOLD, color="green", width=500, text_align=ft.TextAlign.CENTER)
        
        self.pole_input1 = ft.TextField(
            input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d*$", replacement_string=""),
            visible=False, border_color=ft.Colors.GREEN_300 ,width=250
        )
        self.pole_input2 = ft.TextField(
            input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d*$", replacement_string=""),
            visible=False, border_color=ft.Colors.GREEN_300, width=250
        )
        self.pole_input3 = ft.TextField(
            input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d*$", replacement_string=""),
            visible=False, border_color=ft.Colors.GREEN_300, width=250
        )
        
        self.pole_akcyza = ft.TextField(label="Należności akcyza", visible=False, read_only=True, border_color=ft.Colors.GREEN_300, bgcolor=ft.Colors.GREEN_50, width=250)
        self.pole_vat = ft.TextField(label="Należności VAT", visible=False, read_only=True, border_color=ft.Colors.GREEN_300, bgcolor=ft.Colors.GREEN_50, width=250)
        self.pole_clo = ft.TextField(label="Należności cło", visible=False, read_only=True, border_color=ft.Colors.GREEN_300, bgcolor=ft.Colors.GREEN_50, width=250)
        self.pole_av = ft.TextField(label="Należności akcyza+vat", visible=False, read_only=True, border_color=ft.Colors.GREEN_300, bgcolor=ft.Colors.GREEN_50, width=250)
        self.pole_avc = ft.TextField(label="Należności akcyza+vat+cło", visible=False, read_only=True, border_color=ft.Colors.GREEN_300, bgcolor=ft.Colors.GREEN_50, width=250)
        
        self.przycisk_oblicz = ft.Button("Oblicz", on_click=self.glowny_oblicz, visible=False, width=250, bgcolor=ft.Colors.GREEN_300, color=ft.Colors.WHITE, height=50)

        # 1.6 Przycisk Zapisz/Drukuj
        self.menu_zapisz = ft.PopupMenuButton(
            content=ft.Container(
                bgcolor=ft.Colors.BLUE_GREY_600,
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.SAVE, color="white"),
                        ft.Text("Zapisz / Drukuj", color="white", weight=FontWeight.BOLD),
                    ],
                    tight=True,
                ),
                padding=10,
                border_radius=8,
                width=200,
            ),
            items=[
                ft.PopupMenuItem(content="Zapisz do TXT", icon=ft.Icons.TEXT_SNIPPET, on_click=self.zapisz_txt),
                ft.PopupMenuItem(content="Drukuj (Otwórz TXT)", icon=ft.Icons.PRINT, on_click=self.drukuj_txt),
                ft.PopupMenuItem(content="Zapisz do PDF", icon=ft.Icons.PICTURE_AS_PDF, on_click=self.zapisz_pdf),
                ft.PopupMenuItem(content="Drukuj (Otwórz PDF)", icon=ft.Icons.PRINT, on_click=self.drukuj_pdf),
            ],
            visible=False,
            disabled=True
        )

        # 2. Menu rozwijane
        self.menu_lista = ft.PopupMenuButton(
            content=ft.Container(
                bgcolor=ft.Colors.GREEN_300,
                on_hover=self.menu_hover,
                animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.MENU, color="white"),
                        ft.Text("Wybierz rodzaj towaru ▼", color="white", weight=FontWeight.BOLD),
                    ],
                    tight=True,
                ),
                padding=10,
                border_radius=8,
                width=250,
            ),
            items=[
                ft.PopupMenuItem(content="Papierosy przemyt", on_click=lambda e: self.ustaw_tryb("papierosy_przemyt", "Papierosy przemyt", i1="Ilość papierosów (szt.)", v=True, a=True, c=True, av=True, avc=True)),
                ft.PopupMenuItem(content="Papierosy paserstwo", on_click=lambda e: self.ustaw_tryb("papierosy_paser", "Papierosy paserstwo / nabycie", i1="Ilość papierosów (szt.)", v=True, a=True, av=True)),
                ft.PopupMenuItem(content="Wódka przemyt", on_click=lambda e: self.ustaw_tryb("wodka_przemyt", "Wódka przemyt", i1="Ilość litrów (l.)", i2="Zawartość alkoholu (%)", v=True, a=True, av=True)),
                ft.PopupMenuItem(content="Wódka paserstwo", on_click=lambda e: self.ustaw_tryb("wodka_paser", "Wódka paserstwo / nabycie", i1="Ilość litrów (l.)", i2="Zawartość alkoholu (%)", a=True)),
                ft.PopupMenuItem(content="Tytoń przemyt", on_click=lambda e: self.ustaw_tryb("tyton_przemyt", "Tytoń przemyt", i1="Ilość tytoniu (kg)", v=True, a=True, c=True, av=True, avc=True)),
                ft.PopupMenuItem(content="Tytoń paserstwo", on_click=lambda e: self.ustaw_tryb("tyton_paser", "Tytoń paserstwo / nabycie", i1="Ilość tytoniu (kg)", v=True, a=True, av=True)),
                ft.PopupMenuItem(content="Cygara/cygaretki przemyt", on_click=lambda e: self.ustaw_tryb("cygara_przemyt", "Cygara i cygaretki przemyt", i1="Ilość towaru (kg)", v=True, a=True, c=True, av=True, avc=True)),
                ft.PopupMenuItem(content="Cygara/cygaretki paserstwo", on_click=lambda e: self.ustaw_tryb("cygara_paser", "Cygara i cygaretki paserstwo / nabycie", i1="Ilość towaru (kg)", v=True, a=True, av=True)),
                ft.PopupMenuItem(content="Spirytus przemyt", on_click=lambda e: self.ustaw_tryb("spirytus_przemyt", "Spirytus przemyt", i1="Ilość litrów (l.)", i2="Zawartość alkoholu (%)", i3="Kurs Euro", v=True, a=True, c=True, av=True, avc=True)),
                ft.PopupMenuItem(content="Spirytus paserstwo", on_click=lambda e: self.ustaw_tryb("spirytus_paser", "Spirytus paserstwo / nabycie", i1="Ilość litrów (l.)", i2="Zawartość alkoholu (%)", a=True)),
                ft.PopupMenuItem(content="Susz tytoniowy paserstwo", on_click=lambda e: self.ustaw_tryb("susz_paser", "Susz tytoniowy paserstwo / nabycie", i1="Ilość suszu tytoniowego (kg)", v=True, a=True, av=True)),
                ft.PopupMenuItem(content="Wyroby nowatorskie przemyt", on_click=lambda e: self.ustaw_tryb("nowatorskie_przemyt", "Wyroby nowatorskie przemyt", i1="Ilość wyrobów nowatorskich (kg)", v=True, a=True, c=True, av=True, avc=True)),
                ft.PopupMenuItem(content="Wyroby nowatorskie paserstwo", on_click=lambda e: self.ustaw_tryb("nowatorskie_paser", "Wyroby nowatorskie paserstwo / nabycie", i1="Ilość wyrobów nowatorskich (kg)", v=True, a=True, av=True)),
            ],
            tooltip="Wybierz rodzaj towaru",
            menu_position=ft.PopupMenuPosition.UNDER
        )

        # 3. Wygląd formularza
        self.naglowek = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.ADD_HOME, color="white", size=30),
                        bgcolor="green_700", padding=10, border_radius=10,
                    ),
                    ft.Column([
                        ft.Text("KALKULATOR", size=20, weight=ft.FontWeight.BOLD, color="green_900"),
                        ft.Text("CELNO-SKARBOWY 2026", size=12, color="grey_600", italic=True),
                    ], spacing=0)
                ]),
                self.menu_lista
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            margin=ft.Margin.only(bottom=10)
        )

        self.kontener_statusu = ft.Container(
            content=ft.Row([self.pole_towar]),
            padding=10, bgcolor="blue_grey_50", border_radius=8,
            alignment=ft.alignment.Alignment.CENTER, visible=False
        )

        self.sekcja_dane = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("DANE WEJŚCIOWE", size=13, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=1, color="green_100"),
                    ft.Row([self.pole_input1, self.pole_input2, self.pole_input3], spacing=20, wrap=True),
                ], spacing=15),
                padding=20,
            ),
            elevation=2, bgcolor="white", visible=False
        )


        self.sekcja_wyniki = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("PODSUMOWANIE NALEŻNOŚCI", size=13, weight=ft.FontWeight.BOLD, color="green_800"),
                    ft.Divider(height=1, color="green_100"),
                    ft.Row([self.pole_akcyza, self.pole_vat, self.pole_clo], spacing=20, wrap=True),
                    ft.Row([self.pole_av, self.pole_avc], spacing=20, wrap=True),
                ], spacing=15),
                padding=20,
            ),
            elevation=2, visible=False
        )

        self.stopka_akcji = ft.Container(
            content=ft.Row([self.przycisk_oblicz, self.menu_zapisz], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            margin=ft.Margin.only(top=20)
        )

        self.layout_formularza = ft.Container(
            content=ft.Column([
                self.logo_container, self.naglowek, self.kontener_statusu, self.sekcja_dane, self.sekcja_wyniki, self.stopka_akcji,
            ], spacing=10, scroll=ft.ScrollMode.AUTO),
            width=900, padding=30, bgcolor=ft.Colors.WHITE, border_radius=20,
            border=ft.Border.all(1, "green_200"), shadow=ft.BoxShadow(blur_radius=15, color="black12"),
        )

        self.controls = [self.layout_formularza]

    def menu_hover(self, e):
        is_hovered = str(e.data).lower() == "true"
        e.control.bgcolor = ft.Colors.GREEN_900 if is_hovered else ft.Colors.GREEN_300
        e.control.update()

    def ustaw_tryb(self, tryb, nazwa, i1=None, i2=None, i3=None, v=False, a=False, c=False, av=False, avc=False):
        self.wybrany_tryb = tryb
        # Animacja logo
        self.logo.width = 100
        self.logo.height = 100
        self.logo.alignment = ft.Alignment.TOP_LEFT
        self.logo_container.alignment = ft.MainAxisAlignment.START
        
        self.layout_formularza.update()
        self.wyczysc_formularz()
        self.pole_towar.value = nazwa
        
        self.pole_input1.visible = i1 is not None
        if i1: self.pole_input1.label = i1
        
        self.pole_input2.visible = i2 is not None
        if i2: self.pole_input2.label = i2
        
        self.pole_input3.visible = i3 is not None
        if i3: self.pole_input3.label = i3
        
        self.pole_vat.visible = v
        self.pole_akcyza.visible = a
        self.pole_clo.visible = c
        self.pole_av.visible = av
        self.pole_avc.visible = avc
        
        self.przycisk_oblicz.visible = True
        self.kontener_statusu.visible = True
        self.sekcja_wyniki.visible = True
        self.sekcja_dane.visible = True
        self.menu_zapisz.visible = True
        self.menu_zapisz.disabled = True
        
        if i3 == "Kurs Euro":
            self.pobierz_kurs_euro()
            
        self.update()

    def wyczysc_formularz(self):
        pola = [self.pole_input1, self.pole_input2, self.pole_input3, self.pole_akcyza, self.pole_vat, self.pole_clo, self.pole_av, self.pole_avc]
        for pole in pola:
            pole.value = ""
            pole.error = None
            pole.visible = False
            pole.bgcolor = ft.Colors.GREEN_50
        self.przycisk_oblicz.visible = False
        self.menu_zapisz.visible = False
        self.menu_zapisz.disabled = True
        self.update()

    def sformatuj_wyniki(self):

        wynik = f"--- KALKULATOR CELNO-SKARBOWY 2026 ---\n\n"
        wynik += f"Towar: {self.pole_towar.value}\n\n"
        wynik += f"Data: {self.dzisiaj}\n\n"
        wynik += "-" * 40 + "\n"
        
        if self.pole_input1.visible:
            wynik += f"{self.pole_input1.label}: {self.pole_input1.value}\n"
        if self.pole_input2.visible:
            wynik += f"{self.pole_input2.label}: {self.pole_input2.value}\n"
        if self.pole_input3.visible:
            wynik += f"{self.pole_input3.label}: {self.pole_input3.value}\n"
        
        wynik += "-" * 40 + "\n"

        if self.pole_akcyza.visible:
            wynik += f"Akcyza:  {self.pole_akcyza.value}\n\n"
        if self.pole_vat.visible:
            wynik += f"VAT:  {self.pole_vat.value}\n\n"
        if self.pole_clo.visible:
            wynik += f"Cło:  {self.pole_clo.value}\n\n"
        if self.pole_av.visible:
            wynik += f"Akcyza+VAT:  {self.pole_av.value}\n\n"
        if self.pole_avc.visible:
            wynik += f"Akcyza+VAT+Cło:  {self.pole_avc.value}\n\n"
        
        return wynik

    def zapisz_txt(self, e):
        try:
            filename = f"wynik_kalkulacji z {self.dzisiaj}.txt"
            tekst = self.sformatuj_wyniki()
            with open(filename, "w", encoding="utf-8") as f:
                f.write(tekst)
            snack = ft.SnackBar(ft.Text(f"Zapisano pomyślnie do {filename}!"))
            e.page.overlay.append(snack)
            snack.open = True
            e.page.update()
        except Exception as ex:
            print(f"Błąd zapisu TXT: {ex}")

    def zapisz_pdf(self, e):
        try:
            filename = f"wynik_kalkulacji z {self.dzisiaj}.pdf"
            pdf = FPDF()
            pdf.add_page()
            polskie_znaki = {"ą": "a", "ć": "c", "ę": "e", "ł": "l", "ń": "n", "ó": "o", "ś": "s", "ź": "z", "ż": "z",
                             "Ą": "A", "Ć": "C", "Ę": "E", "Ł": "L", "Ń": "N", "Ó": "O", "Ś": "S", "Ź": "Z", "Ż": "Z"}
            tekst = self.sformatuj_wyniki()
            for k, v in polskie_znaki.items():
                tekst = tekst.replace(k, v)
            pdf.set_font("Helvetica", size=12)
            for line in tekst.split("\n"):
                pdf.cell(200, 10, text=line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.output(filename)
            snack = ft.SnackBar(ft.Text(f"Zapisano pomyślnie do {filename}!"))
            e.page.overlay.append(snack)
            snack.open = True
            e.page.update()
        except Exception as ex:
            print(f"Błąd zapisu PDF: {ex}")

    def drukuj_pdf(self, e):
        try:
            pdf = FPDF()
            pdf.add_page()
            polskie_znaki = {"ą": "a", "ć": "c", "ę": "e", "ł": "l", "ń": "n", "ó": "o", "ś": "s", "ź": "z", "ż": "z",
                             "Ą": "A", "Ć": "C", "Ę": "E", "Ł": "L", "Ń": "N", "Ó": "O", "Ś": "S", "Ź": "Z", "Ż": "Z"}
            tekst = self.sformatuj_wyniki()
            for k, v in polskie_znaki.items():
                tekst = tekst.replace(k, v)
            pdf.set_font("Helvetica", size=12)
            for line in tekst.split("\n"):
                pdf.cell(200, 10, text=line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            filename = "temp_wynik.pdf"
            pdf.output(filename)
            if os.path.exists(filename):
                os.startfile(filename, "open")
        except Exception as ex:
            print(f"Błąd drukowania PDF: {ex}")

    def drukuj_txt(self, e):
        try:
            tekst = self.sformatuj_wyniki()
            filename = "temp_wynik.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(tekst)
            if os.path.exists(filename):
                os.startfile(filename, "open")
        except Exception as ex:
            print(f"Błąd drukowania TXT: {ex}")

    def pobierz_liczbe(self, pole):
        surowy_tekst = pole.value.strip() if pole.value else ""
        pole.error = None
        
        if not surowy_tekst:
            pole.error = "Uzupełnij pole!"
            self.update()
            return None
        
        if surowy_tekst == ".":
            pole.error = "Błędna liczba!"
            self.update()
            return None

        if surowy_tekst.startswith("."):
            surowy_tekst = "0" + surowy_tekst
            pole.value = surowy_tekst

        try:
            return float(surowy_tekst)
        except ValueError:
            pole.error = "To nie jest liczba!"
            self.update()
            return None

    def pobierz_kurs_euro(self):
        url = "https://api.nbp.pl/api/exchangerates/rates/a/eur/?format=json"
        try:
            headers = {'Accept': 'application/json', 'User-Agent': 'FletApp/1.0'}
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = json.loads(response.content.decode("utf-8-sig"))
                kurs = data["rates"][0]["mid"]
                data_publikacji = data["rates"][0]["effectiveDate"]
                self.pole_input3.value = f"{kurs:.4f}"
                self.pole_input3.label = f"Kurs EUR (NBP: {data_publikacji})"
                self.update()
        except Exception as ex:
            print(f"Błąd kursu: {ex}")

    def przestepstwo(self, a=0, v=0, c=0):
        self.pole_akcyza.bgcolor = ft.Colors.RED_100 if a > self.prog_przestepstwa else ft.Colors.GREEN_50
        self.pole_vat.bgcolor = ft.Colors.RED_100 if v > self.prog_przestepstwa else ft.Colors.GREEN_50
        self.pole_clo.bgcolor = ft.Colors.RED_100 if c > self.prog_przestepstwa else ft.Colors.GREEN_50
        
        if a > self.prog_przestepstwa: self.pole_akcyza.value += " - PRZESTĘPSTWO!"
        if v > self.prog_przestepstwa: self.pole_vat.value += " - PRZESTĘPSTWO!"
        if c > self.prog_przestepstwa: self.pole_clo.value += " - PRZESTĘPSTWO!"
        self.update()

    def zaladuj_stawki(self):
        # Najpierw próbujemy pobrać z sieci
        try:
            headers = {'Accept': 'application/json', 'User-Agent': 'FletApp/1.0'}
            response = requests.get(STAWKI_URL, headers=headers, timeout=5)
            if response.status_code == 200:
                print("Pobrano stawki z sieci.")
                return json.loads(response.content.decode("utf-8-sig"))
        except Exception as ex:
            print(f"Błąd pobierania stawek z sieci: {ex}. Próba odczytu lokalnego.")

        # Jeśli się nie uda, czytamy z pliku lokalnego
        try:
            with open("stawki.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as ex:
            print(f"Błąd odczytu lokalnego pliku stawek: {ex}")
            return {}

    def glowny_oblicz(self, e):
        i1 = self.pobierz_liczbe(self.pole_input1)
        i2 = self.pobierz_liczbe(self.pole_input2) if self.pole_input2.visible else 0
        i3 = self.pobierz_liczbe(self.pole_input3) if self.pole_input3.visible else 0
        
        if i1 is None or (self.pole_input2.visible and i2 is None) or (self.pole_input3.visible and i3 is None):
            return

        s = self.stawki.get(self.wybrany_tryb)
        if not s: return  # Zabezpieczenie

        a, v, c = 0, 0, 0
        
        if self.wybrany_tryb == "papierosy_przemyt":
            #wc_szt = 34 / 1000
            #s_clo, s_akc, s_vat = 0.5760, 1.40574879, 0.23
            wc = s["wc_mnoznik"] * i1
            a = round(s["s_akc"] * i1, 0)
            c = round(wc * s["s_clo"], 0)
            v = round((wc + c + a) * s["s_vat"], 0)
    
        elif self.wybrany_tryb == "papierosy_paser":
            wc = round(s["wc_mnoznik"] * i1, 0)
            #s_akc, s_vat = 1.40574879, 0.23
            a = round(s["s_akc"] * i1, 0)
            v = round((wc + a) * s["s_vat"], 0)
            
        elif self.wybrany_tryb == "wodka_przemyt":
            #s_akc, s_vat, wc_jedn = 83.91, 0.23, 13
            wc = round(s["wc_jedn"] * i1, 0)
            a = round(s["s_akc"] * (i1 * i2 / 100), 0)
            v = round((wc + a) * s["s_vat"], 0)
            
        elif self.wybrany_tryb == "wodka_paser":
            #s_akc = 83.91
            a = round(s["s_akc"] * (i1 * i2 / 100), 0)
            
        elif self.wybrany_tryb == "tyton_przemyt":
            #s_akc, s_vat, wc_jedn, s_clo = 1329.928790, 0.23, 74, 0.749
            wc = round(s["wc_jedn"] * i1, 0)
            a = round(s["s_akc"] * i1, 0)
            c = round(s["s_clo"] * wc, 0)
            v = round((a + wc + c) * s["s_vat"], 0)
            
        elif self.wybrany_tryb == "tyton_paser":
            #s_akc, s_vat, wc_jedn = 1329.928790, 0.23, 130
            wc = round(s["wc_jedn"] * i1, 0)
            a = round(s["s_akc"] * i1, 0)
            v = round((a + wc) * s["s_vat"], 0)

        elif self.wybrany_tryb == "spirytus_przemyt":
            #s_akc, s_vat, wc_jedn = 83.91, 0.23, 17.50
            c = round((s["s_clo"] / 100) * i3 * i1, 0)
            wc = round(s["wc_jedn"] * i1, 0)
            a = round(s["s_akc"] * (i1 * i2 / 100), 0)
            v = round((wc + a + c) * s["s_vat"], 0)

        elif self.wybrany_tryb == "spirytus_paser":
            #s_akc = 83.91
            a = round(s["s_akc"] * (i1 * i2 / 100), 0)

        elif self.wybrany_tryb == "cygara_przemyt":
            #s_akc, s_vat, wc_jedn, s_clo = 786, 0.23, 10, 0.26
            wc = round(s["wc_jedn"] * i1, 0)
            a = round(s["s_akc"] * i1, 0)
            c = round(s["s_clo"] * wc, 0)
            v = round((a + wc + c) * s["s_vat"], 0)

        elif self.wybrany_tryb == "cygara_paser":
            #s_akc, s_vat, wc_jedn = 786, 0.23, 13
            wc = round(s["wc_jedn"] * i1, 0)
            a = round(s["s_akc"] * i1, 0)
            v = round((a + wc) * s["s_vat"], 0)

        elif self.wybrany_tryb == "nowatorskie_przemyt":
            #s_akc, s_vat, wc_jedn, s_clo = 1477.91, 0.23, 34, 0.166
            wc = round(s["wc_jedn"] * i1, 0)
            a = round(s["s_akc"] * i1, 0)
            c = round(s["s_clo"] * wc, 0)
            v = round((a + wc + c) * s["s_vat"], 0)

        elif self.wybrany_tryb == "nowatorskie_paser":
            #s_akc, s_vat, wc_jedn = 1477.91, 0.23, 40
            wc = round(s["wc_jedn"] * i1, 0)
            a = round(s["s_akc"] * i1, 0)
            v = round((a + wc) * s["s_vat"], 0)

        elif self.wybrany_tryb == "susz_paser":
            #s_akc, s_vat, wc_jedn = 1095.16, 0.08, 20.10
            wc = round(s["wc_jedn"] * i1, 0)
            a = round(s["s_akc"] * i1, 0)
            v = round((a + wc) * s["s_vat"], 0)

        self.pole_akcyza.value = f"{a:.0f} zł"
        self.pole_vat.value = f"{v:.0f} zł"
        self.pole_clo.value = f"{c:.0f} zł"
        self.pole_av.value = f"{a + v:.0f} zł"
        self.pole_avc.value = f"{a + v + c:.0f} zł"
        
        self.menu_zapisz.disabled = False
        self.przestepstwo(a, v, c)
        self.update()

def main(page: ft.Page):
    page.title = "Kalkulator należności celno-skarbowych"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.width = 950
    page.window.height = 820
    #page.scroll= "auto"
    
    # Obsługa favicon
    page.favicon = "favicon.png"
    
    formularz = Formularz_glowny()
    page.add(formularz)

if __name__ == "__main__":
    ft.run(main)
