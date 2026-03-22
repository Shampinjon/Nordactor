import json
import os

from PySide6.QtCore import QTimer, Qt, QVariantAnimation
from PySide6.QtGui import QAction, QKeySequence, QTextCursor, QFont, QPalette, QColor
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QStackedWidget,
    QComboBox,
    QFormLayout,
    QFrame,
    QToolButton,
)


CONFIG_FILE = "config.json"


TRANSLATIONS = {
    "en": {
        "app_name": "Nordactor",
        "app_description": "Write something...",
        "waiting": "Waiting for action...",
        "saved": "Saved",
        "file_opened": "File opened",
        "settings_opened": "Settings opened",
        "settings_saved": "Settings saved",
        "untitled": "Untitled.txt",

        "menu_file": "File",
        "menu_help": "Help",
        "new": "New",
        "open": "Open...",
        "save": "Save",
        "save_as": "Save As...",
        "settings": "Settings",
        "close_tab": "Close Tab",
        "exit": "Exit",
        "about": "About",

        "settings_title": "Settings",
        "settings_subtitle": "Choose interface theme and language",
        "theme": "Theme",
        "language": "Language",
        "back": "Back",

        "theme_system": "System",
        "theme_light": "Light",
        "theme_dark": "Dark",
        "theme_oled": "OLED",

        "language_en": "English",
        "language_ru": "Русский",

        "open_file_title": "Open file",
        "save_file_title": "Save file as",
        "text_files_filter": "Text files (*.txt);;All files (*)",

        "unsaved_title": "Unsaved file",
        "unsaved_message": "File is not saved. Save changes?",

        "error_title": "Error",
        "open_error": "Failed to open file:",
        "save_error": "Failed to save file:",

        "warning_title": "Warning",
        "config_save_error": "Failed to save settings:",

        "about_title": "About",
        "about_message": "Nordactor\nA simple text editor.",
    },
    "ru": {
        "app_name": "Nordactor",
        "app_description": "Напишите что-нибудь...",
        "waiting": "Жду действие...",
        "saved": "Сохранено",
        "file_opened": "Файл открыт",
        "settings_opened": "Открыты настройки",
        "settings_saved": "Настройки сохранены",
        "untitled": "Новый_документ.txt",

        "menu_file": "Файл",
        "menu_help": "Справка",
        "new": "Новый",
        "open": "Открыть...",
        "save": "Сохранить",
        "save_as": "Сохранить как...",
        "settings": "Настройки",
        "close_tab": "Закрыть вкладку",
        "exit": "Выход",
        "about": "О программе",

        "settings_title": "Настройки",
        "settings_subtitle": "Выбери тему интерфейса и язык",
        "theme": "Тема",
        "language": "Язык",
        "back": "Назад",

        "theme_system": "Системная",
        "theme_light": "Светлая",
        "theme_dark": "Тёмная",
        "theme_oled": "OLED",

        "language_en": "English",
        "language_ru": "Русский",

        "open_file_title": "Открыть файл",
        "save_file_title": "Сохранить файл как",
        "text_files_filter": "Текстовые файлы (*.txt);;Все файлы (*)",

        "unsaved_title": "Несохранённый файл",
        "unsaved_message": "Файл не сохранён. Сохранить изменения?",

        "error_title": "Ошибка",
        "open_error": "Не удалось открыть файл:",
        "save_error": "Не удалось сохранить файл:",

        "warning_title": "Предупреждение",
        "config_save_error": "Не удалось сохранить настройки:",

        "about_title": "О программе",
        "about_message": "Nordactor\nПростой текстовый редактор.",
    },
}


THEME_KEYS = ["system", "light", "dark", "oled"]
LANGUAGE_KEYS = ["en", "ru"]


