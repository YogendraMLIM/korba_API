import base64
import re
from pathlib import Path

BASE_UPLOAD_DIR = Path("documents")

DOCUMENT_FIELDS = [
    "aadhaar_copy",
    "electricity_bill",
    "water_bill",
    "sale_deed",
    "property_tax_receipt",
    "building_permission",
    "other_documents",
]


def _safe_filename(filename: str | None, fallback: str) -> str:
    name = Path(filename or fallback).name
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    return name or fallback


def _unique_path(folder: Path, filename: str) -> Path:
    filepath = folder / filename
    if not filepath.exists():
        return filepath

    stem = filepath.stem
    suffix = filepath.suffix
    index = 2
    while True:
        candidate = folder / f"{stem}_{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def _save_upload_file(
    parcel_no: str,
    property_id: str,
    category: str,
    filename: str | None,
    content: bytes,
    fallback_name: str,
) -> str | None:
    if not content:
        return None

    folder = (
        BASE_UPLOAD_DIR
        / category
        / str(parcel_no)
        / str(property_id)
    )
    folder.mkdir(parents=True, exist_ok=True)

    filepath = _unique_path(folder, _safe_filename(filename, fallback_name))
    with open(filepath, "wb") as f:
        f.write(content)

    return filepath.as_posix()


def save_upload_documents(
    parcel_no: str,
    property_id: str,
    documents: dict,
) -> list[dict]:
    saved_documents = []

    for field in DOCUMENT_FIELDS:
        files = documents.get(f"{field}_files", [])
        if not files:
            continue

        for index, upload in enumerate(files, start=1):
            if not isinstance(upload, dict):
                continue

            file_path = _save_upload_file(
                parcel_no=parcel_no,
                property_id=property_id,
                category=field,
                filename=upload.get("filename"),
                content=upload.get("content") or b"",
                fallback_name=f"{field}{index}.bin",
            )
            if file_path:
                saved_documents.append(
                    {
                        "document_type": field,
                        "file_path": file_path,
                    }
                )

    return saved_documents


def save_single_upload_image(
    parcel_no: str,
    property_id: str,
    category: str,
    file_name: str,
    upload: dict | None,
) -> str | None:
    if not isinstance(upload, dict):
        return None

    original_name = _safe_filename(upload.get("filename"), f"{file_name}.bin")
    suffix = Path(original_name).suffix
    fallback_name = f"{file_name}{suffix or '.bin'}"

    return _save_upload_file(
        parcel_no=parcel_no,
        property_id=property_id,
        category=category,
        filename=original_name,
        content=upload.get("content") or b"",
        fallback_name=fallback_name,
    )


def save_base64_documents(
    parcel_no: str,
    property_id: str,
    documents: dict,
) -> list[dict]:
    """
    Save Base64 documents and return document records.

    Returns:
    [
        {
            "document_type": "aadhaar_copy",
            "file_path": "documents/aadhaar_copy/P001/1001/aadhaar_copy1.jpg"
        },
        ...
    ]
    """

    saved_documents = []

    for field in DOCUMENT_FIELDS:

        files = documents.get(f"{field}_files", [])

        if not files:
            continue

        folder = (
            BASE_UPLOAD_DIR
            / field
            / str(parcel_no)
            / str(property_id)
        )

        folder.mkdir(parents=True, exist_ok=True)

        for index, file_data in enumerate(files, start=1):

            if "," in file_data:
                header, encoded = file_data.split(",", 1)

                if "png" in header:
                    ext = ".png"
                elif "pdf" in header:
                    ext = ".pdf"
                elif "jpeg" in header or "jpg" in header:
                    ext = ".jpg"
                else:
                    ext = ".bin"
            else:
                encoded = file_data
                ext = ".jpg"

            filename = f"{field}{index}{ext}"

            filepath = folder / filename

            with open(filepath, "wb") as f:
                f.write(base64.b64decode(encoded))

            saved_documents.append(
                {
                    "document_type": field,
                    "file_path": filepath.as_posix(),
                }
            )

    return saved_documents


def save_single_base64_image(
    parcel_no: str,
    property_id: str,
    category: str,
    file_name: str,
    file_data: str | None,
) -> str | None:
    """
    Save a single Base64 image and return the relative file path.
    """

    if not file_data:
        return None

    if "," in file_data:
        header, encoded = file_data.split(",", 1)

        if "png" in header:
            ext = ".png"
        elif "jpeg" in header or "jpg" in header:
            ext = ".jpg"
        elif "webp" in header:
            ext = ".webp"
        else:
            ext = ".bin"
    else:
        encoded = file_data
        ext = ".jpg"

    folder = (
        BASE_UPLOAD_DIR
        / category
        / str(parcel_no)
        / str(property_id)
    )

    folder.mkdir(parents=True, exist_ok=True)

    filename = f"{file_name}{ext}"
    filepath = folder / filename

    with open(filepath, "wb") as f:
        f.write(base64.b64decode(encoded))

    return filepath.as_posix()
