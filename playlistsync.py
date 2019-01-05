from PyQt5.QtWidgets import (QWidget, QMainWindow, QTextEdit, 
    QAction, QFileDialog, QApplication, QLabel, QPushButton, QGridLayout, QTextEdit, QLineEdit)
from PyQt5.QtGui import QIcon
import sys
import configparser

class PlaylistSync(QWidget):
    
    def __init__(self):
        super().__init__()
        self.music_library = "C:/"
        self.playlist_file = ""
        self.device_music = ""
        self.device_playlist_folder = ""
        
        self.loadConfigFile()
        self.initUI()
        
    def library_path_clicked(self):
       dir_ = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
       self.music_library = dir_
       self.library_path_text.setText(dir_)
       self.config['PATHS']['MusicLibrary'] = self.music_library

    def playlist_file_clicked(self):
        file, extension = QFileDialog.getOpenFileName(None, "Title", "", "M3U (*.m3u)")
        self.playlist_file = file
        self.playlist_file_text.setText(self.playlist_file)
        self.config['PLAYLISTS']['PlaylistFiles'] = self.playlist_file

    def device_music_folder_clicked(self):
        dir_ = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
        self.device_music = dir_
        self.device_music_text.setText(dir_)
        self.config['PATHS']['DeviceMusic'] = self.device_music

    def device_playlist_folder_clicked(self):
        dir_ = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
        self.device_playlist_folder = dir_
        self.device_playlist_text.setText(dir_)
        self.config['PATHS']['DevicePlaylists'] = self.device_playlist_folder

    def loadConfigFile(self):
        self.config = configparser.ConfigParser()
        self.config.read('settings.ini')
        self.music_library = self.config['PATHS']['MusicLibrary']

    def initUI(self):
        library_path = QLabel("Music Library Path")
        playlist_file = QLabel("Playlist File")
        device_music_folder = QLabel("Device Music Folder")
        device_playlist_folder = QLabel("Device Playlist Folder")

        self.library_path_text = QLineEdit()
        self.library_path_text.setText(self.music_library)
        self.playlist_file_text = QLineEdit()
        self.device_music_text = QLineEdit()
        self.device_playlist_text = QLineEdit()

        self.library_path_button = QPushButton("Browse")
        self.library_path_button.clicked.connect(self.library_path_clicked)
        self.playlist_file_button = QPushButton("Browse")
        self.playlist_file_button.clicked.connect(self.playlist_file_clicked)
        self.device_music_button = QPushButton("Browse")
        self.device_music_button.clicked.connect(self.device_music_folder_clicked)
        self.device_playlist_button = QPushButton("Browse")
        self.device_playlist_button.clicked.connect(self.device_playlist_folder_clicked)

        self.sync_button = QPushButton("Sync!")

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(library_path, 1, 0)
        grid.addWidget(self.library_path_text, 1, 1)
        grid.addWidget(self.library_path_button, 1, 2)

        grid.addWidget(playlist_file, 2, 0)
        grid.addWidget(self.playlist_file_text, 2, 1)
        grid.addWidget(self.playlist_file_button, 2, 2)

        grid.addWidget(device_music_folder, 3, 0)
        grid.addWidget(self.device_music_text, 3, 1)
        grid.addWidget(self.device_music_button, 3, 2)

        grid.addWidget(device_playlist_folder, 4, 0)
        grid.addWidget(self.device_playlist_text, 4, 1)
        grid.addWidget(self.device_playlist_button, 4, 2)

        self.setLayout(grid) 
        
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('File dialog')
        self.show()

           
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ps = PlaylistSync()
    sys.exit(app.exec_())