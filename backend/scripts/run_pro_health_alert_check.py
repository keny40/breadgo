import json
import sys
from collections import Counter
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.db.session import SessionLocal
from app.services.pro_daily_brief_service import build_admin_pro_operations_health
from app.services.pro_health_alert_service import generate_pro_health_alerts
from app.services.pro_operations_audit_service import create_pro_operation_audit_log


def main() -> int:
    db = SessionLocal()
    try:
        health = build_admin_pro_operations_health(db)
        generated_count = 0
        skipped_count = 0
        severity_counts: dict[str, int] = {}
        message = "Pro health status is OK. No internal health alerts were generated."

        if health.overall_status in {"WARNING", "CRITICAL"}:
            result = generate_pro_health_alerts(db, health)
            generated_count = result.generated_count
            skipped_count = result.skipped_count
            severity_counts = dict(Counter(alert.severity for alert in result.alerts))
            message = result.message

        create_pro_operation_audit_log(
            db,
            actor=None,
            action_type="RUN_HEALTH_ALERT_CHECK_CLI",
            target_type="HEALTH_ALERT",
            status_value="SUCCESS",
            message="Pro Health Alert scheduler CLI를 실행했습니다.",
            metadata_json={
                "overall_status": health.overall_status,
                "generated_count": generated_count,
                "skipped_count": skipped_count,
            },
        )

        output = {
            "overall_status": health.overall_status,
            "generated_count": generated_count,
            "skipped_count": skipped_count,
            "severity_counts": severity_counts,
            "message": message,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2, default=str))
        return 1 if health.overall_status == "CRITICAL" else 0
    except Exception as exc:
        db.rollback()
        try:
            create_pro_operation_audit_log(
                db,
                actor=None,
                action_type="RUN_HEALTH_ALERT_CHECK_CLI",
                target_type="HEALTH_ALERT",
                status_value="FAILED",
                message=str(exc)[:500],
                metadata_json={"reason": str(exc)[:500]},
            )
        except Exception:
            db.rollback()
        print(json.dumps({"status": "FAILED", "message": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
