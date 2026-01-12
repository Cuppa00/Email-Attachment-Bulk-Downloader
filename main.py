import threading
from tkinter import *
from tkinter import ttk, messagebox, filedialog
from imap_tools import MailBox
from datetime import datetime, timedelta
from pathlib import Path


IMAP_SERVER = "imap.gmail.com"


class EABD:
    def __init__(self, root):
        icon = PhotoImage(file='ico.png')

        self.root = root
        self.root.iconphoto(False, icon)
        self.root.resizable(False, False)

        self.mailbox = None
        self.username_entry = None
        self.password_entry = None
        self.folder_var = None
        self.folder_box = None
        self.sender_entry = None
        self.start_date_entry = None
        self.end_date_entry = None
        self.dir_entry = None
        self.progress_win = None
        self.progress_bar = None

        self.login_screen()

    # ------------------------------ LOGIN SCREEN ------------------------------ #
    def login_screen(self):
        self.root.title("Login")
        self.root.geometry("215x149")

        # Padding configuration
        PAD_X = 15
        PAD_Y = 5

        # Username label and entry
        username_label = Label(self.root, text="Username:")
        username_label.grid(row=0, column=0, sticky="w", padx=PAD_X, pady=(PAD_Y, 0))

        self.username_entry = Entry(self.root, width=30)
        self.username_entry.grid(row=1, column=0, padx=PAD_X, pady=(0, PAD_Y))

        # Password label and entry
        password_label = Label(self.root, text="Password:")
        password_label.grid(row=2, column=0, sticky="w", padx=PAD_X, pady=(PAD_Y, 0))

        self.password_entry = Entry(self.root, width=30, show="*")
        self.password_entry.grid(row=3, column=0, padx=PAD_X, pady=(0, PAD_Y))

        # Submit button
        submit_button = Button(self.root, text="Submit", command=self.attempt_login)
        submit_button.grid(row=4, column=0, pady=(10, PAD_Y))

    def attempt_login(self):
        try:
            self.mailbox = MailBox(IMAP_SERVER).login(
                self.username_entry.get(),
                self.password_entry.get()
            )
            self.show_main_screen()
        except Exception:
            print(self.username_entry.get())
            messagebox.showerror("Login Failed", "Invalid username or password")

    # ------------------------------ LOGIN SCREEN ------------------------------ #
    def show_main_screen(self):
        self.clear_screen()

        self.root.title("Email Attachment Bulk Downloader")
        self.root.geometry("450x215")

        PAD_X = 15
        PAD_Y = 5

        # Folder dropdown
        folder_label = Label(self.root, text="Folder:")
        folder_label.grid(row=0, column=0, sticky="e", padx=PAD_X, pady=(15, 0))
        self.folder_var = StringVar()
        self.folder_box = ttk.Combobox(self.root, textvariable=self.folder_var, state="readonly", width=30)
        self.folder_box.grid(row=0, column=1, pady=(15, 0))

        folders = [f.name for f in self.mailbox.folder.list()]
        self.folder_box["values"] = folders
        if folders:
            self.folder_box.current(0)

        # Sender filter
        sender_label = Label(self.root, text="Sender:")
        sender_label.grid(row=1, column=0, sticky="e", padx=PAD_X, pady=PAD_Y)
        self.sender_entry = Entry(self.root, width=32)
        self.sender_entry.grid(row=1, column=1, pady=PAD_Y)

        # Date range
        start_date_label = Label(self.root, text="Start date (DD-MM-YYYY):")
        start_date_label.grid(row=2, column=0, sticky="e", padx=PAD_X, pady=PAD_Y)
        self.start_date_entry = Entry(self.root, width=32)
        self.start_date_entry.grid(row=2, column=1, pady=PAD_Y)

        end_date_label = Label(self.root, text="End date (DD-MM-YYYY):")
        end_date_label.grid(row=3, column=0, sticky="e", padx=PAD_X, pady=PAD_Y)
        self.end_date_entry = Entry(self.root, width=32)
        self.end_date_entry.grid(row=3, column=1, pady=PAD_Y)

        # Download directory
        download_dir = Label(self.root, text="Download directory:")
        download_dir.grid(row=4, column=0, sticky="e", padx=PAD_X, pady=PAD_Y)
        self.dir_entry = Entry(self.root, width=32)
        self.dir_entry.grid(row=4, column=1, pady=PAD_Y)

        dir_button = Button(self.root, text="Browse", command=self.pick_directory)
        dir_button.grid(row=4, column=2)

        # Start download
        start_download = Button(self.root, text="Download Attachments", command=self.start_download)
        start_download.grid(row=5, column=1, pady=15, sticky="w")

    # --------------------------------- WORKERS -------------------------------- #

    def start_download(self):
        if not self.dir_entry.get():
            messagebox.showerror("Error", "Select a download directory")
            return

        # Create a mew window for progress
        self.progress_win = Toplevel(self.root)
        self.progress_win.title("Downloading Attachments")
        self.progress_win.geometry("400x120")

        Label(self.progress_win, text="Downloading attachments...").pack(pady=15)

        # Progress bar
        self.progress_bar = ttk.Progressbar(self.progress_win, mode="determinate", length=350)
        self.progress_bar.pack(pady=10)

        # Start downloading in background thread
        threading.Thread(target=self.download_worker, daemon=True).start()

    def download_worker(self):
        try:
            self.mailbox.folder.set(self.folder_var.get())

            criteria = self.build_criteria()
            if criteria:
                print("IMAP criteria:", criteria)
                messages = list(self.mailbox.fetch(criteria=criteria, mark_seen=False, reverse=True))
            else:
                print("IMAP criteria: <none>")
                messages = list(self.mailbox.fetch(mark_seen=False, reverse=True))

            print("Messages found:", len(messages))

            attachments = []

            for msg in messages:
                for att in msg.attachments:
                    # Skip inline attachments or any without filename
                    if not att.filename:
                        continue
                    if att.content_disposition == 'inline':
                        continue
                    attachments.append(att)

            total = len(attachments)
            self.progress_bar["maximum"] = total

            download_dir = Path(self.dir_entry.get())
            download_dir.mkdir(exist_ok=True)

            for i, att in enumerate(attachments, start=1):
                path = self.get_unique_path(download_dir, att.filename)
                with open(path, 'wb') as f:
                    f.write(att.payload)

                # Schedule UI update on main thread
                self.root.after(0, self.update_progress, i)

            messagebox.showinfo("Completed", "All attachments downloaded")
            self.progress_win.destroy()     # close the progress window

        except Exception as exception:
            messagebox.showerror("Error", str(exception))
            if hasattr(self, 'progress_win') and self.progress_win.winfo_exists():
                self.progress_win.destroy()

    # --------------------------------- HELPERS -------------------------------- #

    def build_criteria(self):
        parts = []

        sender = self.sender_entry.get().strip()
        if sender:
            parts.append(f'FROM "{sender}"')

        start = self.start_date_entry.get().strip()
        if start:
            try:
                start_date = datetime.strptime(start, "%d-%m-%Y")
                parts.append(f'SINCE {start_date.strftime("%d-%b-%Y")}')
            except ValueError:
                messagebox.showerror("Error", "Invalid start date format. Use DD-MM-YYYY")
                return None

        end = self.end_date_entry.get().strip()
        if end:
            try:
                end_date = datetime.strptime(end, "%d-%m-%Y") + timedelta(days=1)
                parts.append(f'BEFORE {end_date.strftime("%d-%b-%Y")}')
            except ValueError:
                messagebox.showerror("Error", "Invalid end date format. Use DD-MM-YYYY")
                return None

        if not parts:
            return None

        return " ".join(parts)

    def pick_directory(self):
        directory = filedialog.askdirectory()
        self.dir_entry.delete(0, END)
        self.dir_entry.insert(0, directory)

    # Prevent duplicate filenames
    def get_unique_path(self, directory: Path, filename: str):
        base = Path(filename).stem
        suffix = Path(filename).suffix
        candidate = directory / filename
        counter = 1

        while candidate.exists():
            candidate = directory / f"{base} ({counter}){suffix}"
            counter += 1

        return candidate

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def update_progress(self, value):
        self.progress_bar["value"] = value


if __name__ == "__main__":
    screen = Tk()
    EABD(screen)
    screen.mainloop()
