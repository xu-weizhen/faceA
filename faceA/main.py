# -*- coding:utf-8 -*-

import os, _thread, sys, json

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtCore import pyqtSignal, QThread

from faceA import MyUtils
from faceA.ui.ui_base.Form_main import Ui_Form_main
from faceA.ui.Dia_alter import Alter_Dialog
from faceA.ui.Dia_doAllFile import DoAllFile_Dialog

from PIL import Image
from PIL import ImageDraw


class mainD(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form_main()
        self.ui.setupUi(self)
        self.setWindowTitle("人脸属性识别系统")
        self.setWindowFlags(QtCore.Qt.MSWindowsFixedSizeDialogHint)  # 禁止用户改变窗口大小

        # 定义几个按钮的槽连接
        self.ui.pushButton.clicked.connect(self.openfile_button_connect)
        self.ui.pushButton_2.clicked.connect(self.analysisCurPic_button_connect)
        self.ui.pushButton_3.clicked.connect(self.openUnProcesssedFile_button_connect)
        self.ui.pushButton_4.clicked.connect(self.openHaveDonedFile_button_connect)
        self.ui.pushButton_5.clicked.connect(self.doAllFile_button_connect)
        self.ui.pushButton_6.clicked.connect(self.showAllResults_button_connect)
        self.ui.pushButton_7.clicked.connect(self.stopShowResult_button_connect)
        self.ui.pushButton_b.clicked.connect(self.ShowResult_border)
        self.ui.pushButton_p.clicked.connect(self.ShowResult_point)

        # 初始化一些要用到的变量
        self.picpath = ''
        self.result = ''
        self.picnum_toshow = 0
        self.picnum_haveshow = 0
        self.undoPath = r'.\resource\pic_undo'
        self.havedonedPath = r'.\resource\pic_havedone'
        self.doallfilethread = None

    def ShowResult_border(self):
        b_len = len(self.picpath) - 1
        for b_len in range (b_len, 0, -1):
            if (self.picpath[b_len] == '/' and self.picpath[b_len-1] == 'A' and self.picpath[b_len-2] == 'e'):
                break
        picpath_b = self.picpath[0:b_len + 1]
        picpath_b = picpath_b + "result_b.jpg"
        png = QPixmap(picpath_b)

        if png.isNull():
            Alter_Dialog("警报", "图片转换出现错误").exec_()
            return

        # 按与控件的比例，对图像进行缩放
        if png.width() / png.height() > self.ui.label.width() / self.ui.label.height():
            if png.width() < self.ui.label.width():
                png = png.scaledToHeight(png.width() * self.ui.label.height() / png.height(), self.ui.label.height())
            else:
                png = png.scaled(self.ui.label.width(), png.height() * self.ui.label.width() / png.width())
        else:
            if png.height() < self.ui.label.height():
                png = png.scaledToHeight(png.width() * self.ui.label.height() / png.height(), self.ui.label.height())
            else:
                png = png.scaled(png.width() * self.ui.label.height() / png.height(), self.ui.label.height())

        # 把图像放到控件中显示
        MyUtils.getLogger(__name__).info("展示图片" + self.picpath)
        self.ui.label.setPixmap(png)
        return

    def ShowResult_point(self):
        b_len = len(self.picpath) - 1
        for b_len in range (b_len, 0, -1):
            if (self.picpath[b_len] == '/' and self.picpath[b_len-1] == 'A' and self.picpath[b_len-2] == 'e'):
                break
        picpath_b = self.picpath[0:b_len + 1]
        picpath_b = picpath_b + "result_p.jpg"
        png = QPixmap(picpath_b)

        if png.isNull():
            Alter_Dialog("警报", "图片转换出现错误").exec_()
            return

        # 按与控件的比例，对图像进行缩放
        if png.width() / png.height() > self.ui.label.width() / self.ui.label.height():
            if png.width() < self.ui.label.width():
                png = png.scaledToHeight(png.width() * self.ui.label.height() / png.height(), self.ui.label.height())
            else:
                png = png.scaled(self.ui.label.width(), png.height() * self.ui.label.width() / png.width())
        else:
            if png.height() < self.ui.label.height():
                png = png.scaledToHeight(png.width() * self.ui.label.height() / png.height(), self.ui.label.height())
            else:
                png = png.scaled(png.width() * self.ui.label.height() / png.height(), self.ui.label.height())

        # 把图像放到控件中显示
        MyUtils.getLogger(__name__).info("展示图片" + self.picpath)
        self.ui.label.setPixmap(png)
        return

    def showAllResults_button_connect(self):
        if not self.doallfilethread == None:
            if self.doallfilethread.thread_status == 1:
                self.doallfilethread.thread_status = 0
                self.ui.pushButton_6.setText("继续展示")
                return
            elif self.doallfilethread.thread_status == 0:
                self.doallfilethread.thread_status = 1
                self.ui.pushButton_6.setText("暂停展示")
                return

        # 计算进度条
        self.picnum_haveshow = 0
        self.picnum_toshow = int(len(os.listdir(self.havedonedPath)) / 2)
        self.ui.label_4.setText(str(self.picnum_haveshow) + "/" + str(self.picnum_toshow))

        # 定义处理文件的线程
        self.doallfilethread = showFileThread()

        # 定义好更新ui的槽连接
        self.ui.pushButton_6.setText("暂停展示")
        self.doallfilethread.shownew_signal.connect(self.showPicAndResult_connect)

        # 定义好线程中的参数
        self.doallfilethread.setPath(self.havedonedPath)
        self.doallfilethread.setPicSize(self.ui.label.width(), self.ui.label.height())
        self.doallfilethread.start()

    def stopShowResult_button_connect(self):
        if not self.doallfilethread == None:
            self.ui.pushButton_6.setText("展示识别结果")
            self.picnum_haveshow = 0
            self.ui.label_4.setText(str(self.picnum_haveshow) + "/" + str(self.picnum_toshow))
            self.doallfilethread.thread_status = -1

    def openfile_button_connect(self):
        fname = QFileDialog.getOpenFileName(self, '打开文件', './')

        self.picpath = fname[0]
        MyUtils.getLogger(__name__).info("打开文件"+self.picpath)

        if len(self.picpath) < 4 or not (self.picpath[-4:] == '.png' or self.picpath[-4:] == '.jpg'):
            Alter_Dialog("警报", "请选择jpg或者png文件").exec_()
            return

        png = QPixmap(self.picpath)

        if png.isNull():
            Alter_Dialog("警报", "图片转换出现错误").exec_()
            return

        # 按与控件的比例，对图像进行缩放
        if png.width() / png.height() > self.ui.label.width() / self.ui.label.height():
            if png.width() < self.ui.label.width():
                png = png.scaledToHeight(png.width() * self.ui.label.height() / png.height(), self.ui.label.height())
            else:
                png = png.scaled(self.ui.label.width(), png.height() * self.ui.label.width() / png.width())
        else:
            if png.height() < self.ui.label.height():
                png = png.scaledToHeight(png.width() * self.ui.label.height() / png.height(), self.ui.label.height())
            else:
                png = png.scaled(png.width() * self.ui.label.height() / png.height(), self.ui.label.height())

        # 把图像放到控件中显示
        MyUtils.getLogger(__name__).info("展示图片"+self.picpath)
        self.ui.label.setPixmap(png)

    def analysisCurPic_button_connect(self):
        if len(self.picpath) < 4 or not (self.picpath[-4:] == '.png' or self.picpath[-4:] == '.jpg'):
            Alter_Dialog("警报", "请选择jpg或者png文件").exec_()
        else:
            try:
                self.showResult(MyUtils.getPicAnalysisResult(self.picpath), self.picpath)
                MyUtils.getLogger(__name__).info("展示图片分析结果" + self.picpath)
            except Exception as e:
                Alter_Dialog(e.__str__()).exec()

    def openUnProcesssedFile_button_connect(self):
        os.system("explorer.exe %s" % self.undoPath)

    def openHaveDonedFile_button_connect(self):
        os.system("explorer.exe %s" % self.havedonedPath)

    def doAllFile_button_connect(self):
        dfb = DoAllFile_Dialog("图片识别中……")
        dfb.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowMinimizeButtonHint)
        # 在子线程中处理文件
        _thread.start_new_thread(self.doAllFileinThread_threadfunction, (dfb, self.havedonedPath, self.undoPath))
        dfb.exec_()

    # 展示全部文件线程的连接槽函数
    def showPicAndResult_connect(self, pic, result, picpath):
        self.ui.label.setPixmap(pic)
        self.picpath = picpath
        self.showResult(result, picpath)
        self.picnum_haveshow += 1
        MyUtils.getLogger(__name__).info("展示图片及其结果"+picpath)
        self.ui.label_4.setText(str(self.picnum_haveshow) + "/" + str(self.picnum_toshow))
        if (self.picnum_haveshow == self.picnum_toshow):
            self.ui.pushButton_6.setText("展示识别结果")

    # 处理所有文件线程中的运行函数
    def doAllFileinThread_threadfunction(self, dfb, havedonedPath, undoPath):
        i = (int)(len(os.listdir(havedonedPath)) / 2)
        j = i
        num_undo = len(os.listdir(undoPath))
        if num_undo == 0:
            dfb.ui.progressBar.hide()
            dfb.ui.label.setText("没有文件待处理")
            dfb.ui.pushButton.show()
            return

        for root, dirs, files in os.walk(self.undoPath):
            for file in files:
                filepath = os.path.join(root, file)
                MyUtils.getLogger(__name__).info("读取 " + filepath)
                # 判断用户选择的文件是否符合要求，这里只支持png和jpg
                if len(filepath) < 4 or (not (filepath[-4:] == '.png' or filepath[-4:] == '.jpg')):
                    MyUtils.getLogger(__name__).warn(file + "不是jpg或者png文件")
                else:
                    result = ""
                    try:
                        result = MyUtils.getPicAnalysisResult(filepath)
                    except Exception as e:
                        MyUtils.getLogger(__name__).error(e.__str__())

                    os.rename(filepath, os.path.join(self.havedonedPath, str(i)) + filepath[-4:])
                    try:
                        fjson = open(os.path.join(self.havedonedPath, str(i)) + ".json", 'w')
                        fjson.write(result)
                        i += 1
                        fjson.close()
                    except Exception as e:
                        MyUtils.getLogger(__name__).error(e.__str__() + " open " + self.havedonedPath + " failed")

                dfb.ui.progressBar.setValue(100 * (i - j) / num_undo)
        dfb.ui.progressBar.setValue(100)
        dfb.ui.label.setText("识别已经完成")
        dfb.ui.pushButton.show()

    # 这个函数被两个内部函数用到了,在这里写网络请求重试，如果结果是错误，则在这里会进行一次补救
    def showResult(self, result, picpath):

        resultobj = None
        try:
            resultobj = json.JSONDecoder().decode(result)
        except Exception as e:
            MyUtils.getLogger(__name__).error(e.__str__())
        if (resultobj == None or 'error_message' in resultobj):
            try:
                result = MyUtils.getPicAnalysisResult(self.picpath)
                resultobj = json.JSONDecoder().decode(result)
            except Exception as e:
                MyUtils.getLogger(__name__).error(e.__class__ + e.__str__())

        if (resultobj == None):
            text = '数据请求失败'
            self.ui.label_2.setText(text)
            return
        elif ('error_message' in resultobj):
            text = "error_message:" + resultobj['error_message']['value']
            self.ui.label_2.setText(text)
            return

        text = ''
        j = 1
        imgb = Image.open(picpath)
        imgp = Image.open(picpath)
        imgdb = ImageDraw.Draw(imgb)
        imgdp = ImageDraw.Draw(imgp)
        try:
            for i in resultobj['faces']:
                text += "人物" + str(j) + ":\n"
                j += 1
                att = i['attributes']
                text += "年龄: " + str(att['age']['value'])
                text += "\n性别: " + ("女" if att['gender']['value'] == "Female" or att['gender']['value'] == "FEMALE" else "男")
                text += "\n人种: "
                if att['ethnicity']['value'] == 'ASIAN' or att['ethnicity']['value'] == 'Asian':
                    text += "亚洲人"
                elif att['ethnicity']['value'] == 'WHITE' or att['ethnicity']['value'] == 'White':
                    text += "白人"
                elif att['ethnicity']['value'] == 'INDIA' or att['ethnicity']['value'] == 'india':
                    text += "印度人"
                elif att['ethnicity']['value'] == 'BLACK' or att['ethnicity']['value'] == 'black':
                    text += "黑人"
                else:
                    text += att['ethnicity']['value']

                text += "\n笑容程度: " + str(att['smile']['value']) + "\n"
                if att['glass']['value'] == 'None':
                    text += "没有佩戴眼镜"
                elif att['glass']['value'] == 'Dark':
                    text += "佩戴墨镜"
                else:
                    text += "佩戴普通眼镜"
                text += '\n\n'

                point_y = i['face_rectangle']['top']
                point_x = i['face_rectangle']['left']
                height = i['face_rectangle']['height']
                width = i['face_rectangle']['width']
                point1 = (point_x, point_y)
                point2 = (point_x + width, point_y)
                point3 = (point_x, point_y + height)
                point4 = (point_x + width, point_y + height)

                imgdb.line([point1, point2, point4, point3, point1], fill=(0, 0, 255), width=5)

                left_eye_x = i['landmark']['left_eye_center']['x']
                left_eye_y = i['landmark']['left_eye_center']['y']
                left_eye_point = (left_eye_x - 3, left_eye_y - 3, left_eye_x + 3, left_eye_y + 3)
                imgdp.ellipse(left_eye_point, fill='blue')

                right_eye_x = i['landmark']['right_eye_center']['x']
                right_eye_y = i['landmark']['right_eye_center']['y']
                right_eye_point = (right_eye_x - 3, right_eye_y - 3, right_eye_x + 3, right_eye_y + 3)
                imgdp.ellipse(right_eye_point, fill='blue')

                # mouth_x = i['landmark']['mouth_lower_lip_top']['x']
                # mouth_y = i['landmark']['mouth_lower_lip_top']['y']
                # mouth_point = (mouth_x - 3, mouth_y - 3, mouth_x + 3, mouth_y + 3)
                # imgdp.ellipse(mouth_point, fill='blue')

                mouth_x = i['landmark']['mouth_left_corner']['x']
                mouth_y = i['landmark']['mouth_left_corner']['y']
                mouth_point = (mouth_x - 3, mouth_y - 3, mouth_x + 3, mouth_y + 3)
                imgdp.ellipse(mouth_point, fill='blue')

                mouth_x = i['landmark']['mouth_right_corner']['x']
                mouth_y = i['landmark']['mouth_right_corner']['y']
                mouth_point = (mouth_x - 3, mouth_y - 3, mouth_x + 3, mouth_y + 3)
                imgdp.ellipse(mouth_point, fill='blue')

                nose_x = i['landmark']['nose_tip']['x']
                nose_y = i['landmark']['nose_tip']['y']
                nose_point = (nose_x - 3, nose_y - 3, nose_x + 3, nose_y + 3)
                imgdp.ellipse(nose_point, fill='blue')

        except Exception as e:
            MyUtils.getLogger(__name__).error(e.__class__ + e.__str__())

        imgb.save("result_b.jpg")
        imgp.save("result_p.jpg")
        # img.show()
        self.ui.label_2.setText(text)
        self.ui.pushButton_p.setDisabled(False)
        self.ui.pushButton_b.setDisabled(False)


