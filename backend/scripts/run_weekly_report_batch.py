import json
import sys
from decimal import Decimal
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from pydantic import BaseModel

from app.db.session import SessionLocal
from app.services.pro_daily_brief_service import create_admin_weekly_report_batch_run


def to_jsonable(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    return value


def main() -> int:
    db = SessionLocal()
    try:
        batch_run = create_admin_weekly_report_batch_run(
            db,
            run_type="SCHEDULED",
            skip_if_completed=True,
        )
        print(json.dumps(to_jsonable(batch_run), ensure_ascii=False, indent=2, default=str))
        if batch_run.status == "FAILED":
            return 1
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
