import sys
from PyQt4 import QtGui

print("Attempting to load GUI files...")

global qappInstance
qappInstance = None

def errorMissingGUI(gui_type):
    global qappInstance
    if (not QtGui.QApplication.instance()) and (not qappInstance):
        qappInstance = QtGui.QApplication(sys.argv)
    print("ERROR: %s GUI python code not found! Cannot run!" % gui_type)
    QtGui.QMessageBox.critical(None, "Error",
        ("%s GUI python code not found! Cannot run!\n\n" +
        "(If you are a user, this is a bug! If you are a developer... make sure to build your GUI files with BuildUIToPy.py!)") % gui_type)

try:
    import SetupGUI
except ImportError:
    errorMissingGUI("Setup")
    raise

try:
    import DetailsGUI
except ImportError:
    errorMissingGUI("Details")
    raise

try:
    import SortingGUI
except ImportError:
    errorMissingGUI("Sorting")
    raise
