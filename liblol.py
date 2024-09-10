import re
import sys
import os
import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QFileDialog,
                             QLabel, QProgressBar, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Function to sanitize folder names
def sanitize_folder_name(name):
    # Remove invalid characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Truncate to avoid path length issues
    max_length = 255
    if len(name) > max_length:
        name = name[:max_length]
    return name

# Function to get download links and folder name from a webpage
def get_download_links_and_folder_name(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    folder_name = soup.find('h1').get_text(strip=True)
    folder_name = sanitize_folder_name(folder_name)
    for link in soup.find_all('a', href=True):
        if 'download' in link.get('href'):
            links.append(link['href'])
    return links, folder_name

# Worker thread class for downloading files
class DownloadWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    update_filename = pyqtSignal(str)

    def __init__(self, urls, output_folder):
        super().__init__()
        self.urls = urls
        self.output_folder = output_folder

    def run(self):
        for url in self.urls:
            links, folder_name = get_download_links_and_folder_name(url)
            folder_path = os.path.join(self.output_folder, folder_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            for link in links:
                self.update_filename.emit(link.split('/')[-1])
                self.download_file(link, folder_path)
                self.finished.emit(f"Downloaded: {link}")

    def download_file(self, url, folder):
        local_filename = url.split('/')[-1]
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        path = os.path.join(folder, local_filename)

        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded_size += len(chunk)
                progress = int((downloaded_size / total_size) * 100)
                self.progress.emit(progress)

        self.progress.emit(100)

# Main window class
class AutodownloaderApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Input file path
        self.input_path_edit = QLineEdit(self)
        self.input_path_edit.setPlaceholderText("Select input file...")
        layout.addWidget(self.input_path_edit)

        self.input_browse_button = QPushButton("Browse", self)
        self.input_browse_button.clicked.connect(self.select_input_file)
        layout.addWidget(self.input_browse_button)

        # Output folder path
        self.output_path_edit = QLineEdit(self)
        self.output_path_edit.setPlaceholderText("Select output folder...")
        layout.addWidget(self.output_path_edit)

        self.output_browse_button = QPushButton("Browse", self)
        self.output_browse_button.clicked.connect(self.select_output_folder)
        layout.addWidget(self.output_browse_button)

        # Progress bar and filename display
        self.progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar(self)
        self.filename_label = QLabel(self)
        self.progress_layout.addWidget(self.progress_bar)
        self.progress_layout.addWidget(self.filename_label)
        layout.addLayout(self.progress_layout)

        # Start button
        self.start_button = QPushButton("Start Download", self)
        self.start_button.clicked.connect(self.start_download)
        layout.addWidget(self.start_button)

        self.setLayout(layout)
        self.setWindowTitle('Autodownloader')
        self.setGeometry(100, 100, 500, 200)

    def select_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Input File", "", "Text Files (*.txt)")
        if file_path:
            self.input_path_edit.setText(file_path)

    def select_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder_path:
            self.output_path_edit.setText(folder_path)

    def start_download(self):
        input_path = self.input_path_edit.text()
        output_folder = self.output_path_edit.text()

        if not input_path or not output_folder:
            QMessageBox.warning(self, "Warning", "Please select both input and output paths.")
            return

        try:
            with open(input_path, 'r') as file:
                urls = [line.strip() for line in file if line.strip()]

            self.worker = DownloadWorker(urls, output_folder)
            self.worker.progress.connect(self.update_progress)
            self.worker.finished.connect(self.show_message)
            self.worker.update_filename.connect(self.update_filename)
            self.worker.start()

        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "Input file not found.")

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_filename(self, filename):
        self.filename_label.setText(filename)

    def show_message(self, message):
        QMessageBox.information(self, "Info", message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AutodownloaderApp()
    ex.show()
    sys.exit(app.exec_())
