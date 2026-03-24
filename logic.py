import json
import os
import urllib.request
import webbrowser
from PySide6.QtCore import QTimer, Qt, QVariantAnimation
from PySide6.QtGui import QAction, QKeySequence, QTextCursor, QTextDocument, QFont, QPalette, QColor, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QCheckBox,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QStatusBar,
    QTabBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QStackedWidget,
    QComboBox,
    QFormLayout,
    QFrame,
    QToolButton,
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
APP_VERSION = "1.1"
GITHUB_LATEST_URL = "https://api.github.com/repos/Shampinjon/Nordactor/releases/latest"
GITHUB_RELEASES_PAGE = "https://github.com/Shampinjon/Nordactor/releases"
TRANSLATIONS_FILE = os.path.join(BASE_DIR, "translations.json")


def load_translations():
    try:
        with open(TRANSLATIONS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {"en": {}, "ru": {}}


TRANSLATIONS = load_translations()


THEME_KEYS = ["system", "light", "dark", "oled"]
LANGUAGE_KEYS = ["en", "ru"]


class HoverTabBar(QTabBar):
    def __init__(self, restore_callback, max_title_length=22, parent=None):
        super().__init__(parent)
        self.restore_callback = restore_callback
        self.max_title_length = max_title_length
        self.hovered_index = -1
        self.hover_offset = 0
        self.hover_timer = QTimer(self)
        self.hover_timer.setInterval(140)
        self.hover_timer.timeout.connect(self.advance_hover_text)
        self.setMouseTracking(True)
        self.setExpanding(False)
        self.setElideMode(Qt.ElideRight)
        self.setUsesScrollButtons(True)

    def mouseMoveEvent(self, event):
        index = self.tabAt(event.pos())
        if index != self.hovered_index:
            self.set_hovered_index(index)
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.set_hovered_index(-1)
        super().leaveEvent(event)

    def wheelEvent(self, event):
        if self.count() == 0:
            super().wheelEvent(event)
            return

        delta = event.angleDelta().y()
        if delta == 0:
            super().wheelEvent(event)
            return

        current = self.currentIndex()
        if delta < 0 and current < self.count() - 1:
            self.setCurrentIndex(current + 1)
            event.accept()
            return
        if delta > 0 and current > 0:
            self.setCurrentIndex(current - 1)
            event.accept()
            return

        super().wheelEvent(event)

    def set_hovered_index(self, index):
        if self.hovered_index != -1:
            self.restore_callback(self.hovered_index)

        self.hovered_index = -1
        self.hover_timer.stop()
        self.hover_offset = 0

        if index < 0:
            return

        full_title = self.tabToolTip(index) or self.tabText(index)
        if len(full_title) <= self.max_title_length:
            return

        self.hovered_index = index
        self.hover_timer.start()

    def advance_hover_text(self):
        if self.hovered_index < 0 or self.hovered_index >= self.count():
            self.hover_timer.stop()
            return

        full_title = self.tabToolTip(self.hovered_index) or self.tabText(self.hovered_index)
        if len(full_title) <= self.max_title_length:
            self.hover_timer.stop()
            return

        padded = full_title + "   "
        visible = (padded * 2)[self.hover_offset:self.hover_offset + self.max_title_length]
        self.setTabText(self.hovered_index, visible)
        self.hover_offset = (self.hover_offset + 1) % len(padded)


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
        self.check_updates_box = QCheckBox()
        self.restore_tabs_box = QCheckBox()

        self.form_layout.addRow(self.theme_label, self.theme_combo)
        self.form_layout.addRow(self.language_label, self.language_combo)
        self.form_layout.addRow(self.check_updates_box)
        self.form_layout.addRow(self.restore_tabs_box)

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
        self.check_updates_box.setText(t_func("check_updates"))
        self.restore_tabs_box.setText(t_func("restore_tabs"))
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
        self.check_updates_enabled = True
        self.skipped_version = ""
        self.restore_tabs_enabled = True
        self.open_tabs_paths = []
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
        self.tab_bar = HoverTabBar(self.restore_single_tab_title, parent=self.tab_widget)
        self.tab_widget.setTabBar(self.tab_bar)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.setUsesScrollButtons(True)
        self.tab_widget.tabBar().setElideMode(Qt.ElideRight)
        self.tab_widget.tabBar().setExpanding(False)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.update_window_title)

        self.search_panel = self.create_search_panel()

        self.new_tab_button = QToolButton()
        self.new_tab_button.setText("+")
        self.new_tab_button.setCursor(Qt.PointingHandCursor)
        self.new_tab_button.clicked.connect(self.new_tab)
        self.tab_widget.setCornerWidget(self.new_tab_button, Qt.TopRightCorner)

        self.editor_layout.addWidget(self.search_panel)
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
        self.create_shortcuts()
        self.apply_theme(self.current_theme)
        self.refresh_ui_texts()
        self.restore_tabs_on_startup()
        QTimer.singleShot(1500, self.check_for_updates)

    def restore_tabs_on_startup(self):
        restored_any = False

        if self.restore_tabs_enabled:
            for file_path in self.open_tabs_paths:
                if self.open_file_from_path(file_path):
                    restored_any = True

        if not restored_any:
            self.new_tab()

    def get_open_tabs_paths(self):
        paths = []
        for index in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(index)
            if isinstance(widget, EditorTab) and widget.file_path:
                paths.append(widget.file_path)
        return paths
    def normalize_version(self, version: str):
        version = version.strip().lower()
        if version.startswith("v"):
            version = version[1:]
        try:
            return tuple(int(part) for part in version.split("."))
        except ValueError:
            return (0,)
        
    def open_file_from_path(self, file_path):
        if not file_path or not os.path.exists(file_path):
            return False

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
        except Exception:
            return False

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

        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        editor.setTextCursor(cursor)

        return True
    
    def fetch_latest_release(self):
        try:
            request = urllib.request.Request(
                GITHUB_LATEST_URL,
                headers={"User-Agent": "Nordactor"}
            )
            with urllib.request.urlopen(request, timeout=3) as response:
                data = json.loads(response.read().decode("utf-8"))
                tag_name = data.get("tag_name", "")
                html_url = data.get("html_url", GITHUB_RELEASES_PAGE)

                if not tag_name:
                    return None

                latest_version = tag_name.lstrip("v").strip()

                return {
                    "version": latest_version,
                    "url": html_url
                }
        except Exception:
            return None

    def check_for_updates(self):
        if not self.check_updates_enabled:
            return

        release_info = self.fetch_latest_release()
        if not release_info:
            return

        latest_version = release_info["version"]
        release_url = release_info["url"]

        if self.skipped_version == latest_version:
            return

        if self.normalize_version(latest_version) <= self.normalize_version(APP_VERSION):
            return

        self.show_update_dialog(latest_version, release_url)

    def show_update_dialog(self, latest_version, release_url):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(self.t("update_title"))
        msg_box.setText(
            self.t("update_message").format(
                current=APP_VERSION,
                latest=latest_version
            )
        )
        msg_box.setIcon(QMessageBox.Information)

        skip_button = msg_box.addButton(self.t("skip_version"), QMessageBox.ActionRole)
        github_button = msg_box.addButton(self.t("open_github"), QMessageBox.AcceptRole)
        later_button = msg_box.addButton(self.t("later"), QMessageBox.RejectRole)

        msg_box.exec()

        clicked = msg_box.clickedButton()

        if clicked == skip_button:
            self.skipped_version = latest_version
            self.save_config()
        elif clicked == github_button:
            webbrowser.open(release_url)

    def t(self, key):
        return TRANSLATIONS.get(self.current_language, {}).get(key, key)

    def create_shortcuts(self):
        QShortcut(QKeySequence("F3"), self, self.find_next)
        QShortcut(QKeySequence("Shift+F3"), self, self.find_previous)
        QShortcut(QKeySequence("Esc"), self, self.hide_search_panel)

    def create_search_panel(self):
        panel = QFrame()
        panel.setObjectName("SearchPanel")
        panel.hide()

        layout = QHBoxLayout(panel)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        self.search_label = QLabel()
        self.search_input = QLineEdit()
        self.search_input.returnPressed.connect(self.find_next)

        self.search_prev_button = QToolButton()
        self.search_prev_button.setText("↑")
        self.search_prev_button.clicked.connect(self.find_previous)

        self.search_next_button = QToolButton()
        self.search_next_button.setText("↓")
        self.search_next_button.clicked.connect(self.find_next)

        self.search_close_button = QToolButton()
        self.search_close_button.setText("✕")
        self.search_close_button.clicked.connect(self.hide_search_panel)

        layout.addWidget(self.search_label)
        layout.addWidget(self.search_input, 1)
        layout.addWidget(self.search_prev_button)
        layout.addWidget(self.search_next_button)
        layout.addWidget(self.search_close_button)

        return panel

    def toggle_search_panel(self):
        if self.search_panel.isVisible():
            self.hide_search_panel()
        else:
            self.search_panel.show()
            self.search_input.selectAll()

    def hide_search_panel(self):
        if self.search_panel.isVisible():
            self.search_panel.hide()
            self.reset_status_message()

    def _find_text(self, backward=False):
        editor = self.get_current_editor()
        if not editor:
            return

        query = self.search_input.text()
        if not query:
            return

        find_flags = QTextDocument.FindBackward if backward else QTextDocument.FindFlag(0)
        found = editor.find(query, find_flags)

        if not found:
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.End if backward else QTextCursor.Start)
            editor.setTextCursor(cursor)
            found = editor.find(query, find_flags)

        self.show_temporary_status(self.t("found") if found else self.t("not_found"), 1500)

    def find_next(self):
        self._find_text(backward=False)

    def find_previous(self):
        self._find_text(backward=True)

    def create_menu(self):
        self.menuBar().clear()

        self.file_menu = self.menuBar().addMenu(self.t("menu_file"))
        self.edit_menu = self.menuBar().addMenu(self.t("menu_edit"))
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

        self.edit_find_action = QAction(self.t("find"), self)
        self.edit_find_action.setShortcut(QKeySequence("Ctrl+F"))
        self.edit_find_action.triggered.connect(self.toggle_search_panel)
        self.edit_menu.addAction(self.edit_find_action)

        self.find_next_action = QAction(self.t("find_next"), self)
        self.find_next_action.setShortcut(QKeySequence("F3"))
        self.find_next_action.triggered.connect(self.find_next)
        self.edit_menu.addAction(self.find_next_action)

        self.find_previous_action = QAction(self.t("find_previous"), self)
        self.find_previous_action.setShortcut(QKeySequence("Shift+F3"))
        self.find_previous_action.triggered.connect(self.find_previous)
        self.edit_menu.addAction(self.find_previous_action)

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
        self.search_label.setText(f'{self.t("find")}:')
        self.search_input.setPlaceholderText(self.t("search"))
        self.search_prev_button.setToolTip(self.t("find_previous"))
        self.search_next_button.setToolTip(self.t("find_next"))
        self.search_close_button.setToolTip(self.t("close_search"))

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

                #SearchPanel {
                    background: #2d2d2d;
                    border-bottom: 1px solid #3d3d3d;
                }

                QLineEdit {
                    background: #3a3a3a;
                    color: #f0f0f0;
                    border: 1px solid #4a4a4a;
                    border-radius: 8px;
                    padding: 7px 10px;
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

                #SearchPanel {
                    background: #000000;
                    border-bottom: 1px solid #1a1a1a;
                }

                QLineEdit {
                    background: #0c0c0c;
                    color: #f3de47;
                    border: 1px solid #2a2a2a;
                    border-radius: 8px;
                    padding: 7px 10px;
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

            #SearchPanel {
                background: #f0f0f0;
                border-bottom: 1px solid #cfcfcf;
            }

            QLineEdit {
                background: #ffffff;
                color: #111111;
                border: 1px solid #c8c8c8;
                border-radius: 8px;
                padding: 7px 10px;
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
        check_updates = data.get("check_updates", True)
        skipped_version = data.get("skipped_version", "")
        restore_tabs = data.get("restore_tabs", True)
        open_tabs = data.get("open_tabs", [])

        if theme in THEME_KEYS:
            self.current_theme = theme

        if language in LANGUAGE_KEYS:
            self.current_language = language

        self.check_updates_enabled = bool(check_updates)
        self.skipped_version = str(skipped_version)
        self.restore_tabs_enabled = bool(restore_tabs)

        if isinstance(open_tabs, list):
            self.open_tabs_paths = [str(path) for path in open_tabs]

    def save_config(self):
        data = {
            "theme": self.current_theme,
            "language": self.current_language,
            "check_updates": self.check_updates_enabled,
            "skipped_version": self.skipped_version,
            "restore_tabs": self.restore_tabs_enabled,
            "open_tabs": self.get_open_tabs_paths() if self.restore_tabs_enabled else [],
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

    def shorten_tab_title(self, title, max_length=22):
        if len(title) <= max_length:
            return title
        return title[: max_length - 3] + "..."

    def restore_single_tab_title(self, index):
        if index < 0 or index >= self.tab_widget.count():
            return
        widget = self.tab_widget.widget(index)
        if isinstance(widget, EditorTab):
            self.update_tab_title(widget)

    def update_tab_title(self, editor):
        index = self.tab_widget.indexOf(editor)
        if index == -1:
            return

        title = editor.get_display_name(self.t)
        if editor.is_modified():
            title = f"{title} *"

        self.tab_widget.setTabToolTip(index, title)
        self.tab_widget.setTabText(index, self.shorten_tab_title(title))

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

        success = self.open_file_from_path(file_path)
        if success:
            self.show_temporary_status(self.t("file_opened"))
        else:
            QMessageBox.critical(
                self,
                self.t("error_title"),
                f'{self.t("open_error")}\n{file_path}'
            )
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
        self.settings_page.check_updates_box.setChecked(self.check_updates_enabled)
        self.settings_page.restore_tabs_box.setChecked(self.restore_tabs_enabled)
        self.stack.setCurrentWidget(self.settings_page)
        self.status_bar.showMessage(self.t("settings_opened"))

    def show_editor_page(self):
        self.stack.setCurrentWidget(self.editor_page)
        self.reset_status_message()

    def save_settings(self):
        selected_theme = self.settings_page.theme_combo.currentData()
        selected_restore_tabs = self.settings_page.restore_tabs_box.isChecked()
        selected_language = self.settings_page.language_combo.currentData()
        selected_check_updates = self.settings_page.check_updates_box.isChecked()
        self.restore_tabs_enabled = selected_restore_tabs

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

        self.check_updates_enabled = selected_check_updates

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
        self.save_config()
        event.accept()
