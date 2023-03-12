from PySide2.QtWidgets import (QMainWindow,
                               QDockWidget,
                               QMdiArea,
                               QMdiSubWindow,
                               QHeaderView,
                               QAction,
                               QTreeWidgetItem,
                               QTreeWidget,
                               QToolBar,
                               QStatusBar,
                               QTableWidget,
                               QTableWidgetItem,
                               QFileDialog,
                               QMessageBox)
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont, QIcon

from gui.App import App
from gui.Project import Project, GeometryType
from gui.ScriptingWindow import ScriptingWindow
from gui.GeometryWindow import GeometryWindow
from gui.Geometry.Shape import Shape
from gui.Dialogs.NewProject import NewProjectDialog

import json, os
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("Main Window")
        app_icon = QIcon('./gui/res/app_icon.png')
        self.setWindowIcon(app_icon)

        # Create an MDI area and set it as the central widget
        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)
        self.mdi_area.show()

        # Create a dockable widget
        self.projects_dock = QDockWidget("Projects", self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.projects_dock)
        self.property_dock = QDockWidget("Properties", self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.property_dock)

        # Create a projects tree view
        self.projects_tree_widget = QTreeWidget(self)
        self.projects_tree_widget.setHeaderHidden(True)
        self.projects_dock.setWidget(self.projects_tree_widget)
        self.projects_tree_widget.itemDoubleClicked.connect(self.project_tree_double_clicked)
        self.projects_tree_widget.itemClicked.connect(self.project_tree_clicked)

        # Create property table widget
        self.property_table_widget = QTableWidget(self)
        self.property_table_widget.setRowCount(5)
        self.property_table_widget.setColumnCount(2)
        self.property_table_widget.verticalHeader().hide()
        self.property_table_widget.horizontalHeader().hide()
        self.property_table_widget.horizontalHeader().setStretchLastSection(True)
        self.property_table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.property_table_widget.verticalHeader().setDefaultSectionSize(10)
        self.property_dock.setWidget(self.property_table_widget)

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Create the App
        self.main_app = App(self.mdi_area, self.projects_tree_widget, self)

        # Create a projects toolbar
        self.projects_toolbar = QToolBar()
        self.addToolBar(self.projects_toolbar)

        # Create projects menubar
        self.projects_menubar = self.menuBar().addMenu("Project")

        # Create new action
        self.new_action = QAction('New', self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.setIcon(QIcon('./gui/res/document-new.svg'))

        # Create save action
        self.save_action = QAction("Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.setIcon(QIcon('./gui/res/document-save.svg'))

        # Create open action
        self.open_action = QAction("Open", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.setIcon(QIcon('./gui/res/document-open.svg'))

        # Add the actions to the toolbar
        self.new_action.triggered.connect(lambda: NewProjectDialog(self).show())
        self.save_action.triggered.connect(self.save_project)
        self.open_action.triggered.connect(self.open_project)

        actions = [self.new_action, self.open_action, self.save_action]
        self.projects_toolbar.addActions(actions)
        self.projects_menubar.addActions(actions)

    def project_tree_double_clicked(self, item: QTreeWidgetItem, col: int):
        item_data = item.data(col, Qt.UserRole)
        tags = item_data.split("-")
        project_name = tags[0]
        section = tags[1]

        # make the selected project active
        if section == "main":
            self.set_active_project(item, project_name)

        # show the scripting window if closed
        if section == "script":
            p = self.findChildren(Project, project_name)[0]
            self.show_script_sub_win(p)

        # show the geometry window if closed
        if section == "geometry":
            p = self.findChildren(Project, project_name)[0]
            self.show_geometry_sub_win(p)

    def project_tree_clicked(self, item: QTreeWidgetItem, col: int):
        item_data = item.data(col, Qt.UserRole)
        self.status_bar.showMessage(item_data)
        tags = item_data.split("-")
        project_name = tags[0]
        section = tags[1]

        p: Project = self.findChildren(Project, project_name)[0]
        if section == "shape":
            s: Shape = p.shapes[item.text(0)]
            self.property_table_widget.setRowCount(len(s.prop))
            i = 0
            for key, value in s.prop.items():
                self.property_table_widget.setItem(i, 0, QTableWidgetItem(key))
                self.property_table_widget.setItem(i, 1, QTableWidgetItem(str(value)))
                i += 1
        elif section == "transformation":
            shape_item = item.parent()
            s: Shape = p.shapes[shape_item.text(0)]
            transformation_index = shape_item.indexOfChild(item)
            transformation = s.transformations[transformation_index]
            self.property_table_widget.setRowCount(len(transformation.prop))
            i = 0
            for key, value in transformation.prop.items():
                self.property_table_widget.setItem(i, 0, QTableWidgetItem(key))
                self.property_table_widget.setItem(i, 1, QTableWidgetItem(repr(value)))
                i += 1

    def set_active_project(self, item, project_name, col=0):
        normal_font = QFont()
        bold_font = QFont()
        bold_font.setBold(True)
        for project in self.main_app.projects:
            project.main_tree_widget_branch.setFont(col, normal_font)
            project.main_tree_widget_branch.setExpanded(True)
        item.setFont(col, bold_font)
        self.setWindowTitle(project_name)

    def new_project(self, name: str, geometry_type: GeometryType):
        # make the project
        p = Project(name, geometry_type, self)
        self.main_app.projects.append(p)
        self.set_active_project(p.main_tree_widget_branch, name)
        self.projects_tree_widget.insertTopLevelItem(0, p.main_tree_widget_branch)
        self.show_script_sub_win(p)
        self.show_geometry_sub_win(p)
        return p

    def show_script_sub_win(self, project: Project):
        # check if the subWin already exist
        sub_wins = self.mdi_area.subWindowList()
        for sub_win in sub_wins:
            if sub_win.windowTitle() == f"Script ({project.name})":
                self.mdi_area.setActiveSubWindow(sub_win)
                return
        # if sub_win is closed make new one
        script_win = ScriptingWindow(project)
        sub_win = QMdiSubWindow()
        sub_win.setAttribute(Qt.WA_DeleteOnClose, True)
        sub_win.setWidget(script_win)
        sub_win.setWindowIcon(QIcon('./gui/res/script_icon.png'))
        self.mdi_area.addSubWindow(sub_win)
        sub_win.show()

    def show_geometry_sub_win(self, project: Project):
        # check if the subWin already exist
        sub_wins = self.mdi_area.subWindowList()
        for sub_win in sub_wins:
            if sub_win.windowTitle() == f"Geometry ({project.name})":
                self.mdi_area.setActiveSubWindow(sub_win)
                return
        geometry_win = GeometryWindow(project)
        sub_win = QMdiSubWindow()
        sub_win.setAttribute(Qt.WA_DeleteOnClose, True)
        sub_win.setWidget(geometry_win)
        sub_win.setWindowIcon(QIcon('./gui/res/geometry_icon.png'))
        self.mdi_area.addSubWindow(sub_win)
        sub_win.show()

    def save_project(self):
        project: Project = self.main_app.get_project_by_name(self.windowTitle())
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Project", f"{project.name}", "Text Files (*.txt)", options=options)
        if file_name:
            with open(file_name, 'w') as f:
                json.dump(project.dict_form(), f)

    def open_project(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Project", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, 'r') as f:
                project_json = json.load(f)
                file_name = os.path.splitext(os.path.basename(file_path))[0]
                if self.main_app.get_project_by_name(file_name):
                    error_box = QMessageBox()
                    error_box.setIcon(QMessageBox.Critical)
                    error_box.setWindowTitle("Error")
                    error_box.setText("Project already exists.")
                    error_box.setInformativeText(
                        "A project with the same name already exists. Please choose a different name for your project.")
                    error_box.setStandardButtons(QMessageBox.Ok)
                    error_box.exec_()
                    return
                project = self.new_project(file_name, project_json["geometry_type"])
                project.script_text = project_json["script_text"]

