from PyQt4 import QtGui, QtCore
import qdarkstyle

import DetailsGUI
import SetupGUI
import SortingGUI

import os
import sys
import traceback

import colorama
import ansiconv

import IEEEExamScanner

colorama.init()

class IESThread(QtCore.QThread):
    progSignal = QtCore.pyqtSignal(int, int, str, name = "progCallback")
    errSignal = QtCore.pyqtSignal(str, name="errCallback")
    tableSignal = QtCore.pyqtSignal(list, int, name="tableCallback")
    
    def __init__(self, srcdir):
        super(self.__class__, self).__init__()
        self.srcdir = srcdir
        
        #self.progSignal = QtCore.pyqtSignal(int, int, str, name = "progCallback") #QtCore.SIGNAL("progCallback")
        #self.errSignal = QtCore.pyqtSignal(str, name="errCallback") #QtCore.SIGNAL("errCallback")
    
    def __del__(self):
        self.wait()
    
    def run(self):
        res = IEEEExamScanner.scanDir(self.srcdir, self.progCallback, self.errCallback)
        
        # Success!
        if res:
            file_table, total_num_files = res
            self.tableSignal.emit(file_table, total_num_files)
    
    def progCallback(self, current_num, total_num, file_name):
        self.progSignal.emit(current_num, total_num, file_name)
    
    def errCallback(self, err_str):
        self.errSignal.emit(err_str)

class DetailsWindow(QtGui.QDialog, DetailsGUI.Ui_detailsDlg):
    def __init__(self, title, details, parent = None):
        super(self.__class__, self).__init__(parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.MSWindowsFixedSizeDialogHint)
        self.setupUi(self)  # This is defined in design.py file automatically
                            # It sets up layout and widgets that are defined
        
        self.setWindowTitle("IEEE Testbank Tool - " + title)
        
        # Pre-processing
        details = str(details).replace("\n", "<br />\n")
        
        self.detailsTxt.setText("<style>%s</style>%s" % (ansiconv.base_css(), ansiconv.to_html(details)))
        
