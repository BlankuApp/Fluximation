from PySide2.QtWidgets import QMdiArea
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem
from PySide2.QtCore import QObject

from gui.Project import Project


class App(QObject):
    def __init__(self, mdi_area: QMdiArea, projects_tree_widget: QTreeWidget, parent):
        super().__init__(parent)
        self.mdi_area = mdi_area
        self.projects_tree_widget = projects_tree_widget
        self.projects = []



