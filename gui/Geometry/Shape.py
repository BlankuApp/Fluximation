from OCP.IVtkVTK import IVtkVTK_ShapeData
from OCP.IVtkOCC import IVtkOCC_Shape, IVtkOCC_ShapeMesher
from OCP.Prs3d import Prs3d_IsoAspect
from OCP.Quantity import Quantity_Color
from OCP.Aspect import Aspect_TOL_SOLID
from OCP.TColgp import TColgp_Array1OfPnt
from OCP.GeomAPI import GeomAPI_PointsToBSpline
from OCP.BRepPrimAPI import (BRepPrimAPI_MakeBox,
                             BRepPrimAPI_MakeSphere,
                             BRepPrimAPI_MakeCone,
                             BRepPrimAPI_MakeCylinder,
                             BRepPrimAPI_MakeTorus)
from OCP.BRepAlgoAPI import (BRepAlgoAPI_Cut,
                             BRepAlgoAPI_Fuse,
                             BRepAlgoAPI_Common,
                             BRepAlgoAPI_Section)
from OCP.BRepBuilderAPI import (BRepBuilderAPI_Transform,
                                BRepBuilderAPI_MakeEdge,
                                BRepBuilderAPI_MakeWire,
                                BRepBuilderAPI_MakeFace)
from OCP.gp import (gp_Pnt,
                    gp_Vec,
                    gp_Dir,
                    gp_Trsf,
                    gp_Ax2,
                    gp_Circ)
from OCP.gce import gce_MakeCirc
import pyvista as pv
from vtkmodules.vtkFiltersCore import vtkTriangleFilter
from collections import UserList
from PySide2.QtWidgets import QTreeWidgetItem
from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt

import gui._globals
from gui.Geometry.Transformation import (MirrorPoint,
                                         MirrorAxis,
                                         Rotate,
                                         Translate,
                                         Scale)


class ShapeSet(UserList):
    def __init__(self, iterable):
        super().__init__(self._validate_shape(item) for item in iterable)

    def append(self, item):
        self.data.append(self._validate_shape(item))

    def __getitem__(self, shape_name):
        for item in self.data:
            if item.name == shape_name:
                return item
        return None

    @staticmethod
    def _validate_shape(value):
        if isinstance(value, Shape):
            return value
        raise TypeError(f"shape value expected, got {type(value).__name__}")


class Shape:
    def __init__(self, color=None):
        self.initial_ocp = []
        self.actor = []
        self._name = ''
        self.icon = []
        self.geometry_branch = []
        self.transformations = []
        self.color = color

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def vtk(self):
        vtk_shape = IVtkOCC_Shape(self.ocp)
        shape_data = IVtkVTK_ShapeData()
        shape_mesher = IVtkOCC_ShapeMesher()

        drawer = vtk_shape.Attributes()
        drawer.SetUIsoAspect(Prs3d_IsoAspect(Quantity_Color(), Aspect_TOL_SOLID, 1, 0))
        drawer.SetVIsoAspect(Prs3d_IsoAspect(Quantity_Color(), Aspect_TOL_SOLID, 1, 0))
        drawer.SetFaceBoundaryDraw(True)

        shape_mesher.Build(vtk_shape, shape_data)

        rv = shape_data.getVtkPolyData()
        t_filter = vtkTriangleFilter()
        t_filter.SetInputData(rv)
        t_filter.Update(None)

        rv = t_filter.GetOutput()
        pv_box = pv.PolyData(rv)

        # return pv.PolyData(pv_box.points, pv_box.faces)
        return pv_box

    @property
    def ocp(self):
        total_trsf = gp_Trsf()
        for transformation in self.transformations:
            total_trsf.Multiply(transformation.trsf)
        transformed_ocp = BRepBuilderAPI_Transform(self.initial_ocp, total_trsf).Shape()
        # return self.initial_ocp
        return transformed_ocp

    def display(self):
        project = gui._globals.current_project
        vtk_widget = project.geometry_win.vtk_widget
        self.actor = vtk_widget.add_mesh(self.vtk, point_size=0)
        self.actor.name = self.name
        self.color = self.actor.prop.color
        # vtk_widget.reset_camera()

        # display the shape in geometry tree widget
        geometry_tree = project.geometry_tree_widget_branch
        self.geometry_branch = QTreeWidgetItem(geometry_tree, [f"{self.name}"], 0)
        self.geometry_branch.setIcon(0, self.icon)
        self.geometry_branch.setData(0, Qt.UserRole, f"{project.name}-shape")

        # display transformation tree widgets
        for transformation in self.transformations:
            branch = QTreeWidgetItem(self.geometry_branch, [f"{transformation.display_name}"])
            branch.setIcon(0, transformation.icon)
            branch.setData(0, Qt.UserRole, f"{project.name}-transformation-{self.name}")

    def mirror_point(self, center_point: list[float]):
        trsf = MirrorPoint(center_point)
        self.transformations.append(trsf)

    def mirror_axis(self, origin_point: list[float], direction: list[float]):
        trsf = MirrorAxis(origin_point, direction)
        self.transformations.append(trsf)

    def rotate(self, origin_point, direction, angle):
        trsf = Rotate(origin_point, direction, angle)
        self.transformations.append(trsf)

    def translate(self, direction: list[float]):
        trsf = Translate(direction)
        self.transformations.append(trsf)

    def scale(self, center_point: list[float], scale: float):
        trsf = Scale(center_point, scale)
        self.transformations.append(trsf)


