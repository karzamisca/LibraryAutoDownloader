# Autodownloader

## Classes and Functions

### `sanitize_folder_name(name: str) -> str`
Sanitizes a folder name by removing invalid characters and truncating it to a maximum length.

**Parameters:**
- `name` (str): The name to be sanitized.

**Returns:**
- (str): The sanitized folder name.

### `get_download_links_and_folder_name(page_url: str) -> tuple`
Fetches download links and a sanitized folder name from a given webpage URL.

**Parameters:**
- `page_url` (str): The URL of the webpage to fetch data from.

**Returns:**
- tuple: A tuple containing:
  - A list of download links (list of str).
  - A sanitized folder name (str).

### `DownloadWorker(QThread)`
A QThread subclass that handles downloading files from URLs.

**Signals:**
- `progress` (pyqtSignal[int]): Emitted to update the progress bar.
- `finished` (pyqtSignal[str]): Emitted to show a completion message.
- `update_filename` (pyqtSignal[str]): Emitted to update the filename label.

**Methods:**
- `__init__(self, urls: list, output_folder: str)`
  - Initializes the thread with URLs to download and an output folder path.
  
- `run(self)`
  - Runs the thread, fetching links and downloading files.

- `download_file(self, url: str, folder: str)`
  - Downloads a file from a URL and saves it to a specified folder.

### `AutodownloaderApp(QWidget)`
The main application window for the autodownloader.

**Methods:**
- `__init__(self)`
  - Initializes the UI components.

- `initUI(self)`
  - Sets up the UI layout, including input and output paths, progress bar, and start button.

- `select_input_file(self)`
  - Opens a file dialog to select the input file containing URLs.

- `select_output_folder(self)`
  - Opens a folder dialog to select the output folder.

- `start_download(self)`
  - Starts the download process using the input file and output folder.

- `update_progress(self, value: int)`
  - Updates the progress bar with the current progress value.

- `update_filename(self, filename: str)`
  - Updates the filename label with the name of the currently downloading file.

- `show_message(self, message: str)`
  - Shows an informational message box with the given message.

### Main Execution
- The script creates an instance of `QApplication` and `AutodownloaderApp`, and starts the application event loop.
