# File Extractor

A simple desktop tool that scans a folder (and all nested sub-folders), then moves every file into
a single output folder using a naming format you choose, e.g.
`YYYY.MM.DD.HH.MM.SS - <original filename>.<extension>` when dates are enabled. The recorded date is taken from the file's creation time (falling back to the last modified time if creation time is unavailable).

The app gives you a straightforward interface to pick folders, set naming options, view progress,
pause or stop processing, and see a summary when everything is finished. Folder choices and naming
preferences are saved locally and restored the next time you open the app.

If you are a developer, technical details are [below](#developers).

## Download the app

1. Click `FileExtractor-win.zip` above.
2. Click the ellipsis (`...`) near the top right of the page
3. Click **Download**
4. Extract the ZIP file to a location you can find easily (for example, your **Documents** folder)

## Run the app

1. Open the extracted folder (usually `FileExtractor-win`)
2. Double-click the application named `FileExtractor-win` (some systems may include `.exe`)

## Using the app

1. In the window that opens:
   - Click **Choose...** next to **Root folder to search** and pick the top-level folder that holds
     the files you want to collect.
   - Click **Choose...** next to **Output folder** and pick where the files should be moved.
   - Pick your naming options:
     - Leave **Prefix filename with recorded file date** checked to add the date to each filename,
       then choose **date (YYYY.MM.DD)** or **date and time (YYYY.MM.DD.HH.MM.SS)**.
     - Edit the text between the date and the original filename (defaults to ` - `). The example
       text updates as you type so you can see what the filenames will look like.

2. Click **Begin**. The app will:
   1. **Search** the root folder and every subfolder. A progress indicator shows how many files were
      found.
   2. **Validate** that the root folder contains files and that the output folder does not already
      hold the same number of files.
   3. **Process** each file by moving it into the output folder and renaming it according to the
      options you set.

3. While processing:
   - **Pause/Resume**: Click **Pause** to temporarily stop processing, then **Resume** to continue.
   - **Stop**: Click **Stop** to halt the run early.
   - **Progress & ETA**: The bar and caption show how many files have been processed and an
     estimated time remaining. After you click **Begin** the status area also shows **Files found**,
     **Estimated time remaining**, and the run summary.

4. When finished, a **summary** appears listing how many files were found, moved, and whether any
   errors occurred. The buttons are re-enabled so you can run again if needed.

### Notes and tips

- The app uses each file's creation time for the date in the new filename. On systems where creation
  time is unavailable, it falls back to the last modified time.
- If a filename already exists in the output folder, the app automatically adds `_1`, `_2`, etc. to
  keep every file.
- The app moves files (it does not leave copies in the original locations). If you prefer to keep
  the originals, make a backup of the root folder before running.
- The app remembers your folder selections and naming preferences on this computer for the next run.

### Troubleshooting

- **"Missing folders" warning**: Make sure you selected both the root folder and an output folder
  before clicking **Begin**.
- **Validation error about file counts**: The app prevents re-running with the exact same number
  of files already present in the output folder. Choose a different output folder or empty the
  existing one.
- **Build failures**: Ensure Python is installed and the `pip install -r requirements.txt` step
  completed successfully before running `python build.py`.

## Developers

### What you need

- **Windows or macOS computer** with a recent version of Python installed (Python 3.10 or later).
  - Python is only required to run or build the app.
  - The build step produces standalone executables that do **not** need Python.
- About 200 MB of free disk space for the temporary build files.

#### Downloading the project

##### Using git

1. Click the green **Code** button on the GitHub page and copy the remote repository
   (`...JD-File-Restructure.git`).
2. Open a terminal and type

   ```bash
   git clone <remote repository.git>
   ```

#### Using zip

1. Click the green **Code** button on the GitHub page and choose **Download ZIP**.
2. Extract the ZIP file to a location you can find easily (for example, your **Documents** folder).

All of the steps below assume you are working inside that extracted folder.

### Run the app immediately (without building)

This approach uses the Python file directly. It is the quickest way to try the app.

1. Open the project folder.

2. Run `main.py` inside the `app` folder. Either:

   - Open a **terminal/command prompt**, then run

     ```bash
     python app/main.py
     ```

   - **Double click** `main.py`
     - On some systems you may need to right-click and choose **Open With → Python**.

3. The File Extractor window appears.

4. Follow the steps described in [Using the app](#using-the-app).

The next sections include step-by-step terminal instructions.

### Build a standalone executable

Building creates an application that runs without installing Python.

- The build script works on both Windows and macOS; run it on the platform you want the executable for.
- The build script also creates a zip file you can keep or share.

#### One-time setup

1. Make sure Python is installed. If you are unsure, open a terminal (Command Prompt on Windows,
   Terminal on macOS).

2. Check Python version

   ```bash
   python --version
   ```

   If a version number appears (e.g., `Python 3.11.0`), you are ready. If you see an error,
   install Python from [python.org](https://www.python.org/downloads/), then reopen the terminal
   and try again.

3. Install the build tool (PyInstaller). In the same terminal, run:

   ```bash
   python -m pip install -r requirements.txt
   ```

> The build processes below also create a zip file containing the executable and its dependencies,
> stored in the project root (`FileExtractor-<platform>.zip`).

#### Build on Windows

1. Open **Command Prompt**.
2. Change to the project folder.
3. Run the command below, replacing `C:\Users\you\Downloads\JD-File-Restructure` with the actual
   path where you extracted the project.

   ```bash
   cd C:\Users\you\Downloads\JD-File-Restructure
   ```

4. Run the build script:

   ```bash
   python build.py
   ```

5. When the command completes, open the `dist` folder inside the project. You will see a folder
   named `FileExtractor-win` which contains:

   - a folder called `_internal` where the required libraries are stored
   - the executable file

6. Copy this folder anywhere you like and double-click the executable to run it.

7. A zip file with the same contents (`FileExtractor-win.zip`) is also placed in the project root
   for sharing.

#### Build on macOS

1. Open **Terminal** (Applications → Utilities → Terminal).
2. Change to the project folder (update the path to match where you extracted the files):

   ```bash
   cd ~/Downloads/JD-File-Restructure
   ```

3. Run the build script:

   ```bash
   python build.py
   ```

4. After the command finishes, open the `dist` folder in the project. You will find a folder named
   `FileExtractor-mac` containing the app bundle.

   - A zip with the same contents (`FileExtractor-mac.zip`) is also placed in the project root
     for sharing.

5. Move the folder to a convenient location and double-click it to launch.

6. **Start the app** by double-clicking the executable you built (or by running `python app/main.py`).

7. Follow the steps described in [Using the app](#using-the-app).
