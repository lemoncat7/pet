# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 10:57:52 2021

@author: pickaqiu
"""

import json
import os
import sys
import random
import time
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtGui

class DesktopPet(QWidget):
    
    def __init__(self, parent=None,**kwargs):
        super(DesktopPet,self).__init__(parent)
        self.__image_path="."
        self.__json_path="action.json"
        self.sys_icon_flag=False
        self.loadJson()
        
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.SubWindow)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.repaint()
        self.InitImage()
        self.sysIcon()
        self.show()
        #随机动作初始化
        self.action_start=False
        self.action_point=0
        self.is_action=False
        self.action_size=0
        self.random_routine=0
        # 每隔一段时间做个动作
        self.action_timer=QTimer()
        self.action_timer.timeout.connect(self.startAction)
        self.action_timer.start(1000)
        self.timer = QTimer()
        self.timer.timeout.connect(self.randomAct)
        
        # 每隔一段时间检测配置文件
        self.monitor_json=QTimer()
        self.monitor_json.timeout.connect(self.monitorJson)
        self.monitor_json.start(500)
    
    #初始化图片
    def InitImage(self):
        self.image_lab = QLabel(self)
        self.setImage(self.actions["initImage"])
    
    #设置图片
    def setImage(self,image_path):
        path=self.setUpPath(self.__image_path,image_path)
        image = QImage(path)
        self.image_lab.setPixmap(QPixmap.fromImage(image))
        self.resize(image.width(), image.height())

    #设置系统路径
    def setUpPath(self,root,path):
        return os.path.join(root,path)
    
    #设置托盘菜单
    def sysIcon(self):
        if self.sys_icon_flag:
            return
        self.sys_icon_flag=True
        #动作
        quit_act = QAction("退出",self,triggered=self.appQuit)
        path=self.setUpPath(self.__image_path,self.actions["initImage"])
        quit_act.setIcon(QIcon(path))
        #菜单栏
        self.sys_icon_menu = QMenu(self)
        self.sys_icon_menu.addAction(quit_act)
        #系统托盘
        self.sys_icon = QSystemTrayIcon(self)
        self.sys_icon.setIcon(QIcon(path))
        self.sys_icon.setContextMenu(self.sys_icon_menu)
        self.sys_icon.show()

        
    #鼠标左键按下时, 宠物将和鼠标位置绑定
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_follow_mouse = True
            self.mouse_drag_pos = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))
    #鼠标移动, 则宠物也移动
    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.is_follow_mouse:
            self.move(event.globalPos() - self.mouse_drag_pos)
            event.accept()
    #鼠标释放时, 取消绑定
    def mouseReleaseEvent(self, event):
        self.is_follow_mouse = False
        self.setCursor(QCursor(Qt.ArrowCursor))
    
    #读取json文件
    def loadJson(self):
        with open(self.__json_path) as f:
            self.actions = json.load(f)
        self.routine_act=[]
        for action in self.actions:
            if "action" in action:
                self.routine_act.append(self.actions[action])
        self.__image_path=self.actions["route"]
        self.json_before = os.stat(self.__json_path).st_mtime
    
    #检测json文件
    def monitorJson(self):
       if not (os.stat(self.__json_path).st_mtime == self.json_before):
            self.loadJson()
            self.action_size=len(self.current_action["action"])
    
    #开始动作
    def startAction(self):
        if len(self.routine_act) > 0:
            self.action_start=True
            self.randomAct()
    
    #随机动作
    def randomAct(self):
        if not self.is_action:
            self.random_routine=random.randint(0, len(self.routine_act)-1)
            self.is_action=True
            self.action_point=0
            self.current_action=self.routine_act[self.random_routine]
            self.action_size=len(self.current_action["action"])
            time=self.current_action["time"]
            self.timer.start(int(time))
        if self.action_start:
            self.flame(self.current_action["action"])
    #动画
    def flame(self,image):
        #print(self.action_size)
        if self.action_point>=self.action_size:
            self.is_action=False
            self.action_start=False
            self.timer.stop()
            return
        self.setImage(image[self.action_point])
        if self.current_action["name"]=="walk":
            self.movePet()
        self.action_point+=1
    
    #移动
    def movePet(self):
        screen_geo = QDesktopWidget().screenGeometry()
        pet_geo = self.geometry()
        x = pet_geo.x() + int(self.current_action["move"][0])
        y = pet_geo.y() + int(self.current_action["move"][1])
        #print(x,y)
        if x <=0 or y <= 0 or x >= screen_geo.width() - pet_geo.width() or y >= screen_geo.height() - pet_geo.height():
            return
        self.move(x,y)
    
    #退出程序
    def appQuit(self):
        self.close()
        sys.exit(0)
        
        
        
'''run'''
if __name__ == '__main__':
	app = QApplication(sys.argv)
	pet = DesktopPet()
	sys.exit(app.exec_())