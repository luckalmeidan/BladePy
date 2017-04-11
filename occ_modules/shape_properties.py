"""@package occ_modules.shape_properties

Filee that contains the class ShapeManager that is inherited by Core.BladePyCore for Shape Control purposes.

The class has a object compost in Core.BladePyCore. In this file the shape color definitions are also defined and
imported through the GUI for painting shapes and for painting the TreeView widget icons.

"""
import pyparsing

import OCC.Quantity as OCC_Color
import os

from OCC.IGESControl import IGESControl_Controller, IGESControl_Reader
from OCC.IGESCAFControl import IGESCAFControl_Reader
from OCC.TDataStd import TDataStd_Name_GetID, Handle_TDataStd_Name
from OCC.TCollection import TCollection_ExtendedString
from OCC.TDF import TDF_LabelSequence
from OCC.TDocStd import Handle_TDocStd_Document
from OCC.XCAFApp import _XCAFApp
from OCC.XCAFDoc import XCAFDoc_DocumentTool
from OCC.AIS import AIS_ColoredShape
from OCC.TopLoc import TopLoc_Location
from OCC.gp import gp_Trsf, gp_Pnt, gp_Ax1, gp_Dir, gp_Vec
from math import pi
from PyQt4 import QtCore, QtGui
from bladepro_modules.inputfile_writer import InputWriterWindow


shape_colorlist = ["Golden", "Blue", "Red", "White", "Black", "Yellow"]

# set dictionaries for shape colors
shape_colordictionary = {"Black": OCC_Color.Quantity_NOC_BLACK,
                         "White": OCC_Color.Quantity_NOC_ANTIQUEWHITE,
                         "Blue": OCC_Color.Quantity_NOC_BLUE1,
                         "Yellow": OCC_Color.Quantity_NOC_YELLOW,
                         "Golden": OCC_Color.Quantity_NOC_ORANGE3,
                         "Red": OCC_Color.Quantity_NOC_RED3}

# This shape colors are for the icons on tree view list
shape_colordictionaryhex = {"Black": QtGui.QColor(0, 0, 0),
                            "White": QtGui.QColor(255, 255, 255),
                            "Blue": QtGui.QColor(0, 0, 240),
                            "Golden": QtGui.QColor(230, 153, 0),
                            "Yellow": QtGui.QColor(255, 255, 0),
                            "Red": QtGui.QColor(255, 0, 0)}

