import json
import os
import queue
import shutil
import threading
import time
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class FileFlattenerApp:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        self.master.title("File Extractor")
        self.master.geometry("780x520")

        self.config_path = Path.home() / ".file_extractor_settings.json"
        self.root_dir: Path | None = None
        self.output_dir: Path | None = None
        self.files_to_process: list[Path] = []

        self.is_running = False
        self.is_paused = False
        self.stop_event = threading.Event()
        self.status_queue: queue.Queue[str] = queue.Queue()

        self.process_thread: threading.Thread | None = None
        self.total_files = 0
        self.processed_files = 0
        self.error_files: list[tuple[Path, str]] = []
        self.search_start_time: float | None = None
        self.process_start_time: float | None = None
        self.has_started = False

        self.root_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.prefix_date_var = tk.BooleanVar(value=True)
        self.date_format_var = tk.StringVar(value="date")
        self.affix_var = tk.StringVar(value=" - ")
        self.example_name_var = tk.StringVar(value="")

        self._load_settings()
        self._build_ui()
        self._on_prefix_toggle()
        self._update_example_name()
        self._poll_queue()

    def _build_ui(self) -> None:
        padding = {"padx": 10, "pady": 5}

        folders_frame = ttk.LabelFrame(self.master, text="Folders")
        folders_frame.pack(fill=tk.X, **padding)

        ttk.Label(folders_frame, text="Root folder to search:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(folders_frame, textvariable=self.root_var, width=60, state="readonly").grid(row=0, column=1, sticky=tk.W, padx=(5, 5))
        ttk.Button(folders_frame, text="Choose...", command=self._select_root).grid(row=0, column=2, sticky=tk.W)

        ttk.Label(folders_frame, text="Output folder:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(folders_frame, textvariable=self.output_var, width=60, state="readonly").grid(row=1, column=1, sticky=tk.W, padx=(5, 5))
        ttk.Button(folders_frame, text="Choose...", command=self._select_output).grid(row=1, column=2, sticky=tk.W)

        naming_frame = ttk.LabelFrame(self.master, text="Naming options")
        naming_frame.pack(fill=tk.X, **padding)

        self.prefix_checkbox = ttk.Checkbutton(
            naming_frame,
            text="Prefix filename with recorded file date",
            variable=self.prefix_date_var,
            command=self._on_prefix_toggle,
        )
        self.prefix_checkbox.grid(row=0, column=0, columnspan=2, sticky=tk.W)

        self.date_radio = ttk.Radiobutton(
            naming_frame,
            text="date (YY.MM.DD)",
            variable=self.date_format_var,
            value="date",
            command=self._on_date_format_change,
        )
        self.date_radio.grid(row=1, column=0, sticky=tk.W, padx=(20, 10))

        self.datetime_radio = ttk.Radiobutton(
            naming_frame,
            text="date and time (YY.MM.DD.HH.MM.SS)",
            variable=self.date_format_var,
            value="datetime",
            command=self._on_date_format_change,
        )
        self.datetime_radio.grid(row=1, column=1, sticky=tk.W)

        ttk.Label(naming_frame, text="Affix between date and name:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.affix_entry = ttk.Entry(naming_frame, textvariable=self.affix_var, width=20)
        self.affix_entry.grid(row=2, column=1, sticky=tk.W, pady=(5, 0))
        self.affix_var.trace_add("write", lambda *_: self._on_affix_change())

        ttk.Label(naming_frame, textvariable=self.example_name_var, foreground="#444").grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

        control_frame = ttk.Frame(self.master)
        control_frame.pack(fill=tk.X, **padding)

        self.start_button = ttk.Button(control_frame, text="Begin", command=self._start_processing)
        self.start_button.grid(row=0, column=0, sticky=tk.W)

        self.pause_button = ttk.Button(control_frame, text="Pause", command=self._toggle_pause, state=tk.DISABLED)
        self.pause_button.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))

        self.stop_button = ttk.Button(control_frame, text="Stop", command=self._stop_processing, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=2, sticky=tk.W, padx=(5, 0))

        progress_frame = ttk.Frame(self.master)
        progress_frame.pack(fill=tk.X, **padding)

        self.progress_bar = ttk.Progressbar(progress_frame, length=400, mode="determinate")
        self.progress_bar.grid(row=0, column=0, sticky=tk.W)

        self.progress_label_var = tk.StringVar(value="Waiting to start")
        ttk.Label(progress_frame, textvariable=self.progress_label_var).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        self.status_frame = ttk.LabelFrame(self.master, text="Status")
        status_inner = ttk.Frame(self.status_frame)
        status_inner.pack(fill=tk.X, **padding)

        self.search_count_var = tk.StringVar(value="Files found: 0")
        ttk.Label(status_inner, textvariable=self.search_count_var).grid(row=0, column=0, sticky=tk.W)

        self.eta_var = tk.StringVar(value="Estimated time remaining: -")
        ttk.Label(status_inner, textvariable=self.eta_var).grid(row=1, column=0, sticky=tk.W, pady=(2, 0))

        self.summary_text = tk.Text(self.status_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

    def _log_summary(self, message: str) -> None:
        self.summary_text.configure(state=tk.NORMAL)
        self.summary_text.insert(tk.END, message + "\n")
        self.summary_text.see(tk.END)
        self.summary_text.configure(state=tk.DISABLED)

    def _load_settings(self) -> None:
        if not self.config_path.exists():
            return
        try:
            data = json.loads(self.config_path.read_text())
        except (json.JSONDecodeError, OSError):
            return

        root = data.get("root_dir")
        if root:
            self.root_dir = Path(root)
            self.root_var.set(str(self.root_dir))

        output = data.get("output_dir")
        if output:
            self.output_dir = Path(output)
            self.output_var.set(str(self.output_dir))

        self.prefix_date_var.set(bool(data.get("prefix_date", True)))
        self.date_format_var.set(data.get("date_format", "date"))
        self.affix_var.set(data.get("affix_text", " - "))

    def _save_settings(self) -> None:
        payload = {
            "root_dir": str(self.root_dir) if self.root_dir else "",
            "output_dir": str(self.output_dir) if self.output_dir else "",
            "prefix_date": self.prefix_date_var.get(),
            "date_format": self.date_format_var.get(),
            "affix_text": self.affix_var.get(),
        }
        try:
            self.config_path.write_text(json.dumps(payload, indent=2))
        except OSError:
            pass

    def _show_status_container(self) -> None:
        if self.status_frame and not self.status_frame.winfo_ismapped():
            self.status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def _select_root(self) -> None:
        path = filedialog.askdirectory(title="Select the folder to search")
        if path:
            self.root_dir = Path(path)
            self.root_var.set(str(self.root_dir))
            self._save_settings()

    def _select_output(self) -> None:
        path = filedialog.askdirectory(title="Select the output folder")
        if path:
            self.output_dir = Path(path)
            self.output_var.set(str(self.output_dir))
            self._save_settings()

    def _on_prefix_toggle(self) -> None:
        if self.prefix_date_var.get():
            self.date_radio.state(["!disabled"])
            self.datetime_radio.state(["!disabled"])
        else:
            self.date_radio.state(["disabled"])
            self.datetime_radio.state(["disabled"])
        self._update_example_name()
        self._save_settings()

    def _on_date_format_change(self) -> None:
        self._update_example_name()
        self._save_settings()

    def _on_affix_change(self) -> None:
        self._update_example_name()
        self._save_settings()

    def _toggle_pause(self) -> None:
        if not self.is_running:
            return
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.configure(text="Resume")
            self.progress_label_var.set("Paused")
        else:
            self.pause_button.configure(text="Pause")
            self.progress_label_var.set(f"Resuming... {self.processed_files} of {self.total_files}")

    def _stop_processing(self) -> None:
        if not self.is_running:
            return
        self.stop_event.set()
        self.progress_label_var.set("Stopping...")

    def _start_processing(self) -> None:
        if self.is_running:
            return
        if not self.root_dir or not self.output_dir:
            messagebox.showwarning("Missing folders", "Please choose both the root folder and the output folder.")
            return

        self.has_started = True
        self._show_status_container()

        self.summary_text.configure(state=tk.NORMAL)
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.configure(state=tk.DISABLED)

        self.is_running = True
        self.is_paused = False
        self.stop_event.clear()
        self.error_files.clear()
        self.processed_files = 0
        self.total_files = 0
        self.files_to_process = []

        self.start_button.configure(state=tk.DISABLED)
        self.pause_button.configure(state=tk.NORMAL, text="Pause")
        self.stop_button.configure(state=tk.NORMAL)

        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start(10)
        self.progress_label_var.set("Searching for files...")
        self.eta_var.set("Estimated time remaining: -")
        self.search_count_var.set("Files found: 0")

        self.process_thread = threading.Thread(target=self._pipeline, daemon=True)
        self.process_thread.start()

    def _pipeline(self) -> None:
        try:
            self.search_start_time = time.time()
            self._search_files()
            if self.stop_event.is_set():
                return

            if self._validate_before_process():
                if self.stop_event.is_set():
                    return

                self.process_start_time = time.time()
                self._process_files()

        except Exception as exc:  # noqa: BLE001 - user facing error handling
            self.status_queue.put(f"Error: {exc}")
            self._log_summary(f"Unexpected error: {exc}")
        finally:
            self.is_running = False
            self.stop_event.clear()
            self.master.after(0, self._reset_ui_after_run)

    def _search_files(self) -> None:
        if not self.root_dir:
            return

        found_files: list[Path] = []
        for current_root, _, files in os.walk(self.root_dir):
            if self.stop_event.is_set():
                break
            for filename in files:
                if self.stop_event.is_set():
                    break
                while self.is_paused and not self.stop_event.is_set():
                    time.sleep(0.2)
                file_path = Path(current_root) / filename
                found_files.append(file_path)
                self.status_queue.put(f"found:{len(found_files)}")

        self.files_to_process = found_files
        self.total_files = len(found_files)
        self.status_queue.put("search_complete")

    def _validate_before_process(self) -> bool:
        if not self.files_to_process:
            self.status_queue.put("validation_failed:No files found in the selected root folder.")
            return False

        output_count = 0
        if self.output_dir and self.output_dir.exists():
            output_count = sum(1 for item in self.output_dir.iterdir() if item.is_file())

        if output_count == self.total_files:
            self.status_queue.put(
                "validation_failed:The output folder already contains the same number of files as would be created by this action. Either clear the output folder or choose a different one."
            )
            return False

        self.status_queue.put("validation_passed")
        return True

    def _process_files(self) -> None:
        if not self.output_dir:
            return

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate", maximum=max(self.total_files, 1), value=0)
        self.progress_label_var.set("Processing files...")

        for index, file_path in enumerate(self.files_to_process, start=1):
            if self.stop_event.is_set():
                break
            while self.is_paused and not self.stop_event.is_set():
                time.sleep(0.2)

            try:
                timestamp = self._get_recorded_date(file_path)
                new_name = self._build_new_name(file_path, timestamp)
                destination = self.output_dir / new_name
                destination = self._ensure_unique(destination)
                shutil.copy(str(file_path), destination)
                self.processed_files += 1
            except Exception as exc:  # noqa: BLE001 - user facing error handling
                self.error_files.append((file_path, str(exc)))

            self.status_queue.put(f"processed:{index}")
            self._update_eta(index)

        self.status_queue.put("processing_complete")

    def _get_recorded_date(self, file_path: Path) -> datetime:
        try:
            created_time = file_path.stat().st_ctime
        except OSError:
            created_time = file_path.stat().st_mtime
        return datetime.fromtimestamp(created_time)

    def _update_example_name(self) -> None:
        sample_timestamp = datetime(2024, 1, 2, 3, 4, 5)
        base_name = "example"
        extension = ".txt"
        affix = self.affix_var.get()
        if self.prefix_date_var.get():
            date_format = "%Y.%m.%d" if self.date_format_var.get() == "date" else "%Y.%m.%d.%H.%M.%S"
            date_str = sample_timestamp.strftime(date_format)
            example = f"{date_str}{affix}{base_name}{extension}"
        else:
            example = f"{base_name}{extension}"
        self.example_name_var.set(f"Example: {example}")

    def _build_new_name(self, file_path: Path, timestamp: datetime) -> str:
        base_name = file_path.stem
        extension = file_path.suffix
        affix = self.affix_var.get()
        if self.prefix_date_var.get():
            date_format = "%Y.%m.%d" if self.date_format_var.get() == "date" else "%Y.%m.%d.%H.%M.%S"
            date_str = timestamp.strftime(date_format)
            return f"{date_str}{affix}{base_name}{extension}"
        return f"{base_name}{extension}"

    def _ensure_unique(self, destination: Path) -> Path:
        counter = 1
        unique_path = destination
        while unique_path.exists():
            unique_path = destination.with_stem(f"{destination.stem}_{counter}")
            counter += 1
        return unique_path

    def _update_eta(self, processed_count: int) -> None:
        if not self.process_start_time or processed_count == 0:
            return
        elapsed = time.time() - self.process_start_time
        avg_per_file = elapsed / processed_count
        remaining = max(self.total_files - processed_count, 0)
        eta_seconds = avg_per_file * remaining
        self.status_queue.put(f"eta:{int(eta_seconds)}")

    def _poll_queue(self) -> None:
        try:
            while True:
                message = self.status_queue.get_nowait()
                self._handle_status_message(message)
        except queue.Empty:
            pass
        finally:
            self.master.after(200, self._poll_queue)

    def _handle_status_message(self, message: str) -> None:
        if message.startswith("found:"):
            count = int(message.split(":")[1])
            self.search_count_var.set(f"Files found: {count}")
        elif message == "search_complete":
            self.progress_bar.stop()
            self.progress_bar.configure(mode="determinate", maximum=max(self.total_files, 1), value=0)
            self.progress_label_var.set(f"Search complete. {self.total_files} files ready to process.")
        elif message.startswith("validation_failed:" ):
            reason = message.split(":", 1)[1]
            messagebox.showwarning("Cannot start", reason)
            self._log_summary(reason)
            self._reset_ui_after_run()
        elif message == "validation_passed":
            self.progress_label_var.set("Validation complete. Starting processing...")
        elif message.startswith("processed:"):
            count = int(message.split(":")[1])
            self.progress_bar['value'] = count
            self.progress_label_var.set(f"Processing... {count} of {self.total_files}")
        elif message.startswith("eta:"):
            seconds = int(message.split(":")[1])
            self.eta_var.set(f"Estimated time remaining: {self._format_seconds(seconds)}")
        elif message == "processing_complete":
            self._display_summary()
        elif message.startswith("Error:"):
            messagebox.showerror("Error", message)

    def _display_summary(self) -> None:
        errors_text = "\n".join(f"- {path}: {error}" for path, error in self.error_files)
        summary = [
            "Processing finished.",
            f"Total files discovered: {self.total_files}",
            f"Successfully moved: {self.processed_files}",
            f"Errors: {len(self.error_files)}",
        ]
        if errors_text:
            summary.append("\nIssues encountered:\n" + errors_text)
        summary_message = "\n".join(summary)

        self.progress_label_var.set("Completed")
        self.eta_var.set("Estimated time remaining: 0 seconds")
        self._log_summary(summary_message)
        messagebox.showinfo("Done", summary_message)

    def _reset_ui_after_run(self) -> None:
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate", value=0)
        self.start_button.configure(state=tk.NORMAL)
        self.pause_button.configure(state=tk.DISABLED, text="Pause")
        self.stop_button.configure(state=tk.DISABLED)
        self.is_running = False
        self.is_paused = False
        self.stop_event.clear()

    def _format_seconds(self, seconds: int) -> str:
        minutes, sec = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        parts: list[str] = []
        if hours:
            parts.append(f"{hours}h")
        if hours or minutes:
            parts.append(f"{minutes}m")
        parts.append(f"{sec}s")
        return " ".join(parts)


def main() -> None:
    root = tk.Tk()
    app = FileFlattenerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
