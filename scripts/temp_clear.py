from pathlib import Path

def clear():
    folder_path = Path("./temp")

    for file_path in folder_path.iterdir():
        if file_path.is_file():
            file_path.unlink()