class ShapeManager(object):
    """
    This class is a group of methods related to shape properties control.

    All these methods are a linked to Core.BladePyCore by composition. Contains methods that manages the Shape
    appearance such transparency, quality, color. It also has a method capable of transforming the shape by displacing
    or rotating it.

    """

    def __init__(self, OutputViewerWidget):

        ## Object reference to main object
        self.op_viewer = OutputViewerWidget

    def loadShape(self, shape_list):
        """
        Method for loading one or more shapes and displaying to Output Viewer.

        This method uses libraries of iges caf control for fetching sub-shape names within .igs files. This method
        is used when adding a case in the main routine.

        @param shape_list [list] First index contains the path of shape, second index contains a list of display
        exceptions, e.g: [[igs_2d_shape_path, ["HUB", "SHROUD"], [igs_3d_shape_path, ["STREAM"]]
        @return First return contains list of ais_shapes handles and second return contains a list of sub-shape names
        in strings
        """
        loaded_ais_shape = []
        loaded_h_ais_shape = []
        loaded_subshape_names = []
        default_displaying_h_ais_shape = []

        for shape_case in shape_list:

            loaded_shape_filename = os.path.basename(shape_case[0])
            exception_list = shape_case[1]
            exception_list = list(filter(None, exception_list)) # Mistake-prevention of user filling of exception list

            # creates a handle for TdocStd documents
            h_doc = Handle_TDocStd_Document()

            # create the application
            app = _XCAFApp.XCAFApp_Application_GetApplication().GetObject()
            app.NewDocument(TCollection_ExtendedString(""), h_doc)

            # get root assembly
            doc = h_doc.GetObject()
            h_shape_tool = XCAFDoc_DocumentTool().ShapeTool(doc.Main())

            # creates a reader responsible for reading an IGS file
            reader = IGESCAFControl_Reader()
            reader.ReadFile(shape_case[0])

            #  Translates currently loaded IGES file into the document
            reader.Transfer(doc.GetHandle())

            # labels for the shapes. Every IGS file contains a name for each individual shape
            labels = TDF_LabelSequence()

            shape_tool = h_shape_tool.GetObject()
            shape_tool.GetShapes(labels)

            # gets the number of individual shapes contained in the igs file
            nb = reader.NbShapes()

            # for each individual shape gets the label nad creates a AIS_Shape for data contained in reader.Shape()
            for i in range(1, nb + 1):
                label = labels.Value(i)

                h_name = Handle_TDataStd_Name()
                label.FindAttribute(TDataStd_Name_GetID(), h_name)
                str_dump = h_name.GetObject().DumpToString()
                name_subshape = str_dump.split('|')[-2]
                name = "%s - %s" % (loaded_shape_filename, name_subshape)

                loaded_subshape_names.append(name)

                shape = AIS_ColoredShape(reader.Shape(i))
                loaded_ais_shape.append(shape)
                loaded_h_ais_shape.append(shape.GetHandle())

                if not any(iterator in name_subshape for iterator in exception_list):
                    default_displaying_h_ais_shape.append(shape.GetHandle())

                self.op_viewer.master_shape_list.append(shape.GetHandle())

            # number of cases is a variable used to make the loaded shape color different from the previous one
            number_of_cases = self.op_viewer.model.rowCount(self.op_viewer.ui_case_treeview.rootIndex())

            # sets the default attributes for ais shapes handles
            for h_ais_shape in loaded_h_ais_shape:
                self.op_viewer.display.Context.SetDeviationCoefficient(h_ais_shape,
                                                                       self.op_viewer.DC /
                                                                       self.op_viewer.default_shape_factor)
                self.op_viewer.display.Context.SetHLRDeviationCoefficient(h_ais_shape,
                                                                          self.op_viewer.DC_HLR /
                                                                          self.op_viewer.default_shape_factor)
                self.op_viewer.display.Context.SetColor(h_ais_shape,
                                              shape_colordictionary[shape_colorlist[
                                                  (self.op_viewer.default_shape_color + number_of_cases) %
                                                  len(shape_colorlist)]])

                self.op_viewer.display.Context.SetTransparency(h_ais_shape, self.op_viewer.default_shape_transparency)

        # displays the handles of the ais_shapes in the viewer3d context.
        for h_ais_shape in default_displaying_h_ais_shape:
            self.op_viewer.display.Context.Display(h_ais_shape)


        return loaded_h_ais_shape, loaded_subshape_names

    def setQuality(self):
        """
        Sets quality to the current working AIS Shape

        @return None

        """
        if self._exceptionCatch():
            return

        factor = self.op_viewer.ui_shape_quality_dspn.value()

        for i in range(0, len(self.op_viewer.current_h_ais_shape)):
            self.op_viewer.display.Context.SetDeviationCoefficient(self.op_viewer.current_h_ais_shape[i],
                                                                   self.op_viewer.DC / factor)
            self.op_viewer.display.Context.SetHLRDeviationCoefficient(self.op_viewer.current_h_ais_shape[i],
                                                                      self.op_viewer.DC_HLR / factor)

        if self.op_viewer.selectionMode == "surf":
            if self.op_viewer.ui_subcase_list.count() / 2 < len(self.op_viewer.ui_subcase_list.selectedIndexes()):
                self.op_viewer.case_node.setShapeQuality(factor)

            for i in range(0, len(self.op_viewer.ui_subcase_list.selectedIndexes())):
                self.op_viewer.case_node.subshape[self.op_viewer.ui_subcase_list.selectedIndexes()[i].row()][3] = factor

        if self.op_viewer.selectionMode == "shape":
            for i in range(0, len(self.op_viewer.case_node.subshape)):
                self.op_viewer.case_node.subshape[i][3] = factor

    def setTransparency(self):
        """
        Sets transparency to the current working AIS Shape

        @return None

        """
        if self._exceptionCatch():
            return

        transparency = self.op_viewer.ui_shape_transparency_dspn.value()

        for i in range(0, len(self.op_viewer.current_h_ais_shape)):
            self.op_viewer.display.Context.SetTransparency(self.op_viewer.current_h_ais_shape[i], transparency)

        if self.op_viewer.selectionMode == "surf":
            # If the selected items is the majority of the list, then the property is set to the whole Case
            if self.op_viewer.ui_subcase_list.count() / 2 < len(self.op_viewer.ui_subcase_list.selectedIndexes()):
                self.op_viewer.case_node.setShapeTransparency(transparency)

            # set the properties to to the selected shapes
            for i in range(0, len(self.op_viewer.ui_subcase_list.selectedIndexes())):
                index = self.op_viewer.ui_subcase_list.selectedIndexes()[i]
                self.op_viewer.case_node.subshape[index.row()][1] = transparency

        if self.op_viewer.selectionMode == "shape":
            for i in range(0, len(self.op_viewer.case_node.subshape)):
                self.op_viewer.case_node.subshape[i][1] = transparency

    def setColor(self):
        """
        Sets color to the current working AIS Shape

        @return None

        """
        if self._exceptionCatch():
            return

        current_color_combo = self.op_viewer.ui_shape_setcolor_combo.currentText()
        current_color_index_combo = self.op_viewer.ui_shape_setcolor_combo.currentIndex()

        for i in range(0, len(self.op_viewer.current_h_ais_shape)):
            self.op_viewer.display.Context.SetColor(self.op_viewer.current_h_ais_shape[i], shape_colordictionary[current_color_combo])

            self.op_viewer.model.dataChanged.emit(self.op_viewer.ui_case_treeview.currentIndex(),
                                                  self.op_viewer.ui_case_treeview.indexAbove(self.op_viewer.ui_case_treeview.currentIndex()))

        if self.op_viewer.selectionMode == "surf":
            # If the selected items is the majority of the list, then the property is set to the whole Case
            if self.op_viewer.ui_subcase_list.count() / 2 < len(self.op_viewer.ui_subcase_list.selectedIndexes()):
                self.op_viewer.case_node.setShapeColor(current_color_index_combo)

            for i in range(0, len(self.op_viewer.ui_subcase_list.selectedIndexes())):
                index = self.op_viewer.ui_subcase_list.selectedIndexes()[i]
                self.op_viewer.case_node.subshape[index.row()][2] = current_color_index_combo

        if self.op_viewer.selectionMode == "shape":
            for i in range(0, len(self.op_viewer.case_node.subshape)):
                self.op_viewer.case_node.subshape[i][2] = current_color_index_combo

        # self.display.Context.HilightWithColor(self.h_aisshape, Quantity_NOC_WHITE)

        return

    def setTranslation(self):
        """
        Creates an axis in x, y or z depending on user preference.

        gp_Ax1 describes an axis in 3D space. An axis is defined by a point (gp_Pnt) and a direction (gp_Dir) reference

        @return None

        """
        if self._exceptionCatch():
            return

        rotataxis_index_combo = self.op_viewer.ui_shape_rotataxis_combo.currentIndex()

        if self.op_viewer.ui_shape_rotataxis_combo.currentText() == "Z":
            ax1 = gp_Ax1(gp_Pnt(0., 0., 0.), gp_Dir(0, 0, 1))
        elif self.op_viewer.ui_shape_rotataxis_combo.currentText() == "Y":
            ax1 = gp_Ax1(gp_Pnt(0., 0., 0.), gp_Dir(0, 1, 0))
        elif self.op_viewer.ui_shape_rotataxis_combo.currentText() == "X":
            ax1 = gp_Ax1(gp_Pnt(0., 0., 0.), gp_Dir(1, 0, 0))

        # Retrieve the displacements set by user

        x = float(self.op_viewer.ui_shape_xdispl_dspn.value())
        y = float(self.op_viewer.ui_shape_ydispl_dspn.value())
        z = float(self.op_viewer.ui_shape_zdispl_dspn.value())
        teta = float(self.op_viewer.ui_shape_tetarotat_dspn.value()) * pi / 180

        # creates objects of shape transformation (Returns the identity transformation),
        # one for axial and other for x, y, z coordinates
        transf_teta = gp_Trsf()
        transf_xyz = gp_Trsf()

        transf_teta.SetRotation(ax1, teta)

        transf_xyz.SetTranslation(gp_Vec(x, y, z))

        # Calculates the transformation matrix with respect of both transformations.
        transf_matrix = transf_xyz * transf_teta

        # Constructs an local coordinate system object. Note: A Location constructed from a default datum is said
        # to be "empty".
        # ref: https://www.opencascade.com/doc/occt-6.9.1/refman/html/class_top_loc___location.html
        cube_toploc = TopLoc_Location(transf_matrix)

        # Then applies the local coordinate to the current shape
        for i in range(0, len(self.op_viewer.current_h_ais_shape)):
            self.op_viewer.display.Context.SetLocation(self.op_viewer.current_h_ais_shape[i], cube_toploc)

        if self.op_viewer.selectionMode == "surf":
            # If the selected items is the majority of the list, then the property is set to the whole Case
            if self.op_viewer.ui_subcase_list.count() / 2 < len(self.op_viewer.ui_subcase_list.selectedIndexes()):
                self.op_viewer.case_node.setShapeTransformation(x, 0)
                self.op_viewer.case_node.setShapeTransformation(y, 1)
                self.op_viewer.case_node.setShapeTransformation(z, 2)
                self.op_viewer.case_node.setShapeTransformation(teta / pi * 180, 3)
                self.op_viewer.case_node.setShapeTransformation(rotataxis_index_combo, 4)

            for i in range(0, len(self.op_viewer.ui_subcase_list.selectedIndexes())):
                index = self.op_viewer.ui_subcase_list.selectedIndexes()[i]
                self.op_viewer.case_node.subshape[index.row()][0] = [x, y, z, teta / pi * 180, rotataxis_index_combo]


        if self.op_viewer.selectionMode == "shape":
            for i in range(0, len(self.op_viewer.case_node.subshape)):
                self.op_viewer.case_node.subshape[i][0][0] = x
                self.op_viewer.case_node.subshape[i][0][1] = y
                self.op_viewer.case_node.subshape[i][0][2] = z
                self.op_viewer.case_node.subshape[i][0][3] = teta / pi * 180
                self.op_viewer.case_node.subshape[i][0][4] = rotataxis_index_combo

        self.op_viewer.display.Context.UpdateCurrentViewer()

        return

    def hideShape(self):
        """
        Method for hiding selected shape.

        @return None
        """
        if self._exceptionCatch():
            return

        self.op_viewer.display.Context.EraseSelected()

    def displayShape(self):
        """
        Method for displaying selected shape.

        @return None
        """
        if self._exceptionCatch():
            return

        self.op_viewer.display.Context.DisplaySelected()
        self.op_viewer._surfaceChanged()

    def _exceptionCatch(self):
        """
        This functions is a exception catcher: if user tries to wrongly set properties when there is nothing to be
        applied by them


        @return None
        """

        number_of_cases = self.op_viewer.model.rowCount(self.op_viewer.ui_case_treeview.rootIndex())
        if self.op_viewer.current_h_ais_shape is None or number_of_cases == 0:
            print("Action not feasible")
            return True
