import json
import requests
import flet as ft
from flet import FontWeight
import os
from datetime import datetime


# URL do pliku ze stawkami w sieci
STAWKI_URL = "https://raw.githubusercontent.com/RavMav/kalkulator_stawki/main/stawki.json"
TRYBY_KONFIG = {
    "papierosy_przemyt": {
        "menu": "Papierosy przemyt",
        "nazwa": "Papierosy przemyt",
        "i1": "Ilość papierosów (szt.)",
        "wyniki": {"v": True, "a": True, "c": True, "av": True, "avc": True, "w": True},
    },
    "papierosy_paser": {
        "menu": "Papierosy paserstwo",
        "nazwa": "Papierosy paserstwo / nabycie",
        "i1": "Ilość papierosów (szt.)",
        "wyniki": {"v": True, "a": True, "av": True, "w": True},
    },
    "wodka_przemyt": {
        "menu": "Wódka przemyt",
        "nazwa": "Wódka przemyt",
        "i1": "Ilość litrów (l.)",
        "i2": "Zawartość alkoholu (%)",
        "wyniki": {"v": True, "a": True, "av": True, "w": True},
    },
    "wodka_paser": {
        "menu": "Wódka paserstwo",
        "nazwa": "Wódka paserstwo / nabycie",
        "i1": "Ilość litrów (l.)",
        "i2": "Zawartość alkoholu (%)",
        "wyniki": {"a": True, "w": True},
    },
    "tyton_przemyt": {
        "menu": "Tytoń przemyt",
        "nazwa": "Tytoń przemyt",
        "i1": "Ilość tytoniu (kg)",
        "wyniki": {"v": True, "a": True, "c": True, "av": True, "avc": True, "w": True},
    },
    "tyton_paser": {
        "menu": "Tytoń paserstwo",
        "nazwa": "Tytoń paserstwo / nabycie",
        "i1": "Ilość tytoniu (kg)",
        "wyniki": {"v": True, "a": True, "av": True, "w": True},
    },
    "cygara_przemyt": {
        "menu": "Cygara/cygaretki przemyt",
        "nazwa": "Cygara i cygaretki przemyt",
        "i1": "Ilość towaru (kg)",
        "wyniki": {"v": True, "a": True, "c": True, "av": True, "avc": True, "w": True},
    },
    "cygara_paser": {
        "menu": "Cygara/cygaretki paserstwo",
        "nazwa": "Cygara i cygaretki paserstwo / nabycie",
        "i1": "Ilość towaru (kg)",
        "wyniki": {"v": True, "a": True, "av": True, "w": True},
    },
    "spirytus_przemyt": {
        "menu": "Spirytus przemyt",
        "nazwa": "Spirytus przemyt",
        "i1": "Ilość litrów (l.)",
        "i2": "Zawartość alkoholu (%)",
        "i3": "Kurs Euro",
        "wyniki": {"v": True, "a": True, "c": True, "av": True, "avc": True, "w": True},
    },
    "spirytus_paser": {
        "menu": "Spirytus paserstwo",
        "nazwa": "Spirytus paserstwo / nabycie",
        "i1": "Ilość litrów (l.)",
        "i2": "Zawartość alkoholu (%)",
        "wyniki": {"a": True, "w": True},
    },
    "susz_paser": {
        "menu": "Susz tytoniowy paserstwo",
        "nazwa": "Susz tytoniowy paserstwo / nabycie",
        "i1": "Ilość suszu tytoniowego (kg)",
        "wyniki": {"v": True, "a": True, "av": True, "w": True},
    },
    "nowatorskie_przemyt": {
        "menu": "Wyroby nowatorskie przemyt",
        "nazwa": "Wyroby nowatorskie przemyt",
        "i1": "Ilość wyrobów nowatorskich (kg)",
        "wyniki": {"v": True, "a": True, "c": True, "av": True, "avc": True, "w": True},
    },
    "nowatorskie_paser": {
        "menu": "Wyroby nowatorskie paserstwo",
        "nazwa": "Wyroby nowatorskie paserstwo / nabycie",
        "i1": "Ilość wyrobów nowatorskich (kg)",
        "wyniki": {"v": True, "a": True, "av": True, "w": True},
    },
    "e-pap_paser": {
        "menu": "Płyn do e-papierosów paserstwo",
        "nazwa": "Płyn do e-papierosów paserstwo / nabycie",
        "i1": "Ilość płynu (ml)",
        "i2": "Ilość urządzeń (szt.)",
        "wyniki": {"v": True, "a": True, "av": True, "w": True},
    },
    "e-pap_przemyt": {
        "menu": "Płyn do e-papierosów przemyt",
        "nazwa": "Płyn do e-papierosów przemyt",
        "i1": "Ilość płynu (ml)",
        "i2": "Ilość urządzeń (szt.)",
        "wyniki": {"v": True, "a": True, "c": True, "av": True, "avc": True, "w": True},
    },
}

