from PyQt4 import QtGui
import qdarkstyle

import sys
import colorama

from itst import SetupWindow

# NOTE: wrapping things in main() seems to prevent PyQT crash on exit
#      (on Windows, maybe other platforms as well)
def main():
    # Initialize terminal colors for Windows (and do nothing for *nix)
    colorama.init()

    # Create the application and the main window
    app = QtGui.QApplication(sys.argv)
    window = SetupWindow()

    # This is needed to ensure that things clean up nicely
    #app.setActiveWindow(window)

    # Setup stylesheet
    app.setStyleSheet(qdarkstyle.load_stylesheet(pyside = False))

    # Run
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
