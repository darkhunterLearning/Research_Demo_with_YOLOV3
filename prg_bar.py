import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QGridLayout, QWidget, QDesktopWidget
import time

class Progress_bar_dialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        uic.loadUi('Demo/prgbar_dialog.ui', self)

        # cho hiển thị giữa màn hình
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        #Find Children

        #Label
        self.lbl_prg: QtWidgets.QLabel = self.findChild(QtWidgets.QLabel, 'lbl_prg')

        #Progress Bar
        self.prgBar: QtWidgets.QProgressBar = self.findChild(QtWidgets.QProgressBar, 'prgBar')


    
