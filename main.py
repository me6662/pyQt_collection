import sys
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QObject
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5 import QtCore
import cv2

import time
from time import sleep
import threading

form_class = uic.loadUiType("NASA_Barcode_Scanner.ui")[0]

# 화면을 띄우는데 사용되는 Class 선언


class BarcodeCapture(QObject):
    captured = pyqtSignal()

    def __init__(self):
        super().__init__()

    def capture(self):
        self.captured.emit()


class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 바코드 인식 시 사용 변수
        self.is_cap = False
        self.cap_count = 0
        self.cap = BarcodeCapture()
        self.cap.captured.connect(self.on_barcode_captured)

    @pyqtSlot()
    def on_barcode_captured(self):
        # 로그 테스트
        cur_time = time.strftime('%y-%m-%d %H:%M:%S')
        self.cap_count = self.cap_count + 1
        self.te_barcode_log.append(
            cur_time + ' count : ' + f'{self.cap_count}')

        if self.cap_count >= 5:
            self.te_barcode_log.clear()
            self.cap_count = 0

    def Video_to_frame(self):

        cap = cv2.VideoCapture('sample.mp4')

        while True:
            self.ret, self.frame = cap.read()
            if self.ret:
                self.rgbImage = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

                #######################

                #######################
                self.convertToQtFormat = QImage(
                    self.rgbImage.data, self.rgbImage.shape[1], self.rgbImage.shape[0], QImage.Format_RGB888)

                self.pixmap = QPixmap(self.convertToQtFormat)
                self.p = self.pixmap.scaled(
                    640, 480, QtCore.Qt.IgnoreAspectRatio)

                self.lbl_video.setPixmap(self.p)
                self.lbl_video.update()

                ####바코드 cap 테스트###################
                if self.is_cap == True:
                    self.c = self.pixmap.scaled(
                        385, 238, QtCore.Qt.IgnoreAspectRatio)
                    self.lbl_barcode.setPixmap(self.c)
                    self.lbl_barcode.update()

                    self.cap.capture()

                    self.is_cap = False
                #######################

                sleep(0.03)  # 영상 1프레임당 0.03초

            else:
                break

        cap.release()
        cv2.destroyAllWindows()

    # video_to_frame을 쓰레드로 사용

    def video_thread(self):
        thread = threading.Thread(target=self.Video_to_frame)
        thread.daemon = True  # 프로그램 종료시 프로세스도 함께 종료 (백그라운드 재생 X)
        thread.start()

    # keyPressEvent

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
        elif e.key() == Qt.Key_F:
            self.showFullScreen()
        elif e.key() == Qt.Key_N:
            self.showNormal()
        elif e.key() == Qt.Key_Z:
            if self.is_cap == False:
                self.is_cap = True


if __name__ == "__main__":
    # QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    # WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    myWindow.video_thread()
    myWindow.show()

    # 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
