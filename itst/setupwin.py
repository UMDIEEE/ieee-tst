from PyQt4 import QtGui, QtCore

import os
import ansiconv
import traceback

from gui import SetupGUI
from detailswin import DetailsWindow
from sortwin import SortWindow
from taskthread import IESScanThread, IESValidateThread

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
        
        self.statusLbl.linkActivated.connect(self.statusLink)
        
        # Set font
        self.default_font = QtGui.QFont()
        
        self.bold_font = QtGui.QFont()
        self.bold_font.setBold(True)
        self.bold_font.setWeight(75)
        self.testRangeLbl.setFont(self.bold_font)
        
        self.statusLbl.hide()
        
        self.startRangeSpinBox.setRange(1, self.endRangeSpinBox.value())
        
        self.startRangeSpinBox.valueChanged.connect(self.updateEndRange)
        self.endRangeSpinBox.valueChanged.connect(self.updateStartRange)
        
        self.file_list = []
        self.err_str = ""
        self.iesthread = None
        self.last_focus = None
    
    # This fixes a crash issue when exiting...
    #def closeEvent(self, event):
    #    print("Exiting...")
    #    exit()
    
    def updateStartRange(self):
        self.startRangeSpinBox.setRange(1, self.endRangeSpinBox.value())
        self.statusLbl.setText("From file <b>%s</b><br />...to file <b>%s</b>" %
            (self.file_list[self.startRangeSpinBox.value() - 1], self.file_list[self.endRangeSpinBox.value() - 1]))
    
    def updateEndRange(self):
        self.endRangeSpinBox.setMinimum(self.startRangeSpinBox.value())
        self.statusLbl.setText("From file <b>%s</b><br />...to file <b>%s</b>" %
            (self.file_list[self.startRangeSpinBox.value() - 1], self.file_list[self.endRangeSpinBox.value() - 1]))
    
    def about(self):
        msgbox = QtGui.QMessageBox(QtGui.QMessageBox.Information, "About",
            "IEEE Sorting Tool v1.0 by Albert Huang<br /><br /><a style=\"color: white;\" href=\"https://github.com/UMDIEEE/ieee-tst\">GitHub</a>",
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
    
    def setLabelSelDirFirst(self):
        self.testRangeLbl.setFont(self.bold_font)
        self.testRangeLbl.setText("Select the testbank directory first, then select your test range!")
        self.fromLbl.setEnabled(False)
        
        self.startRangeSpinBox.setEnabled(False)
        self.toLbl.setEnabled(False)
        self.endRangeSpinBox.setEnabled(False)
        
        self.goBtn.setEnabled(False)
    
    def dirChanged(self):
        curdir = str(self.testbankDirTxt.text())
        
        self.statusLbl.setStyleSheet("")
        self.statusLbl.setMargin(0)
        self.statusLbl.hide()
        
        if curdir == "":
            self.testbankDirTxt.setStyleSheet("")
            self.setLabelSelDirFirst()
        elif os.path.isdir(curdir):
            #self.testbankDirTxt.setStyleSheet("background-color: #003300;")
            self.goValidate()
        else:
            self.setLabelSelDirFirst()
            self.testbankDirTxt.setStyleSheet("background-color: #660000;")
    
    def list_ies_validate(self, file_list, total_num_files):
        print "Got to this point!"
        
        self.file_list = file_list
        
        # Green background
        self.testbankDirTxt.setStyleSheet("background-color: #003300;")
        
        # Set test range max:
        self.endRangeSpinBox.setMaximum(len(file_list))
        self.endRangeSpinBox.setValue(len(file_list))
        
        self.startRangeSpinBox.setRange(1, self.endRangeSpinBox.value())
        
        self.statusLbl.setText("From file <b>%s</b><br />...to file <b>%s</b>" % (file_list[0], file_list[len(file_list) - 1]))
        self.statusLbl.show()
        
        # Enable test range controls:
        # fromLbl, startRangeSpinBox, toLbl, endRangeSpinBox
        self.fromLbl.setEnabled(True)
        self.startRangeSpinBox.setEnabled(True)
        self.toLbl.setEnabled(True)
        self.endRangeSpinBox.setEnabled(True)
        
        # Set testRangeLbl font and text
        self.testRangeLbl.setFont(self.default_font)
        self.testRangeLbl.setText("Test Range:")
        
        # Enable go button
        self.goBtn.setEnabled(True)
    
    def prog_ies(self, current_num, total_num, file_name):
        self.progressBar.setMaximum(total_num)
        self.progressBar.setValue(current_num)
    
    def statusLink(self, link):
        if (link == "#show_error"):
            msgbox = QtGui.QMessageBox(QtGui.QMessageBox.Critical, "Error",
                "An error occurred while validating the files!",
                QtGui.QMessageBox.Ok, self)
            
            err_msg_split = str(self.err_str).split("\n")
            
            short_err_str = "\n".join(err_msg_split[:5])
            
            if len(err_msg_split) > 5:
                short_err_str += "\n..."
                detailBtn = msgbox.addButton("Show more details...", QtGui.QMessageBox.HelpRole)
            
            msgbox.setInformativeText(ansiconv.to_plain(short_err_str))
            msgbox.setWindowModality(QtCore.Qt.ApplicationModal)
            res = msgbox.exec_()
            
            if len(err_msg_split) > 5:
                if res == 0:
                    detailsWin = DetailsWindow("Error Details", self.err_str, parent = self)
                    detailsWin.setWindowModality(QtCore.Qt.ApplicationModal)
                    detailsWin.exec_()
            
            self.setLabelSelDirFirst()
            self.browseBtn.setFocus()
    
    def err_validate_ies(self, err_str):
        print("VALIDATE ERR")
        self.testbankDirTxt.setStyleSheet("background-color: #660000;")
        
        self.statusLbl.setStyleSheet("background-color: #660000; color: #FFFFFF;")
        self.statusLbl.setText("An error occurred while validating the files! <a style=\"color: white;\" href=\"#show_error\">Show Details...</a>")
        self.statusLbl.setMargin(5)
        self.statusLbl.show()
        
        self.err_str = err_str
        
        self.setLabelSelDirFirst()
        
        if self.last_focus:
            print("Attempting to restore focus to: "+str(self.last_focus))
            self.last_focus.setFocus()
    
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
        #self.goBtn.setEnabled(True)
        
        # Disable the progress bar
        self.progressBar.setEnabled(False)
        self.progressBar.setValue(0)
        
        # Restore focus
        if self.last_focus:
            print("Attempting to restore focus to: "+str(self.last_focus))
            self.last_focus.setFocus()
    
    def table_ies(self, file_table, total_num_files):
        curname = str(self.nameTxt.text()).strip()
        curdir = str(self.testbankDirTxt.text())
        start_range = self.startRangeSpinBox.value()
        end_range = self.endRangeSpinBox.value()
        
        sortWin = SortWindow(curname, curdir, file_table, total_num_files, start_range, end_range)
        self.close()
        sortWin.exec_()
    
    def goValidate(self):
        self.last_focus = QtGui.QApplication.focusWidget()
        self.testRangeLbl.setText("Validating directory...")
        
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
                    
                    self.fromLbl.setEnabled(False)
                    self.startRangeSpinBox.setEnabled(False)
                    self.toLbl.setEnabled(False)
                    self.endRangeSpinBox.setEnabled(False)
                    
                    # Enable the progress bar
                    self.progressBar.setEnabled(True)
                    
                    # Initialize and start thread
                    self.iesthread = IESValidateThread(curdir)
                    self.iesthread.finished.connect(self.end_ies)
                    self.iesthread.progSignal.connect(self.prog_ies)
                    self.iesthread.errSignal.connect(self.err_validate_ies)
                    self.iesthread.listSignal.connect(self.list_ies_validate)
                    self.iesthread.start()
                else:
                    print("Error: Thread already created and started!")
                    raise Exception("Internal IEEE Exam Scanner thread already created and started!")
            except (IOError, OSError), err:
                print("IOError/OSError: " + str(err))
                QtGui.QMessageBox.critical(self, "Error", str(err))
                self.setLabelSelDirFirst()
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
                self.setLabelSelDirFirst()
        elif os.path.isfile(curdir):
            print("Error: file specified, not directory...")
            QtGui.QMessageBox.critical(self, "Error", "You specified a file, not a directory!")
            self.setLabelSelDirFirst()
        else:
            print("Error: can't find directory specified!")
            QtGui.QMessageBox.critical(self, "Error", "The directory you specified does not exist!")
            self.setLabelSelDirFirst()
    
    def go(self):
        if str(self.nameTxt.text()).strip() == "":
            print("ERROR: No name specified!")
            QtGui.QMessageBox.critical(self, "Error", "No name specified.")
            self.nameTxt.setFocus()
            return
        
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
                    self.iesthread = IESScanThread(curdir)
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
