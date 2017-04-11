"""@package occ_modules.qt_display

File that contains customQtViewer3d class that is a customization of the qtViewer3d of OCC library.

The class qtViewer3d is a class that in general setups the visualization and the events for the display of OCC objects.

"""

from OCC.Display.qtDisplay import qtViewer3d

class customQtViewer3d(qtViewer3d):
    """
    Customized class from OCC.Display.qtDisplay.qtViewer3d of PythonOCC, inheriting it and defining a new one.

    This costumized class allows to change de zoom step of mouse wheel event on Qt environment.

    """
    def __init__(self, parent=None):
        super(customQtViewer3d, self).__init__(parent)

    def wheelEvent(self, event):
        """
        Graphic method of the qtViewer3d of pythonOCC that attributes function to Mouse Wheel on Qt environment.

        @param event [QtGui.QWheelEvent] Object created triggered by user Mouse Wheel movement.
        @return None

        """
        try:
            delta = event.delta()
        except:
            delta = event.angleDelta().y()
        if delta > 0:
            zoom_factor = self.zoomfactor
        else:
            zoom_factor = 1 / 2

        # print(self.zoomfactor)
        self._display.Repaint()
        self._display.ZoomFactor(zoom_factor)

    def cursor(self, value):
        if not self._current_cursor == value:

            self._current_cursor = value
            cursor = self._available_cursors.get(value)