class EditorTab(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path = None

        self.setPlaceholderText("")
        self.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        self.setFont(QFont("DejaVu Sans Mono", 12))

    def get_display_name(self, t_func):
        if self.file_path:
            return os.path.basename(self.file_path)
        return t_func("untitled")

    def is_modified(self):
        return self.document().isModified()


class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("SettingsPage")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)

        self.title_label = QLabel()
        self.title_label.setObjectName("SettingsTitle")

        self.subtitle_label = QLabel()
        self.subtitle_label.setObjectName("SettingsSubtitle")

        self.card = QFrame()
        self.card.setObjectName("SettingsCard")

        self.form_layout = QFormLayout(self.card)
        self.form_layout.setContentsMargins(20, 20, 20, 20)
        self.form_layout.setSpacing(14)

        self.theme_label = QLabel()
        self.language_label = QLabel()

        self.theme_combo = QComboBox()
        self.language_combo = QComboBox()

        self.form_layout.addRow(self.theme_label, self.theme_combo)
        self.form_layout.addRow(self.language_label, self.language_combo)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.back_button = QPushButton()
        self.save_button = QPushButton()

        buttons_layout.addWidget(self.back_button)
        buttons_layout.addWidget(self.save_button)

        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.subtitle_label)
        main_layout.addWidget(self.card)
        main_layout.addStretch()
        main_layout.addLayout(buttons_layout)

    def populate_theme_combo(self, t_func, current_theme):
        self.theme_combo.blockSignals(True)
        self.theme_combo.clear()
        self.theme_combo.addItem(t_func("theme_system"), "system")
        self.theme_combo.addItem(t_func("theme_light"), "light")
        self.theme_combo.addItem(t_func("theme_dark"), "dark")
        self.theme_combo.addItem(t_func("theme_oled"), "oled")

        index = self.theme_combo.findData(current_theme)
        if index != -1:
            self.theme_combo.setCurrentIndex(index)
        self.theme_combo.blockSignals(False)

    def populate_language_combo(self, t_func, current_language):
        self.language_combo.blockSignals(True)
        self.language_combo.clear()
        self.language_combo.addItem(t_func("language_en"), "en")
        self.language_combo.addItem(t_func("language_ru"), "ru")

        index = self.language_combo.findData(current_language)
        if index != -1:
            self.language_combo.setCurrentIndex(index)
        self.language_combo.blockSignals(False)

    def refresh_texts(self, t_func, current_theme, current_language):
        self.title_label.setText(t_func("settings_title"))
        self.subtitle_label.setText(t_func("settings_subtitle"))
        self.theme_label.setText(f'{t_func("theme")}:')
        self.language_label.setText(f'{t_func("language")}:')
        self.back_button.setText(t_func("back"))
        self.save_button.setText(t_func("save"))
        self.populate_theme_combo(t_func, current_theme)
        self.populate_language_combo(t_func, current_language)


class NordactorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_theme = "system"
        self.current_language = "en"
        self.theme_animation = None

        self.setWindowTitle("Nordactor")
        self.resize(1100, 720)

        self.status_timer = QTimer(self)
        self.status_timer.setSingleShot(True)
        self.status_timer.timeout.connect(self.reset_status_message)

        self.stack = QStackedWidget()

        self.editor_page = QWidget()
        self.editor_layout = QVBoxLayout(self.editor_page)
        self.editor_layout.setContentsMargins(0, 0, 0, 0)
        self.editor_layout.setSpacing(0)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.update_window_title)

        self.new_tab_button = QToolButton()
        self.new_tab_button.setText("+")
        self.new_tab_button.setCursor(Qt.PointingHandCursor)
        self.new_tab_button.clicked.connect(self.new_tab)
        self.tab_widget.setCornerWidget(self.new_tab_button, Qt.TopRightCorner)

        self.editor_layout.addWidget(self.tab_widget)

        self.settings_page = SettingsPage()
        self.settings_page.save_button.clicked.connect(self.save_settings)
        self.settings_page.back_button.clicked.connect(self.show_editor_page)

        self.stack.addWidget(self.editor_page)
        self.stack.addWidget(self.settings_page)

        self.setCentralWidget(self.stack)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.load_config()
        self.create_menu()
        self.apply_theme(self.current_theme)
        self.refresh_ui_texts()
        self.new_tab()

    def t(self, key):
        return TRANSLATIONS[self.current_language].get(key, key)

    def create_menu(self):
        self.menuBar().clear()

        self.file_menu = self.menuBar().addMenu(self.t("menu_file"))
        self.help_menu = self.menuBar().addMenu(self.t("menu_help"))

        self.new_action = QAction(self.t("new"), self)
        self.new_action.setShortcut(QKeySequence("Ctrl+N"))
        self.new_action.triggered.connect(self.new_tab)
        self.file_menu.addAction(self.new_action)

        self.open_action = QAction(self.t("open"), self)
        self.open_action.setShortcut(QKeySequence("Ctrl+O"))
        self.open_action.triggered.connect(self.open_file)
        self.file_menu.addAction(self.open_action)

        self.save_action = QAction(self.t("save"), self)
        self.save_action.setShortcut(QKeySequence("Ctrl+S"))
        self.save_action.triggered.connect(self.save_file)
        self.file_menu.addAction(self.save_action)

        self.save_as_action = QAction(self.t("save_as"), self)
        self.save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.save_as_action.triggered.connect(self.save_file_as)
        self.file_menu.addAction(self.save_as_action)

        self.file_menu.addSeparator()

        self.settings_action = QAction(self.t("settings"), self)
        self.settings_action.triggered.connect(self.show_settings_page)
        self.file_menu.addAction(self.settings_action)

        self.file_menu.addSeparator()

        self.close_tab_action = QAction(self.t("close_tab"), self)
        self.close_tab_action.setShortcut(QKeySequence("Ctrl+W"))
        self.close_tab_action.triggered.connect(self.close_current_tab)
        self.file_menu.addAction(self.close_tab_action)

        self.file_menu.addSeparator()

        self.exit_action = QAction(self.t("exit"), self)
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)

        self.about_action = QAction(self.t("about"), self)
        self.about_action.triggered.connect(self.show_about)
        self.help_menu.addAction(self.about_action)

    def refresh_ui_texts(self):
        self.create_menu()
        self.settings_page.refresh_texts(self.t, self.current_theme, self.current_language)

        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if isinstance(widget, EditorTab):
                widget.setPlaceholderText(self.t("app_description"))
                self.update_tab_title(widget)

        self.update_window_title()
        self.reset_status_message()

    def is_system_dark(self):
        palette = QApplication.palette()
        window_color = palette.color(QPalette.Window)
        return window_color.lightness() < 128

    def resolve_theme(self, theme_key):
        if theme_key == "system":
            return "dark" if self.is_system_dark() else "light"
        return theme_key

    def get_theme_colors(self, theme_key):
        resolved = self.resolve_theme(theme_key)

        if resolved == "dark":
            return {"bg": "#262626", "text": "#f3de8a"}

        if resolved == "oled":
            return {"bg": "#000000", "text": "#f3de47"}

        return {"bg": "#ffffff", "text": "#111111"}

    def interpolate_color(self, start_color, end_color, progress):
        r = int(start_color.red() + (end_color.red() - start_color.red()) * progress)
        g = int(start_color.green() + (end_color.green() - start_color.green()) * progress)
        b = int(start_color.blue() + (end_color.blue() - start_color.blue()) * progress)
        return QColor(r, g, b)

    def get_theme_stylesheet(self, theme_key):
        resolved = self.resolve_theme(theme_key)

        if resolved == "dark":
            return """
                QMainWindow {
                    background: #252525;
                }

                QMenuBar {
                    background: #2d2d2d;
                    color: #f0f0f0;
                    border-bottom: 1px solid #3b3b3b;
                }

                QMenuBar::item {
                    background: transparent;
                    padding: 6px 10px;
                }

                QMenuBar::item:selected {
                    background: #3a3a3a;
                }

                QMenu {
                    background: #2c2c2c;
                    color: #f0f0f0;
                    border: 1px solid #444444;
                }

                QMenu::item:selected {
                    background: #3a3a3a;
                }

                QTabWidget::pane {
                    border: 1px solid #3d3d3d;
                    background: #2a2a2a;
                }

                QTabBar::tab {
                    background: #313131;
                    color: #dddddd;
                    border: 1px solid #444444;
                    padding: 7px 14px;
                    margin-right: 2px;
                }

                QTabBar::tab:selected {
                    background: #3a3a3a;
                    color: #f5e6a8;
                }

                QPlainTextEdit {
                    background: #262626;
                    color: #f3de8a;
                    border: none;
                    padding: 14px;
                    selection-background-color: #5c5c5c;
                }

                QStatusBar {
                    background: #2d2d2d;
                    color: #d0d0d0;
                    border-top: 1px solid #3d3d3d;
                }

                #SettingsPage {
                    background: #252525;
                }

                #SettingsTitle {
                    color: #f0f0f0;
                    font-size: 24px;
                    font-weight: 700;
                }

                #SettingsSubtitle {
                    color: #b8b8b8;
                    font-size: 13px;
                }

                #SettingsCard {
                    background: #2f2f2f;
                    border: 1px solid #434343;
                    border-radius: 12px;
                }

                QLabel {
                    color: #e8e8e8;
                }

                QComboBox {
                    background: #3a3a3a;
                    color: #f0f0f0;
                    border: 1px solid #4a4a4a;
                    border-radius: 8px;
                    padding: 8px 10px;
                    min-width: 180px;
                }

                QComboBox QAbstractItemView {
                    background: #2f2f2f;
                    color: #f0f0f0;
                    border: 1px solid #4a4a4a;
                    selection-background-color: #444444;
                }

                QPushButton {
                    background: #3b3b3b;
                    color: #f0f0f0;
                    border: 1px solid #4c4c4c;
                    border-radius: 8px;
                    padding: 8px 16px;
                    min-width: 100px;
                }

                QPushButton:hover {
                    background: #474747;
                }

                QPushButton:pressed {
                    background: #555555;
                }

                QToolButton {
                    background: #3b3b3b;
                    color: #f0f0f0;
                    border: 1px solid #4c4c4c;
                    border-radius: 6px;
                    padding: 4px 10px;
                    margin: 4px;
                    font-size: 16px;
                    font-weight: 600;
                }

                QToolButton:hover {
                    background: #474747;
                }

                QToolButton:pressed {
                    background: #555555;
                }
            """

        if resolved == "oled":
            return """
                QMainWindow {
                    background: #000000;
                }

                QMenuBar {
                    background: #000000;
                    color: #f3de47;
                    border-bottom: 1px solid #202020;
                }

                QMenuBar::item {
                    background: transparent;
                    padding: 6px 10px;
                }

                QMenuBar::item:selected {
                    background: #111111;
                }

                QMenu {
                    background: #000000;
                    color: #f3de47;
                    border: 1px solid #222222;
                }

                QMenu::item:selected {
                    background: #111111;
                }

                QTabWidget::pane {
                    border: 1px solid #222222;
                    background: #000000;
                }

                QTabBar::tab {
                    background: #000000;
                    color: #b9b9b9;
                    border: none;
                    border-bottom: 1px solid #111111;
                    padding: 7px 14px;
                    margin-right: 2px;
                }

                QTabBar::tab:selected {
                    color: #f3de47;
                    border-bottom: 1px solid #7a7a7a;
                }

                QPlainTextEdit {
                    background: #000000;
                    color: #f3de47;
                    border: none;
                    padding: 14px;
                    selection-background-color: #333333;
                }

                QStatusBar {
                    background: #000000;
                    color: #9c9c9c;
                    border-top: 1px solid #1a1a1a;
                }

                #SettingsPage {
                    background: #000000;
                }

                #SettingsTitle {
                    color: #f3de47;
                    font-size: 24px;
                    font-weight: 700;
                }

                #SettingsSubtitle {
                    color: #8d8d8d;
                    font-size: 13px;
                }

                #SettingsCard {
                    background: #050505;
                    border: 1px solid #1f1f1f;
                    border-radius: 12px;
                }

                QLabel {
                    color: #e1cf55;
                }

                QComboBox {
                    background: #0c0c0c;
                    color: #f3de47;
                    border: 1px solid #2a2a2a;
                    border-radius: 8px;
                    padding: 8px 10px;
                    min-width: 180px;
                }

                QComboBox QAbstractItemView {
                    background: #0a0a0a;
                    color: #f3de47;
                    border: 1px solid #2a2a2a;
                    selection-background-color: #161616;
                }

                QPushButton {
                    background: #0c0c0c;
                    color: #f3de47;
                    border: 1px solid #2a2a2a;
                    border-radius: 8px;
                    padding: 8px 16px;
                    min-width: 100px;
                }

                QPushButton:hover {
                    background: #141414;
                }

                QPushButton:pressed {
                    background: #1b1b1b;
                }

                QToolButton {
                    background: #0c0c0c;
                    color: #f3de47;
                    border: 1px solid #2a2a2a;
                    border-radius: 6px;
                    padding: 4px 10px;
                    margin: 4px;
                    font-size: 16px;
                    font-weight: 600;
                }

                QToolButton:hover {
                    background: #141414;
                }

                QToolButton:pressed {
                    background: #1b1b1b;
                }
            """

        return """
            QMainWindow {
                background: #f6f6f6;
            }

            QMenuBar {
                background: #ececec;
                color: #111111;
                border-bottom: 1px solid #cfcfcf;
            }

            QMenuBar::item {
                background: transparent;
                padding: 6px 10px;
            }

            QMenuBar::item:selected {
                background: #dddddd;
            }

            QMenu {
                background: #ffffff;
                color: #111111;
                border: 1px solid #cfcfcf;
            }

            QMenu::item:selected {
                background: #e9e9e9;
            }

            QTabWidget::pane {
                border: 1px solid #bfbfbf;
                background: #ffffff;
            }

            QTabBar::tab {
                background: #ebebeb;
                color: #111111;
                border: 1px solid #bfbfbf;
                padding: 7px 14px;
                margin-right: 2px;
            }

            QTabBar::tab:selected {
                background: #ffffff;
            }

            QPlainTextEdit {
                background: #ffffff;
                color: #111111;
                border: none;
                padding: 14px;
                selection-background-color: #cfe3ff;
            }

            QStatusBar {
                background: #f0f0f0;
                color: #333333;
                border-top: 1px solid #cfcfcf;
            }

            #SettingsPage {
                background: #f6f6f6;
            }

            #SettingsTitle {
                color: #111111;
                font-size: 24px;
                font-weight: 700;
            }

            #SettingsSubtitle {
                color: #666666;
                font-size: 13px;
            }

            #SettingsCard {
                background: #ffffff;
                border: 1px solid #d2d2d2;
                border-radius: 12px;
            }

            QLabel {
                color: #222222;
            }

            QComboBox {
                background: #ffffff;
                color: #111111;
                border: 1px solid #c8c8c8;
                border-radius: 8px;
                padding: 8px 10px;
                min-width: 180px;
            }

            QComboBox QAbstractItemView {
                background: #ffffff;
                color: #111111;
                border: 1px solid #c8c8c8;
                selection-background-color: #e8e8e8;
            }

            QPushButton {
                background: #f3f3f3;
                color: #111111;
                border: 1px solid #cfcfcf;
                border-radius: 8px;
                padding: 8px 16px;
                min-width: 100px;
            }

            QPushButton:hover {
                background: #e8e8e8;
            }

            QPushButton:pressed {
                background: #dddddd;
            }

            QToolButton {
                background: #f3f3f3;
                color: #111111;
                border: 1px solid #cfcfcf;
                border-radius: 6px;
                padding: 4px 10px;
                margin: 4px;
                font-size: 16px;
                font-weight: 600;
            }

            QToolButton:hover {
                background: #e8e8e8;
            }

            QToolButton:pressed {
                background: #dddddd;
            }
        """

    def apply_theme(self, theme_key):
        self.current_theme = theme_key
        self.setStyleSheet(self.get_theme_stylesheet(theme_key))

    def animate_theme_change(self, new_theme_key):
        old_colors = self.get_theme_colors(self.current_theme)
        new_colors = self.get_theme_colors(new_theme_key)

        start_bg = QColor(old_colors["bg"])
        end_bg = QColor(new_colors["bg"])
        start_text = QColor(old_colors["text"])
        end_text = QColor(new_colors["text"])

        if self.theme_animation:
            self.theme_animation.stop()

        self.theme_animation = QVariantAnimation(self)
        self.theme_animation.setDuration(280)
        self.theme_animation.setStartValue(0.0)
        self.theme_animation.setEndValue(1.0)

        def on_value_changed(value):
            bg = self.interpolate_color(start_bg, end_bg, value)
            text = self.interpolate_color(start_text, end_text, value)

            for i in range(self.tab_widget.count()):
                widget = self.tab_widget.widget(i)
                if isinstance(widget, EditorTab):
                    widget.setStyleSheet(f"""
                        QPlainTextEdit {{
                            background: {bg.name()};
                            color: {text.name()};
                            border: none;
                            padding: 14px;
                        }}
                    """)

        def on_finished():
            self.apply_theme(new_theme_key)
            for i in range(self.tab_widget.count()):
                widget = self.tab_widget.widget(i)
                if isinstance(widget, EditorTab):
                    widget.setStyleSheet("")

        self.theme_animation.valueChanged.connect(on_value_changed)
        self.theme_animation.finished.connect(on_finished)
        self.theme_animation.start()

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return

        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
        except Exception:
            return

        theme = data.get("theme")
        language = data.get("language")

        if theme in THEME_KEYS:
            self.current_theme = theme

        if language in LANGUAGE_KEYS:
            self.current_language = language

    def save_config(self):
        data = {
            "theme": self.current_theme,
            "language": self.current_language,
        }

        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except Exception as error:
            QMessageBox.warning(
                self,
                self.t("warning_title"),
                f'{self.t("config_save_error")}\n{error}'
            )

    def get_current_editor(self):
        widget = self.tab_widget.currentWidget()
        if isinstance(widget, EditorTab):
            return widget
        return None

    def new_tab(self):
        editor = EditorTab()
        editor.setPlaceholderText(self.t("app_description"))

        index = self.tab_widget.addTab(editor, editor.get_display_name(self.t))
        self.tab_widget.setCurrentIndex(index)

        editor.textChanged.connect(lambda ed=editor: self.on_text_changed(ed))
        self.update_tab_title(editor)
        self.update_window_title()
        self.reset_status_message()

    def on_text_changed(self, editor):
        self.update_tab_title(editor)
        self.update_window_title()

    def update_tab_title(self, editor):
        index = self.tab_widget.indexOf(editor)
        if index == -1:
            return

        title = editor.get_display_name(self.t)
        if editor.is_modified():
            title = f"{title} *"

        self.tab_widget.setTabText(index, title)

    def update_window_title(self):
        editor = self.get_current_editor()
        if not editor:
            self.setWindowTitle(self.t("app_name"))
            return

        title = editor.get_display_name(self.t)
        if editor.is_modified():
            title += " *"

        self.setWindowTitle(f"{title} — {self.t('app_name')}")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.t("open_file_title"),
            "",
            self.t("text_files_filter")
        )

        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
        except Exception as error:
            QMessageBox.critical(
                self,
                self.t("error_title"),
                f'{self.t("open_error")}\n{error}'
            )
            return

        editor = EditorTab()
        editor.setPlainText(content)
        editor.setPlaceholderText(self.t("app_description"))
        editor.file_path = file_path
        editor.document().setModified(False)

        index = self.tab_widget.addTab(editor, editor.get_display_name(self.t))
        self.tab_widget.setCurrentIndex(index)

        editor.textChanged.connect(lambda ed=editor: self.on_text_changed(ed))
        self.update_tab_title(editor)
        self.update_window_title()
        self.show_temporary_status(self.t("file_opened"))

        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        editor.setTextCursor(cursor)

    def save_file(self):
        editor = self.get_current_editor()
        if not editor:
            return False

        if editor.file_path is None:
            return self.save_file_as()

        return self.write_to_path(editor, editor.file_path)

    def save_file_as(self):
        editor = self.get_current_editor()
        if not editor:
            return False

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.t("save_file_title"),
            editor.get_display_name(self.t),
            self.t("text_files_filter")
        )

        if not file_path:
            return False

        success = self.write_to_path(editor, file_path)
        if success:
            editor.file_path = file_path
            self.update_tab_title(editor)
            self.update_window_title()

        return success

    def write_to_path(self, editor, file_path):
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(editor.toPlainText())
        except Exception as error:
            QMessageBox.critical(
                self,
                self.t("error_title"),
                f'{self.t("save_error")}\n{error}'
            )
            return False

        editor.document().setModified(False)
        self.update_tab_title(editor)
        self.update_window_title()
        self.show_temporary_status(self.t("saved"))
        return True

    def maybe_save(self, editor):
        if editor is None or not editor.is_modified():
            return True

        reply = QMessageBox.question(
            self,
            self.t("unsaved_title"),
            self.t("unsaved_message"),
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save
        )

        if reply == QMessageBox.Save:
            self.tab_widget.setCurrentWidget(editor)
            return self.save_file()
        if reply == QMessageBox.Cancel:
            return False
        return True

    def close_current_tab(self):
        current_index = self.tab_widget.currentIndex()
        if current_index != -1:
            self.close_tab(current_index)

    def close_tab(self, index):
        widget = self.tab_widget.widget(index)
        if not isinstance(widget, EditorTab):
            return

        if not self.maybe_save(widget):
            return

        self.tab_widget.removeTab(index)
        widget.deleteLater()

        if self.tab_widget.count() == 0:
            self.close()
            return

        self.update_window_title()
        self.reset_status_message()

    def show_about(self):
        QMessageBox.information(
            self,
            self.t("about_title"),
            self.t("about_message")
        )

    def show_temporary_status(self, message, duration_ms=2000):
        self.status_bar.showMessage(message)
        self.status_timer.start(duration_ms)

    def reset_status_message(self):
        self.status_bar.showMessage(self.t("waiting"))

    def show_settings_page(self):
        self.settings_page.refresh_texts(self.t, self.current_theme, self.current_language)
        self.stack.setCurrentWidget(self.settings_page)
        self.status_bar.showMessage(self.t("settings_opened"))

    def show_editor_page(self):
        self.stack.setCurrentWidget(self.editor_page)
        self.reset_status_message()

    def save_settings(self):
        selected_theme = self.settings_page.theme_combo.currentData()
        selected_language = self.settings_page.language_combo.currentData()

        language_changed = selected_language != self.current_language
        theme_changed = selected_theme != self.current_theme

        if language_changed:
            self.current_language = selected_language
            self.refresh_ui_texts()

        if theme_changed:
            self.animate_theme_change(selected_theme)
            self.current_theme = selected_theme
        else:
            self.apply_theme(self.current_theme)

        self.save_config()
        self.show_editor_page()
        self.show_temporary_status(self.t("settings_saved"))

    def closeEvent(self, event):
        for index in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(index)
            if isinstance(widget, EditorTab) and widget.is_modified():
                self.tab_widget.setCurrentIndex(index)
                if not self.maybe_save(widget):
                    event.ignore()
                    return

        event.accept()