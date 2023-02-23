import sys
import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc

version_list = []

class BuildToolsGui(qtw.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("BuildToolsGui")
        self.setFixedSize(700, 300)
        self.set_ui()
        self.show()

    def set_ui(self):
        layout = qtw.QVBoxLayout()

        label_choose_version = qtw.QLabel('Choose your version :')
        label_choose_version.setAlignment(qtc.Qt.AlignCenter)

        self.q_version_list = qtw.QComboBox()
        for version in version_list:
            self.q_version_list.addItem(version)

        button_build = qtw.QPushButton('Build')
        button_build.clicked.connect(lambda: self.prepare_build())

        self.q_progressbar = qtw.QProgressBar(self)
        self.q_progressbar.setGeometry(30, 40, 200, 25)
        self.q_progressbar.hide()

        self.q_command_output = qtw.QTextEdit()
        self.q_command_output.setReadOnly(True)
        self.q_command_output.hide()

        self.setCentralWidget(label_choose_version)
        layout.addWidget(label_choose_version)
        layout.addWidget(self.q_version_list)
        layout.addWidget(button_build)
        layout.addWidget(self.q_progressbar)
        layout.addWidget(self.q_command_output)
        layout.addStretch()

        container = qtw.QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

def start():
        app = qtw.QApplication(sys.argv)
        window = BuildToolsGui()
        app.exec()

start()