from tkinter import *
from tkinter import ttk, messagebox

import imap_tools
from imap_tools import MailBox, AND

IMAP_SERVER = "imap.gmail.com"


class EABD:
    def __init__(self, root):
        icon = PhotoImage(file='ico.png')

        self.root = root
        self.root.iconphoto(False, icon)
        self.root.title("Email Attachment Bulk Downloader")

        self.mailbox = None
        self.username_entry = None
        self.password_entry = None

        self.login_screen()

    # ------------------------------ LOGIN SCREEN ------------------------------ #
    def login_screen(self):
        self.root.title("Login")
        self.root.geometry("215x149")
        self.root.resizable(False, False)

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
        except imap_tools.errors.MailboxLoginError:
            print(self.username_entry.get())
            messagebox.showerror("Login Failed", "Invalid username or password")

    # ------------------------------ LOGIN SCREEN ------------------------------ #
    def show_main_screen(self):
        return


if __name__ == "__main__":
    screen = Tk()
    EABD(screen)
    screen.mainloop()
