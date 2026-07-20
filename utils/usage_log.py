from fastapi import Depends
from datetime import datetime, timezone

from sqlalchemy import text

def save_api_log(
    engine,
    kpi_name,
    username,
    indus_circle=None,
    district=None
):
    query = text("""
        INSERT INTO weatherdata.api_request_log
        (
            kpi_name,
            username,
            indus_circle,
            district,
            inserted_at
        )
        VALUES
        (
            :kpi_name,
            :username,
            :indus_circle,
            :district,
            :inserted_at
        )
    """)

    with engine.begin() as conn:
        conn.execute(
            query,
            {
                "kpi_name": kpi_name,
                "username": username,
                "indus_circle": indus_circle,
                "district": district,
                "inserted_at": datetime.now(timezone.utc)
            }
        )