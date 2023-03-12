from PySide2.QtWidgets import QMdiArea
from PySide2.QtWidgets import QTreeWidget
from PySide2.QtCore import QObject


class App(QObject):
    def __init__(self, mdi_area: QMdiArea, projects_tree_widget: QTreeWidget, parent):
        super().__init__(parent)
        self.mdi_area = mdi_area
        self.projects_tree_widget = projects_tree_widget
        self.projects = []

    def get_project_by_name(self, name):
        for project in self.projects:
            if project.name == name:
                return project
        return None
