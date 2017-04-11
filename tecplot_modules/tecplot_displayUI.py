# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\FASX781\Desktop\BladePy\tecplot_modules\tecplot_displayUI.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(315, 859)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.ui_tecplot1_dockw = QtGui.QDockWidget(MainWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_tecplot1_dockw.sizePolicy().hasHeightForWidth())
        self.ui_tecplot1_dockw.setSizePolicy(sizePolicy)
        self.ui_tecplot1_dockw.setMinimumSize(QtCore.QSize(69, 70))
        self.ui_tecplot1_dockw.setFeatures(QtGui.QDockWidget.DockWidgetFloatable|QtGui.QDockWidget.DockWidgetMovable)
        self.ui_tecplot1_dockw.setObjectName(_fromUtf8("ui_tecplot1_dockw"))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.ui_tecplot1_dockcontents_vl = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.ui_tecplot1_dockcontents_vl.setObjectName(_fromUtf8("ui_tecplot1_dockcontents_vl"))
        self.ui_tecplot1_widget = QtGui.QWidget(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_tecplot1_widget.sizePolicy().hasHeightForWidth())
        self.ui_tecplot1_widget.setSizePolicy(sizePolicy)
        self.ui_tecplot1_widget.setMinimumSize(QtCore.QSize(0, 0))
        self.ui_tecplot1_widget.setBaseSize(QtCore.QSize(50, 50))
        self.ui_tecplot1_widget.setAcceptDrops(False)
        self.ui_tecplot1_widget.setObjectName(_fromUtf8("ui_tecplot1_widget"))
        self.ui_tecplot1_widget_vl = QtGui.QVBoxLayout(self.ui_tecplot1_widget)
        self.ui_tecplot1_widget_vl.setObjectName(_fromUtf8("ui_tecplot1_widget_vl"))
        self.ui_tecplot1_dockcontents_vl.addWidget(self.ui_tecplot1_widget)
        self.ui_tecplot1_dockw.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.ui_tecplot1_dockw)
        self.ui_tecplot2_dockw = QtGui.QDockWidget(MainWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_tecplot2_dockw.sizePolicy().hasHeightForWidth())
        self.ui_tecplot2_dockw.setSizePolicy(sizePolicy)
        self.ui_tecplot2_dockw.setMinimumSize(QtCore.QSize(69, 70))
        self.ui_tecplot2_dockw.setAccessibleName(_fromUtf8(""))
        self.ui_tecplot2_dockw.setFeatures(QtGui.QDockWidget.DockWidgetFloatable|QtGui.QDockWidget.DockWidgetMovable)
        self.ui_tecplot2_dockw.setObjectName(_fromUtf8("ui_tecplot2_dockw"))
        self.ui_tecplot2_dockcontents = QtGui.QWidget()
        self.ui_tecplot2_dockcontents.setObjectName(_fromUtf8("ui_tecplot2_dockcontents"))
        self.ui_tecplot2_dockcontents_vl = QtGui.QVBoxLayout(self.ui_tecplot2_dockcontents)
        self.ui_tecplot2_dockcontents_vl.setObjectName(_fromUtf8("ui_tecplot2_dockcontents_vl"))
        self.ui_tecplot_widget_2 = QtGui.QWidget(self.ui_tecplot2_dockcontents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_tecplot_widget_2.sizePolicy().hasHeightForWidth())
        self.ui_tecplot_widget_2.setSizePolicy(sizePolicy)
        self.ui_tecplot_widget_2.setObjectName(_fromUtf8("ui_tecplot_widget_2"))
        self.ui_tecplot2_widget_vl = QtGui.QVBoxLayout(self.ui_tecplot_widget_2)
        self.ui_tecplot2_widget_vl.setObjectName(_fromUtf8("ui_tecplot2_widget_vl"))
        self.ui_tecplot2_dockcontents_vl.addWidget(self.ui_tecplot_widget_2)
        self.ui_tecplot2_dockw.setWidget(self.ui_tecplot2_dockcontents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.ui_tecplot2_dockw)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        MainWindow.setWhatsThis(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.ui_tecplot1_dockw.setWindowTitle(_translate("MainWindow", "TecPlot 1", None))
        self.ui_tecplot2_dockw.setWindowTitle(_translate("MainWindow", "TecPlot 2", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

