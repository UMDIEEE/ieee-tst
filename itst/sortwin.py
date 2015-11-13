from PyQt4 import QtGui, QtCore

from gui import SortingGUI
from ies import parseFileName

import re

class SortWindow(QtGui.QDialog, SortingGUI.Ui_sortDlg):
    def __init__(self, confname, srcdir, file_table, num_files, start_range, end_range, state = None):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super(self.__class__, self).__init__(None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.MSWindowsFixedSizeDialogHint)
        self.setupUi(self)  # This is defined in design.py file automatically
                            # It sets up layout and widgets that are defined
        
        # Save input
        self.file_table = file_table
        self.num_files = num_files
        self.confname = confname
        self.srcdir = srcdir
        self.start_range = start_range
        self.end_range = end_range
        self.state = state
        
        if state == None:
            self.current_exam = self.start_range
            self.old_exam = self.current_exam
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
            self.current_exam = self.state["user_state"]["current_exam"]
            self.old_exam = self.current_exam
        
        self.saveBtn.setEnabled(False)
        self.revertBtn.setEnabled(False)
        
        self.testSlider.setRange(start_range, end_range)
        
        self.testSlider.sliderPressed.connect(self.showExamTooltip)
        self.testSlider.sliderReleased.connect(self.changeExam)
        self.testSlider.valueChanged.connect(self.updateCurrentExam)
        
        self.prevTestBtn.clicked.connect(self.decreaseExam)
        self.nextTestBtn.clicked.connect(self.increaseExam)
        self.firstTestBtn.clicked.connect(self.firstExam)
        self.lastTestBtn.clicked.connect(self.lastExam)
        
        self.changeExam()
        
        #self.goBtn.clicked.connect(self.go)
        
        # D:\IEEE Renamed Exams\Mini Testing Valid Exams
    
    def autoFillCurrentExam(self):
        self.current_exam = self.testSlider.value()
        exam_data = self.state["exam_data"][self.current_exam]
        fndata = parseFileName(exam_data["file_name"])
        
        miniAutoFillLog  = "Autofill executed! We tried our best to fill things in, but no guarantees that everything is correct!\n\n"
        miniAutoFillLog += "As always, this is NOT a replacement for actually looking at exams and filling out the info! This is just for your convenience.\n\n"
        miniAutoFillLog += "Please delete this message after reading it! This is meant for YOUR file notes! Messages below indicate what we filled and didn't fill:\n\n"
        
        if not fndata:
            #TODO: error here
            pass
        
        # Class, year, season, professor, exam
        self.classTxt.setText(fndata["class"])
        self.yearSpinBox.setValue(fndata["year"])
        
        miniAutoFillLog += "Class detected: %s\n" % (fndata["class"])
        miniAutoFillLog += "Year detected: %s\n" % (fndata["year"])
        
        # Season: Spring sUmmer Fall Winter
        
        comboIndex = -1
        if fndata["season"] == "S":
            comboIndex = self.semesterCBox.findText("Spring", QtCore.Qt.MatchFixedString)
            miniAutoFillLog += "Semester detected: Spring\n"
        elif fndata["season"] == "U":
            comboIndex = self.semesterCBox.findText("Summer", QtCore.Qt.MatchFixedString)
            miniAutoFillLog += "Semester detected: Summer\n"
        elif fndata["season"] == "F":
            comboIndex = self.semesterCBox.findText("Fall", QtCore.Qt.MatchFixedString)
            miniAutoFillLog += "Semester detected: Fall\n"
        elif fndata["season"] == "W":
            comboIndex = self.semesterCBox.findText("Winter", QtCore.Qt.MatchFixedString)
            miniAutoFillLog += "Semester detected: Winter\n"
        else:
            #TODO: error here
            pass
        
        if comboIndex < 0:
            #TODO: error here
            pass
        
        self.semesterCBox.setCurrentIndex(comboIndex)
        
        # Professor
        name_re_str = r'([A-Z][a-z-]*)([]A-Z][a-z-]*)*'
        name_re = re.compile(name_re_str)
        
        name_m = name_re.match(fndata["professor"])
        
        if name_m:
            if name_m.group(2):
                # We have first and last name!
                self.profFirstNameTxt.setText(name_m.group(1))
                self.profLastNameTxt.setText(name_m.group(2))
                miniAutoFillLog += "Professor detected: %s, %s\n" % (name_m.group(2), name_m.group(1))
            else:
                # Only last name
                self.profLastNameTxt.setText(name_m.group(1))
                miniAutoFillLog += "Professor detected: %s (last name only)\n" % (name_m.group(1))
        else:
            # Error TODO
            pass
        
        # Finally, exam info...
        # Order is important here! Highest to lowest priority...
        if "final" in fndata["exam"].lower():
            self.testTypeFinalRadio.setChecked(True)
            miniAutoFillLog += "Type of test detected: Final\n"
        elif "quiz" in fndata["exam"].lower():
            self.testTypeQuizRadio.setChecked(True)
            miniAutoFillLog += "Type of test detected: Quiz\n"
        elif "midterm" in fndata["exam"].lower():
            self.testTypeMidtermRadio.setChecked(True)
            miniAutoFillLog += "Type of test detected: Midterm\n"
        else:
            # Don't check anything
            miniAutoFillLog += "Couldn't figure out type of test, skipped selecting anything.\n"
            pass
        
        # Extract exam number, if possible
        exam_num_m = re.findall('\d+', fndata["exam"])
        exam_num_roman_m = re.findall('[Ii]+', fndata["exam"])
        
        if len(exam_num_m) == 1:
            self.testNumSpinBox.setValue(int(exam_num_m[0]))
            miniAutoFillLog += "Test number: %d\n" % (int(exam_num_m[0]))
        elif len(exam_num_roman_m) == 1:
            self.testNumSpinBox.setValue(len(exam_num_m[0]))
            miniAutoFillLog += "Test number: %d\n" % (len(exam_num_m[0]))
        else:
            # Don't do anything
            miniAutoFillLog += "Couldn't figure out test number, skipped filling out anything.\n"
            pass
        
        self.fileNotesTxt.setPlainText(miniAutoFillLog)
        
    def showExamTooltip(self):
        tooltipPos = self.testSlider.mapToGlobal(self.testSlider.pos())
        self.current_exam = self.testSlider.value()
        exam_data = self.state["exam_data"][self.current_exam]
        actual_exam_data = exam_data["data"]
        
        fetch_actual_exam_data = lambda x, d=None: (actual_exam_data[x] if x in actual_exam_data else (d if d != None else "N/A"))
        
        print "showExamTooltip: %i / %i" % (self.current_exam, self.num_files)
        
        tooltipText  = "<b>Exam %i / %i</b><br />" % (self.current_exam, self.num_files)
        tooltipText += "<b>File:</b> %s<br />" % (exam_data["file_name"])
        
        if exam_data["filled"]:
            tooltipText += "%s<br />" % ("<span style='color: #00ff00'>Test is Valid</span>")
            tooltipText += "<b>Class:</b> %s<br />" % (fetch_actual_exam_data("class"))
            tooltipText += "<b>When:</b> %s %s<br />" % (fetch_actual_exam_data("season"), fetch_actual_exam_data("year", ""))
            tooltipText += "<b>Professor:</b> %s<br />" % (actual_exam_data["professor"] if "professor" in actual_exam_data else "N/A")
            tooltipText += "<b>Exam:</b> %s %s<br />" % (fetch_actual_exam_data("exam_type"), str(fetch_actual_exam_data("exam_num", "")))
            tooltipText += "<b>Additional exam info:</b><br />%s<br />" % (fetch_actual_exam_data("addl_exam_info"))
            tooltipText += "<b>File notes:</b><br />%s" % (fetch_actual_exam_data("notes"))
        else:
            tooltipText += "<b>(Test not entered yet)</b>"
        
        QtGui.QToolTip.showText(tooltipPos, tooltipText, None)
    
    def firstExam(self):
        self.current_exam = self.start_range
        self.changeExam()
    
    def lastExam(self):
        self.current_exam = self.end_range
        self.changeExam()
    
    def decreaseExam(self):
        if self.current_exam > self.start_range:
            self.current_exam -= 1
            
            self.changeExam()
    
    def increaseExam(self):
        if self.current_exam < self.end_range:
            self.current_exam += 1
            
            self.changeExam()
    
    def changeExam(self):
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
        
        self.currentTestLbl.setText("%s (%i/%i)" % 
            (self.state["exam_data"][self.current_exam]["file_name"], self.current_exam, self.num_files))
    
    def updateCurrentExam(self, examIndex):
        self.current_exam = examIndex
        print "updateCurrentExam: %i / %i" % (self.current_exam, self.num_files)
        
        if self.testSlider.isSliderDown():
            print "skip - call tooltip"
            self.showExamTooltip()
        else:
            self.changeExam()
        
