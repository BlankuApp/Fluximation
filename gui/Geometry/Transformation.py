from OCP.gp import gp_Pnt, gp_Dir, gp_Vec, gp_Ax1, gp_Trsf
from PySide2.QtGui import QIcon


class Transformation:
    def __init__(self):
        self.display_name = ""
        self.trsf = gp_Trsf()
        self.icon = []


class MirrorPoint(Transformation):
    def __init__(self, center_point: list):
        super().__init__()
        self.display_name = "Mirror"
        self.icon = QIcon('./gui/res/PartDesign_Mirrored.svg')
        self.center_point = center_point
        pnt = gp_Pnt(center_point[0], center_point[1], center_point[2])
        self.trsf.SetMirror(pnt)

    @property
    def prop(self):
        return {"center_point": self.center_point}


class MirrorAxis(Transformation):
    def __init__(self, origin_point: list, direction: list):
        super().__init__()
        self.display_name = "Mirror"
        self.icon = QIcon('./gui/res/PartDesign_Mirrored.svg')
        self.origin_point = origin_point
        self.direction = direction
        pnt = gp_Pnt(origin_point[0], origin_point[1], origin_point[2])
        direc = gp_Dir(direction[0], direction[1], direction[2])
        ax1 = gp_Ax1(pnt, direc)
        self.trsf.SetMirror(ax1)

    @property
    def prop(self):
        return {"origin_point": self.origin_point,
                "direction": self.direction}


class Rotate(Transformation):
    def __init__(self, origin_point: list, direction: list, angel: float):
        super().__init__()
        self.display_name = "Rotate"
        self.icon = QIcon('./gui/res/PartDesign_PolarPattern.svg')
        self.origin_point = origin_point
        self.direction = direction
        self.angel = angel
        pnt = gp_Pnt(origin_point[0], origin_point[1], origin_point[2])
        direc = gp_Dir(direction[0], direction[1], direction[2])
        ax1 = gp_Ax1(pnt, direc)
        self.trsf.SetRotation(ax1, angel)

    @property
    def prop(self):
        return {"origin_point": self.origin_point,
                "direction": self.direction,
                "angel": self.angel}


class Translate(Transformation):
    def __init__(self, direction: list[float]):
        super().__init__()
        self.display_name = "Translate"
        self.icon = QIcon('./gui/res/PartDesign_LinearPattern.svg')
        self.direction = direction
        vec = gp_Vec(direction[0], direction[1], direction[2])
        self.trsf.SetTranslation(vec)

    @property
    def prop(self):
        return {"direction": self.direction}


class Scale(Transformation):
    def __init__(self, center_point: list[float], scale: float):
        super().__init__()
        self.display_name = "Scale"
        self.icon = QIcon('./gui/res/PartDesign_Scaled.svg')
        self.center_point = center_point
        self.scale = scale
        pnt = gp_Pnt(center_point[0], center_point[1], center_point[2])
        self.trsf.SetScale(pnt, scale)

    @property
    def prop(self):
        return {"center_point": self.center_point,
                "scale": self.scale}
