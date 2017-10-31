# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import queue
import pytz
from datetime import datetime

import cv2
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from ui import *
from utils.log import logger
from utils.utils import np2qimage

videoCapture = cv2.VideoCapture(0)
videoCapture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
videoCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
timezone = pytz.timezone('Asia/Shanghai')


class ToolBar(QToolBar):
    def __init__(self, title):
        super(ToolBar, self).__init__(title)
        layout = self.layout()
        m = (0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setContentsMargins(*m)
        self.setContentsMargins(*m)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

    def addAction(self, action):
        if isinstance(action, QWidgetAction):
            return super(ToolBar, self).addAction(action)
        btn = QToolButton()
        btn.setDefaultAction(action)
        btn.setToolButtonStyle(self.toolButtonStyle())
        self.addWidget(btn)


class struct(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def newIcon(icon):
    return QIcon(':/' + icon)


def addActions(widget, actions):
    for action in actions:
        if action is None:
            widget.addSeparator()
        elif isinstance(action, QMenu):
            widget.addMenu(action)
        else:
            widget.addAction(action)


def newAction(parent, text, slot=None, shortcut=None, icon=None,
              tip=None, checkable=False, enabled=True):
    """Create a new action and assign callbacks, shortcuts, etc."""
    a = QAction(text, parent)
    if icon is not None:
        a.setIcon(newIcon(icon))
    if shortcut is not None:
        if isinstance(shortcut, (list, tuple)):
            a.setShortcuts(shortcut)
        else:
            a.setShortcut(shortcut)
    if tip is not None:
        a.setToolTip(tip)
        a.setStatusTip(tip)
    if slot is not None:
        a.triggered.connect(slot)
    if checkable:
        a.setCheckable(True)
    a.setEnabled(enabled)
    return a


def centreLayoutWarp(widget):
    layout = QHBoxLayout()
    layout.addWidget(widget, 0, Qt.AlignHCenter)
    return layout


def subHLayout(add_list):
    layout = QHBoxLayout()
    for item in add_list:
        if isinstance(item, QWidget):
            layout.addWidget(item)
        elif item == 'stretch':
            layout.addStretch()
    return layout


class MovableFrame(QFrame):
    def __init__(self, parent=None):
        super(MovableFrame, self).__init__(parent)
        self._mousePressPos = None
        self._mouseMovePos = None

    def mousePressEvent(self, event):
        self._mousePressPos = None
        self._mouseMovePos = None
        if event.button() == Qt.LeftButton:
            self._mousePressPos = event.globalPos()
            self._mouseMovePos = event.globalPos()

        super(MovableFrame, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self._mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            self.move(newPos)
            self._mouseMovePos = globalPos

        super(MovableFrame, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._mousePressPos is not None:
            moved = event.globalPos() - self._mousePressPos
            if moved.manhattanLength() > 3:
                event.ignore()
                return


class ImageWidget(QFrame):
    def __init__(self, pixmap=None, parent=None, min_size=QSize(128, 128),
                 margin=5):
        super(ImageWidget, self).__init__(parent)
        self.default_pixmap = QPixmap('images/head.png')
        self.pixmap = pixmap
        self.imageLabel = QLabel()
        self.imageLabel.setMinimumSize(min_size)
        self.imageLabel.setMaximumSize(QSize(128, 128))
        layout = QHBoxLayout()
        layout.setContentsMargins(margin, margin, margin, margin)
        layout.addWidget(self.imageLabel)
        self.setLayout(layout)
        self.setStyleSheet('''
        QLabel {
        border-top: 2px solid rgb(255, 255, 255, 180);
        border-left: 2px solid rgb(255, 255, 255, 180);
        border-right: 2px solid rgb(255, 255, 255, 180);
        border-bottom: 2px solid rgb(255, 255, 255, 180);
        border-radius: 6px
        }
        ''')

    def paintEvent(self, event):
        self.updateImage()
        super(ImageWidget, self).paintEvent(event)

    def updateImage(self):
        if self.pixmap:
            show_map = self.pixmap.copy()
        else:
            show_map = self.default_pixmap.copy()
        size = self.imageLabel.width() - 2
        show_map = show_map.scaledToWidth(size,
                                          Qt.SmoothTransformation)
        self.imageLabel.setPixmap(show_map)


class NoticeWidget(MovableFrame):
    def __init__(self, parent=None):
        super(NoticeWidget, self).__init__(parent)
        self.ui = UI_NoticeWidget()
        self.ui.setupUI(self)


class DatetimeWidget(MovableFrame):
    def __init__(self, parent=None):
        super(DatetimeWidget, self).__init__(parent)
        self.ui = UI_DatetimeWidget()
        self.ui.setupUI(self)

        self.timer = QTimer()
        self.timer.setInterval(200)
        self.start_timer()
        self.timer.timeout.connect(self.updateDatetime)


    def start_timer(self):
        logger.debug('{}: start timer'.format(self.__class__))
        self.timer.start()

    def stop_timer(self):
        logger.debug('{}: stop timer'.format(self.__class__))
        self.timer.stop()

    def updateDatetime(self):
        now = timezone.localize(datetime.now())
        time_now = '{:02d}:{:02d}:{:02d}'.format(
            now.hour, now.minute, now.second)
        date_now = '{}年{}月{}日'.format(now.year, now.month, now.day)
        self.ui.timeLabel.setText(time_now)
        self.ui.dateLabel.setText(date_now)


class TableWidget(MovableFrame):
    def __init__(self, parent=None):
        super(TableWidget, self).__init__(parent)
        self.ui = UI_TableWidget()
        self.ui.setupUI(self)

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.start_timer()
        self.timer.timeout.connect(self.updateState)

    def start_timer(self):
        logger.debug('{}: start timer'.format(self.__class__))
        self.timer.start()

    def stop_timer(self):
        logger.debug('{}: stop timer'.format(self.__class__))
        self.timer.stop()

    def getAccessNum(self):
        # TODO: add update Access fun
        num = 2
        return num

    def updateAccessNum(self):
        num = self.getAccessNum()
        if num is not None:
            self.ui.label.setText('今日到访人数： {}'.format(num))

    def getTableData(self):
        # TODO: add update table data fun
        data = [['test1', '00:00:00'], ['test2', '00:00:00']]
        return data

    def updateTable(self):
        table_data = self.getTableData()
        if table_data is not None:
            get_len = len(table_data)
            for i in range(self.ui.table.rowCount()):
                name_item = self.ui.table.item(i, 0)
                time_item = self.ui.table.item(i, 1)
                if i < get_len:
                    name_item.setText(table_data[i][0])
                    time_item.setText(table_data[i][1])
                else:
                    name_item.setText('')
                    time_item.setText('')

    def updateState(self):
        self.updateAccessNum()
        self.updateTable()


class WelcomeWidget(MovableFrame):
    def __init__(self, parent=None, width=400, height=300):
        super(WelcomeWidget, self).__init__(parent)
        self.ui = UI_WelcomeWidget()
        self.ui.setupUI(self)

        self.animation = QPropertyAnimation(self, b'size')
        self.animation.setDuration(200)
        self.animation.setStartValue(QSize(20, 20))
        self.animation.setEndValue(QSize(self.ui.default_width,
                                         self.ui.default_height))
        self.detect_activate = True
        self.detect_queue = queue.Queue(10)

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.start_timer()
        self.timer.timeout.connect(self.updateState)
        self.animation.finished.connect(self.after_animation)

    def start_timer(self):
        logger.debug('{}: start timer'.format(self.__class__))
        self.timer.start()

    def stop_timer(self):
        logger.debug('{}: stop timer'.format(self.__class__))
        self.timer.stop()

    def updateDetection(self):
         # TODO: modify update detection fun
        if self.detect_activate and not self.detect_queue.full():
            self.detect_queue.put(['test 20岁', None])

    def updateState(self):
        self.updateDetection()
        logger.debug('detect_activate: {}'.format(self.detect_activate))
        if not self.detect_queue.empty():
            self.detect_activate = False
            detect_data = self.detect_queue.get()
            logger.debug('detect_data: {}'.format(detect_data))
            self.ui.infoLabel.setText(detect_data[0])
            if detect_data[1] is None:
                self.ui.image.pixmap = None
            else:
                self.ui.image.pixmap = QPixmap(detect_data[1])
            self.show()
            self.animation.start()

    def after_animation(self):
        QTimer.singleShot(1500, self.after_action)

    def after_action(self):
        self.hide()
        QTimer.singleShot(1000, self.after_hide)

    def after_hide(self):
        self.detect_activate = True


class WindowMixin(object):
    def menu(self, title, actions=None):
        menu = self.menuBar().addMenu(title)
        if actions:
            addActions(menu, actions)
        return menu

    def toolbar(self, title, actions=None):
        toolbar = ToolBar(title)
        toolbar.setObjectName(u'%sToolBar' % title)
        # toolbar.setOrientation(Qt.Vertical)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        if actions:
            addActions(toolbar, actions)
        self.addToolBar(Qt.BottomToolBarArea, toolbar)
        return toolbar


class MainWindow(QMainWindow, WindowMixin):
    def __init__(self, parent=None, debug=False):
        QWidget.__init__(self, parent)
        self.setMinimumSize(800, 600)
        self.resize(800, 600)
        self._painter = QPainter()
        self.pixmap = QPixmap('test.jpg')
        self.setWindowIcon(QIcon('images/main.png'))

        self.notice = NoticeWidget(self)
        self.datetime = DatetimeWidget(self)
        self.table = TableWidget(self)
        self.welcome = WelcomeWidget(self)
        self.welcome.close()
        self.notice.move(25, 200)
        self.datetime.move(580, 235)
        self.table.move(260, 100)
        self.videoTimer = QTimer()
        self.videoTimer.setInterval(40)
        self.start_timer()

        self.videoTimer.timeout.connect(self.updateCamera)

    def start_timer(self):
        logger.debug('{}: start timer'.format(self.__class__))
        self.videoTimer.start()

    def stop_timer(self):
        logger.debug('{}: stop timer'.format(self.__class__))
        self.videoTimer.stop()

    def updateCamera(self):
        b, frame = videoCapture.read()
        if frame is not None:
            qImg = np2qimage(frame, mode='bgr')
            self.pixmap = QPixmap(qImg)
            self.update()

    def paintEvent(self, ev):
        if self.isEnabled():
            p = self._painter
            p.begin(self)
            p.setRenderHint(QPainter.Antialiasing)
            p.setRenderHint(QPainter.HighQualityAntialiasing)
            p.setRenderHint(QPainter.SmoothPixmapTransform)

            bg_pixmap = QPixmap(self.width(), self.height())
            bg_pixmap.fill(Qt.black)
            p.drawPixmap(0, 0, bg_pixmap)
            scale = self.width() / self.pixmap.width()
            # print(scale)
            p.scale(scale, scale)
            p.translate(self.offsetToCenter(
                self.pixmap.width(), self.pixmap.height()))
            p.drawPixmap(0, 0, self.pixmap)
            p.end()

            off_set = self.offsetToCenter(
                self.welcome.width(), self.welcome.height(), scale=False)
            self.welcome.move(int(off_set.x()), int(off_set.y()))

    def mousePressEvent(self, event):
        focused_widget = QApplication.focusWidget()
        if isinstance(focused_widget, QTextEdit):
            focused_widget.clearFocus()
        super(MainWindow, self).mousePressEvent(event)

    def offsetToCenter(self, width, height, scale=True):
        s = 1
        if scale:
            s = self.width() / width
        area = super(MainWindow, self).size()
        w, h = width * s, height * s
        aw, ah = area.width(), area.height()
        x = (aw-w)/(2*s) if aw > w else 0
        y = (ah-h)/(2*s) if ah > h else 0
        return QPointF(x, y)