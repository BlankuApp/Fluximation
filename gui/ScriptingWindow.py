from PySide2.QtWidgets import QMainWindow, QTextEdit


class ScriptingWindow(QMainWindow):
    def __init__(self, project):
        super().__init__()
        self.setWindowTitle(f"Script ({project.name})")
        self.text_editor = QTextEdit()
        self.setCentralWidget(self.text_editor)
