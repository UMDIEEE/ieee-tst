from PyQt4 import QtGui, QtCore

from gui import SortingGUI

class SortWindow(QtGui.QDialog, SortingGUI.Ui_sortDlg):
    def __init__(self, file_table, num_files, state = None):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super(self.__class__, self).__init__(None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.MSWindowsFixedSizeDialogHint)
        self.setupUi(self)  # This is defined in design.py file automatically
                            # It sets up layout and widgets that are defined
        
        self.file_table = file_table
        self.num_files = num_files
        
        self.saveBtn.setEnabled(False)
        self.revertBtn.setEnabled(False)

        # D:\IEEE Renamed Exams\Mini Testing Valid Exams