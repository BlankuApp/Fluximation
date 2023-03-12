from PySide2.QtWidgets import (QDialog,
                               QLabel,
                               QLineEdit,
                               QHBoxLayout,
                               QVBoxLayout,
                               QRadioButton,
                               QSpacerItem,
                               QSizePolicy,
                               QDialogButtonBox)
from PySide2.QtCore import Qt
from gui.Project import GeometryType


class NewProjectDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setModal(True)
        self.setGeometry(300, 300, 300, QSizePolicy.Minimum)
        self.setMinimumWidth(300)
        self.setWindowTitle("New Project")

        self.error_label = QLabel("A name with that value already exists.\nPlease choose a unique name.")
        self.error_label.setStyleSheet("border: 1px solid red; background-color: #FEE; color: red;")

        # project type
        type_label = QLabel("Geometry Type:")
        self.radio1 = QRadioButton("2D", self)
        self.radio2 = QRadioButton("3D", self)
        self.radio1.setChecked(True)
        type_spacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        type_layout = QHBoxLayout()
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.radio1)
        type_layout.addWidget(self.radio2)
        type_layout.addItem(type_spacer)

        # buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.apply)
        self.button_box.rejected.connect(self.reject)

        # spacer
        main_spacer = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)

        # project name
        name_label = QLabel("Project Name:")
        self.name_line_edit = QLineEdit()
        self.name_line_edit.textChanged.connect(self.check_name)
        name_layout = QHBoxLayout()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_line_edit)

        # find a new name
        name = "Project"
        i = 1
        for p in self.parent().main_app.projects:
            if name == p.name:
                name = f"Project{i}"
                i += 1
            else:
                break
        self.name_line_edit.setText(name)

        # add the contents to the dialog
        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(name_layout)
        self.main_layout.addLayout(type_layout)
        self.main_layout.addWidget(self.error_label)
        self.main_layout.addWidget(self.button_box)
        self.main_layout.addItem(main_spacer)

        self.setLayout(self.main_layout)

    def apply(self):
        name = self.name_line_edit.text()
        if self.radio1.isChecked():
            self.parent().new_project(name, GeometryType.two_dimensional)
        else:
            self.parent().new_project(name, GeometryType.three_dimensional)

        self.accept()

    def check_name(self):
        self.error_label.hide()
        ok_button = self.button_box.buttons()[0]
        ok_button.setEnabled(True)
        name = self.name_line_edit.text()
        for p in self.parent().main_app.projects:
            if name == p.name:
                ok_button.setEnabled(False)
                self.error_label.show()
                return
        self.adjustSize()
