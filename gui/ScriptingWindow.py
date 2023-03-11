from PySide2.QtWidgets import (QMainWindow,
                               QTextEdit,
                               QToolBar,
                               QAction)
from gui.Geometry.Shape import *
import gui._globals


class ScriptingWindow(QMainWindow):
    def __init__(self, project):
        super().__init__()
        self.project = project
        self.setWindowTitle(f"Script ({project.name})")
        self.script_win = self
        self.text_editor = QTextEdit()
        self.text_editor.setText('''box = Box([0, 5, 0], [1, 1, 1])
cone = Cone(1, 0.5, 2)
sphere = Sphere([1,0,0],0.5)
cone = Cut(cone,sphere)
sphere.translate([5,0,0])
points = [[0,0,0],[1,2,0],[2,3,0],[4,3,0],[5,5,0]]
spline = BSpline(points)''')
        self.setCentralWidget(self.text_editor)

        # execution toolbar
        execution_toolbar = QToolBar()
        self.addToolBar(execution_toolbar)

        run_action = QAction("Run", self)
        execution_toolbar.addAction(run_action)

        run_action.triggered.connect(self.run)

    def run(self):
        gui._globals.current_project = self.project
        text = self.text_editor.toPlainText()
        exec(text)

        # draw Shapes in geometry window
        self.project.geometry_win.vtk_widget.clear_actors()
        self.project.shapes.clear()
        for i in range(self.project.geometry_tree_widget_branch.childCount()):
            self.project.geometry_tree_widget_branch.removeChild(self.project.geometry_tree_widget_branch.child(0))
        local_vars = locals()
        key = val = None
        for key, val in local_vars.items():
            if isinstance(val, Shape):
                if val.name == '':
                    val.name = key
                val.display()
                self.project.shapes.append(val)

        self.project.geometry_win.cam_orient_widget.On()

