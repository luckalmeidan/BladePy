"""
@package bladepro_modules.inputfile_writer

File that contains the class InputWriterWindow for adding functions to the BladePy InputWriter layout created in
Qt Designer for the Blade Inputfile writer. The class has the methods for writing BladePro keywords in an input file
and calling the C++ code to run with the generated input file.

"""
from PyQt4 import QtGui, QtCore
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import matplotlib as mpl
import functools

import os
import sys

input_writer_dir = os.path.dirname(__file__)


ui_file = os.path.join(input_writer_dir, "inputfile_writerUI.ui")
py_ui_file = os.path.join(input_writer_dir, "inputfile_writerUI.py")

os.system("pyuic4 -x %s -o %s" % (ui_file, py_ui_file))

from bladepro_modules import inputfile_writerUI

class InputWriterWindow(QtGui.QMainWindow, inputfile_writerUI.Ui_MainWindow):
    """
    Class for creating a GUI for the BladePy Inputfile Writer Widget.

    This class inherits the inputfile_writerUI.Ui_MainWindow, the layout created in Qt Designer.
    This class has methods for generating the inputfiles for running BladePro. Clicking the checkboxes enables the
    usage of the keywords.

    The class can hold up to 10 different User Preferences that can be named any name the user wants.
    The User Preferences are managed by loadSettings() and saveSettings() methods

    """

    def __init__(self, parent=None, OutputViewerWidget=None):

        super(InputWriterWindow, self).__init__(parent)

        self.list_settings = []
        self.file_geometry = ""
        self.working_directory = ""

        # List to up to 10 settings defined
        self.user_settings = [QtCore.QSettings("BladePy", "BladePy\InputWriter\Options{number}".format(number=1)),
                              QtCore.QSettings("BladePy", "BladePy\InputWriter\Options{number}".format(number=2)),
                              QtCore.QSettings("BladePy", "BladePy\InputWriter\Options{number}".format(number=3)),
                              QtCore.QSettings("BladePy", "BladePy\InputWriter\Options{number}".format(number=4)),
                              QtCore.QSettings("BladePy", "BladePy\InputWriter\Options{number}".format(number=5)),
                              QtCore.QSettings("BladePy", "BladePy\InputWriter\Options{number}".format(number=6)),
                              QtCore.QSettings("BladePy", "BladePy\InputWriter\Options{number}".format(number=7)),
                              QtCore.QSettings("BladePy", "BladePy\InputWriter\Options{number}".format(number=8)),
                              QtCore.QSettings("BladePy", "BladePy\InputWriter\Options{number}".format(number=9)),
                              QtCore.QSettings("BladePy", "BladePy\InputWriter\Options{number}".format(number=10))]

        self.last_settings = QtCore.QSettings("BladePy", "BladePy\InputWriter\LastOptions")
        # Consolidates both settings list in one.
        self.list_settings.append(self.last_settings)
        self.list_settings.extend(self.user_settings)

        # Define the instance variable for the setting names list. This is used to save/retrieve user renamed settings.
        self.settings_names = QtCore.QSettings("BladePy", "BladePy\InputWriter\SettingsNames")

        # Initializing GUI
        self.setupUi(self)
        self.setWindowTitle("BladePy - Input Writer")

        # sets a instace variable of the main object of Core
        self.op_viewer = OutputViewerWidget

        # Retrieves settings names defined previously by user. If not defined, it will load the default names.
        if self.settings_names.value("settings_names") is not None:
            self.ui_listsettings_combo.clear()
            self.ui_listsettings_combo.addItems(self.settings_names.value("settings_names"))

        # setting validators and applying, setting signals
        self.no_validator = QtGui.QRegExpValidator()
        self.integer_validator = QtGui.QIntValidator()
        self.double_validator = QtGui.QDoubleValidator()
        self.double_validator.setRange(0, 1, 4)
        self.ui_output_igs_surf_rail_combo.setValidator(self.double_validator)
        self.modifyStreamsValidator()

        QtCore.QObject.connect(self.ui_modify_streams_opt_combo, QtCore.SIGNAL("currentIndexChanged(int)"),
                               self.modifyStreamsValidator)

        # Signal connections
        # Find path button
        self.ui_read_find_btn.clicked.connect(self.readOptionsFind)
        self.ui_working_path_edit.setText(os.path.join(os.path.dirname(__file__)))
        self.ui_read_find_btn.clicked.connect(self._fillExistantOutputs)
        self.ui_working_path_edit.textChanged.connect(self._fillExistantOutputs)

        # Output viewer link

        self.ui_display_selected_btn.clicked.connect(self.openSelectedCases)

        # Settings buttons
        self.ui_renamesetting_btn.clicked.connect(self.renameSetting)
        self.ui_quicklist_chk.clicked.connect(self.quickListFunction)

        # Other Buttons
        self.ui_select_path_btn.clicked.connect(self.selectPath)
        self.ui_generatefile_btn.clicked.connect(self.generateInput)
        self.ui_modify_streams_deleteinput_btn.clicked.connect(self.modifyStreamsRemoveInput)
        self.ui_output_igs_surf_deleterail_btn.clicked.connect(self.outputIGSSurfRemoveRail)
        self.ui_modify_te_help_btn.clicked.connect(self.modifyTEHelp)

        # Run blade pro button
        # TODO: fix this functionality
        # self.ui_run_bladepro_send_btn.clicked.connect(self.runBladePro)

        self.ui_run_bladepro_btn.clicked.connect(self.runBladePro)

        # Toolbar setup
        self._setGUIMenus()

        # Graphic Settings
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(__file__), "icons/help.svg")),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.ui_modify_te_help_btn.setIcon(icon)

    def _fillExistantOutputs(self):
        self.ui_case_name_existent_list.clear()
        working_path = self.ui_working_path_edit.text()

        try:
            list_dir = os.listdir(working_path)
        except FileNotFoundError:
            return

        output_recognized = [".2d.tec.dat", ".surf.igs", ".cur.igs", ".mpth.igs", ".iges", ".igs"]
        list_supported = []
        list_not_supported = []


        for item in list_dir:
            if any(iterator in item for iterator in output_recognized):
                if item[:item.index('.')] not in list_supported:
                    self.ui_case_name_existent_list.addItem(item[:item.index('.')])

                list_supported.append(item[:item.index('.')])
            else:
                list_not_supported.append(item)
                # self.ui_case_name_existent_not_supported_edit.addItem(item)

    def selectPath(self):
        """
        Method accessed by select path button.

        This method is for setting working path.

        @return None
        """
        working_path = self.ui_working_path_edit.text()
        selected_path = QtGui.QFileDialog.getExistingDirectory(self, "Select Directory", working_path)

        if selected_path == "":
            return

        self.ui_working_path_edit.setText(str(selected_path))

    def generateInput(self):
        """
        Calls all other methods related to BladePro keywords to generate an input file

        This method is called by ui_button press or after loading any user settings.
        It calls all keywords methods of BladePro independent if they are going to generate something.

        @return None
        """
        working_path = self.ui_working_path_edit.text()
        case_name = self.ui_case_name_edit.text()

        if case_name is "":
            case_name = "input_preview"

        try:
            generated_input = open(os.path.join(working_path, case_name), 'w')
        except:
            generated_input = open(os.path.join(os.path.dirname(__file__), case_name), 'w')

        # The commented lines are BladePro commands not implemented yed lines are BladePro commands not implemented yet.
        self.readOptions(generated_input)

        self.modifyScale(generated_input)
        self.modifyTE(generated_input)
        self.modifyStreams(generated_input)
        self.modifyTERound(generated_input)

        self.outputIGSSurf(generated_input)
        self.outputIGSCur3d(generated_input)
        self.outputIGSCur2d(generated_input)
        self.outputIGSPnts2Cur(generated_input)
        self.outputIGSPnts2Pnts(generated_input)

        self.outputMapPnts(generated_input)

        self.outputTecplot2d(generated_input)
        self.outputTecplot3d(generated_input)

        self.outputTecplotStreams(generated_input)
        # self.outputTecplotCFDDomainINTF(generated_input)
        # self.outputTecplotMerGrid(generated_input)
        # self.outputTecplotMerGridLETE(generated_input)
        # self.outputTecplotMerGrid3d(generated_input)

        self.outputCamberAngles(generated_input)
        self.outputSweepAngle(generated_input)
        self.outputStreamC(generated_input)
        self.outputStackCur(generated_input)
        self.outputHeightV(generated_input)
        self.outputTEPos(generated_input)
        self.outputTECur(generated_input)
        self.outputLECur(generated_input)
        self.outputCFT(generated_input)
        self.outputRTZT(generated_input)
        self.outputAutoGrid(generated_input)

        # self.outputIGSCFDDomainP2P(generated_input)
        # self.outputIGSCFDDomainB2B(generated_input)
        # self.outputIGSCFDDomainInlet(generated_input)
        # self.outputIGSCFDDomainINTF(generated_input)
        # self.outputIGSCFDDomainPeriodic(generated_input)

        # self.outputCurCFDDomainP2P(generated_input)
        # self.outputCurCFDDomainB2B(generated_input)

        # self.outputGmshCFDDomainP2P(generated_input)
        # self.outputGmshMerGrid(generated_input)
        # self.outputGmshMerGridLETE(generated_input)
        # self.outputGmshInpMerGrid(generated_input)
        # self.outputGmshInpMerGridLETE(generated_input)


        try:
            generated_input = open(os.path.join(working_path, case_name), 'r')
        except FileNotFoundError:
            generated_input = open(os.path.join(os.path.dirname(__file__), 'input_preview.txt'), 'r')
        self.ui_inputpreview_textedit.setPlainText(generated_input.read())

        self.saveSettings(-1)

        print("--------Generated Input File End-----------")

        # setup the initial display here

    def runBladePro(self):

        self.generateInput()

        case_name = self.ui_case_name_edit.text()
        working_path = self.ui_working_path_edit.text()

        QtCore.QCoreApplication.processEvents()
        bladepro_version = self.op_viewer.PreferencesManager.list_settings[1].value("bladepro_settings/default_bladebro_version")
        print("%s Running" % bladepro_version)

        bladepro_command = bladepro_version + " " + os.path.join(working_path, case_name)
        os.system(bladepro_command)

        status_message = "Last Status: %s was run for generating %s outputs" % (bladepro_version, case_name)

        self.ui_application_status_lbl.setText(status_message)
        self._fillExistantOutputs()

    def openSelectedCases(self):
        """
        This method will display Cases selected from Input Writer Widget list.

        @return None
        """
        selected_case_list = self.ui_case_name_existent_list

        # In case user is only input_writer module
        if self.op_viewer is None:
            print("Open Core.py for displaying BladePro outputs")
            return

        for item in selected_case_list.selectedItems():
            self.ui_case_name_edit.setText(item.text())

            self.op_viewer.addCase()

    # Read Section
    def readOptions(self, gen_file):
        """
        This method is called for writing at the input file the type of reading, IBL, IBL2 or CFT-GEO.

        This method and all others will accept one parameter that is gen_file.
        All these methods are all called by generateInput() method.

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        working_path = self.ui_working_path_edit.text()
        if self.ui_read_ibl_rbtn.isChecked():
            if self.ui_read_ibl_fpfile_edit.text() == "":
                read_ibl_file = self.ui_read_ibl_iblfile_edit.text()
                file_abs_path = os.path.join(working_path, read_ibl_file)
                gen_file.write("READ/IBL\n")

                gen_file.write("{file_name_ibl}\n\n".format(file_name_ibl=file_abs_path))
            else:
                gen_file.write("READ/IBL2\n")
                read_ibl_file = self.ui_read_ibl_iblfile_edit.text()
                read_fp_file = self.ui_read_ibl_fpfile_edit.text()
                gen_file.write("{file_name_ibl}\n{file_name_fp}\n\n".format(file_name_ibl=read_ibl_file,
                                                                            file_name_fp=read_fp_file))

        if self.ui_read_cftgeo_rbtn.isChecked():
            # The READ/CFT-GEO keyword will read a general geometry (txt) file from CFturbo version 9 or 10
            # Below the cft-geo filename the number of blades has to be specified since no information about the
            # blade count is included in the cft-geo file.
            read_cft_file = self.ui_read_cftgeo_cftfile_edit.text()
            file_abs_path = os.path.join(working_path, read_cft_file)

            gen_file.write("READ/CFT-GEO\n")
            read_cftgeo_nblades = self.ui_read_cftgeo_nblades_spn.text()
            read_cftgeo_angle = self.ui_read_cftgeo_angle_dspn.text()
            gen_file.write("{file_name_cft}\n{n_blades}\n{angle}\n\n".format(file_name_cft=file_abs_path,
                                                                             n_blades=read_cftgeo_nblades,

                                                                             angle=read_cftgeo_angle))

    def readOptionsFind(self):
        """
        Method for finding geometry file of type *.cft-geo, *.ibl or  *.fp

        @return None
        """
        selected_file = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                                                          self.working_directory,
                                                          "(*.cft-geo *.ibl *.fp);; All Files(*.*)")

        # In case user gives up finding a file, return.
        if not os.path.isfile(selected_file):
            return

        file_geometry = os.path.basename(selected_file)
        self.working_path = os.path.dirname(selected_file)
        case_name = os.path.splitext(file_geometry)[0]
        extension = os.path.splitext(file_geometry)[1]

        if extension == ".ibl":
            self.ui_read_ibl_rbtn.setChecked(True)
            self.ui_read_cftgeo_rbtn.setChecked(False)
            self.ui_read_ibl_iblfile_edit.setText(file_geometry)

        elif extension == ".fp":
            self.ui_read_ibl_rbtn.setChecked(True)
            self.ui_read_cftgeo_rbtn.setChecked(False)
            self.ui_read_ibl_fpfile_edit.setText(file_geometry)

        elif extension == ".cft-geo":
            self.ui_read_cftgeo_rbtn.setChecked(True)
            self.ui_read_cftgeo_cftfile_edit.setText(file_geometry)

        self.ui_case_name_edit.setText(case_name + "_output")
        self.ui_working_path_edit.setText(self.working_path)

    def defineBlade(self, gen_file):
        """
        [NOT IMPLEMENTED]

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_define_blade_chk.isChecked():
            pass

    # Modify Section
    def modifyScale(self, gen_file):
        """
        This keyword will scale the geometry.

        This keyword will scale the geometry with the vector valued scale factor f = (x-sc, y-sc, z-sc)
        with respect to a point C = (xc, yc, zc).

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_modify_scale_chk.isChecked():
            modify_scale_xsc = self.ui_modify_scale_xsc_dspn.text()
            modify_scale_ysc = self.ui_modify_scale_ysc_dspn.text()
            modify_scale_zsc = self.ui_modify_scale_zsc_dspn.text()
            modify_scale_xc = self.ui_modify_scale_xc_dspn.text()
            modify_scale_yc = self.ui_modify_scale_yc_dspn.text()
            modify_scale_zc = self.ui_modify_scale_zc_dspn.text()
            gen_file.write("MODIFY/SCALE\n")
            gen_file.write("{xsc} {ysc} {zsc}\n{xc} {yc} {zc}\n\n".format(xsc=modify_scale_xsc, xc=modify_scale_xc,
                                                                          ysc=modify_scale_ysc, yc=modify_scale_yc,
                                                                          zsc=modify_scale_zsc, zc=modify_scale_zc))

    def modifyTE(self, gen_file):
        """
        This keyword will do a milling operation on the geometry.


        This keyword will do a milling operation on the geometry by cutting the blade geometry with the surface of
        revolution created by the line in the meridional plane defined by the point (z-ref, D/2) with angle gamma.

        There is two options in the GUI, modify/TE and modify/TE/IBL. In modify/TE/IBL diameter, z-reference and gamma
        angled are read from the ibl-file not from the GUI.

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_modify_te_ibl_rbtn.isChecked():
            if self.ui_modify_te_chk.isChecked():
                gen_file.write("MODIFY/TE/IBL\n\n")
        else:
            if self.ui_modify_te_chk.isChecked():
                modify_te_d = self.ui_modify_te_d_dspn.text()
                modify_te_zref = self.ui_modify_te_zref_dspn.text()
                modify_te_gamma = self.ui_modify_te_gamma_dspn.text()

                gen_file.write("MODIFY/TE\n")
                gen_file.write("{d_value} {z_ref} {gamma}\n\n".format(d_value=modify_te_d,
                                                                      z_ref=modify_te_zref,
                                                                      gamma=modify_te_gamma))
    def modifyTERound(self, gen_file):
        """
        This keyword will do a round operation on the TE geometry.




        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        # TODO: Describe Operation
        # TODO: tune dpsn
        round_value = self.ui_modify_te_round_dpsn.text()
        if self.ui_modify_te_round_chk.isChecked():
            gen_file.write("MODIFY/TE/ROUND\n")
            gen_file.write("{round_val}\n\n".format(round_val=round_value))

    def modifyTEHelp(self):
        """
        Auxiliary method that displays the figures to orient the user about coordinates parameters D, Z-ref and Gamma

        @returns None
        """

        # Remove toolbar from matplotlib
        mpl.rcParams['toolbar'] = 'None'

        # Set interactive instance for displaying a new Qt Window(Otherwise it would cause errors with QApplication)
        mpl.interactive(True)

        # Create a figure and an axis object with given size
        modify_te_mpl_fig, modify_te_mpl_ax = plt.subplots(num=None, figsize=(7, 6), dpi=80)

        # Loads the figure to be displayed and displays it

        modify_te_help_figure = mpimg.imread(os.path.join(os.path.dirname(__file__), 'images/help_modify_TE.png'))
        modify_te_mpl_ax.imshow(modify_te_help_figure)

        # Configure the figure display window, removing axis and frames, defining window and figure title
        modify_te_mpl_ax.set_axis_off()
        modify_te_mpl_ax.patch.set_visible(False)
        modify_te_mpl_ax.set_title("Trailing edge milling parameters")
        modify_te_mpl_fig.patch.set_visible(False)
        modify_te_mpl_fig.canvas.set_window_title('MODIFY/TE Keyword Help')
        modify_te_mpl_fig.subplots_adjust(top=.95, bottom=0.0, right=1.0, left=0)

        # Fixating window size
        modify_te_mpl_fig.canvas.window().setFixedSize(modify_te_mpl_fig.canvas.window().size())

    def modifyStreams(self, gen_file):
        """
        This keyword will re-create the blade geometry based on new section profiles created on new stream surfaces.

        The new stream surfaces can be specified in three different ways by method:

        \arg \c ELLIPTIC: constant span positions based on elliptic grid
        \arg \c ORTHOGONAL: constant span positions based on orthogonal grid
        \arg \c FILE: arbitrary stream surfaces read from file.

        The elliptic option will create the new stream surfaces on equally spaced span position where the user
        specifies the number of stream surfaces

        The orthogonal option lets the user specify the interior span positions, i.e. 0 < span < 1.
        Stream surfaces at hub (span = 0) and shroud (span = 1) will automatically be created so the
        total number of stream surfaces will then be n + 2.

        The file option reads the interior stream surfaces (stream surfaces at hub and shroud will automatically
        be created like the elliptic option)

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_modify_streams_chk.isChecked():
            # Create a simple dictionary for combobox index option
            opt_dict = {0: "ELLIPTIC", 1: "ORTHOGONAL", 2: "FILE"}
            modify_streams_method = self.ui_modify_streams_opt_combo.currentIndex()

            gen_file.write("MODIFY/STREAMS\n")

            if opt_dict[modify_streams_method] == "ELLIPTIC":
                # if input is NaN it returns except then it is set to be zero.
                try:
                    modify_streams_input = int(self.ui_modify_streams_input_combo.currentText())
                except ValueError:
                    modify_streams_input = 0

                gen_file.write("{modify_method}\n{n_surfaces}\n\n".format(modify_method=opt_dict[modify_streams_method],
                                                                          n_surfaces=modify_streams_input))

            if opt_dict[modify_streams_method] == "ORTHOGONAL":
                # Retrieves all data from user input list
                modify_streams_input_list = [float(self.ui_modify_streams_input_combo.itemText(i))
                                             for i in range(self.ui_modify_streams_input_combo.count())]

                # removing duplicates by creating and appending items to a templist.

                templist = []
                for i in modify_streams_input_list:
                    if i not in templist:
                        templist.append(i)

                modify_streams_input_list = templist

                # sorts the list of surfs as bladepro requirement
                modify_streams_input_list.sort()

                # counts the number of surfs for bladepro argument
                modify_streams_input_len = len(modify_streams_input_list)

                # concatenate the surfs list to write it to the input file
                modify_streams_input_concatenated = "\n".join(str(i) for i in modify_streams_input_list)

                gen_file.write("{modify_method}\n".format(modify_method=opt_dict[modify_streams_method]))

                gen_file.write("{n_surf}\n{surfs}\n\n".format(n_surf=modify_streams_input_len,
                                                              surfs=modify_streams_input_concatenated))

            if opt_dict[modify_streams_method] == "FILE":
                modify_streams_input = self.ui_modify_streams_input_combo.currentText()
                gen_file.write("{modify_method}\n{file_name}\n\n".format(modify_method=opt_dict[modify_streams_method],
                                                                         file_name=modify_streams_input))

    def modifyStreamsValidator(self):
        """
        Auxiliary method that validates the user input in modify streams keyword

        This method is called by signal-slot system. When the ui_modify_streams_opt_combo combobox item is changed,
        this method is activated. The arguments accepted by each case are:

        \arg \c ELLIPTIC: the argument is a single integer
        \arg \c ORTHOGONAL: the argument can be a list of doubles
        \arg \c FILE: the argument is a single file

        @return None

        """
        opt_dict = {0: "ELLIPTIC", 1: "ORTHOGONAL", 2: "FILE"}

        modify_streams_method = self.ui_modify_streams_opt_combo.currentIndex()

        if opt_dict[modify_streams_method] == "ELLIPTIC":
            self.ui_modify_streams_input_combo.setMaxCount(0)
            self.ui_modify_streams_input_combo.setValidator(self.integer_validator)

        if opt_dict[modify_streams_method] == "ORTHOGONAL":
            self.ui_modify_streams_input_combo.setMaxCount(100)
            self.ui_modify_streams_input_combo.setValidator(self.double_validator)

        if opt_dict[modify_streams_method] == "FILE":
            self.ui_modify_streams_input_combo.setValidator(self.no_validator)
            self.ui_modify_streams_input_combo.setMaxCount(0)

    def modifyStreamsRemoveInput(self):
        """
        Auxiliary method to the modifyStreams method to remove an item of the span positions of combobox

        @return None

        """
        self.ui_modify_streams_input_combo.removeItem(self.ui_modify_streams_input_combo.currentIndex())

    # Output Section
    def outputIGSSurf(self, gen_file):
        """
        This keyword for iges files outputs

        The first field in the GUI allow to choose which surfaces to output and the second to
        define rail curves positions.

        \arg \c 0 - All surfaces
        \arg \c 1 - Blade + flow path
        \arg \c 2 - Blade
        \arg \c 3 - Stream surfaces
        \arg \c 4 - Hub
        \arg \c 5 - Shroud
        \arg \c 6 - Meanline
        \arg \c 10 - All surfaces where hub and shroud are split at LE/TE to be three surfaces each
        \arg \c 11 - Blade + flowpath where hub and shroud are split at LE/TE to be three surfaces each
        \arg \c 14 - Hub split at LE/TE to be three surfaces
        \arg \c 15 - Hub split at LE/TE to be three surfaces

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_igs_surf_chk.isChecked():
            output_igs_surf_option = self.ui_output_igs_surf_opt_combo.currentIndex()
            output_igs_surf_rails_list = [float(self.ui_output_igs_surf_rail_combo.itemText(i))
                                          for i in range(self.ui_output_igs_surf_rail_combo.count())]

            # removing duplicates by creating and appending items to a templist.
            templist = []
            for i in output_igs_surf_rails_list:
                if i not in templist:
                    templist.append(i)

            output_igs_surf_rails_list = templist

            # sorts the list of rails as bladepro requirement
            output_igs_surf_rails_list.sort()

            # counts the number of rails for bladepro argument
            output_igs_surf_rails_len = len(output_igs_surf_rails_list)

            # concatenate the rails list to write it to the input file
            output_igs_surf_rails_concatenated = "\n".join(str(i) for i in output_igs_surf_rails_list)

            gen_file.write("OUTPUT/IGS/SURF\n")
            gen_file.write("{surf_option}\n{n_rails}\n{rails}\n\n".format(surf_option=output_igs_surf_option,
                                                                          n_rails=output_igs_surf_rails_len,
                                                                          rails=output_igs_surf_rails_concatenated))

    def outputIGSSurfRemoveRail(self):
        """
        Auxiliary function to the outputIGSSurf method to remove an item of the rails combobox

        @return None

        """
        self.ui_output_igs_surf_rail_combo.removeItem(self.ui_output_igs_surf_rail_combo.currentIndex())

    def outputIGSCur3d(self, gen_file):
        """
        This keyword outputs the curves in Cartesian x-y-z space to an igs-file.

        The index of the combobox in the GUI determines which curves to include in the file:

        \arg \c 0 - All curves
        \arg \c 1 - Blade + flow path
        \arg \c 2 - Blade
        \arg \c 3 - Stream curves
        \arg \c 4 - Hub
        \arg \c 5 - Shroud

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_igs_cur_3d_chk.isChecked():
            output_igs_cur_3d_option = self.ui_output_igs_cur_3d_opt_combo.currentIndex()

            gen_file.write("OUTPUT/IGS/CUR/3D\n")
            gen_file.write("{_3dcur_option}\n\n".format(_3dcur_option=output_igs_cur_3d_option))

    def outputIGSCur2d(self, gen_file):
        """
        This keyword outputs the blade section profiles.

        The index of the combobox in the GUI allows the user to choose between the space options:

        \arg \c 1 - m'-teta
        \arg \c 2 - m-rteta

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_igs_cur_2d_chk.isChecked():
            output_igs_cur_2d_option = self.ui_output_igs_cur_2d_opt_combo.currentIndex()

            gen_file.write("OUTPUT/IGS/CUR/2D\n")
            gen_file.write("{_2dcur_option}\n\n".format(_2dcur_option=output_igs_cur_2d_option + 1))

    def outputIGSPnts2Cur(self, gen_file):
        """
        This keyword will spline point curves given in "filename" to an igs-file named filename.cur.igs.

        The splined curves will also be revolved around the rotational axis and the resulting surfaces will be
        written to an igs-file named filename.surf.igs.

        Field in the GUI:
        \arg \c Filename: File where the points curves to be splined are located

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_igs_pnts2cur_chk.isChecked():
            output_igs_pnts2cur_file = self.ui_output_igs_pnts2cur_file_edit.text()
            gen_file.write("OUTPUT/IGS/PNTS2CUR\n")
            gen_file.write("{pnt2cur_file}\n\n".format(pnt2cur_file=output_igs_pnts2cur_file))

    def outputIGSPnts2Pnts(self, gen_file):
        """
        This keyword will create an igs-file for visualizing a point.

        Visualization point is set by marking each point in file filename with a star or a cube.

        Field in the GUI:
        \arg \c Filename: File with the points that are going to be marked

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_igs_pnts2pnts_chk.isChecked():
            output_igs_pnts2pnts_file = self.ui_output_igs_pnts2pnts_file_edit.text()
            gen_file.write("OUTPUT/IGS/PNTS2PNTS\n")
            gen_file.write("{pnts2pnts_file}\n\n".format(pnts2pnts_file=output_igs_pnts2pnts_file))

    def outputMapPnts(self, gen_file):
        """
        This keyword will map a Cartesian x-y-z point set.

        The fields in the GUI:

        Point set is given in points.dat (first field) and lying on a stream surface described
        by streamcurve.dat (second field) into the m'-teta space.

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_mappnts_chk.isChecked():
            output_mappnts_points = self.ui_output_mappnts_pointsfile_edit.text()
            output_mappnts_streamcurve = self.ui_output_mappnts_streamcurvefile_edit.text()

            gen_file.write("OUTPUT/MAPPNTS\n")
            gen_file.write("{mappnts_points}\n{mappnts_streamc}\n\n".format(mappnts_points=output_mappnts_points,
                                                                            mappnts_streamc=output_mappnts_streamcurve))

    # Output options
    def outputTecplot2d(self, gen_file):
        """
        This keyword will output the blade geometry including flow path and stream curves in Tecplot format

        Each profile section is a separate zone and can be viewed in Cartesian x-y-z space as well as m'-teta space
        and m-rteta space.

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_tecplot_2d_chk.isChecked():
            gen_file.write("OUTPUT/TECPLOT/2D\n\n")

    def outputTecplot3d(self, gen_file):
        """
        This keyword will output the blade geometry as surfaces in Cartesian x-y-z space.

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_tecplot_3d_chk.isChecked():
            gen_file.write("OUTPUT/TECPLOT/3D\n\n")

    def outputTecplotStreams(self, gen_file):
        """
        This keyword will output the stream surfaces in Tecplot format.

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_tecplot_streams_chk.isChecked():
            gen_file.write("OUTPUT/TECPLOT/STREAMS\n\n")

    def outputTecplotCFDDomainINTF(self, gen_file):
        """
        [NOT IMPLEMENTED]

        This keyword will create interfaces which are lines in the meridional plane (r-z plane) revolved around
        the rotational axis (z-axis)

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_tecplot_cfddomainintf_chk.isChecked():
            pass

    def outputTecplotMerGrid(self, gen_file):
        """
        [NOT IMPLEMENTED]

        This keyword will create a meridional grid in Tecplot format.

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_tecplot_mergrid_chk.isChecked():
            pass

    def outputTecplotMerGridLETE(self, gen_file):
        """
        [NOT IMPLEMENTED]

        This keyword will create a meridional grid in Tecplot format with three domains

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_tecplot_cfddomainintf_chk.isChecked():
            pass

    def outputTecplotMerGrid3d(self, gen_file):
        """
        [NOT IMPLEMENTED]

        This keyword will create a flowpath grid in Tecplot format.

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_tecplot_mergrid3d_chk.isChecked():
            pass

    def outputCamberAngles(self, gen_file):
        """
        This keyword will print the camber angles (beta) for each profile section to file.

        Each meanline will be specified in a separate file with the four columns; z, r, m' and beta.

        The options can be 1 or 2:

        \arg \c 1 is for camber angle measured against circumferential direction
        \arg \c 2 is for camber angle measured against meridional direction

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_camberangles_chk.isChecked():
            output_camberangles_option = self.ui_output_camberangles_opt_combo.currentIndex()
            gen_file.write("OUTPUT/CAMBERANGLES\n")
            gen_file.write("{camberangles_option}\n\n".format(camberangles_option=output_camberangles_option + 1))

    def outputSweepAngle(self, gen_file):
        """
        This keyword will output a .sweep file

        The sweep angle (l) is defined as 90 degrees minus the angle between the leading edge curve tangent vector
        and the meanline leading edge tangent of a blade section

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_sweepangle_chk.isChecked():
            gen_file.write("OUTPUT/SWEEPANGLE\n\n")

    def outputStreamC(self, gen_file):
        """
        This keyword will write the flow path (hub & shroud) and the stream curves to a file.

        The fields in the GUI:

        It will write with n points(r and z coordinates), the first field, on each curve.
        The stream curves will be extended ext (fraction of total curve length), the second field,
        upstream and downstream.

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_streamc_chk.isChecked():
            output_streamc_npoints = self.ui_output_streamc_npoints_spn.text()
            output_streamc_ext = self.ui_output_streamc_extension_dspn.text()
            gen_file.write("OUTPUT/STREAMC\n")
            gen_file.write("{n_points}\n{extension}\n\n".format(n_points=output_streamc_npoints,
                                                                extension=output_streamc_ext))

    def outputStackCur(self, gen_file):
        """
        The stacking position in selected space for each blade section will be written to a file.

        Fields in the GUI:
        \arg \c Stacking \c position: (value between 0 – 1) where 0 is leading edge and 1 is trailing edge.
        \arg \c Stacking \c coordinate: CART or CYL for stacking curve in Cartesian x-y-z space or
        cylindrical r-teta-z space respectively

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_stackcur_chk.isChecked():
            # Create a simple dictionary for combobox index option
            opt_dict = {0: "CART", 1: "CYL"}
            output_stackcur_position = self.ui_output_stackcur_stackpos_dspn.text()
            output_stackcur_coord = self.ui_output_stackcur_opt_combo.currentIndex()
            gen_file.write("OUTPUT/STACKCUR\n")
            gen_file.write("{stkcur_pos}\n{stkcur_coord}\n\n".format(stkcur_pos=output_stackcur_position,
                                                                     stkcur_coord=opt_dict[output_stackcur_coord]))

    def outputHeightV(self, gen_file):
        """
        This keyword will write the streamtube height variation for n points on each stream curve to file.

        The field in the GUI:
        \arg \c npoints: number of points on each stream curve

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_heighv_chk.isChecked():
            output_hvar = self.ui_output_heighv_hvar_spn.text()
            gen_file.write("OUTPUT/HEIGHTV\n")
            gen_file.write("{height_variation}\n\n".format(height_variation=output_hvar))

    def outputTEPos(self, gen_file):
        """
        Write the trailing edge position of each blade section in cylindrical r-teta-z space to a file

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_tepos_chk.isChecked():
            gen_file.write("OUTPUT/TEPOS\n\n")

    def outputTECur(self, gen_file):
        """
        Write trailing edge point curve in meridional plane to a file with n points.

        Field in the GUI:
        \arg \c npoints: number of points in trailing edge point curve in meridional plane

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_tecur_chk.isChecked():
            output_tecur_npoints = self.ui_output_tecur_npoints_spn.text()
            gen_file.write("OUTPUT/TE-CUR\n")
            gen_file.write("{n_points}\n\n".format(n_points=output_tecur_npoints))

    def outputLECur(self, gen_file):
        """
        Write leading edge point curve in meridional plane to a file with n points.

        Field in the GUI:
        \arg \c npoints: number of points in leading edge point curve in meridional plane

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_lecur_chk.isChecked():
            output_lecur_npoints = self.ui_output_lecur_npoints_spn.text()
            gen_file.write("OUTPUT/LE-CUR\n")
            gen_file.write("{n_points}\n\n".format(n_points=output_lecur_npoints))

    def outputRTZT(self, gen_file):
        """
        This keyword will export the geometry to BladeModeler rtzt-format from ANSYS

        The fields in the GUI:
        \arg \c 1 - Number of points on each section profile.
        \arg \c 2 - Thickness definition normal to meanline on stream surface

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_rtzt_chk.isChecked():
            output_rtzt_npoints = self.ui_output_rtzt_npoints_spn.text()
            output_rtzt_thickness = self.ui_output_rtzt_thickness_dpsn.text()
            gen_file.write("OUTPUT/RTZT\n")
            gen_file.write("{n_points}\n{thickness}\n\n".format(n_points=output_rtzt_npoints,
                                                                thickness=output_rtzt_thickness))

    def outputCFT(self, gen_file):
        """
        This keyword will create a CFturbo project file (version 10.1) of a radial impeller geometry

        The fields in the GUI:
        \arg \c 1 - number of sections to create (CFturbo cannot have more than 11 sections).
        \arg \c 2 - angle that can be set to rotate the stream curve around the rotational axis angle degrees.
        If not specified, the default value of the angle parameter is 0 degrees

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_cft_chk.isChecked():
            output_cft_nsect = self.ui_output_cft_nsect_spn.text()
            output_cft_angle = self.ui_output_cft_angle_dspn.text()
            gen_file.write("OUTPUT/CFT\n")
            gen_file.write("{n_sections}\n{angle}\n\n".format(n_sections=output_cft_nsect,
                                                              angle=output_cft_angle))

    def outputAutoGrid(self, gen_file):
        """
        This keyword will create a Numeca .geomTurbo file.

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_autogrid_chk.isChecked():
            gen_file.write("OUTPUT/AUTOGRID\n\n")

    def outputIGSCFDDomainP2P(self, gen_file):
        """
        [NOT IMPLEMENTED]

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_igs_cfddomainp2p_chk.isChecked():
            pass

    def outputIGSCFDDomainB2B(self, gen_file):
        """
        [NOT IMPLEMENTED]

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_igs_cfddomainb2b_chk.isChecked():
            pass

    def outputIGSCFDDomainInlet(self, gen_file):
        """
        [NOT IMPLEMENTED]

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_igs_cfddomaininlet_chk.isChecked():
            pass

    def outputIGSCFDDomainINTF(self, gen_file):
        """
        [NOT IMPLEMENTED]

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_igs_cfddomainintf_chk.isChecked():
            pass

    def outputIGSCFDDomainPeriodic(self, gen_file):
        """
        [NOT IMPLEMENTED]

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_igs_cfddomainperiodic_chk.isChecked():
            pass

    def outputCurCFDDomainP2P(self, gen_file):
        """
        [NOT IMPLEMENTED]

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_cur_cfddomainp2p_chk.isChecked():
            pass

    def outputCurCFDDomainB2B(self, gen_file):
        """
        [NOT IMPLEMENTED]

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_cur_cfddomainb2b_chk.isChecked():
            pass

    def outputGmshCFDDomainP2P(self, gen_file):
        """
        [NOT IMPLEMENTED]

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_gmsh_cfddomainp2p_chk.isChecked():
            pass

    def outputGmshMerGrid(self, gen_file):
        """
        [NOT IMPLEMENTED]

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_gmsh_mergrid_chk.isChecked():
            pass

    def outputGmshMerGridLETE(self, gen_file):
        """
        [NOT IMPLEMENTED]

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_gmsh_mergridlete_chk.isChecked():
            pass

    def outputGmshInpMerGrid(self, gen_file):
        """
        [NOT IMPLEMENTED]

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_gmshinp_mergrid_chk.isChecked():
            pass

    def outputGmshInpMerGridLETE(self, gen_file):
        """
        [NOT IMPLEMENTED]

        @param gen_file [txt] Is the file to what the new lines are being saved to.
        @return None

        """
        if self.ui_output_gmshinp_mergridlete_chk.isChecked():
            pass

            # End of Blade Pro Commands.





    def renameSetting(self):
        """
        Renames the name of user defined settings to make their name represent something to the user.

        This method is called when Rename Setting button is clicked.

        @return None

        """

        # The function below set the text of the current index with the current text in edit line
        self.ui_listsettings_combo.setItemText(self.ui_listsettings_combo.currentIndex(),
                                               self.ui_listsettings_combo.currentText())

        # Save the list names in the system for keeping it after the GUI is closed.
        self.settings_names.setValue("settings_names",
                                     [self.ui_listsettings_combo.itemText(i)
                                      for i in range(self.ui_listsettings_combo.count())])

    def menuFileButtonPressedGroup(self, pressed_btn):
        """
        Method group that wrap only exit function for "file" menu. The others are wrapped in the toolbar pressed group

        @param pressed_btn [QtGui.QAction] Signal emitted by button clicked on ui_file_menur
        @return None
        """
        if pressed_btn.text() == "Exit":
            self.close()
            QtCore.QCoreApplication.exit()
            sys.exit()

    def menuFileBladeproButtonPressedGroup(self, pressed_btn):
        """
        Method group that wrap all functions for File and BladePro buttons in toolbar


        @param pressed_btn [QtGui.QAction] Signal emitted by button clicked on ui_bladepro_toolbar
        @return None
        """
        if self.op_viewer is None:
            return

        if pressed_btn.text() == "Open Output Viewer":
            self.op_viewer.showMaximized()
            self.op_viewer.raise_()

        if pressed_btn.text() == "Preview Inputfile":
            self.generateInput()

        if pressed_btn.text() == "Run BladePro":
            self.runBladePro()

        if pressed_btn.text() == "Run BladePro and Send":
            self.runBladePro()

            # Case user is using only inputfile_writer module
            if self.op_viewer is None:
                print("Open Core.py for displaying BladePro outputs")
                return

            self.op_viewer.addCase()



    def userSettingsButtonPressedGroup(self, button_pressed):
        """
        Method group that wrap all functions for user settings options in toolbar

        @param button_pressed [QtGui.QAction] Signal emitted by button clicked on ui_settings_toolbar
        @return None

        """

        # It will load or save to the current setting list in ui.
        if button_pressed.text() == "Save Set of Commands":
            self.saveSettings(self.ui_listsettings_combo.currentIndex())

        if button_pressed.text() == "Load Set of Commands":
            self.loadSettings(self.ui_listsettings_combo.currentIndex())

        if button_pressed.text() ==  "Load Last Set of Commands":
            self.loadSettings(-1)

        if button_pressed.text() ==  "Preferences":
            self.op_viewer.PreferencesManager.show()
            self.op_viewer.PreferencesManager.raise_()
            
    def loadSettings(self, setting):
        """
        Loads the user settings defined in "setting" index.

        This will check all checkboxes and modify all the fields according to the setting loaded.

        The last user settings is defined by setting = -1.
        Thus, to load last user settings the function call is loadSettings(-1). There is up to 10 sets available,
        starting with setting = 0.

        @param setting [int] Is the ui_listsettings_combo index.
        @return None

        """

        # For some reason, when checkbox isChecked is saved to the user settings, it saves as lowercase letters.
        # A simple solution was to create a simple dictionary
        dct = {"true": True, "false": False, True: True, False: False}

        # The set sums 1, as the first item in python lists is 0 and 0 is reserved for last user settings.
        setting += 1

        # if statement In case the user tries to load settings no previously defined.
        if self.list_settings[setting].value("read_panel/ibl_file") is None:
            QtGui.QMessageBox.about(self, "Warning", "No Setting previously defined for this item")
            return

        # Begin group/end group. Means, e. g. that value("ibl_file") value is stored actually  in
        # value("read_panel/ibl_file")

        try:
            self.list_settings[setting].beginGroup("read_panel")

            self.ui_read_ibl_iblfile_edit.setText(self.list_settings[setting].value("ibl_file"))
            self.ui_read_ibl_fpfile_edit.setText(self.list_settings[setting].value("fp_file"))

            self.ui_read_cftgeo_rbtn.setChecked(dct[self.list_settings[setting].value("cft_option")])
            self.ui_read_cftgeo_cftfile_edit.setText(self.list_settings[setting].value("cft_file"))
            self.ui_read_cftgeo_nblades_spn.setValue(int(self.list_settings[setting].value("cft_nblades")))
            self.ui_read_cftgeo_angle_dspn.setValue(float(self.list_settings[setting].value("cft_angle")))

            self.ui_working_path_edit.setText(self.list_settings[setting].value("working_path"))
            self.ui_case_name_edit.setText(self.list_settings[setting].value("case_name"))

            self.list_settings[setting].endGroup()

            self.list_settings[setting].beginGroup("modify_panel")

            self.list_settings[setting].beginGroup("scale")
            self.ui_modify_scale_chk.setChecked(dct[self.list_settings[setting].value("checkbox")])
            self.ui_modify_scale_xsc_dspn.setValue(float(self.list_settings[setting].value("xsc_value")))
            self.ui_modify_scale_ysc_dspn.setValue(float(self.list_settings[setting].value("ysc_value")))
            self.ui_modify_scale_zsc_dspn.setValue(float(self.list_settings[setting].value("zsc_value")))
            self.ui_modify_scale_xc_dspn.setValue(float(self.list_settings[setting].value("xc_value")))
            self.ui_modify_scale_yc_dspn.setValue(float(self.list_settings[setting].value("yc_value")))
            self.ui_modify_scale_zc_dspn.setValue(float(self.list_settings[setting].value("zc_value")))
            self.list_settings[setting].endGroup()

            self.list_settings[setting].beginGroup("te")
            self.ui_modify_te_chk.setChecked(dct[self.list_settings[setting].value("checkbox")])
            self.ui_modify_te_rbtn.setChecked(dct[self.list_settings[setting].value("te_option")])
            self.ui_modify_te_ibl_rbtn.setChecked(dct[self.list_settings[setting].value("te_ibl_option")])
            self.ui_modify_te_d_dspn.setValue(float(self.list_settings[setting].value("d_value")))
            self.ui_modify_te_zref_dspn.setValue(float(self.list_settings[setting].value("z-ref_value")))
            self.ui_modify_te_gamma_dspn.setValue(float(self.list_settings[setting].value("gamma_value")))

            self.ui_modify_te_round_chk.setChecked(dct[self.list_settings[setting].value("round_checkbox")])
            self.ui_modify_te_round_dpsn.setValue(float(self.list_settings[setting].value("round_value")))

            self.list_settings[setting].endGroup()

            self.ui_modify_streams_chk.setChecked(dct[self.list_settings[setting].value("streams/checkbox")])
            self.ui_modify_streams_opt_combo.setCurrentIndex(int(self.list_settings[setting].value("streams/opt_combo")))
            self.ui_modify_streams_input_combo.setEditText(self.list_settings[setting].value("streams/input"))

            try:
                self.ui_modify_streams_input_combo.addItems(self.list_settings[setting].value("streams/inputlist"))
            except TypeError:
                pass

            self.list_settings[setting].endGroup()

            self.list_settings[setting].beginGroup("output_panel")
            self.ui_output_igs_surf_chk.setChecked(dct[self.list_settings[setting].value("igs_surf/checkbox")])
            self.ui_output_igs_surf_opt_combo.setCurrentIndex(int(self.list_settings[setting].value("igs_surf/opt_combo")))

            self.ui_output_igs_surf_rail_combo.clear()
            try:
                self.ui_output_igs_surf_rail_combo.addItems(self.list_settings[setting].value("igs_surf/rail_combo"))
            except TypeError:
                pass
            self.ui_output_heighv_chk.setChecked(dct[self.list_settings[setting].value("heighv/checkbox")])
            self.ui_output_heighv_hvar_spn.setValue(int(self.list_settings[setting].value("heighv/hvar_value")))

            self.ui_output_igs_cur_3d_chk.setChecked(dct[self.list_settings[setting].value("igs_cur_3d/checkbox")])
            self.ui_output_igs_cur_3d_opt_combo.setCurrentIndex(
                int(self.list_settings[setting].value("igs_cur_3d/opt_combo")))

            self.ui_output_igs_cur_2d_chk.setChecked(dct[self.list_settings[setting].value("igs_cur_2d/checkbox")])
            self.ui_output_igs_cur_2d_opt_combo.setCurrentIndex(
                int(self.list_settings[setting].value("igs_cur_2d/opt_combo")))

            self.ui_output_cft_chk.setChecked(dct[self.list_settings[setting].value("cft/checkbox")])
            self.ui_output_cft_nsect_spn.setValue(int(self.list_settings[setting].value("cft/nsect")))
            self.ui_output_cft_angle_dspn.setValue(float(self.list_settings[setting].value("cft/angle")))

            self.ui_output_rtzt_chk.setChecked(dct[self.list_settings[setting].value("rtzt/checkbox")])
            self.ui_output_rtzt_npoints_spn.setValue(int(self.list_settings[setting].value("rtzt/npoints")))
            self.ui_output_rtzt_thickness_dpsn.setValue(float(self.list_settings[setting].value("rtzt/thickness")))

            self.ui_output_streamc_chk.setChecked(dct[self.list_settings[setting].value("streamc/checkbox")])
            self.ui_output_streamc_npoints_spn.setValue(int(self.list_settings[setting].value("streamc/npoints")))
            self.ui_output_streamc_extension_dspn.setValue(float(self.list_settings[setting].value("streamc/extension")))

            self.ui_output_igs_pnts2cur_chk.setChecked(dct[self.list_settings[setting].value("igs_pnts2cur/checkbox")])
            self.ui_output_igs_pnts2cur_file_edit.setText(self.list_settings[setting].value("igs_pnts2cur/file"))

            self.ui_output_igs_pnts2pnts_chk.setChecked(dct[self.list_settings[setting].value("igs_pnts2pnts/checkbox")])
            self.ui_output_igs_pnts2pnts_file_edit.setText(self.list_settings[setting].value("igs_pnts2pnts/file"))

            self.ui_output_mappnts_chk.setChecked(dct[self.list_settings[setting].value("mappnts/checkbox")])
            self.ui_output_mappnts_pointsfile_edit.setText(self.list_settings[setting].value("mappnts/pointsfile"))
            self.ui_output_mappnts_streamcurvefile_edit.setText(
                self.list_settings[setting].value("mappnts/streamcurvefile"))

            self.ui_output_stackcur_chk.setChecked(dct[self.list_settings[setting].value("stackcur/checkbox")])
            self.ui_output_stackcur_stackpos_dspn.setValue(float(self.list_settings[setting].value("stackcur/stackpos")))
            self.ui_output_stackcur_opt_combo.setCurrentIndex(int(self.list_settings[setting].value("stackcur/opt_combo")))

            self.ui_output_tecur_chk.setChecked(dct[self.list_settings[setting].value("te-cur/checkbox")])
            self.ui_output_tecur_npoints_spn.setValue(int(self.list_settings[setting].value("te-cur/npoints")))

            self.ui_output_lecur_chk.setChecked(dct[self.list_settings[setting].value("le-cur/checkbox")])
            self.ui_output_lecur_npoints_spn.setValue(int(self.list_settings[setting].value("le-cur/npoints")))

            self.ui_output_camberangles_chk.setChecked(dct[self.list_settings[setting].value("camberangles/checkbox")])
            self.ui_output_camberangles_opt_combo.setCurrentIndex(int(self.list_settings[setting].value("camberangles/"
                                                                                                        "opt_combo")))

            self.ui_output_tecplot_2d_chk.setChecked(dct[self.list_settings[setting].value("tecplot_2d/checkbox")])
            self.ui_output_tecplot_3d_chk.setChecked(dct[self.list_settings[setting].value("tecplot_3d/checkbox")])
            self.ui_output_tecplot_streams_chk.setChecked(
                dct[self.list_settings[setting].value("tecplot_streams/checkbox")])

            self.ui_output_sweepangle_chk.setChecked(dct[self.list_settings[setting].value("sweepangle/checkbox")])
            self.ui_output_autogrid_chk.setChecked(dct[self.list_settings[setting].value("autogrid/checkbox")])
            self.ui_output_tepos_chk.setChecked(dct[self.list_settings[setting].value("tepos/checkbox")])

            self.list_settings[setting].endGroup()

        except KeyError:
            message_error = "The pre-defined settings probably accepted a new member. Redefine this setting"
            QtGui.QMessageBox.about(self, "Warning", message_error)

        finally:
            # Clean-up tasks. Closes all possible opened groups

            while self.list_settings[setting].group() is not "":
                self.list_settings[setting].endGroup()
                print(self.list_settings[setting].group())


        self.generateInput()

    def quickListFunction(self):
        """
        Enables list of settings quick navigation.

        This method is called when checking the ui_checkbox for quick list navigating.

        @return None

        """

        # Function to make settings list viewing quicker by connecting signal to loadSettings Method.
        if self.ui_quicklist_chk.isChecked() is True:
            QtCore.QObject.connect(self.ui_listsettings_combo, QtCore.SIGNAL("currentIndexChanged(int)"),
                                   self.loadSettings)

        if self.ui_quicklist_chk.isChecked() is False:
            QtCore.QObject.disconnect(self.ui_listsettings_combo, QtCore.SIGNAL("currentIndexChanged(int)"),
                                      self.loadSettings)

    def saveSettings(self, setting):
        """
        Save the settings defined in "setting" index.

        This will save the current checked checkboxes and the fields in the GUI to the "setting" selected index.

        @param setting [int] Is the ui_listsettings_combo index.
        @return None

        """

        setting += 1

        self.list_settings[setting].beginGroup("read_panel")

        self.list_settings[setting].setValue("ibl_option", self.ui_read_ibl_rbtn.isChecked())
        self.list_settings[setting].setValue("ibl_file", self.ui_read_ibl_iblfile_edit.text())
        self.list_settings[setting].setValue("fp_file", self.ui_read_ibl_fpfile_edit.text())

        self.list_settings[setting].setValue("cft_option", self.ui_read_cftgeo_rbtn.isChecked())
        self.list_settings[setting].setValue("cft_file", self.ui_read_cftgeo_cftfile_edit.text())
        self.list_settings[setting].setValue("cft_nblades", self.ui_read_cftgeo_nblades_spn.value())
        self.list_settings[setting].setValue("cft_angle", self.ui_read_cftgeo_angle_dspn.value())

        self.list_settings[setting].setValue("working_path", self.ui_working_path_edit.text())
        self.list_settings[setting].setValue("case_name", self.ui_case_name_edit.text())

        self.list_settings[setting].endGroup()

        self.list_settings[setting].beginGroup("modify_panel")

        self.list_settings[setting].beginGroup("scale")

        self.list_settings[setting].setValue("checkbox", self.ui_modify_scale_chk.isChecked())
        self.list_settings[setting].setValue("xsc_value", self.ui_modify_scale_xsc_dspn.value())
        self.list_settings[setting].setValue("ysc_value", self.ui_modify_scale_ysc_dspn.value())
        self.list_settings[setting].setValue("zsc_value", self.ui_modify_scale_zsc_dspn.value())
        self.list_settings[setting].setValue("xc_value", self.ui_modify_scale_xc_dspn.value())
        self.list_settings[setting].setValue("yc_value", self.ui_modify_scale_yc_dspn.value())
        self.list_settings[setting].setValue("zc_value", self.ui_modify_scale_zc_dspn.value())
        self.list_settings[setting].endGroup()

        self.list_settings[setting].beginGroup("te")

        self.list_settings[setting].setValue("checkbox", self.ui_modify_te_chk.isChecked())
        self.list_settings[setting].setValue("te_option", self.ui_modify_te_rbtn.isChecked())
        self.list_settings[setting].setValue("te_ibl_option", self.ui_modify_te_ibl_rbtn.isChecked())
        self.list_settings[setting].setValue("d_value", self.ui_modify_te_d_dspn.value())
        self.list_settings[setting].setValue("z-ref_value", self.ui_modify_te_zref_dspn.value())
        self.list_settings[setting].setValue("gamma_value", self.ui_modify_te_gamma_dspn.value())

        self.list_settings[setting].setValue("round_checkbox", self.ui_modify_te_round_chk.isChecked())
        self.list_settings[setting].setValue("round_value", self.ui_modify_te_round_dpsn.value())

        self.list_settings[setting].endGroup()

        self.list_settings[setting].setValue("streams/checkbox", self.ui_modify_streams_chk.isChecked())
        self.list_settings[setting].setValue("streams/opt_combo", self.ui_modify_streams_opt_combo.currentIndex())
        # needs to fix ("input saved value")
        self.list_settings[setting].setValue("streams/input", self.ui_modify_streams_input_combo.currentText())
        self.list_settings[setting].setValue("streams/inputlist",
                                             [float(self.ui_modify_streams_input_combo.itemText(i))
                                              for i in range(self.ui_modify_streams_input_combo.count())])

        self.list_settings[setting].endGroup()

        self.list_settings[setting].beginGroup("output_panel")

        self.list_settings[setting].setValue("igs_surf/checkbox", self.ui_output_igs_surf_chk.isChecked())
        self.list_settings[setting].setValue("igs_surf/opt_combo", self.ui_output_igs_surf_opt_combo.currentIndex())
        self.list_settings[setting].setValue("igs_surf/rail_combo",
                                             [float(self.ui_output_igs_surf_rail_combo.itemText(i))
                                              for i in range(self.ui_output_igs_surf_rail_combo.count())])

        self.list_settings[setting].setValue("igs_cur_3d/checkbox", self.ui_output_igs_cur_3d_chk.isChecked())
        self.list_settings[setting].setValue("igs_cur_3d/opt_combo", self.ui_output_igs_cur_3d_opt_combo.currentIndex())

        self.list_settings[setting].setValue("igs_cur_2d/checkbox", self.ui_output_igs_cur_2d_chk.isChecked())
        self.list_settings[setting].setValue("igs_cur_2d/opt_combo", self.ui_output_igs_cur_2d_opt_combo.currentIndex())

        self.list_settings[setting].setValue("heighv/checkbox", self.ui_output_heighv_chk.isChecked())
        self.list_settings[setting].setValue("heighv/hvar_value", self.ui_output_heighv_hvar_spn.value())

        self.list_settings[setting].setValue("cft/checkbox", self.ui_output_cft_chk.isChecked())
        self.list_settings[setting].setValue("cft/nsect", self.ui_output_cft_nsect_spn.value())
        self.list_settings[setting].setValue("cft/angle", self.ui_output_cft_angle_dspn.value())

        self.list_settings[setting].setValue("rtzt/checkbox", self.ui_output_rtzt_chk.isChecked())
        self.list_settings[setting].setValue("rtzt/npoints", self.ui_output_rtzt_npoints_spn.value())
        self.list_settings[setting].setValue("rtzt/thickness", self.ui_output_rtzt_thickness_dpsn.value())

        self.list_settings[setting].setValue("streamc/checkbox", self.ui_output_streamc_chk.isChecked())
        self.list_settings[setting].setValue("streamc/npoints", self.ui_output_streamc_npoints_spn.value())
        self.list_settings[setting].setValue("streamc/extension", self.ui_output_streamc_extension_dspn.value())

        self.list_settings[setting].setValue("igs_pnts2cur/checkbox", self.ui_output_igs_pnts2cur_chk.isChecked())
        self.list_settings[setting].setValue("igs_pnts2cur/file", self.ui_output_igs_pnts2cur_file_edit.text())

        self.list_settings[setting].setValue("igs_pnts2pnts/checkbox", self.ui_output_igs_pnts2pnts_chk.isChecked())
        self.list_settings[setting].setValue("igs_pnts2pnts/file", self.ui_output_igs_pnts2pnts_file_edit.text())

        self.list_settings[setting].setValue("mappnts/checkbox", self.ui_output_mappnts_chk.isChecked())
        self.list_settings[setting].setValue("mappnts/pointsfile", self.ui_output_mappnts_pointsfile_edit.text())
        self.list_settings[setting].setValue("mappnts/streamcurvefile",
                                             self.ui_output_mappnts_streamcurvefile_edit.text())

        self.list_settings[setting].setValue("stackcur/checkbox", self.ui_output_stackcur_chk.isChecked())
        self.list_settings[setting].setValue("stackcur/stackpos", self.ui_output_stackcur_stackpos_dspn.value())
        self.list_settings[setting].setValue("stackcur/opt_combo", self.ui_output_stackcur_opt_combo.currentIndex())

        self.list_settings[setting].setValue("te-cur/checkbox", self.ui_output_tecur_chk.isChecked())
        self.list_settings[setting].setValue("te-cur/npoints", self.ui_output_tecur_npoints_spn.value())

        self.list_settings[setting].setValue("le-cur/checkbox", self.ui_output_lecur_chk.isChecked())
        self.list_settings[setting].setValue("le-cur/npoints", self.ui_output_lecur_npoints_spn.value())

        self.list_settings[setting].setValue("camberangles/checkbox", self.ui_output_camberangles_chk.isChecked())
        self.list_settings[setting].setValue("camberangles/opt_combo",
                                             self.ui_output_camberangles_opt_combo.currentIndex())

        self.list_settings[setting].setValue("tecplot_2d/checkbox", self.ui_output_tecplot_2d_chk.isChecked())
        self.list_settings[setting].setValue("tecplot_3d/checkbox", self.ui_output_tecplot_3d_chk.isChecked())
        self.list_settings[setting].setValue("tecplot_streams/checkbox", self.ui_output_tecplot_streams_chk.isChecked())

        self.list_settings[setting].setValue("sweepangle/checkbox", self.ui_output_sweepangle_chk.isChecked())
        self.list_settings[setting].setValue("autogrid/checkbox", self.ui_output_autogrid_chk.isChecked())
        self.list_settings[setting].setValue("tepos/checkbox", self.ui_output_tepos_chk.isChecked())
        self.list_settings[setting].endGroup()

    def _setGUIMenus(self):
        """
        This function setups the GUI menu.

        @return None
        """

        output_viewer_actions = [
            [QtGui.QAction(QtGui.QIcon(os.path.join(input_writer_dir, "icons/open_maingui.svg")),
                           "Open Output Viewer", self), "Ctrl+B"]]

        self._setAction(self.ui_output_viewer_toolbar, self.ui_file_menu_, output_viewer_actions, True)

        self.ui_output_viewer_toolbar.actionTriggered[QtGui.QAction].connect(self.userSettingsButtonPressedGroup)

        # list of actions to be added to settings menu
        settings_actions = [
            QtGui.QAction(QtGui.QIcon(os.path.join(input_writer_dir, "icons/save_current_settings.svg")),
                          "Save Set of Commands", self),
            QtGui.QAction(QtGui.QIcon(os.path.join(input_writer_dir, "icons/load_user_settings.svg")),
                          "Load Set of Commands", self),
            QtGui.QAction(QtGui.QIcon(os.path.join(input_writer_dir, "icons/load_last_settings.svg")),
                           "Load Last Set of Commands", self)]

        # shortcuts to be associated to the actions before
        settings_shortcut = ["Ctrl+S", "Ctrl+L", "Ctrl+D"]

        # wrap shortcuts to actions
        settings_actions = zip(settings_actions, settings_shortcut)

        # call method for adding the actions to toolbar and menu
        self._setAction(self.ui_settings_toolbar, self.ui_settings_menu, settings_actions, True)

        preference_actions = [[QtGui.QAction(QtGui.QIcon(os.path.join(input_writer_dir, "icons/Preferences.svg")),
                          "Preferences", self), "Ctrl+P"]]

        self._setAction(self.ui_settings_toolbar, self.ui_settings_menu, preference_actions)


        help_action = [[QtGui.QAction(QtGui.QIcon(os.path.join(input_writer_dir, "icons/help.svg")),
                                      "help", self), "F1"]]

        self._setAction(self.ui_settings_toolbar, self.ui_help_menu, help_action)


        # Connect toolbar to method group
        self.ui_settings_toolbar.actionTriggered[QtGui.QAction].connect(self.userSettingsButtonPressedGroup)

        ui_file_exit_action = [[QtGui.QAction(QtGui.QIcon(os.path.join(input_writer_dir,
                                                                       "icons/System-log-out.svg")),
                                              "Exit", self), "Ctrl+W"]]

        self._setAction(self.ui_file_menu_, None, ui_file_exit_action)

        self.ui_file_menu_.triggered[QtGui.QAction].connect(self.menuFileButtonPressedGroup)


        bladepro_actions = [
            QtGui.QAction(QtGui.QIcon(os.path.join(input_writer_dir, "icons/write_inputfile.svg")),
                           "Preview Inputfile", self),
            QtGui.QAction(QtGui.QIcon(os.path.join(input_writer_dir, "icons/Run_bladepro.png")),
                           "Run BladePro", self),
            QtGui.QAction(QtGui.QIcon(os.path.join(input_writer_dir, "icons/Run_bladepro_send.png")),
                           "Run BladePro and Send", self)]

        bladepro_shorcut = ["Ctrl+P", "Ctrl+B","Ctrl+T"]
        bladepro_actions = zip(bladepro_actions, bladepro_shorcut)

        self._setAction(self.ui_bladepro_menu, self.ui_output_viewer_toolbar, bladepro_actions)
        self.ui_output_viewer_toolbar.actionTriggered[QtGui.QAction].connect(self.menuFileBladeproButtonPressedGroup)


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

def main():
    app = QtGui.QApplication(sys.argv)
    inputwriter_window = InputWriterWindow()

    inputwriter_window.show()
    # MainWindow.setgui()
    app.exec_()

    # inifile.close()
    print("End of Main Function UI")


if __name__ == "__main__":
    main()
