# File Extractor

A simple desktop tool that scans a folder (and all nested sub-folders), then moves every file into a single output folder using the naming format `YYYY.MM.DD.HH.MM.SS_HOMEi_HomeiStudent, <original filename>.<extension>`. The recorded date is taken from the file's creation time (falling back to the last modified time if creation time is unavailable).

The app gives you a straightforward interface to pick folders, view progress, pause or stop processing, and see a summary when everything is finished.

## What you need

- **Windows or macOS computer** with a recent version of Python installed (Python 3.10 or later). Python is only required to run or build the app. The build step produces standalone executables that do **not** need Python.
- About 200 MB of free disk space for the temporary build files.

## Downloading the project

1. Click the green **Code** button on the GitHub page and choose **Download ZIP**.
2. Extract the ZIP file to a location you can find easily (for example, your **Documents** folder).

All of the steps below assume you are working inside that extracted folder.

## Run the app immediately (without building)

This approach uses the Python file directly. It is the quickest way to try the app.

1. Open the project folder you extracted earlier.
2. Double-click `main.py` inside the `app` folder. On some systems you may need to right-click and choose **Open With → Python**.
3. The File Extractor window appears.
4. Follow the on-screen steps described in [Using the app](#using-the-app).

> Tip: If double-clicking `main.py` does not open the app, open a terminal/command prompt, type `python app/main.py`, and press **Enter**. The next sections include step-by-step terminal instructions.

## Build a standalone executable

Building creates an application you can keep or share that runs without installing Python. The same `build.py` script works on both Windows and macOS—run it on the platform you want the executable for.

### One-time setup

1. Make sure Python is installed. If you are unsure, open a terminal (Command Prompt on Windows, Terminal on macOS) and type:
2. Install libraries

   ```bash
   python --version
   ```

   If a version number appears (e.g., `Python 3.11.0`), you are ready. If you see an error, install Python from [python.org](https://www.python.org/downloads/), then reopen the terminal and try again.
3. Install the build tool (PyInstaller). In the same terminal, run:

   ```bash
   python -m pip install -r requirements.txt
   ```

### Build on Windows

1. Open **Command Prompt**.
2. Change to the project folder. Replace `C:\Users\you\Downloads\JD-File-Restructure` with the actual path where you extracted the project:

   ```bash
   cd C:\Users\you\Downloads\JD-File-Restructure
   ```

3. Run the build script:

   ```bash
   python build.py
   ```

4. When the command completes, open the `dist` folder inside the project. You will see a folder named `HomeStudentExtractor-win` that contains the executable file. Copy this folder anywhere you like and double-click the executable to run it.

### Build on macOS

1. Open **Terminal** (Applications → Utilities → Terminal).
2. Change to the project folder (update the path to match where you extracted the files):

   ```bash
   cd ~/Downloads/JD-File-Restructure
   ```

3. Run the build script:

   ```bash
   python build.py
   ```

4. After the command finishes, open the `dist` folder in the project. You will find a folder named `HomeStudentExtractor-mac` containing the app bundle. Move it to a convenient location and double-click it to launch.

## Using the app

1. **Start the app** by double-clicking the executable you built (or by running `python app/main.py`).
2. In the window that opens:
   - Click **Choose...** next to **Root folder to search** and pick the top-level folder that holds the files you want to collect.
   - Click **Choose...** next to **Output folder** and pick where the files should be moved.
3. Click **Begin**. The app will:
   1. **Search** the root folder and every subfolder. A progress indicator shows how many files were found.
   2. **Validate** that the root folder contains files and that the output folder does not already hold the same number of files.
   3. **Process** each file by moving it into the output folder and renaming it to `YYYY.MM.DD_HOMEi_HomeiStudent, <original filename>.<extension>` using the file's creation time.
4. While processing:
   - **Pause/Resume**: Click **Pause** to temporarily stop processing, then **Resume** to continue.
   - **Stop**: Click **Stop** to halt the run early.
   - **Progress & ETA**: The bar and caption show how many files have been processed and an estimated time remaining.
5. When finished, a **summary** appears listing how many files were found, moved, and whether any errors occurred. The buttons are re-enabled so you can run again if needed.

## Notes and tips

- The app uses each file's creation time for the date in the new filename. On systems where creation time is unavailable, it falls back to the last modified time.
- If a filename already exists in the output folder, the app automatically adds `_1`, `_2`, etc. to keep every file.
- The app moves files (it does not leave copies in the original locations). If you prefer to keep the originals, make a backup of the root folder before running.
- You can safely close the window after processing completes. All settings are cleared when the app restarts.

## Troubleshooting

- **"Missing folders" warning**: Make sure you selected both the root folder and an output folder before clicking **Begin**.
- **Validation error about file counts**: The app prevents re-running with the exact same number of files already present in the output folder. Choose a different output folder or empty the existing one.
- **Build failures**: Ensure Python is installed and the `pip install -r requirements.txt` step completed successfully before running `python build.py`.

Enjoy using the File Extractor!
