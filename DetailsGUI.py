# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Details.ui'
#
# Created: Sun Oct 04 13:23:13 2015
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

class Ui_detailsDlg(object):
    def setupUi(self, detailsDlg):
        detailsDlg.setObjectName(_fromUtf8("detailsDlg"))
        detailsDlg.resize(630, 300)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(detailsDlg.sizePolicy().hasHeightForWidth())
        detailsDlg.setSizePolicy(sizePolicy)
        detailsDlg.setSizeGripEnabled(True)
        self.verticalLayout = QtGui.QVBoxLayout(detailsDlg)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.detailsLbl = QtGui.QLabel(detailsDlg)
        self.detailsLbl.setObjectName(_fromUtf8("detailsLbl"))
        self.verticalLayout.addWidget(self.detailsLbl)
        self.detailsTxt = QtGui.QTextEdit(detailsDlg)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Courier New"))
        self.detailsTxt.setFont(font)
        self.detailsTxt.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.detailsTxt.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.detailsTxt.setReadOnly(True)
        self.detailsTxt.setObjectName(_fromUtf8("detailsTxt"))
        self.verticalLayout.addWidget(self.detailsTxt)
        self.detailsBtnBox = QtGui.QDialogButtonBox(detailsDlg)
        self.detailsBtnBox.setOrientation(QtCore.Qt.Horizontal)
        self.detailsBtnBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.detailsBtnBox.setObjectName(_fromUtf8("detailsBtnBox"))
        self.verticalLayout.addWidget(self.detailsBtnBox)

        self.retranslateUi(detailsDlg)
        QtCore.QObject.connect(self.detailsBtnBox, QtCore.SIGNAL(_fromUtf8("accepted()")), detailsDlg.accept)
        QtCore.QObject.connect(self.detailsBtnBox, QtCore.SIGNAL(_fromUtf8("rejected()")), detailsDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(detailsDlg)

    def retranslateUi(self, detailsDlg):
        detailsDlg.setWindowTitle(_translate("detailsDlg", "IEEE Testbank Tool - Details", None))
        self.detailsLbl.setText(_translate("detailsDlg", "Details:", None))

