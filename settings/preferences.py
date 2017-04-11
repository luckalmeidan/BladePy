"""
@package settings.preferences

File that contains the class PreferencesBladePy, for adding functions, for managing
user preferences, to the function-less Dialog Layout preferencesUI.Ui_PreferencesDialog


"""

import os

ui_file = os.path.join(os.path.dirname(__file__), "preferencesUI.ui")
py_ui_file = os.path.join(os.path.dirname(__file__), "preferencesUI.py")

os.system("pyuic4 -x %s -o %s" % (ui_file, py_ui_file))

from PyQt4 import QtCore, QtGui, uic
from settings import preferencesUI

dct = {"true": True, "false": False, True: True, False: False}


class PreferencesBladePy(QtGui.QDialog, preferencesUI.Ui_PreferencesDialog):
    """
    Class with the methods for customizing user preferences.

    """
    def __init__( self, parent=None, OutputViewerWidget=None):

        super(PreferencesBladePy, self).__init__(parent)
        self.setupUi(self)
        self.last_settings = QtCore.QSettings("BladePy", "BladePy\MainApp\LastMainOptions".format(number=1))
        self.user_settings = [QtCore.QSettings("BladePy", "BladePy\MainApp\Options{number}".format(number=1))]
        self.list_settings = []
        self.list_settings.append(self.last_settings)
        self.list_settings.extend(self.user_settings)
        self.first_default = True

        # sets a instace variable of the main object of Core
        self.op_viewer = OutputViewerWidget

        # The try/except below is to prevent the program crashing when opening for the first time in a computer
        try:
            int(self.list_settings[1].value("shapes_settings/default_shape_color"))

        except TypeError:
            # Set standard configuration if it is the first time
            self.saveSettings(1, restore=True)

        finally:

            self.list_settings[1].beginGroup("shapes_settings")

            default_shape_color = int(self.list_settings[1].value("default_shape_color"))
            default_shape_factor = float(self.list_settings[1].value("default_shape_quality"))
            default_shape_transparency = float(self.list_settings[1].value("default_shape_transparency"))
            default_zoom_step = float(self.list_settings[1].value("default_zoomfactor"))

            self.list_settings[1].endGroup()

            self.list_settings[1].beginGroup("outputs_settings")

            default_igs_surf_check_state = dct[self.list_settings[1].value("default_igs_surf_check_state")]
            default_igs_surf_exception = self.list_settings[1].value("default_igs_surf_exception")
            default_igs_3d_cur_check_state = dct[self.list_settings[1].value("default_igs_3d_cur_check_state")]
            default_igs_3d_cur_exception = self.list_settings[1].value("default_igs_3d_cur_exception")
            default_igs_2d_cur_check_state = dct[self.list_settings[1].value("default_igs_2d_cur_check_state")]
            default_igs_2d_cur_exception = self.list_settings[1].value("default_igs_2d_cur_exception")
            default_tecplot_2d_check_state = dct[self.list_settings[1].value("default_tecplot_check_state")]

            self.list_settings[1].endGroup()

            self.list_settings[1].beginGroup("bladepro_settings")

            default_bladebro_version = self.list_settings[1].value("default_bladebro_version")

            self.list_settings[1].endGroup()

        self.ui_preferences_zoom_dpsn.setValue(float(default_zoom_step))
        self.ui_preferences_default_color_combo.setCurrentIndex(default_shape_color)
        self.ui_preferences_default_quality_dspn.setValue(default_shape_factor)
        self.ui_preferences_default_transparency_dspn.setValue(default_shape_transparency)
        self.ui_preferences_igs_surf_chk.setChecked(default_igs_surf_check_state)
        self.ui_preferences_igs_surf_exception_edit.setText(default_igs_surf_exception)

        self.ui_preferences_igs_3d_cur_chk.setChecked(default_igs_3d_cur_check_state)
        self.ui_preferences_igs_3d_cur_exception_edit.setText(default_igs_3d_cur_exception)

        self.ui_preferences_igs_2d_cur_chk.setChecked(default_igs_2d_cur_check_state)
        self.ui_preferences_igs_2d_cur_exception_edit.setText(default_igs_2d_cur_exception)

        self.ui_preferences_tecplot_2d_chk.setChecked(default_tecplot_2d_check_state)

        self.ui_preferences_running_bladepro_version_edit.setText(default_bladebro_version)

        self.ui_preferences_ok_btn.clicked.connect(self.okAction)
        self.ui_preferences_cancel_btn.clicked.connect(self.cancelAction)
        self.ui_preferences_apply_btn.clicked.connect(self.applyAction)

    def okAction(self):
        """
        Method for applying user preferences and closing the dialog.
        
        @return None
        """
        self.applyAction()


        self.close()

    def cancelAction(self):
        """
        Method simply for closing the dialog.

        @return None
        """
        self.close()

    def applyAction(self):
        """
        Method for applying user preferences but not closing the dialog.

        @return None
        """
        self.saveSettings(1)

        self.list_settings[1].beginGroup("shapes_settings")

        self.op_viewer.default_shape_color = int(self.list_settings[1].value("default_shape_color"))
        self.op_viewer.default_shape_factor = float(self.list_settings[1].value("default_shape_quality"))
        self.op_viewer.default_shape_transparency = float(self.list_settings[1].value("default_shape_transparency"))
        self.op_viewer.ui_display_zoomfactor_dspn.setValue(float(self.list_settings[1].value("default_zoomfactor")))

        self.list_settings[1].endGroup()



        # will only update fields in the output_viewer GUI in case the program just started.
        if self.first_default:
            self.op_viewer.ui_shape_setcolor_combo.setCurrentIndex(self.op_viewer.default_shape_color)
            self.op_viewer.ui_shape_quality_dspn.setValue(self.op_viewer.default_shape_factor)
            self.op_viewer.ui_shape_transparency_dspn.setValue(self.op_viewer.default_shape_transparency )

        self.first_default = False



    def saveSettings(self, setting, restore=False):
        """
        Method called by applyAction() that indeed sets the configurations.

        @param setting [int] always 1 for the moment. It support a number of different settings, but not yet
        implemented
        @return None
        """
        if restore is False:
            to_be_default_shape_color = self.ui_preferences_default_color_combo.currentIndex()
            to_be_default_shape_factor = self.ui_preferences_default_quality_dspn.value()
            to_be_default_shape_transparency = self.ui_preferences_default_transparency_dspn.value()
            to_be_default_zoom_step = self.ui_preferences_zoom_dpsn.value()
            to_be_default_igs_surf_check_state = self.ui_preferences_igs_surf_chk.isChecked()
            to_be_default_igs_surf_exception = self.ui_preferences_igs_surf_exception_edit.text()

            to_be_default_igs_3d_cur_check_state = self.ui_preferences_igs_3d_cur_chk.isChecked()
            to_be_default_igs_3d_cur_exception = self.ui_preferences_igs_3d_cur_exception_edit.text()

            to_be_default_igs_2d_cur_check_state = self.ui_preferences_igs_2d_cur_chk.isChecked()
            to_be_default_igs_2d_cur_exception = self.ui_preferences_igs_2d_cur_exception_edit.text()

            to_be_default_tecplot_2d_check_state = self.ui_preferences_tecplot_2d_chk.isChecked()

            to_be_default_bladebro_version = self.ui_preferences_running_bladepro_version_edit.text()


        else:
            # below there is the "standard" values for preferences. This is standard values are set every time a user
            # starts the program for the first time

            to_be_default_shape_color = 0
            to_be_default_shape_factor = 1
            to_be_default_shape_transparency = 0
            to_be_default_zoom_step = 1.2
            to_be_default_igs_surf_check_state = True
            to_be_default_igs_surf_exception = 'HUB; SHROUD; STREAM'

            to_be_default_igs_3d_cur_check_state = True
            to_be_default_igs_3d_cur_exception = 'HUB; SHROUD'

            to_be_default_igs_2d_cur_check_state = False
            to_be_default_igs_2d_cur_exception = ''

            to_be_default_tecplot_2d_check_state = True

            to_be_default_bladebro_version = "bladepro"


        self.list_settings[setting].beginGroup("shapes_settings")

        self.list_settings[setting].setValue("default_shape_color", to_be_default_shape_color)
        self.list_settings[setting].setValue("default_shape_quality", to_be_default_shape_factor)
        self.list_settings[setting].setValue("default_shape_transparency", to_be_default_shape_transparency)
        self.list_settings[setting].setValue("default_zoomfactor", to_be_default_zoom_step)
        self.list_settings[setting].setValue("default_transformation", [0, 0, 0, 0, 2])

        self.list_settings[setting].endGroup()

        self.list_settings[setting].beginGroup("outputs_settings")

        self.list_settings[setting].setValue("default_igs_surf_check_state", to_be_default_igs_surf_check_state)
        self.list_settings[setting].setValue("default_igs_surf_exception", to_be_default_igs_surf_exception)
        self.list_settings[setting].setValue("default_igs_3d_cur_check_state", to_be_default_igs_3d_cur_check_state)
        self.list_settings[setting].setValue("default_igs_3d_cur_exception", to_be_default_igs_3d_cur_exception)
        self.list_settings[setting].setValue("default_igs_2d_cur_check_state", to_be_default_igs_2d_cur_check_state)
        self.list_settings[setting].setValue("default_igs_2d_cur_exception", to_be_default_igs_2d_cur_exception)
        self.list_settings[setting].setValue("default_tecplot_check_state", to_be_default_tecplot_2d_check_state)

        self.list_settings[setting].endGroup()

        self.list_settings[setting].beginGroup("bladepro_settings")

        self.list_settings[setting].setValue("default_bladebro_version", to_be_default_bladebro_version)


        self.list_settings[setting].endGroup()




