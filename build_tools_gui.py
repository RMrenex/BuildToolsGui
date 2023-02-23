import json
import os
from pathlib import Path
import sys, requests
import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc

version_list = []

class BuildToolsGui(qtw.QMainWindow):

    working_directory = Path().absolute()
    file_manager = None
    q_progressbar = None
    q_version_list = None
    q_command_output = None

    def __init__(self):
        super().__init__()
        self.file_manager = FileManager()
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

class FileManager():

    def init_version(self):
        with open('version.json', 'r') as json_file:
            list = json.load(json_file)
            for line in list:
                version_list.append(line['version'])
    
    def download_jar(self, path: Path, q_progressbar: qtw.QProgressBar):
        self.create_output_directory()
        saved_file = f'{path}\output\BuildTools.jar'
        response = requests.get('https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar', stream=True)
        total = int(response.headers.get('content-length', 0))

        q_progressbar.show()
        q_progressbar.setMaximum(total - 1)

        if response.status_code == 200:
            
            with open(saved_file, 'wb') as file:
                for data in response.iter_content(chunk_size=1024):
                    size = file.write(data)
                    q_progressbar.setValue(q_progressbar.value() + size)
            q_progressbar.hide()
            show_message(qtw.QMessageBox.Information, 'Download success', 'BuildTools.jar has been correctly download.', False)
            

    def has_build_tools(self):
        return os.path.isfile('./output/BuildTools.jar')

    def create_output_directory(self):
        os.makedirs('./output', exist_ok=True)

def show_message(icon: qtw.QMessageBox, title: str, text: str, have_buttons: bool):

    q_message = qtw.QMessageBox()
    q_message.setIcon(icon)
    q_message.setWindowTitle(title)
    q_message.setText(text)

    if have_buttons:
        q_message.setStandardButtons(qtw.QMessageBox.Yes | qtw.QMessageBox.No)
            
    return q_message.exec()

def start():
        file_manager = FileManager()
        file_manager.init_version()
        app = qtw.QApplication(sys.argv)
        window = BuildToolsGui()
        app.exec()

start()