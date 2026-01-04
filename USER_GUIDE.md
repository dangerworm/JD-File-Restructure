# File Extractor

A simple desktop tool that scans a folder (and all nested sub-folders), then moves every file into
a single output folder using a user-configurable naming format, e.g.
`YYYY.MM.DD.HH.MM.SS_HOMEi_HomeiStudent, <original filename>.<extension>`.
The recorded date is taken from the file's creation time (falling back to the last modified time
if creation time is unavailable).

The app gives you a straightforward interface to pick folders, view progress, pause or stop
processing, and see a summary when everything is finished.

## Download the app

1. Go to the [Git repository](https://github.com/dangerworm/JD-File-Restructure)

2. Click `FileExtractor-win.zip`

3. Click the ellipsis (`...`) near the top right of the page

4. Click **Download**

5. Extract the ZIP file to a location you can find easily (for example, your **Documents** folder)

## Run the app

1. Open the extracted folder (usually `FileExtractor-win`)

2. Double-click the application named `FileExtractor-win` (some systems may include `.exe`)

## Using the app

1. In the window that opens:
   - Click **Choose...** next to **Root folder to search** and pick the top-level folder that holds
     the files you want to collect.
   - Click **Choose...** next to **Output folder** and pick where the files should be moved.

2. Click **Begin**. The app will:
   1. **Search** the root folder and every subfolder. A progress indicator shows how many files were
      found.
   2. **Validate** that the root folder contains files and that the output folder does not already
      hold the same number of files.
   3. **Process** each file by moving it into the output folder and renaming it according to the
      format you have specified.

3. While processing:
   - **Pause/Resume**: Click **Pause** to temporarily stop processing, then **Resume** to continue.
   - **Stop**: Click **Stop** to halt the run early.
   - **Progress & ETA**: The bar and caption show how many files have been processed and an
     estimated time remaining.

4. When finished, a **summary** appears listing how many files were found, moved, and whether any
   errors occurred. The buttons are re-enabled so you can run again if needed.

## Notes and tips

- The app uses each file's creation time for the date in the new filename. On systems where creation
  time is unavailable, it falls back to the last modified time.
- If a filename already exists in the output folder, the app automatically adds `_1`, `_2`, etc. to
  keep every file.
- The app moves files (it does not leave copies in the original locations). If you prefer to keep
  the originals, make a backup of the root folder before running.
- You can safely close the window after processing completes. All settings are cleared when the app
  restarts.

## Troubleshooting

- **"Missing folders" warning**: Make sure you selected both the root folder and an output folder
  before clicking **Begin**.
- **Validation error about file counts**: The app prevents re-running with the exact same number
  of files already present in the output folder. Choose a different output folder or empty the
  existing one.
- **Build failures**: Ensure Python is installed and the `pip install -r requirements.txt` step
  completed successfully before running `python build.py`.

Enjoy using the File Extractor!
