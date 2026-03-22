import sys
from PySide6.QtWidgets import QApplication
from logic import NordactorWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Nordactor")

    window = NordactorWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()