# 展示文件线程
class showFileThread(QThread):
    shownew_signal = pyqtSignal(object, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        # 三种状态 -1 是终止，0是等待，1是运行
        self.thread_status = 1

    def setPath(self, path):
        self.havedonedPath = path

    def setPicSize(self, width, height):
        self.wid = width
        self.he = height

    def run(self):
        for root, dirs, files in os.walk(self.havedonedPath):
            for file in files:
                while self.thread_status == 0:
                    self.sleep(5)

                if self.thread_status == 1:
                    filepath = os.path.join(root, file)
                    if len(filepath) < 4 or not (filepath[-4:] == '.png' or filepath[-4:] == '.jpg'):
                        pass
                    else:
                        pic = QPixmap(filepath)
                        if pic.isNull():
                            MyUtils.getLogger(__name__).error("警报", "图片转换出现错误")
                        else:
                            # 按与控件的比例，对图像进行缩放
                            if pic.width() / pic.height() > self.wid / self.he:
                                if pic.width() < self.wid:
                                    pic = pic.scaledToHeight(pic.width() * self.he / pic.height(), self.he)
                                else:
                                    pic = pic.scaled(self.wid, pic.height() * self.wid / pic.width())
                            else:
                                if pic.height() < self.he:
                                    pic = pic.scaledToHeight(pic.width() * self.he / pic.height(), self.he)
                                else:
                                    pic = pic.scaled(pic.width() * self.he / pic.height(), self.he)

                        try:
                            file = open(filepath[:-4] + '.json')
                            result = file.read()
                            file.close()
                            self.shownew_signal.emit(pic, result, filepath)
                        except Exception as e:
                            MyUtils.getLogger(__name__).error(e.__str__() + " open " + self.havedonedPath + " failed")

                        self.sleep(3)
                elif self.thread_status == -1:
                    return

        self.thread_status = -1


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = mainD()
    ex.show()
    sys.exit(app.exec_())

"""
@author:raymond
@file:main.py
@time:2018/1/1611:45

@xuweizhen
@file:main.py
@time:2018/7/19 00:15
"""
