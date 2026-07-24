from nanoid import generate
from sqlalchemy.orm import Session

DIGITS = "0123456789"

def generate_unique_id(
    db: Session,
    model,
    field_name: str,
    size: int = 6,
    prefix: str = "",
    max_attempts: int = 10,
) -> str:
    """
    Generate a unique ID by checking the database.

    Args:
        db: SQLAlchemy session
        model: SQLAlchemy model class
        field_name: Column name to check
        size: NanoID length
        prefix: Optional prefix (e.g. SUR, SVR)
        max_attempts: Maximum retry attempts

    Returns:
        Unique ID string
    """
    column = getattr(model, field_name)

    for _ in range(max_attempts):
        unique_id = f"{prefix}{generate(DIGITS, size)}"

        exists = db.query(model).filter(column == unique_id).first()
        if not exists:
            return unique_id
        
    raise Exception("Unable to generate a unique ID.")

