import sys, os, json, requests, subprocess, threading
import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
from pathlib import Path

version_list = []

class BuildToolsGui(qtw.QMainWindow):

    working_directory = Path().absolute()
    file_manager = None
    q_progressbar = None
    q_version_list = None
    q_command_output = None
    button_build = None
    button_cancel = None
    process = None

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

        self.button_build = qtw.QPushButton('Build')
        self.button_build.clicked.connect(lambda: self.prepare_build())

        self.button_cancel = qtw.QPushButton('Cancel')
        self.button_cancel.clicked.connect(lambda: self.cancel_process())
        self.button_cancel.hide()

        self.q_progressbar = qtw.QProgressBar(self)
        self.q_progressbar.setGeometry(30, 40, 200, 25)
        self.q_progressbar.hide()

        self.q_command_output = qtw.QTextEdit()
        self.q_command_output.setReadOnly(True)
        self.q_command_output.hide()

        self.setCentralWidget(label_choose_version)
        layout.addWidget(label_choose_version)
        layout.addWidget(self.q_version_list)
        layout.addWidget(self.button_build)
        layout.addWidget(self.button_cancel)
        layout.addWidget(self.q_progressbar)
        layout.addWidget(self.q_command_output)
        layout.addStretch()

        container = qtw.QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def threading_build(self):
        threading.Thread(target=self.build, daemon=True).start()

    def cancel_process(self):
        print(self.process)
        if self.process is not None:
            self.process.kill()
            self.process = None
            self.button_build.setDisabled(False)
            self.q_command_output.clear()
            show_message(qtw.QMessageBox.Information, 'Process canceled', 'The installation has been cancel', False)

    def build(self):
        version = self.q_version_list.currentText()
        self.process = subprocess.Popen(f'java -jar BuildTools.jar --rev {version}', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd='./output')
        for line in self.process.stdout:
            self.q_command_output.append(line.decode('utf-8'))
            self.q_command_output.ensureCursorVisible()

    def prepare_build(self):
        self.working_directory = Path().absolute()
        if self.file_manager.has_build_tools():
             self.q_command_output.show()
             self.button_cancel.show()
             self.threading_build()
             self.button_build.setDisabled(True)  
        else:
            response = show_message(qtw.QMessageBox.Question, 'Missing jar', 'You don\'t have BuildTools.jar in your current directory.\n Do you want to download the last version of Buildtools.jar?', True)

            if response == qtw.QMessageBox.Yes:
                self.file_manager.download_jar(self.working_directory, self.q_progressbar)

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