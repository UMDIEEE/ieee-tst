import os
import sys
from PyQt4 import uic

ui_to_py = [
            [ "Setup.ui", os.path.join("itst", "gui", "SetupGUI.py") ],
            [ "Sorting.ui", os.path.join("itst", "gui", "SortingGUI.py") ],
            [ "Details.ui", os.path.join("itst", "gui", "DetailsGUI.py") ],
           ]

for ui2py_pair in ui_to_py:
    ui_file, py_file = ui2py_pair
    print("Compiling %s to Python code %s..." % (ui_file, py_file))
    
    if os.path.isfile(py_file + "c"):
        print(" => Removing stale compiled Python code: %s" % (py_file + "c"))
        os.remove(py_file + "c")
    
    try:
        py_file_fh = open(py_file, "w")
    except IOError:
        print("ERROR: Could not open %s for writing!" % py_file)
        sys.exit(1)
    
    uic.compileUi(ui_file, py_file_fh)
    
    py_file_fh.close()