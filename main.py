from imap_tools import MailBox
from pathlib import Path

DOWNLOAD_DIR = Path("attachments")
DOWNLOAD_DIR.mkdir(exist_ok=True)

MAIL_USERNAME = ""
MAIL_PASSWORD = ""

TARGET_FOLDER = ""


# Function to prevent duplicate filenames
def get_unique_path(directory: Path, filename: str) -> Path:
    base = Path(filename).stem
    suffix = Path(filename).suffix

    candidate = directory / filename
    counter = 1

    while candidate.exists():
        candidate = directory / f"{base} ({counter}){suffix}"
        counter += 1

    return candidate


# Email attachment downloader
def download_attachments():
    with MailBox("imap.gmail.com").login(MAIL_USERNAME, MAIL_PASSWORD) as mb:
        mb.folder.set(TARGET_FOLDER)

        for msg in mb.fetch():
            for att in msg.attachments:
                if not att.filename:
                    continue  # skip unnamed attachments
                if att.content_disposition == 'inline':
                    continue

                file_path = get_unique_path(DOWNLOAD_DIR, att.filename)

                with open(file_path, 'wb') as f:
                    f.write(att.payload)


def main():
    download_attachments()


if __name__ == "__main__":
    main()
