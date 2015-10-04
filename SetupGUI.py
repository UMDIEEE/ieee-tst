# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Setup.ui'
#
# Created: Sun Oct 04 10:10:38 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_setupDlg(object):
    def setupUi(self, setupDlg):
        setupDlg.setObjectName(_fromUtf8("setupDlg"))
        setupDlg.resize(387, 241)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(setupDlg.sizePolicy().hasHeightForWidth())
        setupDlg.setSizePolicy(sizePolicy)
        setupDlg.setSizeGripEnabled(False)
        self.gridLayout = QtGui.QGridLayout(setupDlg)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.setupLayout = QtGui.QVBoxLayout()
        self.setupLayout.setMargin(4)
        self.setupLayout.setObjectName(_fromUtf8("setupLayout"))
        self.headerLbl = QtGui.QLabel(setupDlg)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("DejaVu Sans"))
        font.setPointSize(20)
        font.setBold(False)
        font.setWeight(50)
        self.headerLbl.setFont(font)
        self.headerLbl.setObjectName(_fromUtf8("headerLbl"))
        self.setupLayout.addWidget(self.headerLbl)
        self.testbankDirLbl = QtGui.QLabel(setupDlg)
        self.testbankDirLbl.setObjectName(_fromUtf8("testbankDirLbl"))
        self.setupLayout.addWidget(self.testbankDirLbl)
        self.browseLayout = QtGui.QHBoxLayout()
        self.browseLayout.setObjectName(_fromUtf8("browseLayout"))
        self.testbankDirTxt = QtGui.QLineEdit(setupDlg)
        self.testbankDirTxt.setObjectName(_fromUtf8("testbankDirTxt"))
        self.browseLayout.addWidget(self.testbankDirTxt)
        self.browseBtn = QtGui.QPushButton(setupDlg)
        self.browseBtn.setObjectName(_fromUtf8("browseBtn"))
        self.browseLayout.addWidget(self.browseBtn)
        self.goBtn = QtGui.QPushButton(setupDlg)
        self.goBtn.setObjectName(_fromUtf8("goBtn"))
        self.browseLayout.addWidget(self.goBtn)
        self.setupLayout.addLayout(self.browseLayout)
        self.orLbl = QtGui.QLabel(setupDlg)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("DejaVu Sans"))
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.orLbl.setFont(font)
        self.orLbl.setAlignment(QtCore.Qt.AlignCenter)
        self.orLbl.setObjectName(_fromUtf8("orLbl"))
        self.setupLayout.addWidget(self.orLbl)
        self.prevSessionLbl = QtGui.QLabel(setupDlg)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.prevSessionLbl.setFont(font)
        self.prevSessionLbl.setObjectName(_fromUtf8("prevSessionLbl"))
        self.setupLayout.addWidget(self.prevSessionLbl)
        self.resumeBtn = QtGui.QPushButton(setupDlg)
        self.resumeBtn.setEnabled(False)
        self.resumeBtn.setCheckable(False)
        self.resumeBtn.setObjectName(_fromUtf8("resumeBtn"))
        self.setupLayout.addWidget(self.resumeBtn)
        self.progressBar = QtGui.QProgressBar(setupDlg)
        self.progressBar.setEnabled(False)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.setupLayout.addWidget(self.progressBar)
        self.bottomBtnLayout = QtGui.QHBoxLayout()
        self.bottomBtnLayout.setSpacing(50)
        self.bottomBtnLayout.setObjectName(_fromUtf8("bottomBtnLayout"))
        self.aboutBtn = QtGui.QPushButton(setupDlg)
        self.aboutBtn.setObjectName(_fromUtf8("aboutBtn"))
        self.bottomBtnLayout.addWidget(self.aboutBtn)
        self.exitBtn = QtGui.QPushButton(setupDlg)
        self.exitBtn.setObjectName(_fromUtf8("exitBtn"))
        self.bottomBtnLayout.addWidget(self.exitBtn)
        self.setupLayout.addLayout(self.bottomBtnLayout)
        self.gridLayout.addLayout(self.setupLayout, 0, 0, 1, 1)

        self.retranslateUi(setupDlg)
        QtCore.QMetaObject.connectSlotsByName(setupDlg)

    def retranslateUi(self, setupDlg):
        setupDlg.setWindowTitle(_translate("setupDlg", "IEEE Testbank Tool - Setup", None))
        self.headerLbl.setText(_translate("setupDlg", "IEEE Testbank Tool - Setup", None))
        self.testbankDirLbl.setText(_translate("setupDlg", "Testbank Directory:", None))
        self.browseBtn.setText(_translate("setupDlg", "Browse...", None))
        self.goBtn.setText(_translate("setupDlg", "Go >", None))
        self.orLbl.setText(_translate("setupDlg", "- OR -", None))
        self.prevSessionLbl.setText(_translate("setupDlg", "No previous session detected.", None))
        self.resumeBtn.setText(_translate("setupDlg", "Resume from where I left off...", None))
        self.aboutBtn.setText(_translate("setupDlg", "About...", None))
        self.exitBtn.setText(_translate("setupDlg", "Exit", None))

