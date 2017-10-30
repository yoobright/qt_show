# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import sys
import os
import time
import cv2
import traceback
import logging
import pytz
from datetime import datetime

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from utils.log import logger
from utils.utils import np2qimage

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

if sys.version_info[0] >= 3:
    from io import StringIO
else:
    from StringIO import StringIO


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
        border-top: 1px solid rgb(200, 200, 200, 180);
        border-left: 1px solid rgb(200, 200, 200, 180);
        border-right: 1px solid rgb(0, 0, 0, 100);
        border-bottom: 1px solid rgb(0, 0, 0, 100);
        border-radius: 6px
        }
        ''')

    def resizeEvent(self, event):
        self.updateImage()

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
        self.setObjectName('top')
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel('今日公告')
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumHeight(30)
        self.text = QTextEdit()
        layout.addWidget(self.label)
        layout.addWidget(self.text)
        self.resize(200, 200)
        self.setLayout(layout)

        # effect = QGraphicsDropShadowEffect()
        # effect.setBlurRadius(0)
        # effect.setColor(QColor("#000000"))
        # effect.setOffset(1, 1)
        # self.label.setGraphicsEffect(effect)

        self.setStyleSheet(
            '''
            #top {
            background-color: rgb(0, 180, 51, 200);
            border-top: 2px solid rgb(0, 200, 51, 230);
            border-left: 2px solid rgb(0, 200, 51, 230);
            border-right: 2px solid rgb(0, 150, 51, 230);
            border-bottom: 2px solid rgb(0, 150, 51, 230);
            }
            #top:hover {
            border: 2px solid rgb(220, 220, 220, 230);
            }
            '''
        )
        self.text.setStyleSheet(
            '''
            background-color: rgb(0, 0, 0, 0);
            color: white;
            font-size: 16px;
            border: 0px;
            '''
        )
        self.label.setStyleSheet(
            '''
            color: white;
            font-size: 18px;
            font-style: bold;
            background-color:rgb(0, 153, 51, 230)
            '''
        )


class DatetimeWidget(MovableFrame):
    def __init__(self, parent=None):
        super(DatetimeWidget, self).__init__(parent)
        layout = QVBoxLayout()
        self.setObjectName('top')
        self.timeLabel = QLabel('0:00')
        self.dateLabel = QLabel('2000年1月1日')
        self.timeLabel.setAlignment(Qt.AlignCenter)
        self.dateLabel.setAlignment(Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.timeLabel)
        layout.addWidget(self.dateLabel)
        layout.addStretch()
        self.resize(200, 140)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.setInterval(200)
        self.start_timer()
        self.timer.timeout.connect(self.updateDatetime)

        self.setStyleSheet(
            '''
            #top {
            background-color: rgb(51, 180, 255, 200);
            border-top: 2px solid rgb(51, 200, 255, 230);
            border-left: 2px solid rgb(51, 200, 255, 230);
            border-right: 2px solid rgb(51, 150, 255, 230);
            border-bottom: 2px solid rgb(51, 150, 255, 230);
            }
            QLabel {
            color: white;
            font-size: 22px;
            font-style: bold;
            }
            #top:hover {
            border: 2px solid rgb(220, 220, 220, 230);
            }
            '''
        )

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
        self.timeLabel.setText(time_now)
        self.dateLabel.setText(date_now)


class TableWidget(MovableFrame):
    def __init__(self, parent=None):
        super(TableWidget, self).__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setObjectName('top')
        self.label = QLabel('今日到访人数： 0')
        self.label.setMaximumHeight(30)
        self.table = QTableWidget()
        self.init_table()
        down_layout = QHBoxLayout()
        down_layout.addStretch()
        down_layout.addWidget(self.table)
        down_layout.addStretch()
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        layout.addLayout(down_layout)
        # layout.addStretch()
        self.resize(300, 400)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.start_timer()
        self.timer.timeout.connect(self.updateState)

        self.setStyleSheet(
            '''
            #top {
            background-color: rgb(255, 102, 51, 200);
            border-top: 2px solid rgb(250, 123, 80, 230);
            border-left: 2px solid rgb(250, 123, 80, 230);
            border-right: 2px solid rgb(255, 80, 51, 230);
            border-bottom: 2px solid rgb(255, 80, 51, 230);
            }
            QLabel {
            color: white;
            font-size: 20px;
            font-style: bold;
            background-color:rgb(255, 102, 51, 230)
            }
            QTableWidget {
            color: white;
            gridline-color: rgb(167, 97, 83, 200); 
            border: 5px;
            background-color:rgb(0, 0, 0, 0)
            }
            #top:hover {
            border: 2px solid rgb(220, 220, 220, 230);
            }
            '''
        )

    def start_timer(self):
        logger.debug('{}: start timer'.format(self.__class__))
        self.timer.start()

    def stop_timer(self):
        logger.debug('{}: stop timer'.format(self.__class__))
        self.timer.stop()

    def init_table(self):
        self.table.setMinimumHeight(340)
        self.table.setMaximumWidth(200)
        self.table.setColumnCount(2)
        self.table.setRowCount(10)
        self.table.setHorizontalHeaderLabels(['姓名', '访问时间'])
        # self.table.horizontalHeader().setStretchLastSection(True)
        # self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)
        # self.table.setSelectionBehavior(QAbstractItemView.NoSelection)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        for i in range(self.table.rowCount()):
            for j in range(self.table.colorCount()):
                item = QTableWidgetItem('{}, {}'.format(i, j))
                item.setTextAlignment(Qt.AlignCenter)
                if i % 2 > 0:
                    item.setBackground(QColor(255, 102, 51, 200))
                else:
                    item.setBackground(QColor(193, 108, 91, 200))
                self.table.setItem(i, j, item)
        # .setBackgroundColor(Qt.red);
        self.table.horizontalHeader().setStyleSheet(
            '''
            QHeaderView::section{
            color: white;
            background-color:rgb(255, 102, 51, 230);
            padding: 4px;
            border: 1px solid rgb(167, 97, 83, 200)
            }
            '''
        )

    def getAccessNum(self):
        # TODO: add update Access fun
        return '2'

    def updateAccessNum(self):
        num = self.getAccessNum()
        if num is not None:
            self.label.setText('今日到访人数： {}'.format(num))

    def getTableData(self):
        # TODO: add update table data fun
        return [['test1', '00:00:00'], ['test2', '00:00:00']]

    def updateTable(self):
        table_data = self.getTableData()
        if table_data is not None:
            get_len = len(table_data)
            for i in range(self.table.rowCount()):
                name_item = self.table.item(i, 0)
                time_item = self.table.item(i, 1)
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
    def __init__(self, parent=None):
        super(WelcomeWidget, self).__init__(parent)
        layout = QVBoxLayout()
        self.setObjectName('top')
        self.camLabel = QLabel()
        self.camLabel.setMaximumHeight(30)
        self.camLabel.setPixmap(QPixmap('images/cam.png').scaledToHeight(
            self.camLabel.height(), Qt.SmoothTransformation
        ))
        self.camLabel.setAlignment(Qt.AlignCenter)
        self.image = ImageWidget()
        self.infoLabel = QLabel('test 18岁')
        self.infoLabel.setAlignment(Qt.AlignCenter)
        self.welcomeLabel = QLabel('欢迎光临')
        self.welcomeLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.camLabel)
        layout.addWidget(self.image)
        layout.addWidget(self.infoLabel)
        layout.addStretch()
        layout.addWidget(self.welcomeLabel)
        layout.addStretch()
        self.resize(400, 300)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.start_timer()
        self.timer.timeout.connect(self.updateState)

        self.setStyleSheet(
            '''
            #top {
            background-color: rgb(51, 180, 255, 255);
            border-top: 3px solid rgb(51, 200, 255, 255);
            border-left: 3px solid rgb(51, 200, 255, 255);
            border-right: 3px solid rgb(51, 150, 255, 255);
            border-bottom: 3px solid rgb(51, 150, 255, 255);
            }
            '''
        )
        self.infoLabel.setStyleSheet(
            '''
            color: white;
            font-size: 14px;
            '''
        )

        self.welcomeLabel.setStyleSheet(
            '''
            color: white;
            font-size: 22px;
            font-style: bold;
            '''
        )

    def start_timer(self):
        logger.debug('{}: start timer'.format(self.__class__))
        self.timer.start()

    def stop_timer(self):
        logger.debug('{}: stop timer'.format(self.__class__))
        self.timer.stop()

    def updateState(self):
        # TODO: add update state fun
        pass


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
        self.setWindowTitle('test')
        self.setMinimumSize(800, 600)
        self.resize(800, 600)
        self._painter = QPainter()
        self.pixmap = QPixmap('test.jpg')
        self.setWindowIcon(QIcon('images/main.png'))

        self.notice = NoticeWidget(self)
        self.datetime = DatetimeWidget(self)
        self.table = TableWidget(self)
        self.welcome = WelcomeWidget(self)
        self.welcome.hide()
        self.notice.move(25, 200)
        self.datetime.move(580, 235)
        self.table.move(260, 100)
        self.videoTimer = QTimer()
        self.videoTimer.setInterval(30)
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
        off_set = self.offsetToCenter(
                self.welcome.width(), self.welcome.height(), scale=False)
        self.welcome.move(off_set.x(), off_set.y() )

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
            # print(self.pixmap)
            p.drawPixmap(0, 0, self.pixmap)
            p.end()

    def mousePressEvent(self, event):
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


def excepthook(excType, excValue, tracebackobj):
    """
    Global function to catch unhandled exceptions.

    @param excType exception type
    @param excValue exception value
    @param tracebackobj traceback object
    """
    separator = '-' * 80
    logFile = os.path.join(APP_ROOT, "simple.log")
    notice = \
        """An unhandled exception occurred. Please report the problem\n"""\
        """using the error reporting dialog or via email to <%s>.\n"""\
        """A log has been written to "%s".\n\nError information:\n""" % \
        ("yourmail at server.com", logFile)
    versionInfo = "0.0.1"
    timeString = time.strftime("%Y-%m-%d, %H:%M:%S")

    tbinfofile = StringIO()
    traceback.print_tb(tracebackobj, None, tbinfofile)
    tbinfofile.seek(0)
    tbinfo = tbinfofile.read()
    errmsg = '%s: \n%s' % (str(excType), str(excValue))
    sections = [separator, timeString, separator, errmsg, separator, tbinfo]
    msg = '\n'.join(sections)
    try:
        with open(logFile, "w") as f:
            f.write(msg)
            f.write(versionInfo)
    except IOError:
        pass
    errorbox = QMessageBox()
    errorbox.setText(str(notice)+str(msg)+str(versionInfo))
    errorbox.setWindowTitle(' An Unhandled Exception Occurred')
    errorbox.exec_()

sys.excepthook = excepthook

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        app.setFont(QFont('微软雅黑'))
    except Exception:
        print('load font failed')
    debug = 'debug' in sys.argv
    if debug:
        logger.setLevel(logging.DEBUG)
    logger.info('start main app ...')
    myapp = MainWindow(debug=debug)
    myapp.show()
    sys.exit(app.exec_())