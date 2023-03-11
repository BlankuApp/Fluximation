from PySide2.QtWidgets import QMainWindow, QVBoxLayout, QFrame
import pyvistaqt
from vtkmodules.vtkInteractionWidgets import vtkCameraOrientationWidget
import pyvista as pv
pv.global_theme.color_cycler = "default"


class GeometryWindow(QMainWindow):
    def __init__(self, project):
        super().__init__()
        self.project = project
        self.setWindowTitle(f"Geometry ({project.name})")
        project.geometry_win = self
        # create the frame
        self.frame = QFrame()
        v_layout = QVBoxLayout()
        v_layout.setSpacing(0)
        v_layout.setContentsMargins(0, 0, 0, 0)

        # add the pyvista interactor object
        self.vtk_widget = pyvistaqt.QtInteractor(self.frame)
        self.vtk_widget.background_color = "ghostwhite"
        v_layout.addWidget(self.vtk_widget.interactor)

        # add camera orientation widget
        self.cam_orient_widget = vtkCameraOrientationWidget()
        self.cam_orient_widget.SetParentRenderer(self.vtk_widget.renderer)

        self.frame.setLayout(v_layout)
        self.setCentralWidget(self.frame)
