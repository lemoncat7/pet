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
import hashlib
import requests
#from notifypy import Notify
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtGui

class LoginTic():
    def __init__(self):
        self.headers = {
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        }
 
        self.key = '95e60b7082bf475f8f879e642a069a08'
        # 创建一个网络请求session实现登录验证
        self.session = requests.session()
 
    def talkWithTuling(self,text):
        url = 'http://www.tuling123.com/openapi/api'
        data = {
            'key':self.key,         #key
            'info':text,            #发给图灵的内容
            'userid':'123456swh'    #用户id,自己设置1-32的字母和数字组合
        }
        response = requests.post(url=url, headers=self.headers, data=data)
        return response.text
    
    def qingYue(self,text):
        url="http://api.qingyunke.com/api.php?key=free&appid=0&msg="
        response = requests.post(url=url+text)
        return response.text
    
    def OLAMI(self,text):
        t = time.time()
        times=str(int(round(t*1000)))
        tt = "1614526973243"
        secret='057845f72ef54a96a69ca62b786328cd'
        key='d94d8113c2274e0896612d5bb16b7f80'
        mdKey=secret+'api=nli'+"appkey="+key+"timestamp="+times+secret
        log=hashlib.md5(mdKey.encode())
        
        url="https://cn.olami.ai/cloudservice/api"
        data={
            "appkey":"d94d8113c2274e0896612d5bb16b7f80",
            "api":"nli",
            "timestamp":times,
            "sign":log.hexdigest(),
            "cusid":'pickaqiu',
            "rq" : json.dumps({"data_type":"stt","data":{"input_type":"1","text":text}})
        }
        r = requests.post(url=url,data=data)
        return r.text
        

class MyTextEdit(QWidget):
    def __init__(self,parent=None,**kwargs):
        super(MyTextEdit,self).__init__(parent)
        self.setStyleSheet("border-style: none")
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.SubWindow)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.initText()
        self.dx = 0
        self.dy = 0
        self.show()
        
    def initText(self):
         #定时隐藏
        self.text_timer=QTimer()
        self.text_timer.timeout.connect(self.hideText)
        self.text_time=3000
        self.level = 0
        #文本框
        self.edit = QTextEdit(self)
        self.edit.setReadOnly(True)
        self.edit.setStyleSheet("border-radius: 10px;background: #FFFFFF;")
        self.edit.setFont(QFont("华文行楷", 12))
        self.document = self.edit.document()
        self.document.contentsChanged.connect(self.textAreaChanged)
        
    #设定对话框存在时间
    def setTimer(self,time):
        self.text_timer.start(time)
        self.show()
        
    #修改对话框大小
    def textAreaChanged(self):
        self.document.adjustSize()
        newWidth = self.document.size().width() + 30
        newHeight = self.document.size().height() + 10
        if newWidth != self.edit.width():
            self.edit.setFixedWidth(int(newWidth))
        if newHeight != self.edit.height():
            self.edit.setFixedHeight(int(newHeight))
        self.resize(int(newWidth),int(newHeight))
    
    #设定目标位置
    def setDestPoint(self,x,y):
        self.move(x - self.edit.width() , y - int(self.edit.height() / 2) + 40)
            
    
    #设定输入文字
    def setText(self,string, level):
        if level >= self.level:
            self.edit.setText(string)
            self.level = level
        
    def hideText(self):
        self.hide()
        self.text_timer.stop()
        self.level = 0

