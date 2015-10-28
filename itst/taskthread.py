from PyQt4 import QtCore
import traceback
import ies

class IESScanThread(QtCore.QThread):
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
        res = False
        
        try:
            res = ies.scanDir(self.srcdir, self.progCallback, self.errCallback)
        except:
            print("Critical error occurred! Something went really wrong...")
            print(traceback.format_exc())
            self.errSignal.emit("A critical error occurred! This error is a bug, and may cause issues if you continue running this program.\n"
                + traceback.format_exc())
        
        # Success!
        if res:
            file_table, total_num_files = res
            self.tableSignal.emit(file_table, total_num_files)
    
    def progCallback(self, current_num, total_num, file_name):
        self.progSignal.emit(current_num, total_num, file_name)
    
    def errCallback(self, err_str):
        self.errSignal.emit(err_str)

class IESValidateThread(QtCore.QThread):
    progSignal = QtCore.pyqtSignal(int, int, str, name = "progCallback")
    errSignal = QtCore.pyqtSignal(str, name="errCallback")
    listSignal = QtCore.pyqtSignal(list, int, name="listCallback")
    
    def __init__(self, srcdir):
        super(self.__class__, self).__init__()
        self.srcdir = srcdir
        
        #self.progSignal = QtCore.pyqtSignal(int, int, str, name = "progCallback") #QtCore.SIGNAL("progCallback")
        #self.errSignal = QtCore.pyqtSignal(str, name="errCallback") #QtCore.SIGNAL("errCallback")
    
    def __del__(self):
        self.wait()
    
    def run(self):
        res = False
        
        try:
            res = ies.validateDir(self.srcdir, self.progCallback, self.errCallback)
        except:
            print("Critical error occurred! Something went really wrong...")
            print(traceback.format_exc())
            self.errSignal.emit("A critical error occurred! This error is a bug, and may cause issues if you continue running this program.\n"
                + traceback.format_exc())
        
        # Success!
        if res:
            file_list, total_num_files = res
            self.listSignal.emit(file_list, total_num_files)
    
    def progCallback(self, current_num, total_num, file_name):
        self.progSignal.emit(current_num, total_num, file_name)
    
    def errCallback(self, err_str):
        self.errSignal.emit(err_str)
