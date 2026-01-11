from imap_tools import MailBox
from pathlib import Path
import uuid

DOWNLOAD_DIR = Path("attachments")      # Download directory of attachments
DOWNLOAD_DIR.mkdir(exist_ok=True)       # Create directory

MAIL_USERNAME = ""      # Email username
MAIL_PASSWORD = ""      # Email APP password

TARGET_FOLDER = ""      # Target email folder


def main():
    with MailBox("imap.gmail.com").login(MAIL_USERNAME, MAIL_PASSWORD) as mb:
        mb.folder.set(TARGET_FOLDER)

        for msg in mb.fetch():
            for att in msg.attachments:
                filename = att.filename or f"attachment_{uuid.uuid4().hex}"
                file_path = DOWNLOAD_DIR / filename

                with open(file_path, 'wb') as f:
                    f.write(att.payload)


if __name__ == "__main__":
    main()
