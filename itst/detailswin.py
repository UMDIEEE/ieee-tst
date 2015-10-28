from PyQt4 import QtGui, QtCore
import ansiconv

from gui import DetailsGUI

class DetailsWindow(QtGui.QDialog, DetailsGUI.Ui_detailsDlg):
    def __init__(self, title, details, parent = None):
        super(self.__class__, self).__init__(parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.MSWindowsFixedSizeDialogHint)
        self.setupUi(self)  # This is defined in design.py file automatically
                            # It sets up layout and widgets that are defined
        
        self.setWindowTitle("IEEE Testbank Tool - " + title)
        
        # Pre-processing
        details = str(details).replace("\n", "<br />\n")
        
        self.detailsTxt.setText("<style>%s</style>%s" % (ansiconv.base_css(), ansiconv.to_html(details)))