class Box(Shape):
    def __init__(self, point1: list, dimension: list):
        super().__init__()
        self.icon = QIcon('./gui/res/Part_Box.svg')
        self.starting_point = point1
        self.dimension = dimension
        p1 = gp_Pnt(point1[0], point1[1], point1[2])
        p2 = gp_Pnt(point1[0]+dimension[0], point1[1]+dimension[1], point1[2]+dimension[2])
        self.initial_ocp = BRepPrimAPI_MakeBox(p1, p2).Shape()

    @property
    def prop(self):
        return {"name": self.name,
                "color": self.color.hex_rgb,
                "starting point": self.starting_point,
                "dimension": self.dimension}


class Sphere(Shape):
    def __init__(self, center: list, radius: float):
        super().__init__()
        self.icon = QIcon('./gui/res/Part_Sphere.svg')
        self.center_point = center
        self.radius = radius
        center_point = gp_Pnt(center[0], center[1], center[2])
        self.initial_ocp = BRepPrimAPI_MakeSphere(center_point, radius).Shape()

    @property
    def prop(self):
        return {"name": self.name,
                "color": self.color.hex_rgb,
                "center point": self.center_point,
                "radius": self.radius}


class Cone(Shape):
    def __init__(self, r1: float, r2: float, h: float):
        super().__init__()
        self.icon = QIcon('./gui/res/Part_Cone.svg')
        self.r1 = r1
        self.r2 = r2
        self.h = h
        self.initial_ocp = BRepPrimAPI_MakeCone(r1, r2, h).Shape()

    @property
    def prop(self):
        return {"name": self.name,
                "color": self.color.hex_rgb,
                "radius 1": self.r1,
                "radius 2": self.r2,
                "height": self.h}


class Cylinder(Shape):
    def __init__(self, r: float, h: float):
        super().__init__()
        self.icon = QIcon('./gui/res/Part_Cylinder.svg')
        self.r = r
        self.h = h
        self.initial_ocp = BRepPrimAPI_MakeCylinder(r, h).Shape()

    @property
    def prop(self):
        return {"name": self.name,
                "color": self.color.hex_rgb,
                "radius": self.r,
                "height": self.h}


class Torus(Shape):
    def __init__(self, r1: float, r2: float):
        super().__init__()
        self.icon = QIcon('./gui/res/Part_Torus.svg')
        self.r1 = r1
        self.r2 = r2
        self.initial_ocp = BRepPrimAPI_MakeTorus(r1, r2).Shape()

    @property
    def prop(self):
        return {"name": self.name,
                "color": self.color.hex_rgb,
                "inner radius": self.r1,
                "outer radius": self.r2}


