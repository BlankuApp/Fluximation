from PySide2.QtWidgets import QTreeWidgetItem
from PySide2.QtCore import Qt, QObject
from PySide2.QtGui import QIcon
from gui.Geometry.Shape import ShapeSet
from enum import Enum


class GeometryType(Enum):
    two_dimensional = 2
    three_dimensional = 3


class Project(QObject):

    def __init__(self, p_name: str, geometry_type: GeometryType, parent: QObject):
        super().__init__(parent)
        self.name = p_name
        self.setObjectName(f"{self.name}")
        self.shapes = ShapeSet([])
        self.geometry_type = geometry_type
        self.script_text = '''box = Box([0, 5, 0], [1, 1, 1])
cone = Cone(1, 0.5, 2)
sphere = Sphere([1,0,0],0.5)
cone = Cut(cone,sphere)
sphere.translate([5,0,0])
points = [[0,0,0],[1,2,0],[2,3,0],[4,3,0],[5,5,0]]
spline = BSpline(points)'''

        # all about tree widget
        self.main_tree_widget_branch = []
        self.script_tree_widget_branch = []
        self.geometry_tree_widget_branch = []
        self.init_project_tree_widget()

    def init_project_tree_widget(self):
        self.main_tree_widget_branch = QTreeWidgetItem(self.parent().projects_tree_widget, [self.name], 0)
        self.main_tree_widget_branch.setIcon(0, QIcon('./gui/res/project_icon.png'))
        self.main_tree_widget_branch.setData(0, Qt.UserRole, f"{self.name}-main")

        self.script_tree_widget_branch = QTreeWidgetItem(self.main_tree_widget_branch, ["Script"], 0)
        self.script_tree_widget_branch.setIcon(0, QIcon('./gui/res/script_icon.png'))
        self.script_tree_widget_branch.setData(0, Qt.UserRole, f"{self.name}-script")

        self.geometry_tree_widget_branch = QTreeWidgetItem(self.main_tree_widget_branch, ["Geometry"], 0)
        self.geometry_tree_widget_branch.setIcon(0, QIcon('./gui/res/geometry_icon.png'))
        self.geometry_tree_widget_branch.setData(0, Qt.UserRole, f"{self.name}-geometry")

    def dict_form(self):
        return {"geometry_type": self.geometry_type.value,
                "script_text": self.script_text}
