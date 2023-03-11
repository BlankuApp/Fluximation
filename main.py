import sys
from PySide2.QtWidgets import QApplication
from gui.MainWindow import MainWindow

if __name__ == "__main__":
    # Create the application
    app = QApplication(sys.argv)

    # Create and show the main window
    window = MainWindow()
    window.show()

    # Run the event loop
    sys.exit(app.exec_())