class Cut(Shape):
    def __init__(self, tool: Shape, obj: Shape):
        super().__init__()
        self.icon = QIcon('./gui/res/Part_Cut.svg')
        self.tool = tool
        self.object = obj
        self.initial_ocp = BRepAlgoAPI_Cut(self.tool.ocp, self.object.ocp).Shape()

    @property
    def prop(self):
        return {"name": self.name,
                "color": self.color.hex_rgb}


class Fuse(Shape):
    def __init__(self, tool: Shape, obj: Shape):
        super().__init__()
        self.icon = QIcon('./gui/res/Part_Fuse.svg')
        self.tool = tool
        self.object = obj
        self.initial_ocp = BRepAlgoAPI_Fuse(self.tool.ocp, self.object.ocp).Shape()

    @property
    def prop(self):
        return {"name": self.name,
                "color": self.color.hex_rgb}


class Common(Shape):
    def __init__(self, tool: Shape, obj: Shape):
        super().__init__()
        self.icon = QIcon('./gui/res/Part_Common.svg')
        self.tool = tool
        self.object = obj
        self.initial_ocp = BRepAlgoAPI_Common(self.tool.ocp, self.object.ocp).Shape()

    @property
    def prop(self):
        return {"name": self.name,
                "color": self.color.hex_rgb}


class Section(Shape):
    def __init__(self, tool: Shape, obj: Shape):
        super().__init__()
        self.icon = QIcon('./gui/res/Part_Section.svg')
        self.tool = tool
        self.object = obj
        self.initial_ocp = BRepAlgoAPI_Section(self.tool.ocp, self.object.ocp).Shape()

    @property
    def prop(self):
        return {"name": self.name,
                "color": self.color.hex_rgb}


class Line(Shape):
    def __init__(self, first_point: list[float], second_point: list[float], color=None):
        super().__init__(color=color)
        self.icon = QIcon('./gui/res/Sketcher_CreateLine.svg')
        self.first_point = first_point
        self.second_point = second_point
        pnt1 = gp_Pnt(first_point[0], first_point[1], first_point[2])
        pnt2 = gp_Pnt(second_point[0], second_point[1], second_point[2])
        self.initial_ocp = BRepBuilderAPI_MakeEdge(pnt1, pnt2).Shape()

    @property
    def prop(self):
        return {"name": self.name,
                "color": self.color.hex_rgb,
                "first_point": self.first_point,
                "second_point": self.second_point}


class Arc(Shape):
    def __init__(self, center_point: list[float], first_point: list[float], second_point: list[float], color=None):
        super().__init__(color=color)
        self.icon = QIcon('./gui/res/Sketcher_CreateArc.svg')
        self.center_point = center_point
        self.first_point = first_point
        self.second_point = second_point
        pnt1 = gp_Pnt(self.first_point[0], self.first_point[1], self.first_point[2])
        pnt2 = gp_Pnt(self.second_point[0], self.second_point[1], self.second_point[2])
        pntc = gp_Pnt(self.center_point[0], self.center_point[1], self.center_point[2])
        cp1 = gp_Vec(pntc, pnt1)
        cp2 = gp_Vec(pntc, pnt2)
        normal_vec = cp1.Crossed(cp2)
        normal_dir = gp_Dir(normal_vec)
        ax2 = gp_Ax2(pntc, normal_dir)
        radius = pntc.Distance(pnt1)
        circle = gp_Circ(ax2, radius)
        self.initial_ocp = BRepBuilderAPI_MakeEdge(circle, pnt1, pnt2).Shape()

    @property
    def prop(self):
        return {"name": self.name,
                "color": self.color.hex_rgb,
                "center_point": self.center_point,
                "first_point": self.first_point,
                "second_point": self.second_point}


