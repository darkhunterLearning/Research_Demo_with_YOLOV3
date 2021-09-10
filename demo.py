import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt
from  matplotlib import cm
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QWidget, QDesktopWidget
import math
from prg_bar import Progress_bar_dialog
import time
import datetime
from yolo_model import *

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi('Demo/demo.ui', self)
        self.setFixedSize(866, 583)

        self.my_model = YoloModel()
        self.my_model.load_model()


        # cho hiển thị giữa màn hình
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        '''preloaded'''
        self.original_image = None
        self.image = None
        self.img_2_class = None
        self.pos_img = None
        self.non_pos_img = None
        self.path = ''
        self.list_frame = []

        #Find Children
        #Label
        self.lbl_img: QtWidgets.QLabel = self.findChild(QtWidgets.QLabel, 'lbl_img')
        self.lbl_pos: QtWidgets.QLabel = self.findChild(QtWidgets.QLabel, 'lbl_pos')
        self.lbl_non_pos: QtWidgets.QLabel = self.findChild(QtWidgets.QLabel, 'lbl_non_pos')
        self.lbl_num_title: QtWidgets.QLabel = self.findChild(QtWidgets.QLabel, 'lbl_num_title')
        self.lbl_num_frames: QtWidgets.QLabel = self.findChild(QtWidgets.QLabel, 'lbl_num_frames')


        #Button
        self.btn_open: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'btn_open')
        self.btn_detect: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'btn_detect')
        self.btn_export: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'btn_export')
        self.btn_screenshot: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'btn_screenshot')
        self.btn_show_hide: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'btn_show_hide')

        #Spinbox
        self.spbox: QtWidgets.QSpinBox = self.findChild(QtWidgets.QSpinBox, 'spbox')

        #Checkbox
        self.checkbox_pos: QtWidgets.QCheckBox = self.findChild(QtWidgets.QCheckBox, 'checkbox_pos')
        self.checkbox_non_pos: QtWidgets.QCheckBox = self.findChild(QtWidgets.QCheckBox, 'checkbox_non_pos')

        #action
        self.btn_show_hide.setEnabled(False)
        self.checkbox_pos.setEnabled(False)
        self.checkbox_non_pos.setEnabled(False)
        self.btn_open.clicked.connect(self.openFile)
        self.spbox.valueChanged.connect(self.valueChange)
        self.btn_detect.clicked.connect(self.detectImage)
        self.btn_show_hide.clicked.connect(self.showHideLabel)
        self.checkbox_pos.stateChanged.connect(self.enableShowHide)
        self.checkbox_non_pos.stateChanged.connect(self.enableShowHide)
        self.btn_screenshot.clicked.connect(self.screenshot)

        self.show()

    def openFile(self):
        self.btn_detect.setEnabled(True)
        self.lbl_pos.setStyleSheet('font-size:12pt; font-weight:600; font-style:italic; color:#02a100;')
        self.lbl_non_pos.setStyleSheet(' font-size:12pt; font-weight:600; font-style:italic; color:#ff0000;')
        self.lbl_pos.setText('Positive: 0')
        self.lbl_non_pos.setText('Non-Positive: 0')
        self.image = None
        self.list_frame = []
        filename = QtWidgets.QFileDialog.getOpenFileName(None, 'Open File', '', 'Image files (*.png *.xpm *.jpg *.tif);;Video files (*.mp4)')
        is_image = 'Image files (*.png *.xpm *.jpg *.tif)'
        is_video = 'Video files (*.mp4)'
        if filename[1] == is_image:
            self.lbl_num_frames.setEnabled(True) 
            self.lbl_num_frames.setStyleSheet('font-size:10pt; font-weight:600;')
            if filename[0] != '' and filename[0] != None:
                self.lbl_num_frames.setText('/1')
                self.path = filename[0]
                self.original_image = cv2.imread(filename[0])
                self.image = self.original_image
                self.showImage(self.lbl_img, self.image)
            else:
                print("invalid file")
        if filename[1] == is_video:
            num_count = 0
            self.lbl_num_frames.setEnabled(True) 
            self.lbl_num_frames.setStyleSheet('font-size:10pt; font-weight:600;')
            try:
                cap = cv2.VideoCapture(filename[0])
                frameRate = cap.get(cv2.CAP_PROP_FPS) #frame rate
                totalNoFrames = cap.get(cv2.CAP_PROP_FRAME_COUNT) #numbers of frame
                video_length = int(totalNoFrames/frameRate)
                prg_bar_dialog = Progress_bar_dialog()
                prg_bar_dialog.show()
                if video_length > 100:
                    video_length = 100
                self.lbl_num_frames.setText('/'+str(video_length))

                while(num_count != video_length):
                    self.btn_open.setEnabled(False)
                    self.btn_detect.setEnabled(False)
                    self.btn_screenshot.setEnabled(False)
                    self.btn_show_hide.setEnabled(False)
                    self.checkbox_pos.setEnabled(False)
                    self.checkbox_non_pos.setEnabled(False)

                    frameId = cap.get(cv2.CAP_PROP_POS_FRAMES) #current frame number
                    ret, frame = cap.read()
                    if (ret != True):
                        break
                    if (frameId % math.floor(frameRate) == 0):
                        self.list_frame.append(frame)
                        num_count = num_count+1
                        time.sleep(0.1)
                        prg_bar_dialog.prgBar.setValue(num_count*(100/video_length))
                        app.processEvents()

                cap.release()
                self.btn_open.setEnabled(True)
                self.btn_detect.setEnabled(True)
                self.btn_screenshot.setEnabled(True)
                self.spbox.setEnabled(True)
                self.checkbox_pos.setEnabled(True)
                self.checkbox_non_pos.setEnabled(True)
                self.spbox.setMaximum(video_length)
                self.spbox.setValue(1)
                idx = self.spbox.value()
                self.image = self.list_frame[idx-1]
                self.showImage(self.lbl_img, self.image)
                app.processEvents()
     
            except:
                print("File invalid!")    
        else:
            pass

    def showImage(self, label: QtWidgets.QLabel, cv_img = None):
        if cv_img is None:
            cv_img = self.image
        if cv_img is not None:
            height, width = cv_img.shape[:2]
            bytes_per_line = 3 * width
            q_img = QtGui.QImage(cv_img.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888).rgbSwapped()
            label.setPixmap(QtGui.QPixmap(q_img))
        else:
            print("Warning: self.image is empty.")

    def valueChange(self):
        self.btn_detect.setEnabled(True)
        self.btn_show_hide.setEnabled(False)
        self.lbl_pos.setStyleSheet('font-size:12pt; font-weight:600; font-style:italic; color:#02a100;')
        self.lbl_non_pos.setStyleSheet(' font-size:12pt; font-weight:600; font-style:italic; color:#ff0000;')
        self.lbl_pos.setText('Positive: 0')
        self.lbl_non_pos.setText('Non-Positive: 0')
        try:
            idx = self.spbox.value()
            self.image = self.list_frame[idx-1] 
            self.showImage(self.lbl_img, self.image)
        except:
        	print("Error!")

    def detectImage(self):
        if self.image is not None:
            predicted_image, no_class_img, pos_img, non_pos_img, num_non_pos, num_pos = self.my_model.predict(self.image)
            self.btn_show_hide.setEnabled(True)
            self.checkbox_pos.setEnabled(True)
            self.checkbox_non_pos.setEnabled(True)
            #Update self.img_2_class, self.pos_img, self.non_pos_img
            self.img_2_class = predicted_image
            self.original_image = no_class_img
            self.pos_img = pos_img
            self.non_pos_img = non_pos_img

            self.image = predicted_image
            self.showImage(self.lbl_img, self.image)
            self.lbl_pos.setStyleSheet('font-size:12pt; font-weight:600; font-style:italic; color:#02a100;')
            self.lbl_non_pos.setStyleSheet(' font-size:12pt; font-weight:600; font-style:italic; color:#ff0000;')
            self.lbl_pos.setText('Positive: ' + str(num_pos))
            self.lbl_non_pos.setText('Non-Positive: ' + str(num_non_pos))
            self.btn_detect.setEnabled(False)
            self.btn_show_hide.setEnabled(False)

    def showHideLabel(self):
        if self.checkbox_pos.isChecked() and self.checkbox_non_pos.isChecked():
            self.image = self.img_2_class
        if self.checkbox_pos.isChecked() and self.checkbox_non_pos.isChecked() == False:
            self.image = self.pos_img
        if self.checkbox_pos.isChecked() == False and self.checkbox_non_pos.isChecked():
            self.image = self.non_pos_img
        if self.checkbox_pos.isChecked() == False and self.checkbox_non_pos.isChecked() == False:
            self.image = self.original_image
        self.showImage(self.lbl_img, self.image)

    def enableShowHide(self):
        self.btn_show_hide.setEnabled(True)

    def screenshot(self):
        if self.image is not None:
            x = datetime.datetime.now()
            img_name = x.strftime("%d"+"-"+"%m"+"-"+"%Y"+"_"+"%H"+"_"+"%M"+"_"+"%S")
            cv2.imwrite('Demo/output/'+img_name+'.png', self.image)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    tmp = Ui_MainWindow()
    app.exec_()