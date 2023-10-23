import sys
from PySide6.QtWidgets import *
# from PySide6.QtCore import QObject, Slot, Signal
from PySide6.QtCore import QRunnable, Slot, QThreadPool, QEventLoop
import sys
import asyncio
# sys.stdout = open('output.txt','wt', encoding='utf8')
# sys.stderr = open('error.txt','wt', encoding='utf8')

import BlogParser
import CreateComment
import Export
from LoginDialog import LoginDialog

class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.init_UI()
        self.loop = asyncio.get_event_loop()
        dialog = LoginDialog(labels=["id","token"])
        # if dialog.exec() == QDialog.Accepted:
            # id, token = dialog.getInputs()
        id='W1.2.25010157537361170005373651440256024.fIbV3U1xQUa4gxvpTIgqt.1697537393007'
        token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY0NjhkM2FhMTU5N2UzNWRiN2QzYmVjMCIsImlhdCI6MTY5ODA1ODk2NywiZXhwIjoxNjk4NjYzNzY3fQ.nlfrwj89IlnAMeBWQF6g_S4wBaDm-b2z-dch9tJKc6U'
        self.create_comment = CreateComment.CreateComment(token, id)
        # else:
        #     exit()
            
    # async def create_chat(self):
        # await self.create_comment.create_chat()

    def init_UI(self):
        self.id = QLineEdit()
        self.id.setPlaceholderText('ID')

        self.tags = QLineEdit()
        self.tags.setPlaceholderText('태그를 입력해주세요')

        self.target = QLineEdit()
        self.target.setPlaceholderText('가게 이름을 입력해주세요')
        
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(['URL', 'Comment'])

        self.result = QTextEdit()
        self.result.setReadOnly(True)

        self.label = QLabel('')

        self.add_URL_button = QPushButton('링크 추가하기')
        self.add_URL_button.clicked.connect(self.addRow)

        self.delete_URL_button = QPushButton('링크 삭제하기')
        self.delete_URL_button.clicked.connect(self.delRow)

        self.create_comment_button = QPushButton('포스트 생성하기')
        self.create_comment_button.clicked.connect(self.createComments)

        # self.import_button = QPushButton('링크 가져오기')
        # self.import_button.clicked.connect(self.importRows)

        # self.export_button = QPushButton('댓글 내보내기')
        # self.export_button.clicked.connect(self.exportRows)

        self.loading = QProgressBar()

        self.version = QLabel('v1.3.0')

        self.table_widget.cellClicked.connect(self.set_position)
        
        self.threadpool = QThreadPool()
        # self.createCommentsThread = CreateComments()
        # self.createCommentsThread.thread_finished.connect(self.set_comments)

        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout = QVBoxLayout()
        layout.addWidget(self.id)
        layout.addWidget(self.tags)
        layout.addWidget(self.target)
        add_delete_layout = QHBoxLayout()
        add_delete_layout.addWidget(self.add_URL_button)
        add_delete_layout.addWidget(self.delete_URL_button)
        # ex_im_layout = QHBoxLayout()
        # ex_im_layout.addWidget(self.import_button)
        # ex_im_layout.addWidget(self.export_button)
        # layout.addLayout(ex_im_layout)
        layout.addLayout(add_delete_layout)
        layout.addWidget(self.table_widget)
        layout.addWidget(self.label)
        layout.addWidget(self.create_comment_button)
        layout.addWidget(self.result)
        layout.addWidget(self.version)
        self.setLayout(layout)

        self.setWindowTitle('Auto Post')
        self.setGeometry(300, 100, 600, 600)
        self.show()

    def importRows(self):
        # open file dialog
        fname = QFileDialog.getOpenFileName(self, 'Open file', './', '엑셀파일 (*.xlsx *.xls)')
        if fname[0]:
            urls = Export.Import(fname[0])
            for url in enumerate(urls):
                url = url[1]
                row = self.table_widget.rowCount()
                self.table_widget.insertRow(row)
                self.table_widget.setItem(row, 0, QTableWidgetItem(url))
                self.table_widget.setItem(row, 1, QTableWidgetItem(''))

    def exportRows(self):
        fname = QFileDialog.getSaveFileName(self, 'Save file', './', '엑셀파일 (*.xlsx *.xls)')
        rows = self.table_widget.rowCount()
        data = {'URL': [], 'Comment': []}
        for i in range(rows):
            data['URL'].append(self.table_widget.item(i, 0).text())
            data['Comment'].append(self.table_widget.item(i, 1).text())
        Export.Export(fname[0], data)
        self.label.setText('댓글 내보내기 완료')

    def set_position(self, row, col):
        self.position = row

    def delRow(self):
        self.table_widget.removeRow(self.position)

    def addRow(self):
        # open URL input popup
        url, ok = QInputDialog.getText(self, '포스트 URL을 입력해주세요', 'Enter URL:')

        if ok:
            # check URL is valid
            if not url.startswith('https://blog.naver.com/'):
                self.label.setText('URL이 유효하지 않습니다.')
                return
            # check URL is already in table
            for i in range(self.table_widget.rowCount()):
                if url == self.table_widget.item(i, 0).text():
                    self.label.setText('URL이 이미 있습니다.')
                    return
            # add new row
            row = self.table_widget.rowCount()
            self.table_widget.insertRow(row)

            # add url
            self.table_widget.setItem(row, 0, QTableWidgetItem(url))

            # add comment
            self.table_widget.setItem(row, 1, QTableWidgetItem(''))

    def createComments(self):
        self.label.setText('댓글 생성 중...')
        self.add_URL_button.setEnabled(False)
        self.delete_URL_button.setEnabled(False)
        self.create_comment_button.setEnabled(False)

        self.set_comments()

    def set_comments(self):
        rows = self.table_widget.rowCount()
        try:
            futures = [asyncio.ensure_future(self.create_comment.summary(self.target.text(), BlogParser.blog_parser(self.table_widget.item(i, 0).text()))) for i in range(rows)]
            print("start: ", futures)
            summaries = self.loop.run_until_complete(asyncio.gather(*futures))
            text = ""
            for index, summary in enumerate(summaries):
                self.table_widget.setItem(index, 1, QTableWidgetItem(summary))
                text += summary + "\n"
            print("end: ", futures)
            print("text: ", text)
            result = self.loop.run_until_complete(self.create_comment.post(self.id.text(), self.target.text(), self.tags.text(), text))
            self.result.setPlainText(result)
            
        except Exception as e:
            self.label.setText(str(e))
        self.label.setText('댓글 생성 완료')
        self.add_URL_button.setEnabled(True)
        self.delete_URL_button.setEnabled(True)
        self.create_comment_button.setEnabled(True)

    def set_error(self, error):
        self.label.setText(error)
        self.add_URL_button.setEnabled(True)
        self.delete_URL_button.setEnabled(True)
        self.create_comment_button.setEnabled(True)

    def closeEvent(self, QCloseEvent):
        # self.loop.run_until_complete(self.create_comment.delete_chat(None))
        self.loop.close()  

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())