import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox
import threading
import queue

result_queue = queue.Queue()

def select_files_to_analyze():
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(
        title="Select files to analyze",
        filetypes=[("PDF and Image files", "*.pdf *.png *.jpg *.jpeg *.tiff *.bmp")]
    )
    return list(file_paths)

def show_progress_window(files, process_function):
    cancel_flag = False  # Local to show_progress_window

    def cancel():
        nonlocal cancel_flag
        cancel_flag = True

    def run_processing():
        def update_progress(index, message):
            progress_bar["value"] = ((index + 1) / len(files)) * 100
            status_label["text"] = message
            log_text.insert(tk.END, f"{message}\n")
            log_text.see(tk.END)

        def finish_progress():
            result_queue.put("done")

        process_function(
            files,
            update_progress=update_progress,
            finish_progress=finish_progress,
            log_hook=lambda msg: log_text.insert(tk.END, f"{msg}\n"),
            cancel_flag=lambda: cancel_flag
        )

    window = tk.Tk()
    window.title("JD File Organizer - Progress")
    window.geometry("600x400")

    status_label = tk.Label(window, text="Starting...", anchor="w")
    status_label.pack(fill="x", padx=10, pady=5)

    progress_bar = ttk.Progressbar(window, length=580, mode="determinate")
    progress_bar.pack(padx=10, pady=5)

    log_text = scrolledtext.ScrolledText(window, wrap=tk.WORD, height=15)
    log_text.pack(fill="both", expand=True, padx=10, pady=5)

    cancel_button = tk.Button(window, text="Cancel", command=cancel)
    cancel_button.pack(pady=5)

    threading.Thread(target=run_processing, daemon=True).start()

    # Poll for "done" signal from background thread
    def poll_queue():
        try:
            msg = result_queue.get_nowait()
        except queue.Empty:
            window.after(100, poll_queue)
            return

        if msg == "done":
            messagebox.showinfo("Done", "All files processed.")
            window.quit()
            window.destroy()

    window.after(100, poll_queue)
    window.mainloop()
