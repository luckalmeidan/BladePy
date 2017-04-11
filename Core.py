"""@package Core

File that holds the main class BladePyCore for BladePy.
The class inherits modules of the application and display them as widgets. When Core is run, it displays
bladepro_modules.inputfile_writer.InputWriterWindow to start off a case. The user then can setup a BladePro input file
to Run it. The output files generated by BladePro are then displayed the BladePy Output viewer.

It has the BladePyCore Class, which inherits:

\arg \c QtGui.QMainWindow, base class for GUI interface
\arg \c BladePyCore.Ui_MainWindow, base class with function-less layout created in Qt Designer


"""

import os

output_viewer_dir = os.path.dirname(__file__)


ui_file = os.path.join(output_viewer_dir, "output_viewerUI.ui")
py_ui_file = os.path.join(output_viewer_dir, "output_viewerUI.py")

os.system("pyuic4 -x %s -o %s" % (ui_file, py_ui_file))

# OpenCascade Libraries
from OCC.Display.backend import load_backend

used_backend = load_backend()

from OCC.Display.qtDisplay import qtViewer3d

# PyQt Library
from PyQt4 import QtCore, QtGui, uic

# Internal Modules
from occ_modules.shape_properties import ShapeManager, shape_colorlist, shape_colordictionary
from occ_modules.qt_display import customQtViewer3d

from tecplot_modules.tecplot_display import TecPlotWindow

from data_structure.case_model import CaseModel
from data_structure.case_node import CaseNode

from bladepro_modules.inputfile_writer import InputWriterWindow
from settings.preferences import PreferencesBladePy

# Misc import
import logging
import sys
from copy import deepcopy
import functools

import output_viewerUI

# This dictionary works because depending on OS, e.g. the register might save False as false, crashing the program
dct = {"true": True, "false": False, True: True, False: False}

