# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


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


class UI_NoticeWidget(object):
    def setupUI(self, form: QFrame):
        form.setObjectName('NoticeWidget')
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel('今日公告')
        self.label.setObjectName('Label')
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumHeight(30)
        self.text = QTextEdit()
        self.text.setObjectName('Text')
        layout.addWidget(self.label)
        layout.addWidget(self.text)
        form.resize(200, 200)
        form.setLayout(layout)

        form.setStyleSheet(
            '''
            #NoticeWidget {
            background-color: rgb(0, 180, 51, 200);
            border-top: 2px solid rgb(0, 200, 51, 230);
            border-left: 2px solid rgb(0, 200, 51, 230);
            border-right: 2px solid rgb(0, 150, 51, 230);
            border-bottom: 2px solid rgb(0, 150, 51, 230);
            }
            #NoticeWidget:hover {
            border: 2px solid rgb(220, 220, 220, 230);
            }
            #Label {
            color: white;
            font-size: 18px;
            font-style: bold;
            background-color:rgb(0, 153, 51, 230);
            }
            #Text {
            background-color: rgb(0, 0, 0, 0);
            color: white;
            font-size: 16px;
            border: 0px;
            }
            '''
        )


class UI_DatetimeWidget(object):
    def setupUI(self, form: QFrame):
        layout = QVBoxLayout()
        form.setObjectName('DatetimeWidget')
        self.timeLabel = QLabel('0:00')
        self.dateLabel = QLabel('2000年1月1日')
        self.timeLabel.setAlignment(Qt.AlignCenter)
        self.dateLabel.setAlignment(Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.timeLabel)
        layout.addWidget(self.dateLabel)
        layout.addStretch()
        form.resize(200, 140)
        form.setLayout(layout)

        form.setStyleSheet(
            '''
            #DatetimeWidget {
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
            #DatetimeWidget:hover {
            border: 2px solid rgb(220, 220, 220, 230);
            }
            '''
        )


class UI_TableWidget(object):
    def setupUI(self, form: QFrame):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        form.setObjectName('TableWidget')
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
        form.resize(300, 400)
        form.setLayout(layout)

        form.setStyleSheet(
            '''
            #TableWidget {
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
            #TableWidget:hover {
            border: 2px solid rgb(220, 220, 220, 230);
            }
            '''
        )

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


class UI_WelcomeWidget(object):
    default_width = 400
    default_height = 300

    def setupUI(self, form: QFrame):
        layout = QVBoxLayout()
        form.setObjectName('WelcomeWidget')
        self.camLabel = QLabel()
        self.camLabel.setMaximumHeight(30)
        self.camLabel.setPixmap(QPixmap('images/cam.png').scaledToHeight(
            self.camLabel.height(), Qt.SmoothTransformation
        ))
        self.camLabel.setAlignment(Qt.AlignCenter)
        self.image = ImageWidget()
        self.infoLabel = QLabel('test 18岁')
        self.infoLabel.setObjectName('InfoLabel')
        self.infoLabel.setAlignment(Qt.AlignCenter)
        self.welcomeLabel = QLabel('欢迎光临')
        self.welcomeLabel.setObjectName('WelcomeLabel')
        self.welcomeLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.camLabel)
        layout.addWidget(self.image)
        layout.addWidget(self.infoLabel)
        layout.addStretch()
        layout.addWidget(self.welcomeLabel)
        layout.addStretch()

        effect = QGraphicsDropShadowEffect()
        effect.setOffset(0, 0)
        effect.setBlurRadius(30)
        form.setGraphicsEffect(effect)
        form.resize(self.default_height, self.default_height)
        form.setLayout(layout)

        form.setStyleSheet(
            '''
            #WelcomeWidget {
            background-color: rgb(51, 180, 255, 255);
            border-top: 3px solid rgb(51, 200, 255, 255);
            border-left: 3px solid rgb(51, 200, 255, 255);
            border-right: 3px solid rgb(51, 150, 255, 255);
            border-bottom: 3px solid rgb(51, 150, 255, 255);
            }
            #InfoLabel {
            color: white;
            font-size: 14px;
            }
            #WelcomeLabel {
            color: white;
            font-size: 22px;
            font-style: bold;
            }
            '''
        )
