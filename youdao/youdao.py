import random
import sys
import os
import http.client
import hashlib
import urllib
import random
import json

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QPlainTextEdit, QDesktopWidget, QTextEdit, QGridLayout, QPushButton, QMessageBox,
                             QLabel, QMainWindow, QVBoxLayout, QWidget, QSystemTrayIcon, QMenu, QAction, QDialog)


appKey = '2634c6f9069d9715'  # 网易云翻译api
secretKey = 'K3hbukgfqM7E16SqqQf8TIT08zeWQd3e'  # 请不要乱用
baseDir = os.path.dirname(__file__)
dictFileName = os.path.join(baseDir, 'OxfordEnDict.txt')


def translate(q='good', fromLang='auto', toLang='auto'):
    httpClient = None
    myurl = '/api'
    salt = random.randint(1, 65536)
    sign = appKey + q + str(salt) + secretKey
    m1 = hashlib.md5()
    m1.update(sign.encode())
    sign = m1.hexdigest()
    myurl = '{}?appKey={}&q={}&from={}&to={}&salt={}&sign={}'.format(
        myurl, appKey, urllib.parse.quote(q), fromLang, toLang, str(salt), sign)

    try:
        httpClient = http.client.HTTPConnection('openapi.youdao.com')
        httpClient.request('GET', myurl)
        # response是HTTPResponse对象
        response = httpClient.getresponse()
        data = json.loads(response.read().decode('utf-8'))
        return data

    except Exception as e:
        print(e)

    finally:
        if httpClient:
            httpClient.close()


def localtran(q='good', fromLang='auto', toLang='auto'):
    with open(dictFileName) as file:
        for line in file:
            if line:
                li = line.split()
                if li[0] == q:
                    return li[0], li[1]
    return None, None


class YouDao(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def iconActivated(self, reason):
        # reason 没有 QSystemTrayIcon.DoubleClick
        if self.isHidden():
            self.show()
        else:
            self.hide()

    def closeEvent(self, event):
        self.hide()
        event.ignore()

    def open(self):
        self.show()

    def clearTextClicked(self):
        self.textEdit.clear()
        self.preview.clear()

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Return:
            self.confirmClicked()
        else:
            super(YouDao, self).keyPressEvent(event)

    def confirmClicked(self):
        q = self.textEdit.toPlainText()
        # 要翻译的内容为空
        if not q.strip():
            alert = QMessageBox(self)
            alert.setText("你什么也没有输入！！！")
            alert.exec()
            return
        data = translate(q)
        # 没有数据就用本地词典
        if not data:
            key, value = localtran(q)
            if key and value:
                self.preview.setHtml('<i>翻译：</i>{}'.format(value))
            else:
                alert = QMessageBox(self)
                alert.setText("出错了")
                alert.exec()
            return

        usPhonetic = ''
        ukPhonetic = ''
        translation = ''
        web = ''

        html = '''
                   <html>
                        <head></head>
                        <body>
                            <p>{translation}</p>
                            {uk-phonetic}
                            {us-phonetic}
                            {web}
                        </body>
                   </html>
               '''
        if data.get('translation'):
            translation = '<i>翻译：</i>' + \
                ''.join(data.get('translation')) + '<br>'

        if data.get('basic'):
            translation += '<br>'.join(data.get('basic').get('explains'))
            if data.get('basic').get('us-phonetic'):
                usPhonetic = '<h6>英音：<span>[{}]</span></h6>'.format(
                    data.get('basic').get('us-phonetic'))
            if data.get('basic').get('uk-phonetic'):
                ukPhonetic = '<h6>美音：<span>[{}]</span></h6>'.format(
                    data.get('basic').get('uk-phonetic'))

        if data.get('web'):
            web = '网络释义：' + '<br>'.join(','.join(value.get('value'))
                                        for value in data.get('web'))

        values = {
            'translation': translation,
            'us-phonetic': usPhonetic,
            'uk-phonetic': ukPhonetic,
            'web': web
        }

        self.preview.setHtml(html.format(**values))

    def initUI(self):
        # 系统托盘
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(QIcon(os.path.join(baseDir, "youdao.png")))

        self.openAction = QAction(
            QIcon(os.path.join(baseDir, "search.png")), "查单词", self)
        self.openAction.triggered.connect(self.open)
        self.settingAction = QAction(
            QIcon(os.path.join(baseDir, "setting.png")), "设置", self)
        self.quitAction = QAction("退出", self)
        self.quitAction.triggered.connect(QCoreApplication.quit)
        self.qMenu = QMenu(self)
        self.qMenu.addAction(self.openAction)
        self.qMenu.addAction(self.settingAction)
        self.qMenu.addSeparator()
        self.qMenu.addAction(self.quitAction)

        self.trayIcon.setContextMenu(self.qMenu)
        self.trayIcon.activated[QSystemTrayIcon.ActivationReason].connect(
            self.iconActivated)

        self.centralWidget = QWidget(self)

        self.header = QWidget(self)
        self.textEdit = QPlainTextEdit(self.header)
        self.textEdit.setPlaceholderText('请输入')
        self.textEdit.setStyleSheet(
            "QWidget{font-size: 18px;background: #f2f2f2}")

        def enterKeyPressEvent(event):

            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.confirmClicked()
            else:
                QPlainTextEdit.keyPressEvent(self.textEdit, event)
        # 重写QPlainTextEdit的enter事件，enter确认
        self.textEdit.keyPressEvent = enterKeyPressEvent

        self.clearText = QPushButton("清除")
        self.clearText.setStyleSheet("QPushButton{background: #ffffff;}")
        self.clearText.clicked.connect(self.clearTextClicked)
        self.confirm = QPushButton("翻译")
        self.confirm.clicked.connect(self.confirmClicked)
        self.confirm.setStyleSheet(
            "QPushButton{background: #e02433;color: #ffffff}")

        grid = QGridLayout()
        grid.setSpacing(5)
        grid.setContentsMargins(0, 0, 0, 0)
        # 控件， 第几行，第几列，占几行，占几列
        grid.addWidget(self.textEdit, 0, 0, 1, 2)
        grid.addWidget(self.clearText, 1, 0, 1, 1)
        grid.addWidget(self.confirm, 1, 1, 1, 1)
        self.header.setLayout(grid)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText('这里什么都没有。。。')

        self.hbox = QVBoxLayout(self.centralWidget)
        self.hbox.setContentsMargins(6, 6, 6, 6)

        self.hbox.addWidget(self.header)
        self.hbox.addWidget(self.preview)

        self.hbox.setStretch(0, 1)
        self.hbox.setStretch(1, 2)

        self.setCentralWidget(self.centralWidget)
        self.setWindowTitle('有道词典')
        self.setWindowIcon(QIcon(os.path.join(baseDir, 'youdao.png')))

        self.setFixedSize(350, 400)
        self.center()
        # self.setFocusPolicy(Qt.StrongFocus)
        self.show()
        self.trayIcon.show()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2,
                  (screen.height()-size.height())/2)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('YouDao')
    youdao = YouDao()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