class BladePyCore(QtGui.QMainWindow, output_viewerUI.Ui_MainWindow):
    """
    This is the key Class that wraps all the other packages and modules of BladePy.

    This class is responsible for adding functions to the inherited output_viewerUI.Ui_MainWindow function-less
    layout created in Qt Designer.

    This class has methods for managing the display of the outputs generated by BladePro. It has the methods for
    loading any case that was previously generated by BladePro. It can also retrieve the outputs of BladePro as soon
    as they were created if desired in the bladepro_modules.inputfile_writer.InputWriterWindow

    Classes of other BladePy modules of objects created by BladePyCore (composition association)

    For output display:
    \arg \c bladepro_modules.inputfile_writer.InputWriterWindow - For writing inputfiles and BladePro communication
    \arg \c tecplot_modules.tecplot_display.TecPlotWindow - For displaying tecplot graphics
    \arg \c occ_modules.qt_display.customQtViewer3d - For creating a customized viewer for OpenCascade
    \arg \c occ_modules.shape_properties.customQtViewer3d - For creating a customized viewer for OpenCascade

    For data management:
    \arg \c data_structure.case_model.CaseModel - For creating a model for TreeView list
    \arg \c data_structure.case_node.CaseNode - For creating a information center for cases

    For user settings:
    \arg \c settings.preferences.PreferencesBladePy - For managing User Preferences

    """

    def __init__(self, parent=None):

        super(BladePyCore, self).__init__(parent)
        # declaring instance attributes

        ## This attribute is used all around the code and represents the "working" shape.
        self.current_h_ais_shape = None

        ## This attribute is the entity that represents the unity of a case
        self.case_node = None
        self.previous_case_node = None

        ## This attribute is one that is used by the program to tell whether the user is managing a shape or sub-shape
        self.selectionMode = ""

        ## This attribute is a list that contains all shapes loaded in the program
        self.master_shape_list = []

        self.list_settings = []
        self.setupUi(self)
        self.setWindowTitle("BladePy - Output Viewer")

        #
        self.PreferencesManager = PreferencesBladePy(OutputViewerWidget=self)

        ## This attribute is an object used for managing shape properties
        self.ShapeManager = ShapeManager(OutputViewerWidget=self)

        # Setuping GUIs menus
        self._setGUIMenus()

        ## This attribute is the object node of all case nodes.
        self.rootNode = CaseNode("RootNode")

        ## This attribute is the model object that is the intermediary between the tree view and the case node
        self.model = CaseModel(self.rootNode, self)
        self.ui_case_treeview.setModel(self.model)
        self._dataMapper = QtGui.QDataWidgetMapper()

        self.ui_case_treeview.clicked.connect(self._setSelection)
        self.ui_subcase_list.itemClicked.connect(self._surfaceChanged)

        ## This is the object of the QtViewer of PythonOCC
        self.canva = customQtViewer3d(self)
        self.setCentralWidget(self.canva)
        self.canva.InitDriver()

        ## This attribute is OCCViewer.Viewer3d(self.GetHandle()), used to manage the 3D graphics.
        self.display = self.canva._display
        self.display.set_bg_gradient_color(137, 159, 200, 210, 218, 234)

        # Get default display Quality
        ais_context = self.display.GetContext().GetObject()

        self.DC = ais_context.DeviationCoefficient()
        self.DC_HLR = ais_context.HLRDeviationCoefficient()

        # Start linking objects to functions here

        # show/hide shape
        self.ui_shape_hide_btn.clicked.connect(self.ShapeManager.hideShape)
        self.ui_shape_display_btn.clicked.connect(self.ShapeManager.displayShape)

        # Linking graphic options buttons
        self.ui_shape_quality_btn.clicked.connect(self.ShapeManager.setQuality)
        self.ui_shape_settransparency_btn.clicked.connect(self.ShapeManager.setTransparency)
        self.ui_shape_setcolor_btn.clicked.connect(self.ShapeManager.setColor)

        # Linking translation and rotation buttons
        self.ui_shape_settranslation_btn.clicked.connect(self.ShapeManager.setTranslation)

        # Linking views signals
        self.ui_display_zoomfactor_dspn.valueChanged.connect(self.setZoomFactor)

        # Linking misc. functions
        self.ui_deletecase_btn.clicked.connect(self.deleteCase)


        # Setuping tecplot widget from tecplot_modules
        self.TecplotViewerWidget = TecPlotWindow(OutputViewerWidget=self)
        self.ui_tecplot_widget_vl.addWidget(self.TecplotViewerWidget)

        # Linking tecplot buttons
        self.ui_tecplot_setneutral_btn.clicked.connect(self.TecplotViewerWidget.setNeutral)
        self.ui_tecplot_setinvisible_btn.clicked.connect(self.TecplotViewerWidget.setVisibility)
        self.ui_tecplot_toggle_meanlines_btn.clicked.connect(self.TecplotViewerWidget.toggleMeanLines)
        self.ui_tecplot_toggle_bladeprofiles_btn.clicked.connect(self.TecplotViewerWidget.toggleBladeProfiles)

        # Setuping input writer widget from module. Linking signals
        self.InputWriterWidget = InputWriterWindow(OutputViewerWidget=self)

        self.InputWriterWidget.show()

        # Setuping default options

        self.PreferencesManager.applyAction()

    def toolbarViewButtonPressedGroup(self, pressed_btn):
        """
        Method group that wrap all functions for shape viewing toolbar.


        @param pressed_btn [QtGui.QAction] Signal emitted by button clicked on ui_view_toolbar
        @return None

        """
        if pressed_btn.text() == "Front":
            self.display.View_Front()

        if pressed_btn.text() == "Top":
            self.display.View_Top()

        if pressed_btn.text() == "Left":
            self.display.View_Left()

        if pressed_btn.text() == "Rear":
            self.display.View_Rear()

        if pressed_btn.text() == "Bottom":
            self.display.View_Bottom()

        if pressed_btn.text() == "Right":
            self.display.View_Right()

        if pressed_btn.text() == "Axonometric":
            self.display.View_Iso()

        if pressed_btn.text() == "Fit all":
            self.display.FitAll()

        #
        if pressed_btn.text() == "Flat lines":
            self.display.SetModeShaded()
            self.display.Context.DefaultDrawer().GetObject().SetFaceBoundaryDraw(True)
            self.display.View.EnableDepthTest(False)

            for h_shape in self.master_shape_list:
                self.display.Context.SetColor(h_shape, self.display.Context.Color(h_shape))  # Not Optimum Solution

        if pressed_btn.text() == "Shaded":
            self.display.SetModeShaded()
            self.display.Context.DefaultDrawer().GetObject().SetFaceBoundaryDraw(False)
            self.display.View.Redraw()

            for h_shape in self.master_shape_list:
                self.display.Context.SetColor(h_shape, self.display.Context.Color(h_shape))  # Not Optimum Solution

        if pressed_btn.text() == "Wireframe":
            self.display.SetModeWireFrame()

    def toolbarFileButtonPressedGroup(self, pressed_btn):
        """
        Method group that wrap all functions for "file" toolbar.

        @param pressed_btn [QtGui.QAction] Signal emitted by button clicked on ui_file_toolbar
        @return None

        """
        if pressed_btn.text() == "Create New Case":
            self.InputWriterWidget.show()
            self.InputWriterWidget.raise_()
        if pressed_btn.text() == "Open BladePro Case":
            self.openCase()

    def toolbarTecplotButtonPressedGroup(self, pressed_btn):
        """
        Method group that wrap all functions for tecplot options in toolbar.

        @param pressed_btn [QtGui.QAction] Signal emitted by button clicked on ui_tecplot_toolbar
        @return None
        """

        if pressed_btn.text() == "tabify":
            self.TecplotViewerWidget.tabifyDockWidget(self.TecplotViewerWidget.ui_tecplot1_dockw,
                                                      self.TecplotViewerWidget.ui_tecplot2_dockw)
            self.TecplotViewerWidget.ui_tecplot1_dockw.raise_()

        if pressed_btn.text() == "set_horizontal":
            self.TecplotViewerWidget.splitDockWidget(self.TecplotViewerWidget.ui_tecplot1_dockw,
                                                     self.TecplotViewerWidget.ui_tecplot2_dockw, QtCore.Qt.Vertical)

            self.TecplotViewerWidget.splitDockWidget(self.TecplotViewerWidget.ui_tecplot1_dockw,
                                                     self.TecplotViewerWidget.ui_tecplot2_dockw, QtCore.Qt.Horizontal)

        if pressed_btn.text() == "set_vertical":
            self.TecplotViewerWidget.splitDockWidget(self.TecplotViewerWidget.ui_tecplot1_dockw,
                                                     self.TecplotViewerWidget.ui_tecplot2_dockw, QtCore.Qt.Horizontal)

            self.TecplotViewerWidget.splitDockWidget(self.TecplotViewerWidget.ui_tecplot1_dockw,
                                                     self.TecplotViewerWidget.ui_tecplot2_dockw, QtCore.Qt.Vertical)

        if pressed_btn.text() == "debug_tecplot":  # developer
            self.TecplotViewerWidget.DebugTecplot_Function()

    def toolbarSettingsButtonPressedGroup(self, pressed_btn):
        """
        Method group that wrap all functions for "settings" toolbar.

        @param pressed_btn [QtGui.QAction] Signal emitted by button clicked on ui_file_toolbar
        @return None

        """
        if pressed_btn.text() == "Preferences":
            self.PreferencesManager.show()
            self.PreferencesManager.raise_()

    def menuFileButtonPressedGroup(self, pressed_btn):
        """
        Method group that wrap only exit function for "file" menu.

        @param pressed_btn [QtGui.QAction] Signal emitted by button clicked on ui_file_menur
        @return None
        """
        # TODO Naybe this is not the best way to exit the program
        if pressed_btn.text() == "Exit":
            self.InputWriterWidget.close()
            self.close()
            QtCore.QCoreApplication.exit()
            sys.exit()

    def openCase(self):
        """
        Opens a case previously generated by BladePro.

        Any file generated by BladePro can be used to open case. The program will look for other files with the same
        case name in the same folder.

        @return None

        """
        repeated_case = []
        # First triggers a GUI FileDialog.
        selected_files = QtGui.QFileDialog.getOpenFileNames(self, 'Open file',
                                                            self.InputWriterWidget.ui_working_path_edit.text(),
                                                            "(*.dat *.igs *.iges *.rtzt);; All Files(*.*)")

        # Case the user gives up opening a BladePro case

        # Sets the working_path attribute of Input Writer Widget to facilitate opening further files. It will memorize
        # the folder of the last loaded case.

        for file in selected_files:
            self.InputWriterWidget.working_path = os.path.dirname(file)

            # Removes the path from the selected file.
            file_geometry = os.path.basename(file)

            # Strips the file from the extension.
            case_name = file_geometry[:file_geometry.index('.')]

            # Prevents the program from loading repeated Cases for files from same Case
            if case_name in repeated_case:
                continue

            repeated_case.append(case_name)
            # As stated before, it will set Input Writer fields.
            self.InputWriterWidget.ui_case_name_edit.setText(case_name)
            self.InputWriterWidget.ui_working_path_edit.setText(self.InputWriterWidget.working_path)

            # Triggers method for adding a case
            self.addCase()



    def addCase(self)-> object:

        """
        Method that adds a Case in Output Viewer.

        This will be triggered by the Output Viewer when opening an existing case or when Run BladePro button
        is clicked in in the Input Writer GUI. This method will read files related to the working case. Currently, the
        addCase method supports three outputs from BladePro.

        \arg IGS 3D Curves;
        \arg IGS Surfaces;
        \arg Tecplots 2D.

        @return None

        """

        to_be_loaded_shape_list = []


        igs_surf_exists = False
        igs_3d_cur_exists = False
        igs_2d_cur_exists = False
        tecplot_exists = False

        self.PreferencesManager.list_settings[1].beginGroup("outputs_settings")

        igs_surf_check_state = dct[self.PreferencesManager.list_settings[1].value("default_igs_surf_check_state")]
        igs_cur_3d_check_state = dct[self.PreferencesManager.list_settings[1].value("default_igs_3d_cur_check_state")]
        igs_cur_2d_check_state = dct[self.PreferencesManager.list_settings[1].value("default_igs_2d_cur_check_state")]
        tecplot_2d_check_state = dct[self.PreferencesManager.list_settings[1].value("default_tecplot_check_state")]

        igs_surf_exception = self.PreferencesManager.list_settings[1].value("default_igs_surf_exception")
        igs_3d_cur_exception = self.PreferencesManager.list_settings[1].value("default_igs_3d_cur_exception")
        igs_2d_cur_exception = self.PreferencesManager.list_settings[1].value("default_igs_2d_cur_exception")

        self.PreferencesManager.list_settings[1].endGroup()

        # Gets the name of the adding case in a field in Input Writer Widget
        to_add_case_name = self.InputWriterWidget.ui_case_name_edit.text()

        if tecplot_2d_check_state:
            # Gets the -possible- tecplot output of BladePro
            tecplot_output_file_path = os.path.join(self.InputWriterWidget.ui_working_path_edit.text(),
                                          self.InputWriterWidget.ui_case_name_edit.text()) + ".2d.tec.dat"

            # bool of existence of a tecplot output for the adding case
            tecplot_exists = os.path.isfile(tecplot_output_file_path)

        # same as tecplot output for igs surf output
        if igs_surf_check_state:
            igs_surf_output_file_path = os.path.join(self.InputWriterWidget.ui_working_path_edit.text(),
                                    self.InputWriterWidget.ui_case_name_edit.text()) + ".surf.igs"

            igs_surf_exists = os.path.isfile(igs_surf_output_file_path)

            # gives an extra chance of opening a .igs file by eliminating .surf of the name
            if not igs_surf_exists:
                igs_surf_output_file_path = os.path.join(self.InputWriterWidget.ui_working_path_edit.text(),
                                        self.InputWriterWidget.ui_case_name_edit.text()) + ".igs"
                igs_surf_exists = os.path.isfile(igs_surf_output_file_path)

        if igs_cur_3d_check_state:
            # same as tecplot output for igs 3d curves output
            igs_3d_cur_output_file_path = os.path.join(self.InputWriterWidget.ui_working_path_edit.text(),
                                      self.InputWriterWidget.ui_case_name_edit.text()) + ".cur.igs"

            igs_3d_cur_exists = os.path.isfile(igs_3d_cur_output_file_path)

        if igs_cur_2d_check_state:
            # same as tecplot output for igs 3d curves output
            igs_2d_cur_output_file_path = os.path.join(self.InputWriterWidget.ui_working_path_edit.text(),
                                      self.InputWriterWidget.ui_case_name_edit.text()) + ".mpth.igs"

            igs_2d_cur_exists = os.path.isfile(igs_2d_cur_output_file_path)

        # if not a single file is found for the adding case, displays a message and returns
        if not any([tecplot_exists, igs_surf_exists, igs_3d_cur_exists, igs_2d_cur_exists]):
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Information)

            msg.setText("No BladePro Outputs to display")
            msg.setWindowTitle("No Output")

            msg.exec_()
            return
        # starts loading CAD files

        # Mistake-prevention of user filling of exception list
        permited_characters_except_list = [" ", ",", "/"]
        for permited_character in permited_characters_except_list:
            igs_surf_exception = igs_surf_exception.replace(permited_character, ";")
            igs_3d_cur_exception = igs_3d_cur_exception.replace(permited_character, ";")
            igs_2d_cur_exception = igs_2d_cur_exception.replace(permited_character, ";")

        igs_surf_exception = igs_surf_exception.split(";")
        igs_3d_cur_exception = igs_3d_cur_exception.split(";")
        igs_2d_cur_exception = igs_2d_cur_exception.split(";")

        # appending all igs files to one list to be loaded by iges_reader
        if igs_surf_exists:
            to_be_loaded_shape_list.append([igs_surf_output_file_path, igs_surf_exception])

        if igs_3d_cur_exists:
            to_be_loaded_shape_list.append([igs_3d_cur_output_file_path, igs_3d_cur_exception])

        if igs_2d_cur_exists:
            to_be_loaded_shape_list.append([igs_2d_cur_output_file_path, igs_2d_cur_exception])

        # Calling the method loading a shape
        loaded_h_ais_shape, loaded_subshape_names = self.ShapeManager.loadShape(to_be_loaded_shape_list)

        # end of IGS shape loading routine
        loaded_tecplot_plotlines_list = []

        # start of tecplot output loading. If the adding case does have this output type
        if tecplot_exists:

            # calls a method of Tecplot Widget for loading the csv file.
            self.TecplotViewerWidget.openTecplot(tecplot_output_file_path)

            # fetches the attributes loaded in the Tecplot Widget
            loaded_tecplot_blade_plotlines = self.TecplotViewerWidget.tecplot_blade_plotlines
            loaded_tecplot_stream_plotlines = self.TecplotViewerWidget.tecplot_stream_plotlines
            loaded_tecplot_mean_plotlines = self.TecplotViewerWidget.tecplot_mean_plotlines
            loaded_tecplot_profile_plotlines = self.TecplotViewerWidget.tecplot_profile_plotlines
            loaded_tecplot_thickness_plotlines = self.TecplotViewerWidget.tecplot_thickness_plotlines

            # Group all Tcplots in a single list with all lists
            loaded_tecplot_plotlines_list.append(loaded_tecplot_blade_plotlines)
            loaded_tecplot_plotlines_list.append(loaded_tecplot_stream_plotlines)
            loaded_tecplot_plotlines_list.append(loaded_tecplot_profile_plotlines)
            loaded_tecplot_plotlines_list.append(loaded_tecplot_mean_plotlines)
            loaded_tecplot_plotlines_list.append(loaded_tecplot_thickness_plotlines)

            # Glitch is expected for the line below. If so, just put a try/except.
            try:
                loaded_tecplot_meanbeta_plotlines = self.TecplotViewerWidget.tecplot_meanbeta_plotlines
                loaded_tecplot_plotlines_list.append(loaded_tecplot_meanbeta_plotlines)
            except AttributeError:
                pass

        # Creates a Case Node from datastructure module with the loaded shape and loaded tecplot

        CaseNode(to_add_case_name, loaded_h_ais_shape, loaded_subshape_names, loaded_tecplot_plotlines_list,
                 self.rootNode)

        # Updates the model for the tree view and sets it.
        self.model = CaseModel(self.rootNode)
        self.ui_case_treeview.setModel(self.model)
        self.ui_case_treeview.setCurrentIndex(self.model.index(self.model.rowCount(
            self.ui_case_treeview.rootIndex()) - 1, 0, self.ui_case_treeview.rootIndex()))

        # Maps the Case Node to fields in the GUI
        self._setMapper()

        # Enabling Buttons after loading file:

        self.selectionMode = "shape"

        # Raise the screen with loaded outputs
        self.show()
        self.raise_()
        self._setSelection(self.ui_case_treeview.currentIndex(), old=None)

    def deleteCase(self):
        """
        Method for deleting loaded cases in model tree view.

        It deletes the interactive AIS Shape, the tecplots from Display and data structure.

        @return None

        """
        # Firstly, removes all lines in a nested loop

        # Verify if there is anything to delete. If not, return function
        if self.model.rowCount(self.ui_case_treeview.rootIndex()) == 0:
            return

        for n in range(0, len(self.case_node.tecplotLists())):
            for line in self.case_node.tecplotLists()[n]:
                line.remove()

        # Updates canvas
        self.TecplotViewerWidget._canvas_1.draw()
        self.TecplotViewerWidget._canvas_2.draw()
        self.current_h_ais_shape = self.case_node.shapeHAIS()

        for i in range(0, len(self.current_h_ais_shape)):
            self.display.Context.Remove(self.current_h_ais_shape[i])

        # Remove the node from data structure.
        self.case_node.parent().removeChild(self.case_node.row())

        # Re-sets model and re-applies it to the tree view list
        self.model = CaseModel(self.rootNode)
        self.ui_case_treeview.setModel(self.model)
        self.ui_subcase_list.clear()

        # The code is used to make the last item of the list selected.
        # Exception when deleting last object in list. It will try to do remapping, but there is nothing else to remap.
        try:
            self.ui_case_treeview.setCurrentIndex(self.model.index(self.model.rowCount(
                self.ui_case_treeview.rootIndex()) - 1, 0, self.ui_case_treeview.rootIndex()))

            self._setSelection(self.ui_case_treeview.currentIndex(), old=None)
            self._setMapper()
        except IndexError:
            pass

    def setZoomFactor( self ):
        """
        Sets the zoom factor for shape viewing.

        @return None

        """
        self.canva.zoomfactor = self.ui_display_zoomfactor_dspn.value()

    def _surfaceChanged( self ):
        """
        Method function that controls the situation when a sub-shape is selected in the ListWidget.

        This trigger the mapping of the sub-shape individual properties to the controls in the GUI

        @return None

        """

        if self.ui_subcase_list.selectedIndexes() == []:
            self._setSelection(self.ui_case_treeview.currentIndex(), old=None)
            return

        # This is a trigger that identifies that the program is in surface mode selection
        self.selectionMode = "surf"
        subshape_ref = self.case_node.subshape[self.ui_subcase_list.currentRow()]

        # Mapping the subshape to the GUI controls
        self.ui_shape_transparency_dspn.setValue(subshape_ref[1])
        self.ui_shape_setcolor_combo.setCurrentIndex(subshape_ref[2])
        self.ui_shape_quality_dspn.setValue(subshape_ref[3])
        self.ui_shape_xdispl_dspn.setValue(float(subshape_ref[0][0]))
        self.ui_shape_ydispl_dspn.setValue(float(subshape_ref[0][1]))
        self.ui_shape_zdispl_dspn.setValue(float(subshape_ref[0][2]))
        self.ui_shape_tetarotat_dspn.setValue(float(subshape_ref[0][3]))
        self.ui_shape_rotataxis_combo.setCurrentIndex(
            int(subshape_ref[0][4]))

        # When the selection is in "Surf" mode, the mapping of the case is temporary deactivated.
        self._removeMapper()

        # Gets the shape of the current case
        self.current_h_ais_shape = self.case_node.shapeHAIS()

        sub_shape = []
        # Gets the subshape selected in TreeWidget in the current case shape
        for i in range(0, len(self.ui_subcase_list.selectedIndexes())):
            sub_shape.append(self.current_h_ais_shape[self.ui_subcase_list.selectedIndexes()[i].row()])

        # Sets that the current working shape handle is the list of sub_shapes
        self.current_h_ais_shape = sub_shape

        self.display.Context.ClearSelected()

        # When subshapes are clicked in the TreeWidget, they are highlighted for identification.
        for i in range(0, len(self.current_h_ais_shape)):
            self.display.Context.AddOrRemoveSelected(self.current_h_ais_shape[i])

    def _setSelection( self, current, old=None ):
        """
        This function is a slot that many signals reach. Mainly by tree view object signal
        QtCore.SIGNAL("currentChanged(QModelIndex, QModelIndex)". It is necessary to modify the
        instance variable case_node to the tree view pointer, so others methods can change data in CaseNodes object.


        @param current [QtCore.QModelIndex] Model index of tree view that is current selection
        @param old [QtCore.QModelIndex] Model index of tree view that was previous selection

        @return None

        """
        self.selectionMode = "shape"
        self.case_node = current.internalPointer()

        # Except in case when there is no previously selected item in model list. This except will catch errors
        # every time you load a case for the first time. AttributeError is NoneType does not has .internalPointer.
        try:
            self.previous_case_node = old.internalPointer()
        except AttributeError:
            pass

        self.current_h_ais_shape = self.case_node.shapeHAIS()
        self.ui_subcase_list.clear()

        for i in range(0, len(self.current_h_ais_shape)):
            self.ui_subcase_list.addItem(self.case_node._supshape_names[i])

        self.display.Context.ClearSelected()

        for i in range(0, len(self.current_h_ais_shape)):
            self.display.Context.AddOrRemoveSelected(self.current_h_ais_shape[i])

        self.display.Context.UpdateCurrentViewer()

        # if cause for syncing buttons to selected case
        if self.case_node.tecplotIsVisible():
            self.ui_tecplot_setinvisible_btn.setChecked(False)
            self.ui_tecplot_setneutral_btn.setEnabled(True)
            self.ui_tecplot_toggle_bladeprofiles_btn.setEnabled(True)
            self.ui_tecplot_toggle_meanlines_btn.setEnabled(True)

        else:
            self.ui_tecplot_setinvisible_btn.setChecked(True)
            self.ui_tecplot_setneutral_btn.setEnabled(False)
            self.ui_tecplot_toggle_bladeprofiles_btn.setEnabled(False)
            self.ui_tecplot_toggle_meanlines_btn.setEnabled(False)

        if self.case_node.tecplotBladeProfilesIsVisible():
            self.ui_tecplot_toggle_bladeprofiles_btn.setChecked(False)
        else:
            self.ui_tecplot_toggle_bladeprofiles_btn.setChecked(True)

        if self.case_node.tecplotMeanLinesIsVisible():
            self.ui_tecplot_toggle_meanlines_btn.setChecked(False)
        else:
            self.ui_tecplot_toggle_meanlines_btn.setChecked(True)

        if self.case_node.tecplotIsNeutral():
            self.ui_tecplot_setneutral_btn.setChecked(True)
        else:
            self.ui_tecplot_setneutral_btn.setChecked(False)

        self._setMapper()

    def _setMapper( self ):
        """
        This function is called for wrapping tree view and UI controls, mapping the item selection with the controls
        in UI, e.g. Shape Quality, Transparency, Color etc.

        @return None

        """
        self.ui_case_treeview.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self._dataMapper.setModel(self.model)
        self._dataMapper.addMapping(self.ui_selectedcase_edit, 0)
        self._dataMapper.addMapping(self.ui_tecplot_setneutral_btn, 1, 'selectedOption')
        self._dataMapper.addMapping(self.ui_shape_quality_dspn, 3)
        self._dataMapper.addMapping(self.ui_shape_transparency_dspn, 4)
        self._dataMapper.addMapping(self.ui_shape_setcolor_combo, 5, 'currentIndex')
        self._dataMapper.addMapping(self.ui_shape_xdispl_dspn, 6)
        self._dataMapper.addMapping(self.ui_shape_ydispl_dspn, 7)
        self._dataMapper.addMapping(self.ui_shape_zdispl_dspn, 8)
        self._dataMapper.addMapping(self.ui_shape_tetarotat_dspn, 9)
        self._dataMapper.addMapping(self.ui_shape_rotataxis_combo, 10, 'currentIndex')

        self._dataMapper.setCurrentModelIndex(self.ui_case_treeview.currentIndex())

    def _removeMapper( self ):
        """
        This function is called for unwrapping tree view and UI controls, mapping the item selection with the controls
        in UI, e.g. Shape Quality, Transparency, Color etc.

        @return None
        """
        self._dataMapper.setModel(self.model)
        self._dataMapper.removeMapping(self.ui_selectedcase_edit)
        self._dataMapper.removeMapping(self.ui_tecplot_setneutral_btn)
        self._dataMapper.removeMapping(self.ui_shape_quality_dspn)
        self._dataMapper.removeMapping(self.ui_shape_transparency_dspn)
        self._dataMapper.removeMapping(self.ui_shape_setcolor_combo)
        self._dataMapper.removeMapping(self.ui_shape_xdispl_dspn)
        self._dataMapper.removeMapping(self.ui_shape_ydispl_dspn)
        self._dataMapper.removeMapping(self.ui_shape_zdispl_dspn)
        self._dataMapper.removeMapping(self.ui_shape_tetarotat_dspn)
        self._dataMapper.removeMapping(self.ui_shape_rotataxis_combo)

    def _setGUIMenus(self):
        """
        This function setups the GUI menu.

        @return None
        """
        # Setting tecplot menu actions

        tecplot_actions = [QtGui.QAction(QtGui.QIcon(os.path.join(output_viewer_dir, "icons/tecplot/tabify.png")),
                                         "tabify", self),
                           QtGui.QAction(QtGui.QIcon(os.path.join(output_viewer_dir, "icons/tecplot/set_horizontal.png")),
                                         "set_horizontal", self),
                           QtGui.QAction(QtGui.QIcon(os.path.join(output_viewer_dir, "icons/tecplot/set_vertical.png")),
                                         "set_vertical", self)]

        for action in tecplot_actions:
            self.ui_tecplot_toolbar.addAction(action)

        self.ui_tecplot_toolbar.actionTriggered[QtGui.QAction].connect(self.toolbarTecplotButtonPressedGroup)

        # setting cad menu actions
        draw_actions = [QtGui.QAction(QtGui.QIcon(os.path.join(output_viewer_dir, "icons/views/flatlines_drawstyle.svg")),
                                      "Flat lines", self),
                        QtGui.QAction(QtGui.QIcon(os.path.join(output_viewer_dir, "icons/views/shaded_drawstyle.svg")),
                                      "Shaded", self),
                        QtGui.QAction(QtGui.QIcon(os.path.join(output_viewer_dir, "icons/views/wire_drawstyle.svg")),
                                      "Wireframe", self)]

        draw_shortcut = ["", "", ""]
        draw_actions = zip(draw_actions, draw_shortcut)

        view_actions_1 = [QtGui.QAction(QtGui.QIcon(os.path.join(output_viewer_dir, "icons/views/fitall_view.svg")),
                                        "Fit all", self),
                          QtGui.QAction(QtGui.QIcon(os.path.join(output_viewer_dir, "icons/views/iso_view.svg")),
                                        "Axonometric", self)]

        view_shortcut_1 = ["", "0"]
        view_actions_1 = zip(view_actions_1, view_shortcut_1)

        view_actions_2 = [QtGui.QAction(QtGui.QIcon(os.path.join(output_viewer_dir, "icons/views/front_view.svg")),
                                        "Front", self),
                          QtGui.QAction(QtGui.QIcon(os.path.join(output_viewer_dir, "icons/views/top_view.svg")),
                                        "Top", self),
                          QtGui.QAction(QtGui.QIcon(os.path.join(output_viewer_dir, "icons/views/right_view.svg")),
                                        "Right", self)]

        view_shortcut_2 = ["1", "2", "3"]
        view_actions_2 = zip(view_actions_2, view_shortcut_2)

        view_actions_3 = [QtGui.QAction(QtGui.QIcon(os.path.join(output_viewer_dir, "icons/views/bottom_view.svg")),
                                        "Bottom", self),
                          QtGui.QAction(QtGui.QIcon(os.path.join(output_viewer_dir, "icons/views/rear_view.svg")),
                                        "Rear", self),
                          QtGui.QAction(QtGui.QIcon(os.path.join(output_viewer_dir, "icons/views/left_view.svg")),
                                        "Left", self)]

        view_shortcut_3 = ["4", "5", "6"]
        view_actions_3 = zip(view_actions_3, view_shortcut_3)

        self._setAction(self.ui_draw_view_submenu_, self.ui_view_toolbar, draw_actions)
        self._setAction(self.ui_standard_view_submenu_, self.ui_view_toolbar, view_actions_1, True)
        self._setAction(self.ui_standard_view_submenu_, self.ui_view_toolbar, view_actions_2, True)
        self._setAction(self.ui_standard_view_submenu_, self.ui_view_toolbar, view_actions_3)

        self.ui_view_toolbar.actionTriggered[QtGui.QAction].connect(self.toolbarViewButtonPressedGroup)

        # setting file menu actions
        file_actions = [QtGui.QAction(QtGui.QIcon(os.path.join(output_viewer_dir, "icons/basic/Document-new.svg")),
                                      "Create New Case", self),
                        QtGui.QAction(QtGui.QIcon(os.path.join(output_viewer_dir, "icons/basic/Document-open.svg")),
                                      "Open BladePro Case", self)]

        file_shortcut = ["Ctrl+N", "Ctrl+O"]
        file_actions = zip(file_actions, file_shortcut)
        self._setAction(self.ui_file_menu_, self.ui_file_toolbar, file_actions, True)
        self.ui_file_toolbar.actionTriggered[QtGui.QAction].connect(self.toolbarFileButtonPressedGroup)

        settings_actions = [QtGui.QAction(QtGui.QIcon(os.path.join(output_viewer_dir, "icons/basic/Preferences.svg")),
                                          "Preferences", self)]
        settings_shortcut = ["Ctrl+P"]
        settings_actions = zip(settings_actions, settings_shortcut)
        self._setAction(self.ui_edit_menu, self.ui_settings_toolbar, settings_actions)
        self.ui_settings_toolbar.actionTriggered[QtGui.QAction].connect(self.toolbarSettingsButtonPressedGroup)
        self.ui_settings_toolbar.actionTriggered[QtGui.QAction].connect(self.toolbarSettingsButtonPressedGroup)

        ui_file_exit_action = [[QtGui.QAction(QtGui.QIcon(os.path.join(output_viewer_dir, "icons/basic/System-log-out.svg")),
                                              "Exit", self), "Ctrl+W"]]
        self._setAction(self.ui_file_menu_, None, ui_file_exit_action)
        self.ui_file_menu_.triggered[QtGui.QAction].connect(self.menuFileButtonPressedGroup)

    @staticmethod
    def _setAction(menu=None, toolbar=None, action_list=None, separator=False):
        """
        This function sets an action for a menu or a toolbar.

        @param menu [QtGui.QMenu] The menu to where the action will be added
        @param toolbar [QtGui.QToolBar] The toolbar to where the action will be added
        @param action_list [list(QtGui.QAction, str)] The list of actions and their shortcuts to be added
        @param separator [bool] Add separator in the menu if necessary

        @return None


        """
        for action in action_list:
            action[0].setShortcut(action[1])
            if menu is not None:
                menu.addAction(action[0])

            if toolbar is not None:
                toolbar.addAction(action[0])

        if separator:
            if menu is not None:
                menu.addSeparator()

            if toolbar is not None:
                toolbar.addSeparator()

    def _setDefaultOptions(self):
        """
        This function setups the GUIs default properties in the beginning of the algorithm.

        @return None
        """
        self.list_settings = self.PreferencesManager.list_settings

        # set initial values. This "default" variables will be used all around the program.
        # If the user hit Ok or Apply in the Preferences window, this method will be called again to update the
        # default variables



    def _toggleStatusBar(self):
        """
        [NOT IMPLEMENTED]

        """
        pass
        # self.statusbar.hideOrShow()

def main():
    app = QtGui.QApplication(sys.argv)

    main_window = BladePyCore()
    # MainWindow.setgui()
    app.exec_()

    # inifile.close()
    print("End of Main Function UI")
    sys.exit(app.exec_())
    return main_window


if __name__ == "__main__":
    main()