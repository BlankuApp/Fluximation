from PySide2.QtWidgets import QMainWindow, QDockWidget, QMdiArea, QMdiSubWindow
from PySide2.QtWidgets import QTreeWidget, QToolBar, QStatusBar
from PySide2.QtWidgets import QAction, QTreeWidgetItem
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont, QIcon

from gui.App import App
from gui.Project import Project
from gui.ScriptingWindow import ScriptingWindow
from gui.GeometryWindow import GeometryWindow


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
        self.projects_tree_widget = QTreeWidget()
        self.projects_tree_widget.setHeaderHidden(True)
        self.projects_dock.setWidget(self.projects_tree_widget)
        self.projects_tree_widget.itemDoubleClicked.connect(self.project_tree_double_clicked)

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Create the App
        self.main_app = App(self.mdi_area, self.projects_tree_widget, self)

        # Create a projects toolbar
        self.projects_toolbar = QToolBar()
        self.addToolBar(self.projects_toolbar)

        # Create an action for the projects_toolbar
        self.new_action = QAction('New', self)

        # Add the new_action to the toolbar
        self.new_action.triggered.connect(self.add_project)

        self.projects_toolbar.addAction(self.new_action)

    def project_tree_double_clicked(self, item: QTreeWidgetItem, col: int):
        item_data = item.data(0, Qt.UserRole)
        self.status_bar.showMessage(item_data)
        project_name, section = item_data.split("-")

        # make the selected project active
        if section == "main":
            self.set_active_project(item, project_name)

        # show the scripting window if closed
        if section == "script":
            p = self.findChildren(Project, project_name)[0]
            self.show_script_sub_win(p)

    def set_active_project(self, item, project_name, col=0):
        normal_font = QFont()
        bold_font = QFont()
        bold_font.setBold(True)
        for project in self.main_app.projects:
            project.main_tree_widget_branch.setFont(col, normal_font)
        item.setFont(col, bold_font)
        self.setWindowTitle(project_name)

    def add_project(self):
        # find new name
        name = "Project"
        i = 1
        for p in self.main_app.projects:
            if name == p.name:
                name = f"Project{i}"
                i += 1
            else:
                break

        # make the project
        p = Project(name, self)
        self.main_app.projects.append(p)
        self.set_active_project(p.main_tree_widget_branch, name)
        self.projects_tree_widget.insertTopLevelItem(0, p.main_tree_widget_branch)
        self.show_script_sub_win(p)
        self.show_geometry_sub_win(p)

    def show_script_sub_win(self, project: Project):
        script_win = ScriptingWindow(project)
        sub_win = QMdiSubWindow()
        sub_win.setAttribute(Qt.WA_DeleteOnClose, True)
        sub_win.setWidget(script_win)
        sub_win.setWindowIcon(QIcon('./gui/res/script_icon.png'))
        self.mdi_area.addSubWindow(sub_win)
        sub_win.show()

    def show_geometry_sub_win(self, project: Project):
        geometry_win = GeometryWindow(project)
        sub_win = QMdiSubWindow()
        sub_win.setAttribute(Qt.WA_DeleteOnClose, True)
        sub_win.setWidget(geometry_win)
        sub_win.setWindowIcon(QIcon('./gui/res/geometry_icon.png'))
        self.mdi_area.addSubWindow(sub_win)
        sub_win.show()