class Arc3Point(Shape):
    def __init__(self, first_point: list[float], second_point: list[float], third_point: list[float], color=None):
        super().__init__(color=color)
        self.icon = QIcon('./gui/res/Sketcher_Create3PointArc.svg')
        self.first_point = first_point
        self.second_point = second_point
        self.third_point = third_point
        pnt1 = gp_Pnt(self.first_point[0], self.first_point[1], self.first_point[2])
        pnt2 = gp_Pnt(self.second_point[0], self.second_point[1], self.second_point[2])
        pnt3 = gp_Pnt(self.third_point[0], self.third_point[1], self.third_point[2])
        circle = gce_MakeCirc(pnt1, pnt2, pnt3).Value()
        self.initial_ocp = BRepBuilderAPI_MakeEdge(circle, pnt1, pnt3).Shape()

    @property
    def prop(self):
        return {"name": self.name,
                "color": self.color.hex_rgb,
                "first_point": self.first_point,
                "second_point": self.second_point,
                "third_point": self.third_point}


class Circle(Shape):
    def __init__(self, center_point: list[float], normal_vector: list[float], radius: float, color=None):
        super().__init__(color=color)
        self.icon = QIcon('./gui/res/Sketcher_CreateCircle.svg')
        self.normal_vector = normal_vector
        self.center_point = center_point
        self.radius = radius
        pntc = gp_Pnt(self.center_point[0], self.center_point[1], self.center_point[2])
        normal_vec = gp_Vec(self.normal_vector[0], self.normal_vector[1], self.normal_vector[2])
        normal_dir = gp_Dir(normal_vec)
        ax2 = gp_Ax2(pntc, normal_dir)
        circle = gp_Circ(ax2, radius)
        edge = BRepBuilderAPI_MakeEdge(circle).Edge()
        wire = BRepBuilderAPI_MakeWire(edge).Wire()
        self.initial_ocp = BRepBuilderAPI_MakeFace(wire).Shape()

    @property
    def prop(self):
        return {"name": self.name,
                "color": self.color.hex_rgb,
                "center_point": self.center_point,
                "normal_vector": self.normal_vector,
                "radius": self.radius}


class Circle3Point(Shape):
    def __init__(self, first_point: list[float], second_point: list[float], third_point: list[float], color=None):
        super().__init__(color=color)
        self.icon = QIcon('./gui/res/Sketcher_Create3PointCircle.svg')
        self.first_point = first_point
        self.second_point = second_point
        self.third_point = third_point
        pnt1 = gp_Pnt(self.first_point[0], self.first_point[1], self.first_point[2])
        pnt2 = gp_Pnt(self.second_point[0], self.second_point[1], self.second_point[2])
        pnt3 = gp_Pnt(self.third_point[0], self.third_point[1], self.third_point[2])
        circle = gce_MakeCirc(pnt1, pnt2, pnt3).Value()
        edge = BRepBuilderAPI_MakeEdge(circle).Edge()
        wire = BRepBuilderAPI_MakeWire(edge).Wire()
        self.initial_ocp = BRepBuilderAPI_MakeFace(wire).Shape()

    @property
    def prop(self):
        return {"name": self.name,
                "color": self.color.hex_rgb,
                "first_point": self.first_point,
                "second_point": self.second_point,
                "third_point": self.third_point}


class BSpline(Shape):
    def __init__(self, points: list, color=None):
        super().__init__(color=color)
        self.icon = QIcon('./gui/res/Sketcher_CreateBSpline.svg')
        self.points = points

        n = len(self.points)
        pnt_array = TColgp_Array1OfPnt(1, n)
        for i in range(n):
            pnt = gp_Pnt(self.points[i][0], self.points[i][1], self.points[i][2])
            pnt_array.SetValue(i+1, pnt)

        curve = GeomAPI_PointsToBSpline(pnt_array).Curve()
        self.initial_ocp = BRepBuilderAPI_MakeEdge(curve).Shape()

    @property
    def prop(self):
        return {"name": self.name,
                "color": self.color.hex_rgb,
                "points": self.points}