class Formularz_glowny(ft.Column):
    def __init__(self):
        super().__init__()
        self.save_file_picker = ft.FilePicker()
        self.save_file_picker.on_result = self.on_save_result
        # self.expand = True
        #self.max_width = 1000  # Lub inna wartość większa niż Twój max_width
        self.horizontal_alignment = ft.CrossAxisAlignment.STRETCH

        self.prog_przestepstwa = 4608 * 5
        self.akcyza_urzadzenie = 0
        self.wybrany_tryb = None
        # Ustawienie poprawnej strefy czasowej (Polska +1h względem UTC na serwerach)
        teraz = datetime.now() #+ timedelta(hours=1)
        self.dzisiaj = teraz.strftime("%d-%m-%y_%H-%M-%S")

        
        # W klasie Twojego formularza:
        self.stawki = self.zaladuj_stawki()
        self.tryby_konfig = TRYBY_KONFIG

        # Logo
        self.logo = ft.Container(
            content=ft.Image(
                src="Kas_winieta.jpg",
                fit=ft.BoxFit.CONTAIN,
            ),
            width=260,
            height=260,
            alignment=ft.Alignment.CENTER if hasattr(ft.Alignment, "CENTER") else ft.Alignment.CENTER,
            animate=ft.Animation(600, ft.AnimationCurve.EASE_IN_OUT),
        )

        self.logo_container = ft.Row([self.logo], alignment=ft.MainAxisAlignment.CENTER)

        # 1. Tworzymy pola na formularzu
        self.pole_towar = ft.Text("", size=20, weight=ft.FontWeight.BOLD, color="green", text_align=ft.TextAlign.CENTER)
        
        self.pole_input1 = ft.TextField(
            input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d*$", replacement_string=""),
            visible=False, border_color=ft.Colors.GREEN_300, col={"sm": 12, "md": 4}, keyboard_type=ft.KeyboardType.TEXT,
            on_submit=self.obsluga_enter, enable_suggestions=False, on_blur=self.obsluga_enter,
        )
        
        self.pole_input2 = ft.TextField(
            input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d*$", replacement_string=""),
            visible=False, border_color=ft.Colors.GREEN_300, col={"sm": 12, "md": 4}, keyboard_type=ft.KeyboardType.TEXT,
            on_submit=self.obsluga_enter, enable_suggestions=False, on_blur=self.obsluga_enter,
        )
        
        self.pole_input3 = ft.TextField(
            input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d*$", replacement_string=""),
            visible=False, border_color=ft.Colors.GREEN_300, col={"sm": 12, "md": 4}, keyboard_type=ft.KeyboardType.TEXT,
        )
        
        self.pole_akcyza = ft.TextField(label="Należności akcyza", visible=False, read_only=True, border_color=ft.Colors.GREEN_300, bgcolor=ft.Colors.GREEN_50, col={"sm": 12, "md": 4})
        
        self.pole_vat = ft.TextField(label="Należności VAT", visible=False, read_only=True, border_color=ft.Colors.GREEN_300, bgcolor=ft.Colors.GREEN_50, col={"sm": 12, "md": 4})
        
        self.pole_clo = ft.TextField(label="Należności cło", visible=False, read_only=True, border_color=ft.Colors.GREEN_300, bgcolor=ft.Colors.GREEN_50, col={"sm": 12, "md": 4})
        
        self.pole_av = ft.TextField(label="Należności akcyza+vat", visible=False, read_only=True, border_color=ft.Colors.GREEN_300, bgcolor=ft.Colors.GREEN_50, col={"sm": 12, "md": 4})
        
        self.pole_avc = ft.TextField(label="Należności akcyza+vat+cło", visible=False, read_only=True, border_color=ft.Colors.GREEN_300, bgcolor=ft.Colors.GREEN_50, col={"sm": 12, "md": 4})

        self.pole_wartosc = ft.TextField(label="Wartość rynkowa", visible=False, read_only=True,border_color=ft.Colors.GREEN_300, bgcolor=ft.Colors.GREEN_50,col={"sm": 12, "md": 4})

        self.przycisk_oblicz = ft.Button(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.CALCULATE, color="white"),
                    ft.Text("Oblicz", color="white", weight=FontWeight.BOLD),
                ],
                alignment = ft.MainAxisAlignment.CENTER
            ),
            on_click=self.glowny_oblicz,
            visible=False,
            bgcolor=ft.Colors.GREEN_300,
            color=ft.Colors.WHITE,
            height=50,
            col={"sm": 12, "md": 4}
        )

        # 1.6 Przycisk Podglądu
        self.przycisk_podglad = ft.Button(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.PICTURE_AS_PDF, color="white"),
                    ft.Text("Drukuj / Zapisz", color="white", weight=FontWeight.BOLD),
                ],
                tight=True,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            bgcolor=ft.Colors.BLUE_GREY_600,
            on_click=self.otworz_okno_numeru,
            visible=False,
            height=50,
            col={"sm": 12, "md": 4}
        )

        self.przycisk_wyczysc = ft.OutlinedButton(
            "WYCZYŚĆ",
            icon=ft.Icons.CLEANING_SERVICES,
            on_click=self.wyczysc_pola,
            style=ft.ButtonStyle(color="red_400"),
            visible=False, # Czerwony kolor dla wyróżnienia akcji resetu
            height=50,
            col={"sm": 12, "md": 4},
        )

            # 2. Menu rozwijane
        menu_items = []
        for tryb_id, cfg in self.tryby_konfig.items():
            menu_items.append(
                ft.PopupMenuItem(
                    content=cfg["menu"],
                    on_click=lambda e, t=tryb_id: e.page.run_task(self.ustaw_tryb, t),
                )
            )

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
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                padding=10,
                border_radius=8,
            ),
            items=menu_items,
            tooltip="Wybierz rodzaj towaru",
            menu_position=ft.PopupMenuPosition.UNDER,
            width=250

        )

        # 3. Wygląd formularza
        self.naglowek = ft.Container(
            content=ft.ResponsiveRow([
                ft.Column([
                    ft.Text("KALKULATOR", size=20, weight=ft.FontWeight.BOLD, color="green_900"),
                    ft.Text("CELNO-SKARBOWY 2026", size=12, color="grey_600", italic=True),
                ],
                    spacing=0,
                    col={"sm": 12, "md": 5},
                    alignment=ft.MainAxisAlignment.START
                ),
                ft.Container(
                    self.menu_lista,
                    col={"sm": 12, "md": 7},
                    #expand=True,
                    alignment=ft.Alignment.CENTER_RIGHT #if os.name != "nt" else ft.Alignment.CENTER_LEFT,
                    )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(left=20, right=20, bottom=10, top=10)
        )

        self.kontener_statusu = ft.Container(
            content=ft.ResponsiveRow([self.pole_towar], alignment=ft.MainAxisAlignment.CENTER),
            padding=10, bgcolor="blue_grey_50", border_radius=8,
            alignment=ft.Alignment.CENTER if hasattr(ft.Alignment, "CENTER") else ft.Alignment.CENTER, visible=False
        )

        self.sekcja_dane = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("DANE WEJŚCIOWE", size=13, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=1, color="green_100"),
                    ft.ResponsiveRow([self.pole_input1, self.pole_input2, self.pole_input3], spacing=20),
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
                    ft.ResponsiveRow([self.pole_akcyza, self.pole_vat, self.pole_clo], spacing=20),
                    ft.ResponsiveRow([self.pole_wartosc, self.pole_av, self.pole_avc], spacing=20),
                ], spacing=15),
                padding=20,
            ),
            elevation=2, visible=False
        )

        self.stopka_akcji = ft.Container(
            content=ft.ResponsiveRow([self.przycisk_oblicz, self.przycisk_podglad, self.przycisk_wyczysc], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            margin=ft.Margin.only(top=20)
        )

        self.scroll = ft.ScrollMode.AUTO
        self.layout_formularza = ft.Container(
            content=ft.Column([
                self.logo_container, self.naglowek, self.kontener_statusu, self.sekcja_dane, self.sekcja_wyniki, self.stopka_akcji,
            ], spacing=10),
            padding=ft.padding.only(left=20, right=20, top=10, bottom=40), bgcolor=ft.Colors.WHITE, border_radius=20,
            border=ft.Border.all(1, "green_200"), shadow=ft.BoxShadow(blur_radius=15, color="black12")
        )
        self.layout_formularza.max_width = 900

        self.controls = [self.layout_formularza]

        # Pole na numer sprawy
        self.pole_nr_sprawy = ft.TextField(
            label="Numer sprawy (opcjonalnie)",
            hint_text="np. DS/123/2026",
            width=300,
            border_color="green_700"
        )

        # Okno dialogowe
        self.dialog_numeru = ft.AlertDialog(
            title=ft.Text("DODAJ NUMER SPRAWY", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text("Możesz dodać numer sprawy, który pojawi się na wydruku:", size=12),
                self.pole_nr_sprawy
            ], tight=True),
            actions=[
                ft.TextButton("Dalej", width=100, on_click=self.finalny_zapis_pdf)
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

    async def _refresh(self, control=None):
        target = control or self
        if hasattr(target, "update_async"):
            await target.update_async()
        else:
            target.update()

    def _format_kwota(self, value):
        return f"{value:.0f} zl"

    def _ustaw_wyniki_pol(self, a, v, c, w):
        self.pole_akcyza.value = self._format_kwota(a)
        self.pole_vat.value = self._format_kwota(v)
        self.pole_clo.value = self._format_kwota(c)
        self.pole_wartosc.value = self._format_kwota(w)
        self.pole_av.value = self._format_kwota(a + v)
        self.pole_avc.value = self._format_kwota(a + v + c)

    async def obsluga_enter(self, e):
        # Jeśli pole 1 straciło fokus (blur) lub naciśnięto Enter
        if e.control == self.pole_input1:
            # Jeśli pole 2 jest widoczne, skocz do niego
            if self.pole_input2.visible:
                # Tylko jeśli pole 2 nie ma jeszcze wartości lub jesteśmy w on_submit
                # (on_blur wywoła się też gdy użytkownik sam kliknie w inne pole)
                await self.pole_input2.focus()
            else:
                # Jeśli pole 2 jest ukryte, licz od razu
                await self.glowny_oblicz(None)

        # Jeśli pole 2 straciło fokus (blur) lub naciśnięto Enter
        elif e.control == self.pole_input2:
            # W drugim polu zawsze wyzwala obliczenia
            await self.glowny_oblicz(None)

        await self._refresh()


    async def wyczysc_pola(self, e):
        # Lista wszystkich pól, które mogą wymagać czyszczenia
        pola = [
            self.pole_input1, self.pole_input2, self.pole_wartosc, self.pole_nr_sprawy,
            self.pole_akcyza, self.pole_vat, self.pole_clo, self.pole_av, self.pole_avc
        ]

        # Jeden "if" ukryty w pętli (tzw. list comprehension lub prosta pętla)
        for pole in pola:
            if pole.visible:
                pole.value = ""
                pole.bgcolor = ft.Colors.GREEN_50

        # Dodatkowo ukrywamy przycisk PDF, bo dane zniknęły
        self.przycisk_podglad.visible = False
        self.przycisk_wyczysc.visible = False

        await self._refresh()
        await self.pole_input1.focus()
        await self._refresh()

    async def finalny_zapis_pdf(self, e):
        # 1. Zamykamy okno dialogowe
        self.dialog_numeru.open = False
        await self._refresh(self.page)

        # 2. Wywołujemy Twój pierwotny kod zapisu
        # Przekazujemy 'e', aby FilePicker wiedział, kto go wywołał
        await self.otworz_podglad(e)
        # czyścimy pole numeru sprawy
        self.pole_nr_sprawy.value = ""


    async def did_mount_async(self):
        if self.page:
            self.page.overlay.append(self.save_file_picker)
            await self._refresh(self.page)

    async def menu_hover(self, e):
        is_hovered = str(e.data).lower() == "true"
        e.control.bgcolor = ft.Colors.GREEN_900 if is_hovered else ft.Colors.GREEN_300
        await self._refresh(e.control)

    async def ustaw_tryb(self, tryb):
        config = self.tryby_konfig.get(tryb)
        if not config:
            return

        self.wybrany_tryb = tryb
        # Animacja logo
        self.logo.width = 100
        self.logo.height = 100
        self.logo.alignment = ft.Alignment.top_left if hasattr(ft.Alignment, "top_left") else ft.Alignment(-1, -1)
        self.logo_container.alignment = ft.MainAxisAlignment.START

        await self._refresh(self.layout_formularza)
        await self.wyczysc_formularz()
        self.pole_towar.value = config["nazwa"]

        i1 = config.get("i1")
        i2 = config.get("i2")
        i3 = config.get("i3")

        self.pole_input1.visible = i1 is not None
        if i1:
            self.pole_input1.label = i1

        self.pole_input2.visible = i2 is not None
        if i2:
            self.pole_input2.label = i2

        self.pole_input3.visible = i3 is not None
        if i3:
            self.pole_input3.label = i3

        wyniki = config.get("wyniki", {})
        self.pole_vat.visible = wyniki.get("v", False)
        self.pole_akcyza.visible = wyniki.get("a", False)
        self.pole_clo.visible = wyniki.get("c", False)
        self.pole_av.visible = wyniki.get("av", False)
        self.pole_avc.visible = wyniki.get("avc", False)
        self.pole_wartosc.visible = wyniki.get("w", False)

        self.przycisk_oblicz.visible = True
        self.kontener_statusu.visible = True
        self.sekcja_wyniki.visible = True
        self.sekcja_dane.visible = True
        self.przycisk_podglad.visible = False

        if i3 == "Kurs Euro":
            await self.pobierz_kurs_euro()

        await self._refresh()
        # Teraz dajemy fokus na pierwsze widoczne pole (opcjonalnie na iOS)
        # if self.pole_input1.visible:
        #     await self.pole_input1.focus()
        # elif self.pole_input2.visible:
        #     await self.pole_input2.focus()
        # await self.update_async() if hasattr(self, "update_async") else self.update()

    async def wyczysc_formularz(self):
        pola = [self.pole_input1, self.pole_input2, self.pole_input3, self.pole_akcyza, self.pole_vat, self.pole_clo, self.pole_wartosc, self.pole_av, self.pole_avc]
        for pole in pola:
            pole.value = ""
            pole.error = None
            pole.visible = False
            pole.bgcolor = ft.Colors.GREEN_50
        self.przycisk_oblicz.visible = False
        self.przycisk_podglad.visible = False
        await self._refresh()


    async def otworz_podglad(self, e):
        try:
            # Informacja o generowaniu
            snack = ft.SnackBar(ft.Text("Przygotowanie pliku PDF..."), duration=2000)
            self.page.overlay.append(snack)
            snack.open = True
            await self._refresh(self.page)

            # Zapisujemy PDF do zmiennej tymczasowej w celu późniejszego zapisu przez FilePicker
            pdf_bytes = self.generuj_pdf_bytes()
            
            # Otwieramy okno wyboru lokalizacji zapisu i czekamy na wynik (async w tej wersji Flet)
            # W wersji 0.80.5 FilePicker.save_file jest asynchroniczny i przyjmuje parametry.
            # Zmieniamy parametry na bardziej kompatybilne dla tej wersji
            try:
                saved_path = await self.save_file_picker.save_file(
                    file_name=f"wynik_kalkulacji_z_{self.dzisiaj}.pdf",
                    allowed_extensions=["pdf"],
                    src_bytes=pdf_bytes,
                )
            except TypeError:
                # Na wypadek, gdyby save_file w tej wersji przyjmował inne argumenty
                saved_path = await self.save_file_picker.save_file()
            
            if saved_path:
                # W starszych wersjach flet-desktop/web zapisywanie bajtów odbywało się po zdarzeniu on_result
                # Ale spróbujmy zapisać plik jeśli mamy ścieżkę (tylko desktop)
                if not self.page.web:
                    with open(saved_path, "wb") as f:
                        f.write(pdf_bytes)

                success_snack = ft.SnackBar(ft.Text(f"Plik został zapisany!"), bgcolor=ft.Colors.GREEN_400)
                self.page.overlay.append(success_snack)
                success_snack.open = True
                
                # Próba otwarcia zapisanego pliku (tylko na Windows/Desktop)
                if not (self.page.web or self.page.platform.is_mobile()):
                    url_path = saved_path.replace("\\", "/")
                    if not url_path.startswith("/"):
                        url_path = "/" + url_path
                    await self.page.launch_url_async(f"file://{url_path}") if hasattr(self.page, "launch_url_async") else self.page.launch_url(f"file://{url_path}")
                
                await self._refresh(self.page)
            
        except Exception as ex:
            print(f"Błąd przygotowania podglądu: {ex}")
            error_snack = ft.SnackBar(ft.Text(f"Błąd: {ex}"))
            self.page.overlay.append(error_snack)
            error_snack.open = True
            await self._refresh(self.page)

    def generuj_pdf_bytes(self):
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()

        font_path = os.path.join("assets", "Arial.ttf")

        # 1. Obsługa czcionki (Twój sprawdzony mechanizm)
        if os.path.exists(font_path):
            pdf.add_font("Arial", "", font_path)
            pdf.add_font("Arial", "B", font_path)
            base_font = "Arial"
        else:
            base_font = "Helvetica"

        # --- NAGŁÓWEK ---
        pdf.set_font(base_font, size=16 if base_font == "Arial" else 14)
        pdf.set_text_color(0, 100, 0)  # Zielony jak w Twoim UI
        pdf.cell(0, 10, "RAPORT KALKULACJI CELNO-SKARBOWEJ", ln=True, align='C')
        pdf.ln(5)

        # --- TABELA Z DANYMI (Zamiast tekstowego split("\n")) ---
        pdf.set_text_color(0, 0, 0)
        pdf.set_font(base_font, size=11)

        # Przygotowanie danych do tabeli (filtrowanie widocznych pól)
        dane_tabeli = [
            ("Numer sprawy", self.pole_nr_sprawy.value),
            ("Rodzaj towaru", self.pole_towar.value),
            ("Data wygenerowania", self.dzisiaj),
            ("", "")  # Odstęp
        ]

        # Dane wejściowe
        if self.pole_input1.visible: dane_tabeli.append((self.pole_input1.label, self.pole_input1.value))
        if self.pole_input2.visible: dane_tabeli.append((self.pole_input2.label, self.pole_input2.value))
        if self.pole_input3.visible: dane_tabeli.append((self.pole_input3.label, self.pole_input3.value))

        dane_tabeli.append(("", ""))  # Odstęp

        # Wyniki
        if self.pole_akcyza.visible: dane_tabeli.append(("Podatek akcyzowy", self.pole_akcyza.value))
        if self.pole_clo.visible: dane_tabeli.append(("Cło", self.pole_clo.value))
        if self.pole_vat.visible: dane_tabeli.append(("Podatek VAT", self.pole_vat.value))
        if self.pole_wartosc.visible: dane_tabeli.append(("Wartość rynkowa", self.pole_wartosc.value))
        if self.pole_av.visible: dane_tabeli.append(("SUMA (Akcyza+VAT)", self.pole_av.value))
        if self.pole_avc.visible: dane_tabeli.append(("SUMA (Akcyza+Vat+Cło)", self.pole_avc.value))

        # Rysowanie tabeli (Metoda .table() tworzy ładne ramki)
        with pdf.table(width=170, col_widths=(100, 70), align="C") as table:
            for row_data in dane_tabeli:
                row = table.row()
                for item in row_data:
                    # Jeśli nie ma czcionki Arial, podmieniamy znaki w locie
                    if base_font == "Helvetica":
                        polskie_znaki = {"ą": "a", "ć": "c", "ę": "e", "ł": "l", "ń": "n", "ó": "o", "ś": "s", "ź": "z",
                                         "ż": "z",
                                         "Ą": "A", "Ć": "C", "Ę": "E", "Ł": "L", "Ń": "N", "Ó": "O", "Ś": "S", "Ź": "Z",
                                         "Ż": "Z"}
                        for k, v in polskie_znaki.items():
                            item = item.replace(k, v)
                    row.cell(str(item) if item is not None else "")
            # Przejdź na dół strony
        # Przejdź na 28mm od dołu strony
        pdf.set_y(-30)
        pdf.set_font(base_font, size=8)
        # Używamy cell zamiast multi_cell, bo zajmuje tylko jedną linię
        pdf.cell(0, 10, "Niniejszy wydruk ma charakter informacyjny i nie stanowi dokumentu urzędowego.", align="C", ln=False)

        return pdf.output()

    def otworz_okno_numeru(self, e):
        self.page.overlay.append(self.dialog_numeru)
        self.dialog_numeru.open = True
        self.page.update()

    def on_save_result(self, e: ft.FilePickerResultEvent):
        return

    async def pobierz_liczbe(self, pole):
        surowy_tekst = pole.value.strip() if pole.value else ""
        pole.error = None
        
        if not surowy_tekst:
            pole.error = "Uzupełnij pole!"
            await self._refresh()
            return None
        
        if surowy_tekst == ".":
            pole.error = "Błędna liczba!"
            await self._refresh()
            return None

        if surowy_tekst.startswith("."):
            surowy_tekst = "0" + surowy_tekst
            pole.value = surowy_tekst

        try:
            return float(surowy_tekst)
        except ValueError:
            pole.error = "To nie jest liczba!"
            await self._refresh()
            return None

    async def pobierz_kurs_euro(self):
        url = "https://api.nbp.pl/api/exchangerates/rates/a/eur/?format=json"
        try:
            headers = {'Accept': 'application/json', 'User-Agent': 'FletApp/1.0'}
            # Używamy httpx dla asynchronicznych zapytań
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    kurs = data["rates"][0]["mid"]
                    data_publikacji = data["rates"][0]["effectiveDate"]
                    self.pole_input3.value = f"{kurs:.4f}"
                    self.pole_input3.label = f"Kurs EUR (NBP: {data_publikacji})"
                    await self._refresh()
        except Exception as ex:
            print(f"Błąd kursu: {ex}")

    async def przestepstwo(self, a=0, v=0, c=0):
        self.pole_akcyza.bgcolor = ft.Colors.RED_100 if a > self.prog_przestepstwa else ft.Colors.GREEN_50
        self.pole_vat.bgcolor = ft.Colors.RED_100 if v > self.prog_przestepstwa else ft.Colors.GREEN_50
        self.pole_clo.bgcolor = ft.Colors.RED_100 if c > self.prog_przestepstwa else ft.Colors.GREEN_50
        
        if a > self.prog_przestepstwa: self.pole_akcyza.value += " - PRZESTĘPSTWO!"
        if v > self.prog_przestepstwa: self.pole_vat.value += " - PRZESTĘPSTWO!"
        if c > self.prog_przestepstwa: self.pole_clo.value += " - PRZESTĘPSTWO!"
        await self._refresh()

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

    async def glowny_oblicz(self, e):
        # Aktualizacja daty i godziny przy każdym przeliczeniu (poprawka dla Render)
        teraz = datetime.now() #+ timedelta(hours=1)
        self.dzisiaj = teraz.strftime("%d-%m-%y_%H-%M-%S")
        
        i1 = await self.pobierz_liczbe(self.pole_input1)
        if i1 is None:
            return
            
        i2 = await self.pobierz_liczbe(self.pole_input2) if self.pole_input2.visible else 0
        i3 = await self.pobierz_liczbe(self.pole_input3) if self.pole_input3.visible else 0
        
        if (self.pole_input2.visible and i2 is None) or (self.pole_input3.visible and i3 is None):
            return

        s = self.stawki.get(self.wybrany_tryb)
        if not s: return  # Zabezpieczenie

        a, v, c, w = 0, 0, 0, 0
        
        if self.wybrany_tryb == "papierosy_przemyt":
            wc = s["wc_mnoznik"] * i1
            a = round(s["s_akc"] * i1, 0)
            c = round(wc * s["s_clo"], 0)
            v = round((wc + c + a) * s["s_vat"], 0)
            w = round(s["s_wartosc"] * i1, 0)
    
        elif self.wybrany_tryb == "papierosy_paser":
            wc = round(s["wc_mnoznik"] * i1, 0)
            a = round(s["s_akc"] * i1, 0)
            v = round((wc + a) * s["s_vat"], 0)
            w = round(s["s_wartosc"] * i1, 0)
            
        elif self.wybrany_tryb == "wodka_przemyt":
            wc = round(s["wc_jedn"] * i1, 0)
            a = round(s["s_akc"] * (i1 * i2 / 100), 0)
            v = round((wc + a) * s["s_vat"], 0)
            w = round(s["s_wartosc"] * i1, 0)
            
        elif self.wybrany_tryb == "wodka_paser":
            a = round(s["s_akc"] * (i1 * i2 / 100), 0)
            w = round(s["s_wartosc"] * i1, 0)
            
        elif self.wybrany_tryb == "tyton_przemyt":
            wc = round(s["wc_jedn"] * i1, 0)
            a = round(s["s_akc"] * i1, 0)
            c = round(s["s_clo"] * wc, 0)
            v = round((a + wc + c) * s["s_vat"], 0)
            w = round(s["s_wartosc"] * i1, 0)
            
        elif self.wybrany_tryb == "tyton_paser":
            wc = round(s["wc_jedn"] * i1, 0)
            a = round(s["s_akc"] * i1, 0)
            v = round((a + wc) * s["s_vat"], 0)
            w = round(s["s_wartosc"] * i1, 0)

        elif self.wybrany_tryb == "spirytus_przemyt":
            c = round((s["s_clo"] / 100) * i3 * i1, 0)
            wc = round(s["wc_jedn"] * i1, 0)
            a = round(s["s_akc"] * (i1 * i2 / 100), 0)
            v = round((wc + a + c) * s["s_vat"], 0)
            w = round(s["s_wartosc"] * i1, 0)

        elif self.wybrany_tryb == "spirytus_paser":
            a = round(s["s_akc"] * (i1 * i2 / 100), 0)
            w = round(s["s_wartosc"] * i1, 0)

        elif self.wybrany_tryb == "cygara_przemyt":
            wc = round(s["wc_jedn"] * i1, 0)
            a = round(s["s_akc"] * i1, 0)
            c = round(s["s_clo"] * wc, 0)
            v = round((a + wc + c) * s["s_vat"], 0)
            w = round(s["s_wartosc"] * i1, 0)

        elif self.wybrany_tryb == "cygara_paser":
            #s_akc, s_vat, wc_jedn = 786, 0.23, 13
            wc = round(s["wc_jedn"] * i1, 0)
            a = round(s["s_akc"] * i1, 0)
            v = round((a + wc) * s["s_vat"], 0)
            w = round(s["s_wartosc"] * i1, 0)

        elif self.wybrany_tryb == "nowatorskie_przemyt":
            wc = round(s["wc_jedn"] * i1, 0)
            a = round(s["s_akc"] * i1, 0)
            c = round(s["s_clo"] * wc, 0)
            v = round((a + wc + c) * s["s_vat"], 0)
            w = round(s["s_wartosc"] * i1, 0)

        elif self.wybrany_tryb == "nowatorskie_paser":
            wc = round(s["wc_jedn"] * i1, 0)
            a = round(s["s_akc"] * i1, 0)
            v = round((a + wc) * s["s_vat"], 0)
            w = round(s["s_wartosc"] * i1, 0)

        elif self.wybrany_tryb == "susz_paser":
            wc = round(s["wc_jedn"] * i1, 0)
            a = round(s["s_akc"] * i1, 0)
            v = round((a + wc) * s["s_vat"], 0)
            w = round(s["s_wartosc"] * i1, 0)

        elif self.wybrany_tryb == "e-pap_przemyt":
            wc = round(s["wc_jedn"] * i1, 0)
            akcyza_plynu = round(s["s_akc"] * i1, 0)
            a = round((s["s_akc2"] * i2) + akcyza_plynu, 0) if i2 > 0 else akcyza_plynu
            c = round(s["s_clo"] * wc, 0)
            v = round((a + wc + c) * s["s_vat"], 0)
            w = round(s["s_wartosc"] * i1, 0)

        elif self.wybrany_tryb == "e-pap_paser":
            wc = round(s["wc_jedn"] * i1, 0)
            akcyza_plynu = round(s["s_akc"] * i1, 0)
            a = round((s["s_akc2"] * i2) + akcyza_plynu, 0) if i2 > 0 else akcyza_plynu
            c = 0
            v = round((a + wc) * s["s_vat"], 0)
            w = round(s["s_wartosc"] * i1, 0)

        self._ustaw_wyniki_pol(a, v, c, w)
        
        self.przycisk_podglad.visible = True
        self.przycisk_wyczysc.visible = True
        await self.przestepstwo(a, v, c)
        await self._refresh()




async def main(page: ft.Page):
    # --- Konfiguracja strony ---
    page.theme_mode = ft.ThemeMode.LIGHT
    page.title = "Kalkulator należności celno-skarbowych"
    page.scroll = ft.ScrollMode.HIDDEN
    page.padding = 10
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # --- 1. DODANIE KLASY ---
    formularz = Formularz_glowny()
    await page.add_async(formularz) if hasattr(page, "add_async") else page.add(formularz)


    # Finalne odświeżenie strony
    await page.update_async() if hasattr(page, "update_async") else page.update()


if __name__ == "__main__":
    # Zmieniamy ft.app na ft.run
    ft.run(
        main,
        assets_dir="assets",
        view=ft.AppView.WEB_BROWSER
    )