class SetupWindow(QtGui.QDialog, SetupGUI.Ui_setupDlg):
    def __init__(self):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super(self.__class__, self).__init__(None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.MSWindowsFixedSizeDialogHint)
        self.setupUi(self)  # This is defined in design.py file automatically
                            # It sets up layout and widgets that are defined
        self.browseBtn.clicked.connect(self.browse_folder)
        self.goBtn.clicked.connect(self.go)
        
        self.aboutBtn.clicked.connect(self.about)
        self.exitBtn.clicked.connect(self.exit)
        
        self.testbankDirTxt.textChanged.connect(self.dirChanged)
        
        self.iesthread = None
    
    def about(self):
        msgbox = QtGui.QMessageBox(QtGui.QMessageBox.Information, "About",
            "IEEE Sorting Tool v1.0 by Albert Huang<br /><br /><a style=\"color: white;\" href=\"http://example.com/\">Click Here!</a>",
            QtGui.QMessageBox.Ok, self)
        msgbox.setTextFormat(QtCore.Qt.RichText)
        msgbox.setWindowModality(QtCore.Qt.ApplicationModal)
        res = msgbox.exec_()
        #QtGui.QMessageBox.information(self, "About", )
    
    def browse_folder(self):
        curdir = str(self.testbankDirTxt.text())
        if (curdir != "") and os.path.isdir(curdir):
            directory = QtGui.QFileDialog.getExistingDirectory(self, "Pick a folder", curdir)
        else:
            directory = QtGui.QFileDialog.getExistingDirectory(self, "Pick a folder")
        
        if directory:
            self.testbankDirTxt.setText(directory)
    
    def exit(self):
        QtGui.QApplication.quit()
    
    def dirChanged(self):
        curdir = str(self.testbankDirTxt.text())
        if curdir == "":
            self.testbankDirTxt.setStyleSheet("")
        elif os.path.isdir(curdir):
            self.testbankDirTxt.setStyleSheet("background-color: #003300;")
        else:
            self.testbankDirTxt.setStyleSheet("background-color: #660000;")
    
    def prog_ies(self, current_num, total_num, file_name):
        self.progressBar.setMaximum(total_num)
        self.progressBar.setValue(current_num)
    
    def err_ies(self, err_str):
        self.testbankDirTxt.setStyleSheet("background-color: #660000;")
        
        msgbox = QtGui.QMessageBox(QtGui.QMessageBox.Critical, "Error",
            "An error occurred while scanning the files!",
            QtGui.QMessageBox.Ok, self)
        
        err_msg_split = str(err_str).split("\n")
        
        short_err_str = "\n".join(err_msg_split[:5])
        
        if len(err_msg_split) > 5:
            short_err_str += "\n..."
            detailBtn = msgbox.addButton("Show more details...", QtGui.QMessageBox.HelpRole)
        
        msgbox.setInformativeText(ansiconv.to_plain(short_err_str))
        msgbox.setWindowModality(QtCore.Qt.ApplicationModal)
        res = msgbox.exec_()
        
        if len(err_msg_split) > 5:
            if res == 0:
                detailsWin = DetailsWindow("Error Details", err_str, parent = self)
                detailsWin.setWindowModality(QtCore.Qt.ApplicationModal)
                detailsWin.exec_()
        self.browseBtn.setFocus()
    
    def end_ies(self):
        # Set the thread to None
        self.iesthread = None
        
        # Enable fields
        self.testbankDirTxt.setEnabled(True)
        self.browseBtn.setEnabled(True)
        self.goBtn.setEnabled(True)
        
        # Disable the progress bar
        self.progressBar.setEnabled(False)
        self.progressBar.setValue(0)
    
    def table_ies(self, file_table, total_num_files):
        sortWin = SortWindow(file_table, total_num_files)
        self.close()
        sortWin.exec_()
    
    def go(self):
        curdir = str(self.testbankDirTxt.text())
        if os.path.isdir(curdir):
            try:
                os.listdir(curdir)
                # If we made it this far, we should be able to start scanning!
                if not self.iesthread:
                    # Disable all fields
                    self.testbankDirTxt.setEnabled(False)
                    self.browseBtn.setEnabled(False)
                    self.goBtn.setEnabled(False)
                    
                    # Enable the progress bar
                    self.progressBar.setEnabled(True)
                    
                    # Initialize and start thread
                    self.iesthread = IESThread(curdir)
                    self.iesthread.finished.connect(self.end_ies)
                    self.iesthread.progSignal.connect(self.prog_ies)
                    self.iesthread.errSignal.connect(self.err_ies)
                    self.iesthread.tableSignal.connect(self.table_ies)
                    self.iesthread.start()
                else:
                    print("Error: Thread already created and started!")
                    raise Exception("Internal IEEE Exam Scanner thread already created and started!")
            except (IOError, OSError), err:
                print("IOError/OSError: " + str(err))
                QtGui.QMessageBox.critical(self, "Error", str(err))
            except Exception, err:
                print("Critical error occurred! Something went really wrong...")
                print(traceback.format_exc())
                msgbox = QtGui.QMessageBox(QtGui.QMessageBox.Critical, "Error",
                    "A critical error occurred! This error is a bug, and may cause issues if you continue running this program.",
                    QtGui.QMessageBox.Abort | QtGui.QMessageBox.Ignore, self)
                msgbox.setDefaultButton(QtGui.QMessageBox.Abort)
                msgbox.setEscapeButton(QtGui.QMessageBox.Abort)
                msgbox.setInformativeText(traceback.format_exc())
                msgbox.setWindowModality(QtCore.Qt.ApplicationModal)
                res = msgbox.exec_()
                if res == QtGui.QMessageBox.Abort:
                    QtGui.QApplication.quit()
        elif os.path.isfile(curdir):
            print("Error: file specified, not directory...")
            QtGui.QMessageBox.critical(self, "Error", "You specified a file, not a directory!")
        else:
            print("Error: can't find directory specified!")
            QtGui.QMessageBox.critical(self, "Error", "The directory you specified does not exist!")

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
        
        self.endRangeSpinBox.setRange(1, num_files)
        self.endRangeSpinBox.setValue(num_files)
        
        self.saveBtn.setEnabled(False)
        self.revertBtn.setEnabled(False)
        
        self.startRangeSpinBox.setRange(1, self.endRangeSpinBox.value())
        
        self.startRangeSpinBox.valueChanged.connect(self.updateEndRange)
        self.endRangeSpinBox.valueChanged.connect(self.updateStartRange)
        self.lockTestRangeChk.stateChanged.connect(self.updateRangeLock)
    
    def updateStartRange(self):
        self.startRangeSpinBox.setRange(1, self.endRangeSpinBox.value())
    
    def updateEndRange(self):
        self.endRangeSpinBox.setRange(self.startRangeSpinBox.value(), self.num_files)
    
    def updateRangeLock(self, state):
        locked = (state == QtCore.Qt.Checked)
        
        en_state = not locked
        
        self.fromLbl.setEnabled(en_state)
        self.toLbl.setEnabled(en_state)
        self.startRangeSpinBox.setEnabled(en_state)
        self.endRangeSpinBox.setEnabled(en_state)
        
        if locked:
            self.lockTestRangeChk.setText("Uncheck to unlock the test range.")
        else:
            self.lockTestRangeChk.setText("Check to lock the test range.")
        
        # D:\IEEE Renamed Exams\Mini Testing Valid Exams

# create the application and the main window
app = QtGui.QApplication(sys.argv)
window = SetupWindow()
#window = SortWindow()

# setup stylesheet
app.setStyleSheet(qdarkstyle.load_stylesheet(pyside = False))

# run
window.show()
app.exec_()