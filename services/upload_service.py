from pathlib import Path
import shutil
from fastapi import UploadFile
from fastapi import UploadFile

from pathlib import Path
import shutil
from fastapi import UploadFile

BASE_UPLOAD_DIR = Path("documents")


def save_document(
    property_id: str,
    document_name: str,
    file: UploadFile,
) -> str:
    """
    Saves as:
    documents/<document_name>/<property_id>/<document_name>.<ext>
    """

    extension = Path(file.filename).suffix.lower()

    folder = BASE_UPLOAD_DIR / document_name / property_id
    folder.mkdir(parents=True, exist_ok=True)

    filename = f"{document_name}{extension}"

    file_path = folder / filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path.as_posix()




def save_documents(
    property_id: str,
    documents: dict,
) -> dict:

    saved_documents = {}

    for key, value in documents.items():

        if value is None:
            saved_documents[key] = None
            continue

        if not isinstance(value, UploadFile):
            saved_documents[key] = value
            continue

        saved_documents[key] = save_document(
            property_id=property_id,
            document_name=key,
            file=value
        )

    return saved_documents