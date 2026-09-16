"""Signal Bot Auto Responder - professional dark cyber control panel.

Local GUI for preparing/reviewing authorized Signal group content.
This interface does not automate anti-abuse controls, verification, CAPTCHA,
or platform-control bypasses.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
import webbrowser

from .config import Settings
from .daily_content import generate_variations
from .storage import Storage


GREEN = "#39ff88"
GREEN_DARK = "#0b6b3a"
GREEN_MID = "#16c96a"
BLACK = "#070a09"
CHARCOAL = "#0d1210"
PANEL = "#101815"
PANEL_2 = "#131d18"
BORDER = "#1e6b45"
WHITE = "#f2fff8"
MUTED = "#8da99b"
RED = "#ff5c6c"
YELLOW = "#ffd166"

LANGUAGES = {
    "English": {
        "flag": "🇬🇧",
        "message_generator": "MESSAGE GENERATOR",
        "saved_packs": "SAVED PACKS",
        "authorized_groups": "AUTHORIZED GROUPS",
        "scheduler": "SCHEDULER",
        "settings": "SETTINGS",
        "logs": "LOGS",
        "about": "ABOUT",
        "today_message": "Today's message",
        "generate": "Generate 24 Variations",
        "select_all": "Select All",
        "deselect_all": "Clear All",
        "save": "Save Approved Pack",
        "message_variations": "Message variations",
        "group_name": "Name",
        "group_id": "Group ID",
        "add_group": "Add Group",
        "remove_selected": "Remove Selected",
        "no_groups": "No groups configured.",
        "enabled": "Enabled",
        "disabled": "Disabled",
        "ready": "Ready",
        "telegram": "JOIN US ON TELEGRAM",
        "version": "v2.0.0",
    },
    "हिन्दी (Hindi)": {
        "flag": "🇮🇳",
        "message_generator": "संदेश जनरेटर",
        "saved_packs": "सेव्ड पैक्स",
        "authorized_groups": "अधिकृत ग्रुप",
        "scheduler": "शेड्यूलर",
        "settings": "सेटिंग्स",
        "logs": "लॉग्स",
        "about": "अबाउट",
        "today_message": "आज का संदेश",
        "generate": "24 वैरिएशन बनाएं",
        "select_all": "सभी चुनें",
        "deselect_all": "सभी हटाएं",
        "save": "स्वीकृत पैक सेव करें",
        "message_variations": "संदेश वैरिएशन",
        "group_name": "नाम",
        "group_id": "ग्रुप ID",
        "add_group": "ग्रुप जोड़ें",
        "remove_selected": "चयनित हटाएं",
        "no_groups": "कोई ग्रुप कॉन्फ़िगर नहीं है।",
        "enabled": "सक्रिय",
        "disabled": "निष्क्रिय",
        "ready": "तैयार",
        "telegram": "टेलीग्राम पर जुड़ें",
        "version": "v2.0.0",
    },
    "Русский (Russian)": {
        "flag": "🇷🇺",
        "message_generator": "ГЕНЕРАТОР СООБЩЕНИЙ",
        "saved_packs": "СОХРАНЁННЫЕ ПАКЕТЫ",
        "authorized_groups": "РАЗРЕШЁННЫЕ ГРУППЫ",
        "scheduler": "ПЛАНИРОВЩИК",
        "settings": "НАСТРОЙКИ",
        "logs": "ЖУРНАЛЫ",
        "about": "О ПРОГРАММЕ",
        "today_message": "Сообщение на сегодня",
        "generate": "Создать 24 варианта",
        "select_all": "Выбрать все",
        "deselect_all": "Очистить все",
        "save": "Сохранить одобренный пакет",
        "message_variations": "Варианты сообщений",
        "group_name": "Название",
        "group_id": "ID группы",
        "add_group": "Добавить группу",
        "remove_selected": "Удалить выбранные",
        "no_groups": "Группы не настроены.",
        "enabled": "Включено",
        "disabled": "Отключено",
        "ready": "Готово",
        "telegram": "МЫ В TELEGRAM",
        "version": "v2.0.0",
    },
    "Español (Spanish)": {
        "flag": "🇪🇸",
        "message_generator": "GENERADOR DE MENSAJES",
        "saved_packs": "PAQUETES GUARDADOS",
        "authorized_groups": "GRUPOS AUTORIZADOS",
        "scheduler": "PROGRAMADOR",
        "settings": "AJUSTES",
        "logs": "REGISTROS",
        "about": "ACERCA DE",
        "today_message": "Mensaje de hoy",
        "generate": "Generar 24 variaciones",
        "select_all": "Seleccionar todo",
        "deselect_all": "Limpiar todo",
        "save": "Guardar paquete aprobado",
        "message_variations": "Variaciones del mensaje",
        "group_name": "Nombre",
        "group_id": "ID del grupo",
        "add_group": "Añadir grupo",
        "remove_selected": "Eliminar seleccionados",
        "no_groups": "No hay grupos configurados.",
        "enabled": "Activo",
        "disabled": "Desactivado",
        "ready": "Listo",
        "telegram": "ÚNETE EN TELEGRAM",
        "version": "v2.0.0",
    },
    "العربية (Arabic)": {
        "flag": "🇸🇦",
        "message_generator": "مولّد الرسائل",
        "saved_packs": "الحزم المحفوظة",
        "authorized_groups": "المجموعات المصرّح بها",
        "scheduler": "المجدول",
        "settings": "الإعدادات",
        "logs": "السجلات",
        "about": "حول",
        "today_message": "رسالة اليوم",
        "generate": "إنشاء 24 تنويعاً",
        "select_all": "تحديد الكل",
        "deselect_all": "مسح الكل",
        "save": "حفظ الحزمة المعتمدة",
        "message_variations": "تنويعات الرسالة",
        "group_name": "الاسم",
        "group_id": "معرّف المجموعة",
        "add_group": "إضافة مجموعة",
        "remove_selected": "إزالة المحدد",
        "no_groups": "لا توجد مجموعات مهيأة.",
        "enabled": "مفعّل",
        "disabled": "معطّل",
        "ready": "جاهز",
        "telegram": "انضم إلينا على تيليجرام",
        "version": "v2.0.0",
    },
    "中文 (Chinese)": {
        "flag": "🇨🇳",
        "message_generator": "消息生成器",
        "saved_packs": "已保存数据包",
        "authorized_groups": "授权群组",
        "scheduler": "调度器",
        "settings": "设置",
        "logs": "日志",
        "about": "关于",
        "today_message": "今日消息",
        "generate": "生成 24 个变体",
        "select_all": "全选",
        "deselect_all": "清除全部",
        "save": "保存已批准数据包",
        "message_variations": "消息变体",
        "group_name": "名称",
        "group_id": "群组 ID",
        "add_group": "添加群组",
        "remove_selected": "删除所选",
        "no_groups": "尚未配置群组。",
        "enabled": "已启用",
        "disabled": "已禁用",
        "ready": "就绪",
        "telegram": "加入 TELEGRAM",
        "version": "v2.0.0",
    },
    "Norsk (Norwegian)": {
        "flag": "🇳🇴",
        "message_generator": "MELDINGSGENERATOR",
        "saved_packs": "LAGREDE PAKKER",
        "authorized_groups": "AUTORISERTE GRUPPER",
        "scheduler": "PLANLEGGER",
        "settings": "INNSTILLINGER",
        "logs": "LOGGER",
        "about": "OM",
        "today_message": "Dagens melding",
        "generate": "Generer 24 varianter",
        "select_all": "Velg alle",
        "deselect_all": "Fjern alle",
        "save": "Lagre godkjent pakke",
        "message_variations": "Meldingsvarianter",
        "group_name": "Navn",
        "group_id": "Gruppe-ID",
        "add_group": "Legg til gruppe",
        "remove_selected": "Fjern valgte",
        "no_groups": "Ingen grupper konfigurert.",
        "enabled": "Aktivert",
        "disabled": "Deaktivert",
        "ready": "Klar",
        "telegram": "BLI MED PÅ TELEGRAM",
        "version": "v2.0.0",
    },
    "Čeština (Czech)": {
        "flag": "🇨🇿",
        "message_generator": "GENERÁTOR ZPRÁV",
        "saved_packs": "ULOŽENÉ BALÍČKY",
        "authorized_groups": "AUTORIZOVANÉ SKUPINY",
        "scheduler": "PLÁNOVAČ",
        "settings": "NASTAVENÍ",
        "logs": "PROTOKOLY",
        "about": "O APLIKACI",
        "today_message": "Dnešní zpráva",
        "generate": "Vygenerovat 24 variant",
        "select_all": "Vybrat vše",
        "deselect_all": "Zrušit výběr",
        "save": "Uložit schválený balíček",
        "message_variations": "Varianty zpráv",
        "group_name": "Název",
        "group_id": "ID skupiny",
        "add_group": "Přidat skupinu",
        "remove_selected": "Odebrat vybrané",
        "no_groups": "Nejsou nakonfigurovány žádné skupiny.",
        "enabled": "Povoleno",
        "disabled": "Zakázáno",
        "ready": "Připraveno",
        "telegram": "PŘIPOJTE SE NA TELEGRAM",
        "version": "v2.0.0",
    },
    "Deutsch (German)": {
        "flag": "🇩🇪",
        "message_generator": "NACHRICHTENGENERATOR",
        "saved_packs": "GESPEICHERTE PAKETE",
        "authorized_groups": "AUTORISIERTE GRUPPEN",
        "scheduler": "PLANER",
        "settings": "EINSTELLUNGEN",
        "logs": "PROTOKOLLE",
        "about": "ÜBER",
        "today_message": "Heutige Nachricht",
        "generate": "24 Varianten erstellen",
        "select_all": "Alle auswählen",
        "deselect_all": "Alle abwählen",
        "save": "Genehmigtes Paket speichern",
        "message_variations": "Nachrichtenvarianten",
        "group_name": "Name",
        "group_id": "Gruppen-ID",
        "add_group": "Gruppe hinzufügen",
        "remove_selected": "Ausgewählte entfernen",
        "no_groups": "Keine Gruppen konfiguriert.",
        "enabled": "Aktiviert",
        "disabled": "Deaktiviert",
        "ready": "Bereit",
        "telegram": "AUF TELEGRAM BEITRETEN",
        "version": "v2.0.0",
    },
    "Français (French)": {
        "flag": "🇫🇷",
        "message_generator": "GÉNÉRATEUR DE MESSAGES",
        "saved_packs": "PACKS ENREGISTRÉS",
        "authorized_groups": "GROUPES AUTORISÉS",
        "scheduler": "PLANIFICATEUR",
        "settings": "PARAMÈTRES",
        "logs": "JOURNAUX",
        "about": "À PROPOS",
        "today_message": "Message du jour",
        "generate": "Générer 24 variantes",
        "select_all": "Tout sélectionner",
        "deselect_all": "Tout effacer",
        "save": "Enregistrer le pack approuvé",
        "message_variations": "Variantes de message",
        "group_name": "Nom",
        "group_id": "ID du groupe",
        "add_group": "Ajouter un groupe",
        "remove_selected": "Supprimer la sélection",
        "no_groups": "Aucun groupe configuré.",
        "enabled": "Activé",
        "disabled": "Désactivé",
        "ready": "Prêt",
        "telegram": "REJOIGNEZ-NOUS SUR TELEGRAM",
        "version": "v2.0.0",
    },
    "Italiano (Italian)": {
        "flag": "🇮🇹",
        "message_generator": "GENERATORE DI MESSAGGI",
        "saved_packs": "PACCHETTI SALVATI",
        "authorized_groups": "GRUPPI AUTORIZZATI",
        "scheduler": "PIANIFICATORE",
        "settings": "IMPOSTAZIONI",
        "logs": "REGISTRI",
        "about": "INFORMAZIONI",
        "today_message": "Messaggio di oggi",
        "generate": "Genera 24 varianti",
        "select_all": "Seleziona tutto",
        "deselect_all": "Deseleziona tutto",
        "save": "Salva pacchetto approvato",
        "message_variations": "Varianti del messaggio",
        "group_name": "Nome",
        "group_id": "ID gruppo",
        "add_group": "Aggiungi gruppo",
        "remove_selected": "Rimuovi selezionati",
        "no_groups": "Nessun gruppo configurato.",
        "enabled": "Abilitato",
        "disabled": "Disabilitato",
        "ready": "Pronto",
        "telegram": "UNISCITI A TELEGRAM",
        "version": "v2.0.0",
    },
    "Português (Portuguese)": {
        "flag": "🇵🇹",
        "message_generator": "GERADOR DE MENSAGENS",
        "saved_packs": "PACOTES GUARDADOS",
        "authorized_groups": "GRUPOS AUTORIZADOS",
        "scheduler": "AGENDADOR",
        "settings": "DEFINIÇÕES",
        "logs": "REGISTOS",
        "about": "SOBRE",
        "today_message": "Mensagem de hoje",
        "generate": "Gerar 24 variações",
        "select_all": "Selecionar tudo",
        "deselect_all": "Limpar tudo",
        "save": "Guardar pacote aprovado",
        "message_variations": "Variações da mensagem",
        "group_name": "Nome",
        "group_id": "ID do grupo",
        "add_group": "Adicionar grupo",
        "remove_selected": "Remover selecionados",
        "no_groups": "Nenhum grupo configurado.",
        "enabled": "Ativado",
        "disabled": "Desativado",
        "ready": "Pronto",
        "telegram": "JUNTE-SE A NÓS NO TELEGRAM",
        "version": "v2.0.0",
    },
    "日本語 (Japanese)": {
        "flag": "🇯🇵",
        "message_generator": "メッセージジェネレーター",
        "saved_packs": "保存済みパック",
        "authorized_groups": "承認済みグループ",
        "scheduler": "スケジューラー",
        "settings": "設定",
        "logs": "ログ",
        "about": "概要",
        "today_message": "今日のメッセージ",
        "generate": "24個のバリエーションを生成",
        "select_all": "すべて選択",
        "deselect_all": "すべて解除",
        "save": "承認済みパックを保存",
        "message_variations": "メッセージのバリエーション",
        "group_name": "名前",
        "group_id": "グループID",
        "add_group": "グループを追加",
        "remove_selected": "選択項目を削除",
        "no_groups": "グループが設定されていません。",
        "enabled": "有効",
        "disabled": "無効",
        "ready": "準備完了",
        "telegram": "TELEGRAMに参加",
        "version": "v2.0.0",
    },
    "한국어 (Korean)": {
        "flag": "🇰🇷",
        "message_generator": "메시지 생성기",
        "saved_packs": "저장된 패키지",
        "authorized_groups": "승인된 그룹",
        "scheduler": "스케줄러",
        "settings": "설정",
        "logs": "로그",
        "about": "정보",
        "today_message": "오늘의 메시지",
        "generate": "24개 변형 생성",
        "select_all": "모두 선택",
        "deselect_all": "모두 지우기",
        "save": "승인된 패키지 저장",
        "message_variations": "메시지 변형",
        "group_name": "이름",
        "group_id": "그룹 ID",
        "add_group": "그룹 추가",
        "remove_selected": "선택 항목 삭제",
        "no_groups": "구성된 그룹이 없습니다.",
        "enabled": "활성화",
        "disabled": "비활성화",
        "ready": "준비 완료",
        "telegram": "텔레그램 참여",
        "version": "v2.0.0",
    },
    "Türkçe (Turkish)": {
        "flag": "🇹🇷",
        "message_generator": "MESAJ OLUŞTURUCU",
        "saved_packs": "KAYDEDİLEN PAKETLER",
        "authorized_groups": "YETKİLİ GRUPLAR",
        "scheduler": "ZAMANLAYICI",
        "settings": "AYARLAR",
        "logs": "GÜNLÜKLER",
        "about": "HAKKINDA",
        "today_message": "Bugünün mesajı",
        "generate": "24 varyasyon oluştur",
        "select_all": "Tümünü seç",
        "deselect_all": "Tümünü temizle",
        "save": "Onaylanan paketi kaydet",
        "message_variations": "Mesaj varyasyonları",
        "group_name": "Ad",
        "group_id": "Grup ID",
        "add_group": "Grup ekle",
        "remove_selected": "Seçilenleri kaldır",
        "no_groups": "Yapılandırılmış grup yok.",
        "enabled": "Etkin",
        "disabled": "Devre dışı",
        "ready": "Hazır",
        "telegram": "TELEGRAM'A KATIL",
        "version": "v2.0.0",
    },
}

class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("SIGNAL BOT - Security101")
        self.geometry("1400x900")
        self.minsize(1050, 720)
        self.configure(bg=BLACK)

        self.storage = Storage()
        self.settings = Settings.from_env()

        self.vars: list[tuple[tk.BooleanVar, tk.Text]] = []
        self.group_vars: dict[str, tk.BooleanVar] = {}
        self.current_language = "English"
        self.nav_buttons: dict[str, tk.Button] = {}

        self._configure_fonts()
        self._build_header()
        self._build_body()
        self._build_footer()
        self.refresh_groups()

    def _configure_fonts(self) -> None:
        self.font_body = ("Segoe UI", 10)
        self.font_small = ("Segoe UI", 9)
        self.font_title = ("Segoe UI", 19, "bold")
        self.font_section = ("Segoe UI", 12, "bold")
        self.font_mono = ("Consolas", 10)

    def _button(self, parent, text, command, width=None, primary=False):
        kwargs = {
            "text": text,
            "command": command,
            "font": ("Segoe UI", 9, "bold"),
            "fg": BLACK if primary else WHITE,
            "bg": GREEN if primary else PANEL_2,
            "activeforeground": BLACK if primary else WHITE,
            "activebackground": GREEN_MID if primary else GREEN_DARK,
            "relief": "flat",
            "bd": 0,
            "cursor": "hand2",
            "padx": 12,
            "pady": 8,
        }
        if width:
            kwargs["width"] = width
        return tk.Button(parent, **kwargs)

    def _label(self, parent, text, **kwargs):
        base = {
            "bg": parent.cget("bg"),
            "fg": WHITE,
            "font": self.font_body,
        }
        base.update(kwargs)
        return tk.Label(parent, text=text, **base)

    def _panel(self, parent, **kwargs):
        base = {
            "bg": PANEL,
            "highlightbackground": BORDER,
            "highlightcolor": BORDER,
            "highlightthickness": 1,
            "bd": 0,
        }
        base.update(kwargs)
        return tk.Frame(parent, **base)

    def _build_header(self) -> None:
        header = tk.Frame(self, bg=BLACK, height=125)
        header.pack(fill="x", padx=18, pady=(14, 0))
        header.pack_propagate(False)

        # Stylized shield/signal logo drawn with Tk Canvas so the application
        # remains dependency-free.
        logo = tk.Canvas(header, width=86, height=92, bg=BLACK, highlightthickness=0)
        logo.pack(side="left", padx=(4, 12))
        # Hooded/cyberpunk silhouette.
        logo.create_arc(9, 0, 77, 76, start=195, extent=150, outline=GREEN, width=4)
        logo.create_polygon(
            16, 34, 24, 18, 43, 10, 62, 18, 70, 34,
            63, 70, 23, 70, fill="#030504", outline=GREEN, width=2
        )
        logo.create_polygon(
            28, 31, 43, 25, 58, 31, 51, 52, 35, 52,
            fill="#020303", outline=GREEN_MID, width=2
        )
        logo.create_line(34, 38, 40, 36, fill=GREEN, width=3)
        logo.create_line(52, 38, 46, 36, fill=GREEN, width=3)
        logo.create_arc(25, 18, 61, 55, start=215, extent=110, outline=GREEN, width=2)
        logo.create_line(43, 61, 43, 81, fill=GREEN, width=3)
        logo.create_line(30, 75, 43, 86, fill=GREEN, width=3)
        logo.create_line(56, 75, 43, 86, fill=GREEN, width=3)
        logo.create_arc(20, 2, 66, 48, start=205, extent=130, outline=GREEN_MID, width=2)

        title_box = tk.Frame(header, bg=BLACK)
        title_box.pack(side="left", fill="both", expand=True)

        tk.Label(
            title_box,
            text="SIGNAL",
            bg=BLACK,
            fg=WHITE,
            font=("Segoe UI", 26, "bold"),
        ).pack(anchor="w")
        tk.Label(
            title_box,
            text="BOT",
            bg=BLACK,
            fg=GREEN,
            font=("Segoe UI", 26, "bold"),
        ).pack(anchor="w", pady=(0, 0))
        tk.Label(
            title_box,
            text="AUTO RESPONDER  •  SECURE  •  PRIVATE  •  AUTHORIZED",
            bg=BLACK,
            fg=MUTED,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", pady=(2, 0))

        right = tk.Frame(header, bg=BLACK)
        right.pack(side="right", anchor="n", pady=6)

        lang_row = tk.Frame(right, bg=BLACK)
        lang_row.pack(anchor="e")
        tk.Label(lang_row, text="🌐", bg=BLACK, fg=GREEN, font=("Segoe UI", 12)).pack(side="left")
        self.language_var = tk.StringVar(value="🇬🇧 English")
        self.language_menu = tk.OptionMenu(
            lang_row,
            self.language_var,
            *[f"{v['flag']} {k}" for k, v in LANGUAGES.items()],
            command=self._language_changed,
        )
        self.language_menu.configure(
            bg=PANEL_2,
            fg=WHITE,
            activebackground=GREEN_DARK,
            activeforeground=WHITE,
            highlightthickness=1,
            highlightbackground=BORDER,
            relief="flat",
            font=self.font_body,
        )
        self.language_menu["menu"].configure(
            bg=PANEL_2, fg=WHITE, activebackground=GREEN_DARK, activeforeground=WHITE
        )
        self.language_menu.pack(side="left", padx=(5, 0))

        tg = self._panel(right, width=300, height=60)
        tg.pack_propagate(False)
        tg.pack(anchor="e", pady=(10, 0))
        tk.Label(
            tg, text="✈  JOIN US ON TELEGRAM",
            bg=PANEL, fg=GREEN, font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=10, pady=(7, 0))
        links = tk.Frame(tg, bg=PANEL)
        links.pack(anchor="w", padx=10)
        for handle in ("@RU_LAPSUS", "@CODERX0981"):
            self._button(
                links,
                handle,
                lambda h=handle: webbrowser.open("https://t.me/" + h.lstrip("@")),
            ).pack(side="left", padx=(0, 6), pady=4)

    def _build_body(self) -> None:
        body = tk.Frame(self, bg=BLACK)
        body.pack(fill="both", expand=True, padx=18, pady=8)

        self.sidebar = tk.Frame(body, bg=BLACK, width=230)
        self.sidebar.pack(side="left", fill="y", padx=(0, 14))
        self.sidebar.pack_propagate(False)

        self.content = tk.Frame(body, bg=BLACK)
        self.content.pack(side="left", fill="both", expand=True)

        self._build_sidebar()
        self._build_message_view()

    def _build_sidebar(self) -> None:
        items = [
            ("message_generator", "💬"),
            ("saved_packs", "▤"),
            ("authorized_groups", "♣"),
            ("scheduler", "◷"),
            ("settings", "⚙"),
            ("logs", "▣"),
            ("about", "ⓘ"),
        ]
        self.sidebar_title = tk.Label(
            self.sidebar,
            text="CONTROL PANEL",
            bg=BLACK,
            fg=MUTED,
            font=("Segoe UI", 9, "bold"),
        )
        self.sidebar_title.pack(anchor="w", pady=(2, 8))

        for key, icon in items:
            button = tk.Button(
                self.sidebar,
                text=f"{icon}   {LANGUAGES['English'][key]}",
                anchor="w",
                font=("Segoe UI", 10, "bold"),
                bg=GREEN if key == "message_generator" else PANEL,
                fg=BLACK if key == "message_generator" else WHITE,
                activebackground=GREEN_DARK,
                activeforeground=WHITE,
                relief="flat",
                bd=0,
                padx=14,
                pady=12,
                cursor="hand2",
                command=lambda k=key: self._navigate(k),
            )
            button.pack(fill="x", pady=2)
            self.nav_buttons[key] = button

        spacer = tk.Frame(self.sidebar, bg=BLACK)
        spacer.pack(fill="both", expand=True)

        card = self._panel(self.sidebar)
        card.pack(fill="x", pady=8)
        tk.Label(
            card,
            text="SECURITY101",
            bg=PANEL,
            fg=GREEN,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", padx=12, pady=(12, 2))
        tk.Label(
            card,
            text="SECURE\nPRIVATE\nEFFICIENT",
            justify="left",
            bg=PANEL,
            fg=MUTED,
            font=("Consolas", 9, "bold"),
        ).pack(anchor="w", padx=12, pady=(2, 12))

    def _clear_content(self) -> None:
        for child in self.content.winfo_children():
            child.destroy()

    def _navigate(self, key: str) -> None:
        self._clear_content()
        for k, button in self.nav_buttons.items():
            active = k == key
            button.configure(bg=GREEN if active else PANEL, fg=BLACK if active else WHITE)

        if key == "message_generator":
            self._build_message_view()
        elif key == "authorized_groups":
            self._build_groups_view()
        elif key == "saved_packs":
            self._build_info_view("SAVED PACKS", "Saved message packs are stored locally in the SQLite database.")
        elif key == "scheduler":
            self._build_info_view(
                "SCHEDULER",
                f"Configured interval: {self.settings.interval_minutes} minutes\n"
                f"Configured cycle: {self.settings.cycle_hours} hours\n\n"
                "The scheduler component is available to the local application. "
                "Use the authorized transport configuration for any actual delivery.",
            )
        elif key == "settings":
            self._build_info_view(
                "SETTINGS",
                f"Variations: {self.settings.variation_count}\n"
                f"Interval: {self.settings.interval_minutes} minutes\n"
                f"Cycle: {self.settings.cycle_hours} hours",
            )
        elif key == "logs":
            self._build_info_view("LOGS", "Local application activity and status information.")
        elif key == "about":
            self._build_about()

    def _build_message_view(self) -> None:
        # Source panel
        source_panel = self._panel(self.content)
        source_panel.pack(fill="x", pady=(0, 10))

        heading = tk.Frame(source_panel, bg=PANEL)
        heading.pack(fill="x", padx=14, pady=(12, 8))
        self.source_heading = tk.Label(
            heading,
            text="01  •  ENTER YOUR MESSAGE",
            bg=PANEL,
            fg=WHITE,
            font=self.font_section,
        )
        self.source_heading.pack(side="left")

        self.source = tk.Text(
            source_panel,
            height=5,
            wrap="word",
            bg="#09100d",
            fg=WHITE,
            insertbackground=GREEN,
            selectbackground=GREEN_DARK,
            selectforeground=WHITE,
            font=("Segoe UI", 11),
            relief="flat",
            bd=0,
            padx=12,
            pady=10,
        )
        self.source.pack(fill="x", padx=14, pady=(0, 10))

        control = tk.Frame(source_panel, bg=PANEL)
        control.pack(fill="x", padx=14, pady=(0, 14))

        self.generate_button = self._button(
            control, "✦  GENERATE 24 VARIATIONS", self.generate, primary=True
        )
        self.generate_button.pack(side="left")

        self.status = tk.Label(
            control, text="READY", bg=PANEL, fg=GREEN, font=("Consolas", 9, "bold")
        )
        self.status.pack(side="right", padx=5)

        # Review panel
        review = self._panel(self.content)
        review.pack(fill="both", expand=True)

        top = tk.Frame(review, bg=PANEL)
        top.pack(fill="x", padx=14, pady=(12, 7))
        self.review_heading = tk.Label(
            top,
            text="02  •  REVIEW & EDIT VARIATIONS  (24)",
            bg=PANEL,
            fg=WHITE,
            font=self.font_section,
        )
        self.review_heading.pack(side="left")

        self._button(top, "☑  SELECT ALL", self.select_all).pack(side="right", padx=(5, 0))
        self._button(top, "□  CLEAR ALL", self.deselect_all).pack(side="right", padx=(5, 0))

        container = tk.Frame(review, bg=PANEL)
        container.pack(fill="both", expand=True, padx=14, pady=(0, 10))

        self.canvas = tk.Canvas(container, bg=PANEL, highlightthickness=0)
        scroll = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.frame = tk.Frame(self.canvas, bg=PANEL)

        self.frame.bind(
            "<Configure>",
            lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw", width=850)
        self.canvas.configure(yscrollcommand=scroll.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        bottom = tk.Frame(review, bg=PANEL)
        bottom.pack(fill="x", padx=14, pady=(0, 12))
        self._button(bottom, "▣  SAVE APPROVED PACK", self.save, primary=True).pack(side="right")

    def _build_groups_view(self) -> None:
        panel = self._panel(self.content)
        panel.pack(fill="both", expand=True)

        tk.Label(
            panel, text="AUTHORIZED SIGNAL GROUPS",
            bg=PANEL, fg=WHITE, font=self.font_title
        ).pack(anchor="w", padx=18, pady=(18, 3))
        tk.Label(
            panel,
            text="Only groups explicitly configured in local storage are shown here.",
            bg=PANEL, fg=MUTED, font=self.font_body
        ).pack(anchor="w", padx=18, pady=(0, 15))

        form = tk.Frame(panel, bg=PANEL)
        form.pack(fill="x", padx=18, pady=(0, 12))

        tk.Label(form, text="NAME", bg=PANEL, fg=MUTED, font=self.font_small).grid(row=0, column=0, sticky="w")
        tk.Label(form, text="GROUP ID", bg=PANEL, fg=MUTED, font=self.font_small).grid(row=0, column=1, sticky="w", padx=(12, 0))

        self.group_name = tk.Entry(
            form, width=25, bg="#09100d", fg=WHITE, insertbackground=GREEN,
            relief="flat", font=self.font_body
        )
        self.group_name.grid(row=1, column=0, sticky="ew", pady=5)

        self.group_id = tk.Entry(
            form, width=38, bg="#09100d", fg=WHITE, insertbackground=GREEN,
            relief="flat", font=self.font_body
        )
        self.group_id.grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=5)

        self._button(form, "ï¼‹ ADD GROUP", self.add_group, primary=True).grid(
            row=1, column=2, padx=12, pady=5
        )
        self._button(form, "REMOVE SELECTED", self.remove_selected_groups).grid(
            row=1, column=3, pady=5
        )
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=2)

        self.groups_frame = tk.Frame(panel, bg=PANEL)
        self.groups_frame.pack(fill="both", expand=True, padx=18, pady=8)

    def _build_info_view(self, title: str, body: str) -> None:
        panel = self._panel(self.content)
        panel.pack(fill="both", expand=True)
        tk.Label(panel, text=title, bg=PANEL, fg=WHITE, font=self.font_title).pack(
            anchor="w", padx=20, pady=(20, 8)
        )
        tk.Label(
            panel, text=body, justify="left", anchor="nw",
            bg=PANEL, fg=MUTED, font=self.font_body
        ).pack(fill="x", padx=20, pady=10)

    def _build_about(self) -> None:
        panel = self._panel(self.content)
        panel.pack(fill="both", expand=True)

        tk.Label(panel, text="SIGNAL BOT", bg=PANEL, fg=WHITE,
                 font=("Segoe UI", 30, "bold")).pack(pady=(50, 0))
        tk.Label(panel, text="AUTO RESPONDER", bg=PANEL, fg=GREEN,
                 font=("Segoe UI", 18, "bold")).pack()
        tk.Label(panel, text="v2.0.0", bg=PANEL, fg=MUTED,
                 font=self.font_body).pack(pady=8)

        tk.Label(
            panel,
            text="Built by SecMod aka Security101",
            bg=PANEL, fg=GREEN, font=("Segoe UI", 13, "bold")
        ).pack(pady=(25, 6))
        tk.Label(
            panel,
            text="Professional local control panel for message preparation,\n"
                 "review, approved-pack storage, and authorized group configuration.",
            bg=PANEL, fg=WHITE, justify="center", font=self.font_body
        ).pack(pady=6)

        tk.Label(
            panel,
            text="Telegram",
            bg=PANEL, fg=MUTED, font=("Segoe UI", 10, "bold")
        ).pack(pady=(28, 4))

        links = tk.Frame(panel, bg=PANEL)
        links.pack()
        for handle in ("@RU_LAPSUS", "@CODERX0981"):
            self._button(
                links, handle,
                lambda h=handle: webbrowser.open("https://t.me/" + h.lstrip("@"))
            ).pack(side="left", padx=5)

    def _build_footer(self) -> None:
        footer = tk.Frame(self, bg=BLACK, height=34)
        footer.pack(fill="x", padx=18, pady=(0, 8))
        footer.pack_propagate(False)

        tk.Label(
            footer,
            text="v2.0.0",
            bg=BLACK,
            fg=GREEN,
            font=("Consolas", 9, "bold"),
        ).pack(side="left")

        tk.Label(
            footer,
            text="   Built by SecMod aka Security101",
            bg=BLACK,
            fg=MUTED,
            font=("Segoe UI", 9),
        ).pack(side="left")

        tk.Label(
            footer,
            text=(
                f"Interval: {self.settings.interval_minutes} min   •   "
                f"Cycle: {self.settings.cycle_hours} h   •   "
                f"Variations: {self.settings.variation_count}"
            ),
            bg=BLACK,
            fg=MUTED,
            font=("Consolas", 9),
        ).pack(side="right")

    def refresh_groups(self) -> None:
        if not hasattr(self, "groups_frame"):
            return

        for child in self.groups_frame.winfo_children():
            child.destroy()

        self.group_vars.clear()
        groups = self.storage.get_groups()

        if not groups:
            tk.Label(
                self.groups_frame,
                text="NO AUTHORIZED GROUPS CONFIGURED",
                bg=PANEL, fg=MUTED, font=self.font_body
            ).pack(anchor="w", pady=12)
            return

        for group in groups:
            row = tk.Frame(self.groups_frame, bg=PANEL_2, highlightbackground=BORDER,
                           highlightthickness=1)
            row.pack(fill="x", pady=4)

            enabled = tk.BooleanVar(value=group["enabled"])
            self.group_vars[group["group_id"]] = enabled

            cb = tk.Checkbutton(
                row,
                text=group["name"],
                variable=enabled,
                command=lambda gid=group["group_id"], var=enabled: self.toggle_group(gid, var),
                bg=PANEL_2, fg=WHITE, selectcolor=BLACK,
                activebackground=PANEL_2, activeforeground=WHITE,
                font=("Segoe UI", 10, "bold"),
            )
            cb.pack(side="left", padx=10, pady=9)

            tk.Label(
                row, text=f"ID: {group['group_id']}",
                bg=PANEL_2, fg=MUTED, font=self.font_mono
            ).pack(side="left", padx=12)

            state = "ENABLED" if group["enabled"] else "DISABLED"
            tk.Label(
                row, text=state,
                bg=PANEL_2, fg=GREEN if group["enabled"] else RED,
                font=("Consolas", 9, "bold")
            ).pack(side="right", padx=12)

    def add_group(self) -> None:
        name = self.group_name.get().strip()
        group_id = self.group_id.get().strip()

        if not name or not group_id:
            messagebox.showwarning("Missing information", "Enter both a group name and group ID.")
            return

        try:
            self.storage.add_group(name, group_id)
        except Exception as exc:
            messagebox.showerror("Could not add group", str(exc))
            return

        self.group_name.delete(0, "end")
        self.group_id.delete(0, "end")
        self.refresh_groups()
        self.status.config(text=f"ADDED GROUP: {name}") if hasattr(self, "status") else None

    def toggle_group(self, group_id: str, variable: tk.BooleanVar) -> None:
        enabled = variable.get()
        self.storage.set_group_enabled(group_id, enabled)
        self.refresh_groups()
        if hasattr(self, "status"):
            self.status.config(text=f"GROUP {'ENABLED' if enabled else 'DISABLED'}: {group_id}")

    def remove_selected_groups(self) -> None:
        # A checked row means enabled. Removal is intentionally limited to
        # unchecked/disabled groups, matching the existing application logic.
        selected = [
            group_id for group_id, variable in self.group_vars.items()
            if not variable.get()
        ]

        if not selected:
            messagebox.showinfo("Nothing selected", "Disable the groups you want to remove.")
            return

        if not messagebox.askyesno(
            "Confirm removal", f"Remove {len(selected)} disabled group(s)?"
        ):
            return

        for group_id in selected:
            self.storage.remove_group(group_id)

        self.refresh_groups()
        if hasattr(self, "status"):
            self.status.config(text=f"REMOVED {len(selected)} GROUP(S)")

    def generate(self) -> None:
        source = self.source.get("1.0", "end").strip()

        if not source:
            messagebox.showwarning("Missing message", "Enter today's message first.")
            return

        for child in self.frame.winfo_children():
            child.destroy()
        self.vars.clear()

        variations = generate_variations(source, self.settings.variation_count)

        for number, message in enumerate(variations, 1):
            row = tk.Frame(
                self.frame, bg=PANEL_2, highlightbackground=BORDER,
                highlightthickness=1, pady=3
            )
            row.pack(fill="x", padx=2, pady=3)

            approved = tk.BooleanVar(value=True)
            tk.Checkbutton(
                row, text=f"{number:02d}", variable=approved,
                bg=PANEL_2, fg=GREEN, selectcolor=BLACK,
                activebackground=PANEL_2, activeforeground=WHITE,
                font=("Consolas", 10, "bold")
            ).pack(side="left", padx=6)

            box = tk.Text(
                row, height=2, wrap="word",
                bg="#09100d", fg=WHITE, insertbackground=GREEN,
                selectbackground=GREEN_DARK, selectforeground=WHITE,
                font=self.font_body, relief="flat", bd=0, padx=8, pady=5
            )
            box.insert("1.0", message)
            box.pack(side="left", fill="x", expand=True, padx=(0, 6), pady=3)

            self.vars.append((approved, box))

        self.status.config(text=f"{len(variations)} VARIATIONS READY")

    def select_all(self) -> None:
        for approved, _ in self.vars:
            approved.set(True)

    def deselect_all(self) -> None:
        for approved, _ in self.vars:
            approved.set(False)

    def save(self) -> None:
        source = self.source.get("1.0", "end").strip()

        if not source or len(self.vars) != 24:
            messagebox.showwarning("Nothing to save", "Generate 24 variations first.")
            return

        approved_text: list[str] = []
        for approved, box in self.vars:
            if approved.get():
                text = box.get("1.0", "end").strip()
                if text:
                    approved_text.append(text)

        if len(approved_text) != 24:
            messagebox.showwarning(
                "24 approvals required",
                "Please approve all 24 variations before saving."
            )
            return

        pack_id = self.storage.save_pack(source, approved_text)
        self.status.config(text=f"SAVED PACK #{pack_id} • 24 VARIATIONS")
        messagebox.showinfo("Saved", "Today's 24-message pack has been saved.")

    def _language_changed(self, selection: str) -> None:
        name = selection.split(" ", 1)[1] if " " in selection else selection
        self.current_language = name
        data = LANGUAGES.get(name, LANGUAGES["English"])

        # Update navigation labels without reconstructing the working state.
        keys = [
            "message_generator", "saved_packs", "authorized_groups",
            "scheduler", "settings", "logs", "about"
        ]
        icons = ["💬", "▤", "♣", "◷", "⚙", "▣", "ⓘ"]
        for (key, icon) in zip(keys, icons):
            if key in self.nav_buttons:
                self.nav_buttons[key].configure(
                    text=f"{icon}   {data[key]}"
                )

        def widget_alive(widget) -> bool:
            try:
                return bool(widget.winfo_exists())
            except (tk.TclError, AttributeError):
                return False

        if hasattr(self, "source_heading") and widget_alive(self.source_heading):
            self.source_heading.configure(
                text=f"01  •  {data['today_message'].upper()}"
            )

        if hasattr(self, "review_heading") and widget_alive(self.review_heading):
            self.review_heading.configure(
                text=f"02  •  {data['message_variations'].upper()}  (24)"
            )

        if hasattr(self, "generate_button") and widget_alive(self.generate_button):
            self.generate_button.configure(
                text=f"✦  {data['generate'].upper()}"
            )

        if hasattr(self, "status") and widget_alive(self.status):
            self.status.configure(text=data["ready"].upper())


def main() -> None:
    App().mainloop()


if __name__ == "__main__":
    main()