class DesktopPet(QWidget):
    
    def __init__(self, parent=None,**kwargs):
        super(DesktopPet,self).__init__(parent)
        self.old_width = 0
        self.old_height = 0
        self.setStyleSheet("border-style: none")
        
        #图灵
        self.tuLing = LoginTic();
        
        self.__image_path="."
        self.__json_path="action.json"
        self.sys_icon_flag=False
        self.action_time=1000
        self.loadJson()
        self.current_action=[]
        self.hbox = QHBoxLayout()
        self.setLayout(self.hbox)
        self.op = QtWidgets.QGraphicsOpacityEffect()
        
        #点击文本
        self.clickup_text_flag=True
        self.text_json_flag=True
        self.text_flags = {"clickup_text_flag" : True,"text_json_flag" : True, "talk_flag" : False}
       
        self.is_follow_mouse=False
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.SubWindow)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.repaint()
        self.sysIcon()
        self.show()
        self.pet_point={"x":"0","y":"0"}
        self.recordPoint()
        #随机动作初始化
        self.action_start=False
        self.action_point=0
        #随机动画
        self.is_action=False
        #固定动画
        self.is_fixed_action=False
        self.action_size=0
        self.random_routine=0
        # 每隔一段时间做个动作
        self.timers=[]
        self.action_timer=QTimer()
        self.action_timer.timeout.connect(self.startAction)
        self.action_timer.start(self.action_time)
        self.timer = QTimer()
        self.timer.timeout.connect(self.randomAct)        
        #点击动画
        self.click_timer=QTimer()
        self.click_timer.timeout.connect(self.clickUpAction)
        self.clickd_timer=QTimer()
        self.clickd_timer.timeout.connect(self.clickDownAction)
        self.clickd_time=50
        self.timers.append(self.action_timer)
        self.timers.append(self.timer)
        self.timers.append(self.click_timer)
        self.timers.append(self.clickd_timer)
        #初始化文本框
        self.image_width = 0
        self.image_height = 0
        #self.InitText()
        self.edit = MyTextEdit()
        #文本移动定时器
        self.edit_timer=QTimer()
        self.edit_timer.timeout.connect(self.editMove)
        self.edit_timer.start(50)
        self.InitImage()
        self.writeText("你好呀 召唤师",0,2000)
        # 每隔一段时间检测配置文件
        self.monitor_json=QTimer()
        self.monitor_json.timeout.connect(self.monitorJson)
        self.monitor_json.start(500)
        # 弹窗定时
        self.dilag_timer=QTimer()
        self.dilag_timer.timeout.connect(self.dilagWrite)
         
    
    #关闭计时器组
    def closeTimer(self,time=None):
        for t in self.timers:
            if t != time:
                t.stop()
    
    #记录坐标
    def recordPoint(self):
        pet_geo = self.geometry()
        s = "mid"
        if int(self.pet_point['x']) < pet_geo.x():
            s = "right"
        if int(self.pet_point['x']) > pet_geo.x():
            s = "left"
        self.pet_point['x'] = str(pet_geo.x())
        self.pet_point['y'] = str(pet_geo.y())
        #print(s)
        return s
    
    def editMove(self):
        self.edit.setDestPoint(self.geometry().x(),self.geometry().y())
    
    #初始化图片
    def InitImage(self):
        self.image_lab = QLabel(self)
        self.hbox.addWidget(self.image_lab)
        self.setImage(self.actions["initImage"])
    
    #设置图片
    def setImage(self,image_path):
        path=self.setUpPath(self.__image_path,image_path)
        image = QImage(path)
        self.image_lab.setPixmap(QPixmap.fromImage(image))
        #self.resize(image.width(),image.height())
        
    #关闭写文档标识
    def closeTextFlag(self,flag=None,b=False):
        for f in self.text_flags:
            if flag != self.text_flags[f]:
                self.text_flags[flag] = b
        
    #从json 写入文本框
    def writeTextFromJson(self,action,level):
        self.writeText(action["text"],level)
    
    #写入文本框
    def writeText(self,string,level,time=3000):
        self.edit.setTimer(time)
        self.edit.setText(string,level)
            
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
            self.writeTextFromJson(self.click_act,2)
            self.recordPoint()
            self.is_follow_mouse = True
            self.mouse_drag_pos = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))
            if len(self.click_act):
                self.closeTimer(self.click_timer)
                self.click_timer.start(int(self.click_act["time"])) 
        if event.button() == Qt.RightButton:
            self.dilag_timer.start(100)
           
    def dilagWrite(self):
         self.dilag_timer.stop()
         text, ok = QInputDialog.getText(self, "皮卡丘","请输入对话:",QLineEdit.Normal)
         if ok:
             s = self.tuLing.OLAMI(text)
             t = json.loads(s)["data"]["nli"][0]["desc_obj"]["result"]
             #print(t)
             self.writeText(t,3)
            
    #鼠标移动, 则宠物也移动
    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.is_follow_mouse:
            self.move(event.globalPos() - self.mouse_drag_pos)
            event.accept()
            
            
    #鼠标释放时, 取消绑定
    def mouseReleaseEvent(self, event):
        #print("click down")
        if not self.is_follow_mouse:
            return
        self.is_follow_mouse = False
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.closeTimer(self.clickd_timer)
        self.clickd_timer.start(self.clickd_time)
    
    #鼠标点击时动画
    def clickUpAction(self):
        s = self.recordPoint()
        if s == "mid":
            if "clickUp" in self.click_act:
                #print(self.click_act["clickUp"])
                self.fixedAct(self.click_act["clickUp"])
        elif s == "left":
            if "clickLeft" in self.click_act:
                #print(self.click_act["clickUp"])
                self.fixedAct(self.click_act["clickLeft"])
        elif s == "right":
            if "clickRight" in self.click_act:
                #print(self.click_act["clickUp"])
                self.fixedAct(self.click_act["clickRight"])
    
    def clickDownAction(self):
        if "clickDown" in self.click_act:
            self.fixedAct(self.click_act["clickDown"]["action"])
            if "move" in self.click_act["clickDown"]:
                flag = self.movePet(int(self.click_act["clickDown"]["move"][0]),
                             int(self.click_act["clickDown"]["move"][1]))
                if not flag:
                    self.writeTextFromJson(self.click_act["clickDown"],2)
                    self.text_flags["clickup_text_flag"]=True
                    self.clickd_timer.stop()
                    self.clickd_time=50
                    self.floorDownAction()
                    self.clickfd_timer=QTimer()
                    self.clickfd_timer.timeout.connect(self.floorDownAction)
                    self.timers.append(self.clickfd_timer)
                    self.clickfd_timer.start(int(self.click_act["clickDown"]["time"]))
                    return
                if self.clickd_time > 6:
                    self.clickd_time-=5
                    self.clickd_timer.start(self.clickd_time)
                
    #着陆动画
    def floorDownAction(self):
        if "floor" in self.click_act["clickDown"]:
            if self.flame(self.click_act["clickDown"]["floor"],
                       len(self.click_act["clickDown"]["floor"]),
                       False):
                self.closeTimer(self.action_timer)
                self.action_timer.start(self.action_time)
        else:
            self.closeTimer(self.action_timer)
            self.action_timer.start(self.action_time)
                            
    
    #读取json文件
    def loadJson(self):
        with open(self.__json_path,"rb") as f:
            self.actions = json.load(f)
        self.routine_act=[]
        self.click_act=[]
        for action in self.actions:
            if "action" in action:
                self.routine_act.append(self.actions[action])
            if "click" in action:
                self.click_act=self.actions[action]
            if "radomTime" in action:
                self.old_act_time = self.action_time
                self.action_time = int(self.actions[action])
        self.__image_path=self.actions["route"]
        self.json_before = os.stat(self.__json_path).st_mtime
    
    #检测json文件
    def monitorJson(self):
       if not (os.stat(self.__json_path).st_mtime == self.json_before):
            self.loadJson()
            if "action" in self.current_action:
                self.action_size=len(self.current_action["action"])
            if self.old_act_time != self.action_time:
                self.action_timer.start(self.action_time)
    
    #开始动作
    def startAction(self):
        if not self.is_fixed_action and len(self.routine_act) > 0:
            self.action_start=True
            self.randomAct()
    
    #动作参数初始化
    def initAct(self):
        #print("init action")
        #随机动作初始化
        self.action_start=False
        self.action_point=0
        #随机动画
        self.is_action=False
        self.action_size=0
        self.random_routine=0
        
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
            self.writeTextFromJson(self.current_action,1)
            self.flame(self.current_action["action"],len(self.current_action["action"]),False) 
            #print(self.current_action)
            if self.current_action["name"] == "walk" or self.current_action["name"] == "fly" or self.current_action["name"] == "flydown":
                self.movePet(int(self.current_action["move"][0]),int(self.current_action["move"][1]))
    
    #固定动作
    def fixedAct(self,images):
        if self.action_start:
            self.initAct()
        self.flame(images,len(images),True)
            
    
    #动画
    def flame(self,image,size,loop):
        #print(self.action_point,size)
        if self.action_point>=size:
            self.action_point=0
            if self.flyDown():
                return
            self.is_action=False
            self.action_start=False
            self.timer.stop()
            if not loop:
                return True
        self.setImage(image[self.action_point])
        self.action_point+=1
        return False
    
    #飞行
    def flyDown(self):
        if "name" in self.current_action and self.current_action["name"] == "fly":
            self.current_action = self.current_action["down"]
            self.action_size=len(self.current_action["action"])
            self.timer.start(int(self.current_action["time"]))
            return True
        return False
    
    #移动
    def movePet(self,xPoint,yPoint):
        screen_geo = QDesktopWidget().screenGeometry()
        pet_geo = self.geometry()
        x = pet_geo.x() + xPoint
        y = pet_geo.y() + yPoint
        #print(pet_geo.width(),pet_geo.height())
        #print(pet_geo.x(),pet_geo.y(), xPoint,yPoint)
        #print(x,y,screen_geo.width() - self.image_width,screen_geo.height() - self.image_height )
        if self.x() < 0 or self.y() < 0 or x + self.width() >= screen_geo.width() or y + self.height() >= screen_geo.height():
            return False
        self.move(x,y)
        return True
    
    #退出程序
    def appQuit(self):
        self.close()
        sys.exit(0)
        
        
        
'''run'''
if __name__ == '__main__':
    #notification = Notify()
    #notification.title = "Cool Title"
    #notification.message = "Even cooler message."
    #notification.send()
    app = QApplication(sys.argv)
    pet = DesktopPet()
    sys.exit(app.exec_())