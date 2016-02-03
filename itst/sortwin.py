from PyQt4 import QtGui, QtCore

from gui import SortingGUI
from ies import parseFileName, getScriptPath

import re
import os
import sys
import subprocess
import traceback

import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class SortWindow(QtGui.QDialog, SortingGUI.Ui_sortDlg):
    def __init__(self, confname, srcdir, file_table, num_files, start_range, end_range, state = None):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super(self.__class__, self).__init__(None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.MSWindowsFixedSizeDialogHint)
        self.setupUi(self)  # This is defined in design.py file automatically
                            # It sets up layout and widgets that are defined
        
        self.setWindowFlags(self.windowFlags() &
            QtCore.Qt.WindowMinimizeButtonHint &
            QtCore.Qt.WindowSystemMenuHint)
        
        # Save input
        self.file_table = file_table
        self.num_files = num_files
        self.confname = confname
        self.srcdir = srcdir
        self.start_range = start_range
        self.end_range = end_range
        self.state = state
        
        self.current_exam = -1
        
        if state == None:
            current_exam = self.start_range
            #self.old_exam = self.current_exam
            self.state = {
                            "user_state" : {
                                                "current_exam" : 1,
                                                "confname" : confname,
                                                "srcdir" : srcdir,
                                                "start_range" : start_range,
                                                "end_range" : end_range,
                                                "num_files" : num_files,
                                           },
                            "exam_data"  : {}
                         }
            # Populate exam data table
            f_index = 1
            for f_entry in file_table:
                # (filename, mime type)
                if (f_index >= self.start_range) and (f_index <= self.end_range):
                    self.state["exam_data"][f_index] = { "file_name" : f_entry[0], "filled": False, "data" : {} }
                f_index += 1
        else:
            current_exam = self.state["user_state"]["current_exam"]
            #self.old_exam = self.current_exam
        
        # This is an invalid value, but it will get changed once
        # self.changeExam() is called!
        #self.old_exam = -1
        
        # Viewing exam (for tooltip updates)
        self.viewing_exam = current_exam
        
        self.formDirty = False
        self.examChanging = False
        
        self.saveBtn.setEnabled(False)
        self.revertBtn.setEnabled(False)
        
        # Save / revert connect
        self.saveBtn.clicked.connect(self.saveExamData)
        self.revertBtn.clicked.connect(self.revertExamData)
        
        self.testSlider.setRange(start_range, end_range)
        
        self.testSlider.sliderPressed.connect(self.showExamTooltip)
        #self.testSlider.sliderReleased.connect(self.changeExam)
        self.testSlider.setTracking(False)
        
        # We need QueuedConnection to make things workaround a Qt bug
        # with sliders moving around by themselves when a QDialog is
        # present...
        self.testSlider.valueChanged.connect(self.changeExamSlider, QtCore.Qt.QueuedConnection)
        self.testSlider.sliderMoved.connect(self.updateCurrentExam, QtCore.Qt.QueuedConnection)
        
        #self.testSlider.valueChanged.connect(self.changeExamSlider)
        #self.testSlider.sliderMoved.connect(self.updateCurrentExam)
        
        self.prevTestBtn.clicked.connect(self.decreaseExam)
        self.nextTestBtn.clicked.connect(self.increaseExam)
        self.openTestBtn.clicked.connect(self.openExam)
        self.firstTestBtn.clicked.connect(self.firstExam)
        self.lastTestBtn.clicked.connect(self.lastExam)
        
        self.autofillBtn.clicked.connect(self.autoFillCurrentExam)
        
        # Set dirty states
        
        # Valid text radio button group
        self.validTestAllGoodRadio.toggled.connect(self.changeFormHandler)
        self.validTestWrongTestRadio.toggled.connect(self.changeFormHandler)
        self.validTestJunkRadio.toggled.connect(self.changeFormHandler)
        
        # Class textbox
        self.classTxt.textChanged.connect(self.changeFormHandler)
        
        # Semester combobox
        self.semesterCBox.currentIndexChanged.connect(self.changeFormHandler)
        
        # Year spinbox
        self.yearSpinBox.valueChanged.connect(self.changeFormHandler)
        
        # Professor last name, first name textboxes
        self.profLastNameTxt.textChanged.connect(self.changeFormHandler)
        self.profFirstNameTxt.textChanged.connect(self.changeFormHandler)
        
        # Exam type - Quiz/Midterm/Final radio button group
        self.testTypeQuizRadio.toggled.connect(self.changeFormHandler)
        self.testTypeMidtermRadio.toggled.connect(self.changeFormHandler)
        self.testTypeFinalRadio.toggled.connect(self.changeFormHandler)
        
        # Test number spinbox
        self.testNumSpinBox.valueChanged.connect(self.changeFormHandler)
        
        # Test Scan/Original Type - radio button group
        self.testScannedRadio.toggled.connect(self.changeFormHandler)
        self.testOCRWithImageRadio.toggled.connect(self.changeFormHandler)
        self.testOCRWithoutImageRadio.toggled.connect(self.changeFormHandler)
        self.testOriginalRadio.toggled.connect(self.changeFormHandler)
        
        # Contains problems/solutions
        self.testProblemsCheckBox.toggled.connect(self.changeFormHandler)
        self.testSolutionsCheckBox.toggled.connect(self.changeFormHandler)
        
        # Addl exam info + file notes
        self.addlExamInfoTxt.textChanged.connect(self.changeFormHandler)
        self.fileNotesTxt.textChanged.connect(self.changeFormHandler)
        
        # Open timer
        self.openCountdown = 10
        
        self.openTimer = QtCore.QTimer()
        self.openTimer.setInterval(1000)
        self.openTimer.timeout.connect(self.openExamCountdown)
        
        ###########
        
        self.changeExam(current_exam)
        
        #self.goBtn.clicked.connect(self.go)
        
        # D:\IEEE Renamed Exams\Mini Testing Valid Exams
    
    def openExamCountdown(self):
        if self.openCountdown >= 0:
            self.openTestBtn.setEnabled(False)
            if self.openCountdown > 0:
                self.openTestBtn.setText("Opening... (%is)" % self.openCountdown)
            else:
                self.openTestBtn.setText("Opened! (%is)" % self.openCountdown)
            self.openCountdown -= 1
        else:
            self.openTimer.stop()
            self.openCountdown = 10
            self.openTestBtn.setText("Open")
            self.openTestBtn.setEnabled(True)
    
    def openExam(self):
        # Disable button!
        self.openTestBtn.setEnabled(False)
        self.openTestBtn.setText("Opening... (%is)" % self.openCountdown)
        
        # Start countdown...
        self.openTimer.start()
        
        # Figure out path
        exam_fn = self.state["exam_data"][self.current_exam]["file_name"]
        exam_full_path = os.path.join(self.state["user_state"]["srcdir"], exam_fn)
        
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', exam_full_path))
        elif os.name == 'nt':
            os.startfile(exam_full_path)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', exam_full_path))
    
    def closeEvent(self, event):
        if self.confirmExamState(task = "exiting"):
            self.writeExamData(check_exist = True)
            event.accept()
        else:
            event.ignore()
    
    # If check_exist is True, only write data if the data exists at all.
    def writeExamData(self, check_exist = False):
        exam_data_file = os.path.join(getScriptPath(), "exam_data.yml")
        if check_exist:
            file_exist = False
            try:
                test_fh = open(exam_data_file)
                test_fh.close()
                file_exist = True
            except:
                pass
            
            if not file_exist:
                return
        
        try:
            print "Saving to: %s" % (exam_data_file)
            config_fh = open(exam_data_file, "w")
            config_fh.write(yaml.dump(self.state, Dumper=Dumper))
            config_fh.close()
        except IOError:
            msgbox = QtGui.QMessageBox(QtGui.QMessageBox.Critical, "Error",
                "Could not save exam data! Error details:\n\n" + traceback.format_exc(),
                QtGui.QMessageBox.Ok, self)
    
    def saveExamData(self):
        # Save data from form!
        exam_data = self.state["exam_data"][self.current_exam]
        
        # First, set filled flag
        exam_data["filled"] = True
        
        # Set class data
        if self.classTxt.text(): exam_data["data"]["class"] = str(self.classTxt.text())
        else: exam_data["data"].pop("class", None)
        
        # Set profLastName
        if self.profLastNameTxt.text(): exam_data["data"]["profLastName"] = str(self.profLastNameTxt.text())
        else: exam_data["data"].pop("profLastName", None)
        
        # Set profFirstName
        if self.profFirstNameTxt.text(): exam_data["data"]["profFirstName"] = str(self.profFirstNameTxt.text())
        else: exam_data["data"].pop("profFirstName", None)
        
        # Set info
        if self.addlExamInfoTxt.text(): exam_data["data"]["info"] = str(self.addlExamInfoTxt.text())
        else: exam_data["data"].pop("info", None)
        
        # Set semester
        if self.semesterCBox.currentText(): exam_data["data"]["semester"] = str(self.semesterCBox.currentText())
        else: exam_data["data"].pop("semester", None)
        
        # Set status
        if self.validTestAllGoodRadio.isChecked(): exam_data["data"]["status"] = "good"
        elif self.validTestWrongTestRadio.isChecked(): exam_data["data"]["status"] = "wrongtest"
        elif self.validTestJunkRadio.isChecked(): exam_data["data"]["status"] = "junk"
        else: exam_data["data"].pop("status", None)
        
        # Set type
        if self.testTypeQuizRadio.isChecked(): exam_data["data"]["type"] = "Quiz"
        elif self.testTypeMidtermRadio.isChecked(): exam_data["data"]["type"] = "Midterm"
        elif self.testTypeFinalRadio.isChecked(): exam_data["data"]["type"] = "Final"
        else: exam_data["data"].pop("type", None)
        
        # Set year
        exam_data["data"]["year"] = self.yearSpinBox.value()
        
        # Set testNum
        exam_data["data"]["testNum"] = self.testNumSpinBox.value()
        
        # Set origin
        if self.testScannedRadio.isChecked(): exam_data["data"]["origin"] = "scanned"
        elif self.testOCRWithImageRadio.isChecked(): exam_data["data"]["origin"] = "ocrwithimage"
        elif self.testOCRWithoutImageRadio.isChecked(): exam_data["data"]["origin"] = "ocrwithoutimage"
        elif self.testOriginalRadio.isChecked(): exam_data["data"]["origin"] = "original"
        else: exam_data["data"].pop("type", None)
        
        # Set includes
        # This one's kinda funky, but we pop it off, then check for existence
        exam_data["data"].pop("includes", None)
        if self.testProblemsCheckBox.isChecked(): exam_data["data"]["includes"] = "problems"
        if self.testSolutionsCheckBox.isChecked():
            if "includes" in exam_data["data"]:
                exam_data["data"]["includes"] += ",solutions"
            else:
                exam_data["data"]["includes"] = "solutions"
        
        # Set fileNotes
        if self.fileNotesTxt.toPlainText(): exam_data["data"]["fileNotes"] = str(self.fileNotesTxt.toPlainText())
        else: exam_data["data"].pop("fileNotes", None)
        
        # Actually save file!
        self.writeExamData()
        
        # Disable revert/save, validate everything
        self.revertBtn.setEnabled(False)
        self.saveBtn.setEnabled(False)
        self.validateAllWidgets()
        
        # Unset dirty bit
        self.unsetDirtyBit()
    
    def populateExamData(self):
        exam_data = self.state["exam_data"][self.current_exam]
        
        # Clear dirty bit
        self.unsetDirtyBit()
        
        # We set this since we're changing stuff
        self.examChanging = True
        
        # Clear everything!
        self.clearAllWidgets()
        
        # Set label
        self.currentTestLbl.setText("%s (%i/%i)" % 
            (exam_data["file_name"], self.current_exam, self.num_files))
        
        # Set window title
        self.setWindowTitle("%s (%i/%i) - IEEE Testbank Tool" % 
            (exam_data["file_name"], self.current_exam, self.num_files))
        
        # Actually populate data!
        if exam_data["filled"]:
            if "class" in exam_data["data"]:
                self.classTxt.setText(exam_data["data"]["class"])
            if "profLastName" in exam_data["data"]:
                self.profLastNameTxt.setText(exam_data["data"]["profLastName"])
            if "profFirstName" in exam_data["data"]:
                self.profFirstNameTxt.setText(exam_data["data"]["profFirstName"])
            if "info" in exam_data["data"]:
                self.addlExamInfoTxt.setText(exam_data["data"]["info"])
            if "semester" in exam_data["data"]:
                comboIndex = self.semesterCBox.findText(exam_data["data"]["semester"], QtCore.Qt.MatchFixedString)
                # Even if search fails, comboIndex will be set to -1, which works - nothing is set at all!
                self.semesterCBox.setCurrentIndex(comboIndex)
            if "status" in exam_data["data"]:
                if exam_data["data"]["status"] == "good":
                    self.validTestAllGoodRadio.setChecked(True)
                elif exam_data["data"]["status"] == "wrongtest":
                    self.validTestWrongTestRadio.setChecked(True)
                elif exam_data["data"]["status"] == "junk":
                    self.validTestJunkRadio.setChecked(True)
                else:
                    print("Warning: Invalid exam status detected! (Got: %s)" % exam_data["data"]["status"])
            if "type" in exam_data["data"]:
                if exam_data["data"]["type"] == "Quiz":
                    self.testTypeQuizRadio.setChecked(True)
                elif exam_data["data"]["type"] == "Midterm":
                    self.testTypeMidtermRadio.setChecked(True)
                elif exam_data["data"]["type"] == "Final":
                    self.testTypeFinalRadio.setChecked(True)
                else:
                    print("Warning: Invalid exam type detected! (Got: %s)" % exam_data["data"]["type"])
            if "origin" in exam_data["data"]:
                if exam_data["data"]["origin"] == "scanned":
                    self.testScannedRadio.setChecked(True)
                elif exam_data["data"]["origin"] == "ocrwithimage":
                    self.testOCRWithImageRadio.setChecked(True)
                elif exam_data["data"]["origin"] == "ocrwithoutimage":
                    self.testOCRWithoutImageRadio.setChecked(True)
                elif exam_data["data"]["origin"] == "original":
                    self.testOriginalRadio.setChecked(True)
                else:
                    print("Warning: Invalid origin scan/original detected! (Got: %s)" % exam_data["data"]["origin"])
            if "includes" in exam_data["data"]:
                if "problems" in exam_data["data"]["includes"]:
                    self.testProblemsCheckBox.setChecked(True)
                if "solutions" in exam_data["data"]["includes"]:
                    self.testSolutionsCheckBox.setChecked(True)
                if (not (("problems" in exam_data["data"]["includes"]) or ("solutions" in exam_data["data"]["includes"]))) and exam_data["data"]["includes"] != "":
                    print("Warning: Invalid includes detected! (Got: %s)" % exam_data["data"]["includes"])
            if "year" in exam_data["data"]:
                self.yearSpinBox.setValue(exam_data["data"]["year"])
            if "testNum" in exam_data["data"]:
                self.testNumSpinBox.setValue(exam_data["data"]["testNum"])
            if "fileNotes" in exam_data["data"]:
                self.fileNotesTxt.setPlainText(exam_data["data"]["fileNotes"])
        
        # Revert state to regular
        self.examChanging = False
    
    def revertExamData(self):
        confirm = QtGui.QMessageBox.question(self, "Revert everything?",
            "Are you sure you want to revert everything to the currently stored data? All unsaved fields will be erased.",
            QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        
        if confirm == QtGui.QMessageBox.Yes:
            self.populateExamData()
            self.revertBtn.setEnabled(False)
            self.saveBtn.setEnabled(False)
    
    def clearButtons(self, group, btns):
        # Exclusive must be turned off, or otherwise setting one to
        # False will trigger another
        if group:
            group.setExclusive(False)
        
        for btn in btns:
            btn.setChecked(False)
        
        # Re-enable exclusive (for button groups)
        if group:
            group.setExclusive(True)
    
    def clearAllWidgets(self):
        # Test status radio buttons
        self.clearButtons(self.testValidBtnGroup,
                                [
                                    self.validTestAllGoodRadio,
                                    self.validTestWrongTestRadio,
                                    self.validTestJunkRadio,
                                ]
                            )
        
        # Class textbox
        self.classTxt.setText("")
        
        # Semester combobox
        self.semesterCBox.setCurrentIndex(-1)
        
        # Year spinbox
        self.yearSpinBox.setValue(2016)
        
        # Professor last name, first name textboxes
        self.profLastNameTxt.setText("")
        self.profFirstNameTxt.setText("")
        
        # Exam type - Quiz/Midterm/Final radio button group
        self.clearButtons(self.testTypeBtnGroup,
                                [
                                    self.testTypeQuizRadio,
                                    self.testTypeMidtermRadio,
                                    self.testTypeFinalRadio,
                                ]
                            )
        
        # Test number spinbox
        self.testNumSpinBox.setValue(0)
        
        # Exam scan type - Scanned/OCRw/woImage/Original radio button group
        self.clearButtons(self.testScanOrigBtnGroup,
                                [
                                    self.testScannedRadio,
                                    self.testOCRWithImageRadio,
                                    self.testOCRWithoutImageRadio,
                                    self.testOriginalRadio,
                                ]
                            )
        
        # Exam contains - checkboxes
        self.clearButtons(None,
                                [
                                    self.testProblemsCheckBox,
                                    self.testSolutionsCheckBox,
                                ]
                            )
        
        # Addl exam info + file notes
        self.addlExamInfoTxt.setText("")
        self.fileNotesTxt.setPlainText("")
        
        # Validate everything
        self.validateAllWidgets()
    
    def handleUnknownWidget(self, widget):
        print "UNKNOWN! sender is: %s" % str(self.sender().__class__.__name__)
        print "         sender object name is: %s" % str(self.sender().objectName())
    
    def setDirtyBit(self, widget = None):
        print "Dirty bit set! (Called by: %s)" % sys._getframe().f_back.f_code.co_name
        self.formDirty = True
        
        self.revertBtn.setEnabled(True)
        self.saveBtn.setEnabled(True)
        
        if widget:
            self.invalidateWidget(widget)
    
    def unsetDirtyBit(self, widget = None):
        print "Dirty bit reset! (Called by: %s)" % sys._getframe().f_back.f_code.co_name
        self.formDirty = False
        
        self.revertBtn.setEnabled(False)
        self.saveBtn.setEnabled(False)
        
        if widget:
            self.invalidateWidget(widget)
    
    def invalidateWidget(self, widget):
        if widget.__class__ is QtGui.QComboBox:
            # Workaround for bug when color isn't set for the actual
            # combobox (but instead only the list of items in the combo)
            widget.setStyleSheet("background-color: #660000; color: white; padding: 0px 0px 0px 0px; /*This makes text colour work*/")
        else:
            widget.setStyleSheet("background-color: #660000; color: white;")
    
    def validateWidget(self, widget):
        widget.setStyleSheet("")
    
    def validateAllWidgets(self):
        self.validateWidget(self.validTestAllGoodRadio)
        self.validateWidget(self.validTestWrongTestRadio)
        self.validateWidget(self.validTestJunkRadio)
        
        # Class textbox
        self.validateWidget(self.classTxt)
        
        # Semester combobox
        self.validateWidget(self.semesterCBox)
        
        # Year spinbox
        self.validateWidget(self.yearSpinBox)
        
        # Professor last name, first name textboxes
        self.validateWidget(self.profLastNameTxt)
        self.validateWidget(self.profFirstNameTxt)
        
        # Exam type - Quiz/Midterm/Final radio button group
        self.validateWidget(self.testTypeQuizRadio)
        self.validateWidget(self.testTypeMidtermRadio)
        self.validateWidget(self.testTypeFinalRadio)
        
        # Scanned/Orig radio button group
        self.validateWidget(self.testScannedRadio)
        self.validateWidget(self.testOCRWithImageRadio)
        self.validateWidget(self.testOCRWithoutImageRadio)
        self.validateWidget(self.testOriginalRadio)
        
        # Contains Checkboxes
        self.validateWidget(self.testProblemsCheckBox)
        self.validateWidget(self.testSolutionsCheckBox)
        
        # Test number spinbox
        self.validateWidget(self.testNumSpinBox)
        
        # Addl exam info + file notes
        self.validateWidget(self.addlExamInfoTxt)
        self.validateWidget(self.fileNotesTxt)
    
    def changeFormHandler(self, arg = None):
        exam_data = self.state["exam_data"][self.current_exam]
        
        if self.examChanging:
            print "No dirty bit will be set."
            return
        
        print self.sender().__class__.__name__ , "Printing()", self.__class__.__name__
        print arg
        
        self.validateWidget(self.sender())
        
        # We could check for empty form, but this requires more validation
        # then that!
        
        # Determine type of widget
        if self.sender().__class__ is QtGui.QLineEdit:
            print "qlineedit"
            
            # Which widget?
            if self.sender() is self.classTxt:
                # If data is defined, and if the data matches, don't do anything. Otherwise, invalidate!
                if not (("class" in exam_data["data"]) and (exam_data["data"]["class"] == self.classTxt.text())):
                    print "invalidated class"
                    self.setDirtyBit(self.sender())
                
                print "classTxt"
            elif self.sender() is self.profLastNameTxt:
                if not (("profLastName" in exam_data["data"]) and (exam_data["data"]["profLastName"] == self.profLastNameTxt.text())):
                    print "invalidated profLastName"
                    self.setDirtyBit(self.sender())
                
                print "profLastNameTxt"
            elif self.sender() is self.profFirstNameTxt:
                if not (("profFirstName" in exam_data["data"]) and (exam_data["data"]["profFirstName"] == self.profFirstNameTxt.text())):
                    print "invalidated profFirstName"
                    self.setDirtyBit(self.sender())
                
                print "profFirstNameTxt"
            elif self.sender() is self.addlExamInfoTxt:
                if not (("info" in exam_data["data"]) and (exam_data["data"]["info"] == self.addlExamInfoTxt.text())):
                    print "invalidated info / addlExamInfoTxt"
                    self.setDirtyBit(self.sender())
                
                print "addlExamInfoTxt"
            else:
                self.handleUnknownWidget(self.sender())
            
        elif self.sender().__class__ is QtGui.QComboBox:
            print "QComboBox"
            
            # Which widget?
            if self.sender() is self.semesterCBox:
                if not (("semester" in exam_data["data"]) and (exam_data["data"]["semester"] == self.semesterCBox.currentText())):
                    print "invalidated semester"
                    self.setDirtyBit(self.sender())
                
                print "semesterCBox"
            else:
                self.handleUnknownWidget(self.sender())
        elif self.sender().__class__ is QtGui.QRadioButton:
            print "QRadioButton"
            
            # If the arg is False, validate the widget.
            if not arg:
                self.validateWidget(self.sender())
            else:
                # Which widget?
                if self.sender() is self.validTestAllGoodRadio:
                    if not (("status" in exam_data["data"]) and (exam_data["data"]["status"] == "good")):
                        print "invalidated status / validTestAllGoodRadio"
                        self.setDirtyBit(self.sender())
                    
                    print "validTestAllGoodRadio"
                elif self.sender() is self.validTestWrongTestRadio:
                    if not (("status" in exam_data["data"]) and (exam_data["data"]["status"] == "wrongtest")):
                        print "invalidated status / validTestWrongTestRadio"
                        self.setDirtyBit(self.sender())
                    
                    print "validTestWrongTestRadio"
                elif self.sender() is self.validTestJunkRadio:
                    if not (("status" in exam_data["data"]) and (exam_data["data"]["status"] == "junk")):
                        print "invalidated status / validTestJunkRadio"
                        self.setDirtyBit(self.sender())
                    
                    print "validTestJunkRadio"
                elif self.sender() is self.testTypeQuizRadio:
                    if not (("type" in exam_data["data"]) and (exam_data["data"]["type"] == "Quiz")):
                        print "invalidated type / testTypeQuizRadio"
                        self.setDirtyBit(self.sender())
                    
                    print "testTypeQuizRadio"
                elif self.sender() is self.testTypeMidtermRadio:
                    if not (("type" in exam_data["data"]) and (exam_data["data"]["type"] == "Midterm")):
                        print "invalidated type / testTypeMidtermRadio"
                        self.setDirtyBit(self.sender())
                    
                    print "testTypeMidtermRadio"
                elif self.sender() is self.testTypeFinalRadio:
                    if not (("type" in exam_data["data"]) and (exam_data["data"]["type"] == "Final")):
                        print "invalidated type / testTypeFinalRadio"
                        self.setDirtyBit(self.sender())
                    
                    print "testTypeFinalRadio"
                elif self.sender() is self.testScannedRadio:
                    if not (("origin" in exam_data["data"]) and (exam_data["data"]["origin"] == "scanned")):
                        print "invalidated type / testScannedRadio"
                        self.setDirtyBit(self.sender())
                    
                    print "testScannedRadio"
                elif self.sender() is self.testOCRWithImageRadio:
                    if not (("origin" in exam_data["data"]) and (exam_data["data"]["origin"] == "ocrwithimage")):
                        print "invalidated type / testOCRWithImageRadio"
                        self.setDirtyBit(self.sender())
                    
                    print "testOCRWithImageRadio"
                elif self.sender() is self.testOCRWithoutImageRadio:
                    if not (("origin" in exam_data["data"]) and (exam_data["data"]["origin"] == "ocrwithoutimage")):
                        print "invalidated type / testOCRWithoutImageRadio"
                        self.setDirtyBit(self.sender())
                    
                    print "testOCRWithoutImageRadio"
                elif self.sender() is self.testOriginalRadio:
                    if not (("origin" in exam_data["data"]) and (exam_data["data"]["origin"] == "original")):
                        print "invalidated type / testOriginalRadio"
                        self.setDirtyBit(self.sender())
                    
                    print "testOriginalRadio"
                else:
                    self.handleUnknownWidget(self.sender())
            
        elif self.sender().__class__ is QtGui.QCheckBox:
            print "QCheckBox"
            
            if not arg:
                # Which widget?
                if self.sender() is self.testProblemsCheckBox:
                    if not (("includes" in exam_data["data"]) and (not ("problems" in exam_data["data"]["includes"]))):
                        print "invalidated type / testProblemsCheckBox"
                        self.setDirtyBit(self.sender())
                    
                    print "testProblemsCheckBox"
                elif self.sender() is self.testSolutionsCheckBox:
                    if not (("includes" in exam_data["data"]) and (not ("solutions" in exam_data["data"]["includes"]))):
                        print "invalidated type / testSolutionsCheckBox"
                        self.setDirtyBit(self.sender())
                    
                    print "testSolutionsCheckBox"
                else:
                    self.handleUnknownWidget(self.sender())

            else:
                # Which widget?
                if self.sender() is self.testProblemsCheckBox:
                    if not (("includes" in exam_data["data"]) and ("problems" in exam_data["data"]["includes"])):
                        print "invalidated type / testProblemsCheckBox"
                        self.setDirtyBit(self.sender())
                    
                    print "testProblemsCheckBox"
                elif self.sender() is self.testSolutionsCheckBox:
                    if not (("includes" in exam_data["data"]) and ("solutions" in exam_data["data"]["includes"])):
                        print "invalidated type / testSolutionsCheckBox"
                        self.setDirtyBit(self.sender())
                    
                    print "testSolutionsCheckBox"
                else:
                    self.handleUnknownWidget(self.sender())
            
        elif self.sender().__class__ is QtGui.QSpinBox:
            print "QSpinBox"
            
            # Which widget?
            if self.sender() is self.yearSpinBox:
                if not (("year" in exam_data["data"]) and (exam_data["data"]["year"] == self.yearSpinBox.value())):
                    print "invalidated year"
                    self.setDirtyBit(self.sender())
                
                print "yearSpinBox"
            elif self.sender() is self.testNumSpinBox:
                if not (("testNum" in exam_data["data"]) and (exam_data["data"]["testNum"] == self.testNumSpinBox.value())):
                    print "invalidated testNum"
                    self.setDirtyBit(self.sender())
                
                print "testNumSpinBox"
            else:
                self.handleUnknownWidget(self.sender())
        elif self.sender().__class__ is QtGui.QPlainTextEdit:
            print "QPlainTextEdit"
            
            if self.sender() is self.fileNotesTxt:
                if not (("fileNotes" in exam_data["data"]) and (exam_data["data"]["fileNotes"] == self.fileNotesTxt.toPlainText())):
                    print "invalidated fileNotes"
                    self.setDirtyBit(self.sender())
                
                print "fileNotesTxt"
            else:
                self.handleUnknownWidget(self.sender())
        else:
            print "UNKNOWN WIDGET TYPE - BUG!"
            self.handleUnknownWidget(self.sender())
    
    def autoFillCurrentExam(self):
        confirm = QtGui.QMessageBox.question(self, "Perform autofill?",
            "Autofill will try to guess the fields based on the file name. Doing autofill will overwrite any fields that have not been saved. Are you sure you want to autofill?",
            QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        
        if not (confirm == QtGui.QMessageBox.Yes):
            return
        
        #self.current_exam = self.testSlider.value()
        exam_data = self.state["exam_data"][self.current_exam]
        fndata = parseFileName(exam_data["file_name"])
        
        miniAutoFillLog  = "Autofill executed! We tried our best to fill things in, but no guarantees that everything is correct!\n\n"
        miniAutoFillLog += "As always, this is NOT a replacement for actually looking at exams and filling out the info! This is just for your convenience.\n\n"
        miniAutoFillLog += "Please delete this message after reading it! This is meant for YOUR file notes! Messages below indicate what we filled and didn't fill:\n\n"
        
        if not fndata:
            #TODO: error here
            pass
        
        # Class, year, semester, professor, exam
        self.classTxt.setText(fndata["class"])
        self.yearSpinBox.setValue(fndata["year"])
        
        self.setDirtyBit(self.classTxt)
        self.setDirtyBit(self.yearSpinBox)
        
        miniAutoFillLog += "Class detected: %s\n" % (fndata["class"])
        miniAutoFillLog += "Year detected: %s\n" % (fndata["year"])
        
        # Semester/Season: Spring sUmmer Fall Winter
        
        comboIndex = -1
        if fndata["semester"] == "S":
            comboIndex = self.semesterCBox.findText("Spring", QtCore.Qt.MatchFixedString)
            miniAutoFillLog += "Semester detected: Spring\n"
        elif fndata["semester"] == "U":
            comboIndex = self.semesterCBox.findText("Summer", QtCore.Qt.MatchFixedString)
            miniAutoFillLog += "Semester detected: Summer\n"
        elif fndata["semester"] == "F":
            comboIndex = self.semesterCBox.findText("Fall", QtCore.Qt.MatchFixedString)
            miniAutoFillLog += "Semester detected: Fall\n"
        elif fndata["semester"] == "W":
            comboIndex = self.semesterCBox.findText("Winter", QtCore.Qt.MatchFixedString)
            miniAutoFillLog += "Semester detected: Winter\n"
        else:
            #TODO: error here
            pass
        
        if comboIndex < 0:
            #TODO: error here
            pass
        
        self.semesterCBox.setCurrentIndex(comboIndex)
        self.setDirtyBit(self.semesterCBox)
        
        # Professor
        name_re_str = r'([A-Z][a-z-]*)([]A-Z][a-z-]*)*'
        name_re = re.compile(name_re_str)
        
        name_m = name_re.match(fndata["professor"])
        
        if name_m:
            if name_m.group(2):
                # We have first and last name!
                self.profFirstNameTxt.setText(name_m.group(1))
                self.profLastNameTxt.setText(name_m.group(2))
                self.setDirtyBit(self.profFirstNameTxt)
                self.setDirtyBit(self.profLastNameTxt)
                miniAutoFillLog += "Professor detected: %s, %s\n" % (name_m.group(2), name_m.group(1))
            else:
                # Only last name
                self.profLastNameTxt.setText(name_m.group(1))
                self.setDirtyBit(self.profLastNameTxt)
                miniAutoFillLog += "Professor detected: %s (last name only)\n" % (name_m.group(1))
        else:
            # Error TODO
            pass
        
        # Finally, exam info...
        # Order is important here! Highest to lowest priority...
        if "final" in fndata["exam"].lower():
            self.testTypeFinalRadio.setChecked(True)
            self.setDirtyBit(self.testTypeFinalRadio)
            miniAutoFillLog += "Type of test detected: Final\n"
        elif "quiz" in fndata["exam"].lower():
            self.testTypeQuizRadio.setChecked(True)
            self.setDirtyBit(self.testTypeQuizRadio)
            miniAutoFillLog += "Type of test detected: Quiz\n"
        elif "midterm" in fndata["exam"].lower():
            self.testTypeMidtermRadio.setChecked(True)
            self.setDirtyBit(self.testTypeMidtermRadio)
            miniAutoFillLog += "Type of test detected: Midterm\n"
        else:
            # Don't check anything
            miniAutoFillLog += "Couldn't figure out type of test, skipped selecting anything.\n"
            miniAutoFillLog += "Placing test suffix in additional exam info field.\n"
            self.addlExamInfoTxt.setText(fndata["exam"])
        
        # Extract exam number, if possible
        exam_num_m = re.findall('\d+', fndata["exam"])
        exam_num_roman_m = re.findall('[Ii]+', fndata["exam"])
        
        if len(exam_num_m) == 1:
            self.testNumSpinBox.setValue(int(exam_num_m[0]))
            self.setDirtyBit(self.testNumSpinBox)
            miniAutoFillLog += "Test number: %d\n" % (int(exam_num_m[0]))
        elif len(exam_num_roman_m) == 1:
            self.testNumSpinBox.setValue(len(exam_num_m[0]))
            self.setDirtyBit(self.testNumSpinBox)
            miniAutoFillLog += "Test number: %d\n" % (len(exam_num_m[0]))
        else:
            # Don't do anything
            miniAutoFillLog += "Couldn't figure out test number, skipped filling out anything.\n"
            pass
        
        self.fileNotesTxt.setPlainText(miniAutoFillLog)
        self.setDirtyBit(self.fileNotesTxt)
    
    def convertStatus(self, actual_exam_data):
        if "status" in actual_exam_data:
            if actual_exam_data["status"] == "good":
                return "<span style='color: #00ff00'><b>Test is Valid</b></span>"
            elif actual_exam_data["status"] == "wrongtest":
                return "<span style='color: #ffa500'><b>Wrong Test (Needs to be Renamed)</b></span>"
            elif actual_exam_data["status"] == "junk":
                return "<span style='color: #ff0000'><b>Junk (Not an Exam)</b></span>"
            else:
                return "<span style='color: #800080'><b>INVALID STATUS! (Bug or corrupt file?)</b></span>"
        else:
            return ""
    
    def convertOrigin(self, actual_exam_data):
        if "origin" in actual_exam_data:
            if actual_exam_data["origin"] == "scanned":
                return "Scanned"
            elif actual_exam_data["origin"] == "ocrwithimage":
                return "OCR with Image"
            elif actual_exam_data["origin"] == "ocrwithoutimage":
                return "OCR without Image"
            elif actual_exam_data["origin"] == "original":
                return "Original"
            else:
                return "<span style='color: #800080'><b>INVALID ORIGIN! (Bug or corrupt file?)</b></span>"
        else:
            return "N/A"
    
    def convertIncludes(self, actual_exam_data):
        if "includes" in actual_exam_data:
            ret = ""
            print "DEBUG: convertIncludes data is %s" % actual_exam_data["includes"]
            if "problems" in actual_exam_data["includes"]:
                ret += "Problems"
            if "solutions" in actual_exam_data["includes"]:
                if ret == "":
                    ret += "Solutions"
                else:
                    ret += " and Solutions"
            if (ret == "") and (actual_exam_data["includes"] != ""):
                return "<span style='color: #800080'><b>INVALID INCLUDES! (Bug or corrupt file?)</b></span>"
            return ret
        else:
            return "N/A"
    
    def showExamTooltip(self):
        tooltipPos = self.testSlider.mapToGlobal(self.testSlider.pos())
        #self.current_exam = self.testSlider.value()
        exam_data = self.state["exam_data"][self.viewing_exam]
        actual_exam_data = exam_data["data"]
        
        fetch_actual_exam_data = lambda x, d=None: (str(actual_exam_data[x]) if x in actual_exam_data else (d if d != None else "N/A"))
        
        print "showExamTooltip: %i / %i" % (self.viewing_exam, self.num_files)
        
        tooltipText  = "<b>Exam %i / %i</b><br />" % (self.viewing_exam, self.num_files)
        tooltipText += "<b>File:</b> %s<br />" % (exam_data["file_name"])
        
        if exam_data["filled"]:
            tooltipText += "%s<br />" % (self.convertStatus(actual_exam_data))
            tooltipText += "<b>Class:</b> %s<br />" % (fetch_actual_exam_data("class"))
            tooltipText += "<b>When:</b> %s %s<br />" % (fetch_actual_exam_data("semester"), fetch_actual_exam_data("year", ""))
            tooltipText += "<b>Professor (last, first):</b><br />%s, %s<br />" % (fetch_actual_exam_data("profLastName", "<i>(No last name)</i>"), \
                                                                             fetch_actual_exam_data("profFirstName", "<i>(No first name)</i>"))
            tooltipText += "<b>Exam:</b> %s %s<br />" % (fetch_actual_exam_data("type"), fetch_actual_exam_data("testNum", ""))
            tooltipText += "<b>Origin:</b> %s<br />" % (self.convertOrigin(actual_exam_data))
            tooltipText += "<b>Includes:</b> %s<br />" % (self.convertIncludes(actual_exam_data))
            tooltipText += "<b>Additional exam info:</b><br />%s<br />" % (fetch_actual_exam_data("info"))
            tooltipText += "<b>File notes:</b><br />%s" % (fetch_actual_exam_data("fileNotes"))
        else:
            tooltipText += "<b>(Test not entered yet)</b>"
        
        QtGui.QToolTip.showText(tooltipPos, tooltipText, None)
    
    def confirmExamState(self, task = "switching exams"):
        if self.formDirty:
            confirm = QtGui.QMessageBox.question(self, "Save exam?",
                "You have not saved the exam data yet. Do you want to save the exam data before %s? All unsaved fields will be erased." % task,
                QtGui.QMessageBox.Save, QtGui.QMessageBox.Discard, QtGui.QMessageBox.Cancel)
            
            if confirm == QtGui.QMessageBox.Save:
                self.saveExamData()
                return True
            elif confirm == QtGui.QMessageBox.Discard:
                return True
            else:
                return False
        else:
            return True
    
    def firstExam(self):
        self.changeExam(self.start_range)
    
    def lastExam(self):
        self.changeExam(self.end_range)
    
    def decreaseExam(self):
        if self.current_exam > self.start_range:
            self.changeExam(self.current_exam - 1)
    
    def increaseExam(self):
        if self.current_exam < self.end_range:
            self.changeExam(self.current_exam + 1)
    
    def changeExam(self, newExamIndex):
        print "changeExam called! (Called by: %s)" % sys._getframe().f_back.f_code.co_name
        if self.current_exam == newExamIndex:
            print "  -> Ignoring call, old_exam == current_exam"
            return
        
        confirm = self.confirmExamState()
        
        if confirm:
            # Change old exam to new one
            self.current_exam = newExamIndex
            
            # Set examChanging to prevent dirty set
            self.examChanging = True
            
            # Reset countdown, as necessary
            self.openTimer.stop()
            self.openCountdown = 10
            self.openTestBtn.setText("Open")
            self.openTestBtn.setEnabled(True)
            
            # Set directional buttons
            if self.current_exam == self.start_range:
                self.prevTestBtn.setEnabled(False)
                self.firstTestBtn.setEnabled(False)
            else:
                self.prevTestBtn.setEnabled(True)
                self.firstTestBtn.setEnabled(True)
            
            if self.current_exam == self.end_range:
                self.nextTestBtn.setEnabled(False)
                self.lastTestBtn.setEnabled(False)
            else:
                self.nextTestBtn.setEnabled(True)
                self.lastTestBtn.setEnabled(True)
            
            self.testSlider.setValue(self.current_exam)
            
            self.populateExamData()
            
            # Set examChanging to allow dirty set
            self.examChanging = False
        else:
            self.testSlider.setValue(self.current_exam)
        
        # Set user state for saving later
        self.state["user_state"]["current_exam"] = self.current_exam
        
        # Return result
        return confirm
    
    def updateCurrentExam(self, examIndex):
        self.viewing_exam = examIndex
        print "updateCurrentExam: %i / %i" % (self.viewing_exam, self.num_files)
        
        if self.testSlider.isSliderDown():
            print "skip - call tooltip"
            self.showExamTooltip()
        else:
            print "slider not down"
        #else:
        #    self.changeExam()
    
    def changeExamSlider(self, examIndex):
        print "changeExamSlider called with examIndex = %i" % examIndex
        #confirm = QtGui.QMessageBox.question(self, "Save exam?",
        #        "You have not saved the exam data yet. Do you want to save the exam data before BOOM? All unsaved fields will be erased.",
        #        QtGui.QMessageBox.Save, QtGui.QMessageBox.Discard, QtGui.QMessageBox.Cancel)
        self.changeExam(self.testSlider.value())
        #if self.changeExam():
        #    self.testSlider.blockSignals(True)
            
