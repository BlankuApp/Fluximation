from PySide2.QtWidgets import QMainWindow, QVBoxLayout, QFrame
import pyvista as pv
import pyvistaqt


from vtkmodules.vtkFiltersCore import vtkTriangleFilter

from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.IVtkVTK import IVtkVTK_ShapeData
from OCP.IVtkOCC import IVtkOCC_Shape, IVtkOCC_ShapeMesher

from OCP.Prs3d import Prs3d_IsoAspect
from OCP.Quantity import Quantity_Color
from OCP.Aspect import Aspect_TOL_SOLID


class GeometryWindow(QMainWindow):
    def __init__(self, project):
        super().__init__()
        self.setWindowTitle(f"Geometry ({project.name})")
        # create the frame
        self.frame = QFrame()
        vlayout = QVBoxLayout()

        # add the pyvista interactor object
        self.vtk_widget = pyvistaqt.QtInteractor(self.frame)
        vlayout.addWidget(self.vtk_widget.interactor)

        self.frame.setLayout(vlayout)
        self.setCentralWidget(self.frame)

        my_box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
        # my_box = BRepPrimAPI_MakeSphere(1.0).Shape()
        # Initialize aShape variable: e.g. load it from BREP file
        vtk_shape = IVtkOCC_Shape(my_box)
        shape_data = IVtkVTK_ShapeData()
        shape_mesher = IVtkOCC_ShapeMesher()

        drawer = vtk_shape.Attributes()
        drawer.SetUIsoAspect(Prs3d_IsoAspect(Quantity_Color(), Aspect_TOL_SOLID, 1, 0))
        drawer.SetVIsoAspect(Prs3d_IsoAspect(Quantity_Color(), Aspect_TOL_SOLID, 1, 0))
        drawer.SetFaceBoundaryDraw(True)

        shape_mesher.Build(vtk_shape, shape_data)

        self.rv = shape_data.getVtkPolyData()
        t_filter = vtkTriangleFilter()
        t_filter.SetInputData(self.rv)
        t_filter.Update()

        self.rv = t_filter.GetOutput()
        pv_box = pv.PolyData(self.rv)

        mesh = pv.PolyData(pv_box.points, pv_box.faces)

        self.vtk_widget.add_mesh(mesh)
        self.vtk_widget.reset_camera()
