import sys
import requests
import pickle
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox, QMainWindow, QFrame, QGridLayout, QGroupBox, QCheckBox
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt
import json


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dark_mode = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Github Traffic Viewer')
        self.setGeometry(300, 300, 400, 200)

        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)

        mainLayout = QVBoxLayout(self.mainWidget)

        self.tokenGroupBox = QGroupBox("Github Access")
        self.tokenLayout = QGridLayout()
        self.tokenGroupBox.setLayout(self.tokenLayout)

        self.tokenLabel = QLabel("Access Token")
        self.tokenLabel.setFont(QFont('Arial', 10))
        self.tokenEntry = QLineEdit()
        self.tokenEntry.setEchoMode(QLineEdit.Password)
        self.tokenLayout.addWidget(self.tokenLabel, 0, 0)
        self.tokenLayout.addWidget(self.tokenEntry, 0, 1)

        self.usernameLabel = QLabel("Username")
        self.usernameLabel.setFont(QFont('Arial', 10))
        self.usernameEntry = QLineEdit()
        self.tokenLayout.addWidget(self.usernameLabel, 1, 0)
        self.tokenLayout.addWidget(self.usernameEntry, 1, 1)

        self.darkModeButton = QCheckBox("Dark Mode")
        self.darkModeButton.stateChanged.connect(self.toggle_dark_mode)
        self.tokenLayout.addWidget(self.darkModeButton, 2, 0, 1, 2)

        self.viewButton = QPushButton('Get Traffic Data')
        self.viewButton.clicked.connect(self.get_traffic)
        self.viewButton.setFont(QFont('Arial', 10))

        self.resultLabel = QLabel("")
        self.resultLabel.setFont(QFont('Arial', 10))

        mainLayout.addWidget(self.tokenGroupBox)
        mainLayout.addWidget(self.viewButton)
        mainLayout.addWidget(self.resultLabel)

        self.load_credentials()

    def load_credentials(self):
        try:
            with open("save.p", "rb") as f:
                data = pickle.load(f)
                self.tokenEntry.setText(data.get('token', ''))
                self.usernameEntry.setText(data.get('username', ''))
                self.dark_mode = data.get('dark_mode', False)
                self.darkModeButton.setChecked(self.dark_mode)
                self.set_dark_mode()
        except (FileNotFoundError, EOFError):
            pass

    def save_credentials(self):
        data = {'token': self.tokenEntry.text(), 'username': self.usernameEntry.text(), 'dark_mode': self.dark_mode}
        with open("save.p", "wb") as f:
            pickle.dump(data, f)

    def toggle_dark_mode(self):
        self.dark_mode = self.darkModeButton.isChecked()
        self.set_dark_mode()
        self.save_credentials()

    def set_dark_mode(self):
        palette = self.palette()

        if self.dark_mode:
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)
        else:
            QApplication.setPalette(QApplication.style().standardPalette())

        QApplication.setPalette(palette)

    def get_traffic(self):
        self.save_credentials()

        access_token = self.tokenEntry.text()
        username = self.usernameEntry.text()

        headers = {
            'Authorization': f'token {access_token}',
            'Accept': 'application/vnd.github.v3+json',
        }

        try:
            response = requests.get(f'https://api.github.com/users/{username}/repos', headers=headers)
            response.raise_for_status()
            repos = response.json()

            total_views = 0
            total_clones = 0

            for repo in repos:
                repo_name = repo['name']
                response = requests.get(f'https://api.github.com/repos/{username}/{repo_name}/traffic/views', headers=headers)
                views_data = response.json()
                total_views += sum([view['count'] for view in views_data['views']])

                response = requests.get(f'https://api.github.com/repos/{username}/{repo_name}/traffic/clones', headers=headers)
                clones_data = response.json()
                total_clones += clones_data['count']

            self.resultLabel.setText(f'Total views: {total_views}\nTotal clones: {total_clones}')

        except requests.exceptions.HTTPError as err:
            QMessageBox.warning(self, 'Error', f'An error occurred: {err}')


if __name__ == '__main__':
    app = QApplication(sys.argv)

    ex = MyApp()
    ex.show()

    sys.exit(app.exec_())
