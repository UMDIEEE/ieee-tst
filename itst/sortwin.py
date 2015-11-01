from PyQt4 import QtGui, QtCore

from gui import SortingGUI

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
            self.current_exam = 1
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
    
    def showExamTooltip(self):
        tooltipPos = self.testSlider.mapToGlobal(self.testSlider.pos())
        self.current_exam = self.testSlider.value()
        
        print "showExamTooltip: %i / %i" % (self.current_exam, self.num_files)
        
        tooltipText  = "<b>Exam %i / %i</b><br />" % (self.current_exam, self.num_files)
        tooltipText += "%s<br />" % ("<span style='color: #00ff00'>Test is Valid</span>")
        tooltipText += "<b>Class:</b> ENEE123<br />"
        tooltipText += "<b>When:</b> Fall 2015<br />"
        tooltipText += "<b>Professor:</b> Bob Bob<br />"
        tooltipText += "<b>Exam:</b> Quiz 2<br />"
        tooltipText += "<b>Additional exam info:</b><br />Circuits<br />"
        tooltipText += "<b>File notes:</b><br />Notes"
        
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
        
