from PyQt5.QtWidgets import (QWidget, QMainWindow, QTextEdit, 
    QAction, QFileDialog, QApplication, QLabel, QPushButton, QGridLayout, QTextEdit, QLineEdit, QProgressBar)
from PyQt5.QtGui import QIcon
import sys
import os
import configparser
import time
from shutil import copyfile
import ntpath
import _thread

#TODO:
# PyQT thread for copying and progress bar
# include full common path for device if greater than root dir
# remove playlist and files option
# copy album art
# Fix unable to copy royksopp file

#returns the point where two strings differ
def str_compare(str1, str2):
    for i in range(len(str1)):
        if i > len(str2) - 1:
            return -1
        if str1[i] != str2[i]:
            return i
    return -1

def copy_file(src, dest, force=False):
    dirname = os.path.dirname(dest)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
        print("making dir : " + dirname)

    if force or not os.path.isfile(dest):
        try:
            copyfile(src, dest) 
        except FileNotFoundError:
            print("Couldn't find : " + src)

class SyncProgress(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(30, 20 , 260, 25)
        self.fileText = QLabel(self)
        #self.fileText.setText("Exmaple filename.mp3")
        self.fileText.move(30, 60)
        self.setGeometry(300, 300, 280, 100)
        self.setWindowTitle("Copying files..")
        self.show()

    def updateFilename(self, filename):
        self.fileText.setText(filename)

    def updatePBar(self, value):
        self.progress_bar.setValue(value)

    def quit():
        self.quit()        


class PlaylistSync(QWidget):
    
    def __init__(self):
        super().__init__()
        self.music_library = "C:/"
        self.playlist_file = ""
        self.device_music = ""
        self.device_playlist_folder = ""
        self.config_filename = ""
        
        self.loadConfigFile('settings.ini')
        self.initUI()
        
    def library_path_clicked(self):
       dir_ = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
       self.music_library = dir_
       self.library_path_text.setText(dir_)
       self.config['PATHS']['MusicLibrary'] = self.music_library
       self.saveConfig()

    def playlist_file_clicked(self):
        file, extension = QFileDialog.getOpenFileName(None, "Title", "", "M3U (*.m3u)")
        self.playlist_file = file
        self.playlist_file_text.setText(self.playlist_file)
        self.config['PLAYLISTS']['PlaylistFiles'] = self.playlist_file
        self.saveConfig()

    def device_music_folder_clicked(self):
        dir_ = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
        self.device_music = dir_
        self.device_music_text.setText(dir_)
        self.config['PATHS']['DeviceMusic'] = self.device_music
        self.saveConfig()

    def device_playlist_folder_clicked(self):
        dir_ = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
        self.device_playlist_folder = dir_
        self.device_playlist_text.setText(dir_)
        self.config['PATHS']['DevicePlaylists'] = self.device_playlist_folder
        self.saveConfig()

    def loadConfigFile(self, config_filename):
        self.config = configparser.ConfigParser()
        self.config_filename = config_filename
        self.config.read(config_filename)
        self.music_library = self.config['PATHS']['MusicLibrary']
        self.playlist_file = self.config['PLAYLISTS']['PlaylistFiles']
        self.device_music = self.config['PATHS']['DeviceMusic']
        self.device_playlist_folder = self.config['PATHS']['DevicePlaylists']

    def saveConfig(self):
        with open(self.config_filename, 'w') as configfile:
            self.config.write(configfile)

    def setPBarPercent(self, percent):
        self.progress_bar.setValue(percent)

    def copy_files(self, src_files, dest_files, window):
        for i in range(len(src_files)):
            src = src_files[i]
            dest = dest_files[i]
            percent = (i/len(src_files)) * 100
            #self.window.updateFilename(source_files[i])
            #self.window.updatePBar(percent)
            #window.setPBarPercent(percent)
            #time.sleep(0.1)
            copy_file(src, dest)
       # window.setPBarPercent(0)

    def syncWithDevice(self):
        playlist_file_lines = []
        with open(self.playlist_file, 'r') as playlist_file:
            playlist_file_lines = playlist_file.readlines()

        read_next_line = False
        playlist_tracks = []
        for line in playlist_file_lines:
            if read_next_line:
                playlist_tracks.append(line[:-1])
                read_next_line = False
            if "#EXTINF" in line:
                read_next_line = True

        source_files = []
        last_char = self.music_library[len(self.music_library) - 1]
        if last_char == "/" or last_char == "\\":
            self.music_library = self.music_library[:-1]
        
        for track in playlist_tracks:
            # Remove last path symbol
            source = self.music_library + track
            source_files.append(source)

        #TODO: copy album art and other files

        dest_files = []
        for track in playlist_tracks:
            dest = self.device_music + track
            dest_path = os.path.dirname(dest)
            #print("Path: " + dest_path)
            dest_files.append(dest)

        #TODO: Show popup
        #self.window = SyncProgress()
        _thread.start_new_thread(self.copy_files, (source_files, dest_files, self))
        #for i in range(len(source_files)):
        #    src = source_files[i]
        #    dest = dest_files[i]
        #    percent = (i/len(playlist_tracks)) * 100
            #self.window.updateFilename(source_files[i])
            #self.window.updatePBar(percent)
        #    self.setPBarPercent(percent)
            #time.sleep(0.1)
        #    copy_file(src, dest)
        #self.window.close()

        self.setPBarPercent(0)

        diff_pt = str_compare(self.device_playlist_folder, self.device_music)
        common_path = self.device_playlist_folder[:diff_pt]
        #print("Common path: " + common_path)

        music_paths = os.path.split(self.device_music)
        relative_music_dirs = []
        #TODO: include full common path
        for dir in music_paths:
            if dir != common_path:
                relative_music_dirs.append(dir)

        playlist_paths = os.path.split(self.device_playlist_folder)
        diff_from_relative = 0
        for dir in playlist_paths:
            if dir != common_path:
                diff_from_relative += 1

        to_relative_path = ""
        for i in range(diff_from_relative):
            to_relative_path += "../"

        playlist_prepend = os.path.join(to_relative_path, *relative_music_dirs)
        #print(playlist_prepend)

        dest_playlist_file_lines = []
        for line in playlist_file_lines:
            if not "#EXTINF" in line and not "#EXTM3U" in line and len(line) > 1:
                path = playlist_prepend + line
                dest_playlist_file_lines.append(path)
            else:
                dest_playlist_file_lines.append(line)
        playlist_filename = ntpath.basename(self.playlist_file)
        dest_playlist_filename = os.path.join(self.device_playlist_folder, playlist_filename)
        print("Dest playlist filename: " + dest_playlist_filename)
        with open(dest_playlist_filename, 'w') as dest_playlistfile:
            for line in dest_playlist_file_lines:
                dest_playlistfile.write(line)
        #copy_file(self.playlist_file, dest_playlist_filename, force=True)


    def initUI(self):
        library_path = QLabel("Music Library Path")
        playlist_file = QLabel("Playlist File")
        device_music_folder = QLabel("Device Music Folder")
        device_playlist_folder = QLabel("Device Playlist Folder")

        self.library_path_text = QLineEdit()
        self.library_path_text.setText(self.music_library)
        self.playlist_file_text = QLineEdit(self.playlist_file)
        self.device_music_text = QLineEdit(self.device_music)
        self.device_playlist_text = QLineEdit(self.device_playlist_folder)

        self.library_path_button = QPushButton("Browse")
        self.library_path_button.clicked.connect(self.library_path_clicked)
        self.playlist_file_button = QPushButton("Browse")
        self.playlist_file_button.clicked.connect(self.playlist_file_clicked)
        self.device_music_button = QPushButton("Browse")
        self.device_music_button.clicked.connect(self.device_music_folder_clicked)
        self.device_playlist_button = QPushButton("Browse")
        self.device_playlist_button.clicked.connect(self.device_playlist_folder_clicked)

        self.sync_button = QPushButton("Sync!")
        self.sync_button.clicked.connect(self.syncWithDevice)

        self.progress_bar = QProgressBar(self)
        #self.copy_filename = QLabel(self)
        #self.copy_filename.setText("Example filename.txt")

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

        grid.addWidget(self.sync_button, 5, 2)
        grid.addWidget(self.progress_bar, 5, 0, 1, 2)
        
        #grid.addWidget(self.copy_filename, 6, 0)

        self.setLayout(grid) 
        
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Playlist Synchroniser')
        self.show()

           
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ps = PlaylistSync()
    sys.exit(app.exec_())