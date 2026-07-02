import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE_URL = os.environ.get("BREADGO_API_BASE_URL", "http://localhost:8000").rstrip("/")
PASSWORD = "12345678"
SMOKE_REGION = {
    "sido": "서울특별시",
    "sigungu": "강남구",
    "dong": "역삼동",
}

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@dataclass
class ApiResponse:
    status_code: int
    body: Any


class SmokeTestError(Exception):
    def __init__(self, step: str, status_code: int | None, body: Any) -> None:
        self.step = step
        self.status_code = status_code
        self.body = body
        super().__init__(step)


def print_pass(step: str) -> None:
    print(f"[PASS] {step}")


def print_fail(error: SmokeTestError) -> None:
    print(f"[FAIL] {error.step}")
    print(f"status_code: {error.status_code if error.status_code is not None else 'N/A'}")
    print("response_body:")
    if isinstance(error.body, str):
        print(error.body)
    else:
        print(json.dumps(error.body, ensure_ascii=False, indent=2))


def decode_body(raw_body: bytes) -> Any:
    if not raw_body:
        return None
    text = raw_body.decode("utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def request_json(
    step: str,
    method: str,
    path: str,
    token: str | None = None,
    payload: dict[str, Any] | None = None,
) -> ApiResponse:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(
        url=f"{BASE_URL}{path}",
        data=body,
        headers=headers,
        method=method,
    )

    try:
        with urlopen(request, timeout=15) as response:
            return ApiResponse(
                status_code=response.status,
                body=decode_body(response.read()),
            )
    except HTTPError as exc:
        raise SmokeTestError(step, exc.code, decode_body(exc.read())) from exc
    except URLError as exc:
        raise SmokeTestError(step, None, str(exc.reason)) from exc
    except TimeoutError as exc:
        raise SmokeTestError(step, None, "Request timed out") from exc


def expect_status(step: str, response: ApiResponse, expected: set[int]) -> Any:
    if response.status_code not in expected:
        raise SmokeTestError(step, response.status_code, response.body)
    print_pass(step)
    return response.body


def expect_dict_with_keys(step: str, body: Any, keys: set[str], status_code: int = 200) -> dict[str, Any]:
    if not isinstance(body, dict) or not keys.issubset(body.keys()):
        raise SmokeTestError(
            step,
            status_code,
            {
                "expected_keys": sorted(keys),
                "actual_body": body,
            },
        )
    return body


def expect_http_error_status(
    step: str,
    method: str,
    path: str,
    token: str | None,
    expected: set[int],
    payload: dict[str, Any] | None = None,
) -> Any:
    try:
        response = request_json(step=step, method=method, path=path, token=token, payload=payload)
    except SmokeTestError as exc:
        if exc.status_code in expected:
            print_pass(step)
            return exc.body
        raise
    raise SmokeTestError(step, response.status_code, response.body)


def login(email: str, label: str) -> str:
    body = expect_status(
        label,
        request_json(
            step=label,
            method="POST",
            path="/api/v1/auth/login",
            payload={"email": email, "password": PASSWORD},
        ),
        {200},
    )
    token = body.get("access_token") if isinstance(body, dict) else None
    if not token:
        raise SmokeTestError(label, 200, body)
    return token


def is_local_base_url() -> bool:
    return BASE_URL.startswith("http://localhost") or BASE_URL.startswith("http://127.0.0.1")


def seed_local_demo_data_if_available() -> bool:
    if not is_local_base_url():
        return False

    try:
        from seed_demo import main as seed_demo_main
    except Exception as exc:  # pragma: no cover - best-effort fallback for local smoke only.
        print(f"[WARN] Local demo seed import failed: {exc}")
        return False

    print("[INFO] Local region product data is missing. Re-seeding demo data and retrying once.")
    seed_demo_main()
    return True


def verify_adapter_mock_readiness() -> None:
    try:
        from app.services.delivery_provider_service import assert_mock_delivery_provider_ready
        from app.services.external_integration_readiness_service import assert_external_integration_readiness_ready
        from app.services.notification_provider_service import assert_mock_notification_provider_ready
        from app.services.payment_provider_service import assert_mock_payment_provider_ready
        from app.services.pos_provider_service import assert_mock_pos_provider_ready
    except Exception as exc:
        raise SmokeTestError("Adapter mock readiness imports", None, str(exc)) from exc

    try:
        assert_mock_payment_provider_ready()
    except Exception as exc:
        raise SmokeTestError("Payment provider adapter mock dry-run", None, str(exc)) from exc
    print_pass("Payment provider adapter mock dry-run")

    try:
        assert_mock_delivery_provider_ready()
    except Exception as exc:
        raise SmokeTestError("Delivery provider adapter mock dry-run", None, str(exc)) from exc
    print_pass("Delivery provider adapter mock dry-run")

    try:
        assert_mock_notification_provider_ready()
    except Exception as exc:
        raise SmokeTestError("Notification provider adapter mock dry-run", None, str(exc)) from exc
    print_pass("Notification provider adapter mock dry-run")

    try:
        assert_mock_pos_provider_ready()
    except Exception as exc:
        raise SmokeTestError("POS provider adapter mock dry-run", None, str(exc)) from exc
    print_pass("POS provider adapter mock dry-run")

    try:
        assert_external_integration_readiness_ready()
    except Exception as exc:
        raise SmokeTestError("External integration readiness dry-run", None, str(exc)) from exc
    print_pass("External integration readiness dry-run")


def region_products_path() -> str:
    return f"/api/v1/regions/products?{urlencode(SMOKE_REGION)}"


def describe_region_expectation() -> dict[str, Any]:
    return {
        "expected_region": SMOKE_REGION,
        "expected_product_condition": {
            "status": "ACTIVE",
            "quantity": "> 0",
        },
        "hint": "Run `python scripts/seed_demo.py` for local smoke data.",
    }


def load_region_products(seed_retry: bool = True) -> list[dict[str, Any]]:
    path = region_products_path()
    products = expect_status(
        "Region products found",
        request_json("Region products found", "GET", path),
        {200},
    )
    if isinstance(products, list) and products:
        return products

    if seed_retry and seed_local_demo_data_if_available():
        products = expect_status(
            "Region products found after local seed",
            request_json("Region products found after local seed", "GET", path),
            {200},
        )
        if isinstance(products, list) and products:
            return products

    raise SmokeTestError(
        "Region products found",
        200,
        {
            **describe_region_expectation(),
            "actual_products": products,
        },
    )


def main() -> int:
    try:
        health = expect_status(
            "Health check",
            request_json("Health check", "GET", "/health"),
            {200},
        )
        if not isinstance(health, dict) or health.get("status") != "ok":
            raise SmokeTestError("Health check", 200, health)

        verify_adapter_mock_readiness()

        google_oauth_status = expect_status(
            "Google OAuth status loaded",
            request_json(
                step="Google OAuth status loaded",
                method="GET",
                path="/api/v1/auth/google/status",
            ),
            {200},
        )
        expect_dict_with_keys(
            "Google OAuth status loaded",
            google_oauth_status,
            {"enabled", "message"},
        )

        unique_suffix = str(int(__import__("time").time() * 1000))
        expect_http_error_status(
            "Public signup blocks merchant role",
            "POST",
            "/api/v1/auth/register",
            None,
            {403},
            payload={
                "email": f"blocked-merchant-{unique_suffix}@breadgo.test",
                "password": PASSWORD,
                "full_name": "Blocked Merchant",
                "role": "merchant",
            },
        )
        expect_http_error_status(
            "Public signup blocks admin role",
            "POST",
            "/api/v1/auth/register",
            None,
            {403},
            payload={
                "email": f"blocked-admin-{unique_suffix}@breadgo.test",
                "password": PASSWORD,
                "full_name": "Blocked Admin",
                "role": "admin",
            },
        )

        application_payload = {
            "store_name": f"Smoke Bakery {unique_suffix}",
            "owner_name": "Smoke Owner",
            "email": f"merchant-apply-{unique_suffix}@breadgo.test",
            "password": PASSWORD,
            "phone": "010-0000-0000",
            "business_registration_number": f"SMOKE-{unique_suffix}",
            "address": "서울특별시 강남구 테스트로 1",
            "region_sido": "서울특별시",
            "region_sigungu": "강남구",
            "region_dong": "역삼동",
            "product_category": "베이커리",
            "pickup_available_time": "18:00-21:00",
            "note": "Smoke test merchant application",
        }
        application = expect_status(
            "Merchant application created",
            request_json(
                step="Merchant application created",
                method="POST",
                path="/api/v1/merchants/apply",
                payload=application_payload,
            ),
            {201},
        )
        application_id = application.get("id") if isinstance(application, dict) else None
        if not application_id or application.get("status") != "PENDING":
            raise SmokeTestError("Merchant application created", 201, application)

        rejection_payload = {
            **application_payload,
            "store_name": f"Reject Bakery {unique_suffix}",
            "email": f"merchant-reject-{unique_suffix}@breadgo.test",
            "business_registration_number": f"REJECT-{unique_suffix}",
        }
        rejection_application = expect_status(
            "Merchant application for rejection created",
            request_json(
                step="Merchant application for rejection created",
                method="POST",
                path="/api/v1/merchants/apply",
                payload=rejection_payload,
            ),
            {201},
        )
        rejection_application_id = rejection_application.get("id") if isinstance(rejection_application, dict) else None
        if not rejection_application_id:
            raise SmokeTestError("Merchant application for rejection created", 201, rejection_application)

        customer_token = login("customer@breadgo.test", "Customer login")

        expect_http_error_status(
            "Customer direct merchant register blocked",
            "POST",
            "/api/v1/merchants/register",
            customer_token,
            {403},
            payload={
                "business_name": "Blocked Merchant",
                "business_registration_number": f"DIRECT-{unique_suffix}",
                "representative_name": "Blocked",
                "phone_number": "010-1111-1111",
            },
        )

        products = load_region_products()

        product = next(
            (
                item
                for item in products
                if item.get("status") == "ACTIVE" and int(item.get("quantity", 0)) > 0
            ),
            None,
        )
        if product is None and seed_local_demo_data_if_available():
            products = load_region_products(seed_retry=False)
            product = next(
                (
                    item
                    for item in products
                    if item.get("status") == "ACTIVE" and int(item.get("quantity", 0)) > 0
                ),
                None,
            )
        if product is None:
            raise SmokeTestError(
                "Active product with stock found",
                200,
                {
                    **describe_region_expectation(),
                    "actual_products": products,
                },
            )
        print_pass("Active product with stock found")

        reservation = expect_status(
            "Reservation created",
            request_json(
                step="Reservation created",
                method="POST",
                path="/api/v1/reservations",
                token=customer_token,
                payload={"product_id": product["id"], "quantity": 1},
            ),
            {201},
        )
        reservation_id = reservation.get("id") if isinstance(reservation, dict) else None
        pickup_code = reservation.get("pickup_code") if isinstance(reservation, dict) else None
        if not reservation_id or not pickup_code:
            raise SmokeTestError("Reservation created", 201, reservation)

        ready_payment = expect_status(
            "Mock payment ready",
            request_json(
                step="Mock payment ready",
                method="POST",
                path="/api/v1/payments/mock/ready",
                token=customer_token,
                payload={"reservation_id": reservation_id, "method": "MOCK_CARD"},
            ),
            {201},
        )
        payment_id = ready_payment.get("id") if isinstance(ready_payment, dict) else None
        if not payment_id:
            raise SmokeTestError("Mock payment ready", 201, ready_payment)

        paid_payment = expect_status(
            "Mock payment confirmed",
            request_json(
                step="Mock payment confirmed",
                method="POST",
                path="/api/v1/payments/mock/confirm",
                token=customer_token,
                payload={"payment_id": payment_id},
            ),
            {200},
        )
        if not isinstance(paid_payment, dict) or paid_payment.get("status") != "PAID":
            raise SmokeTestError("Mock payment confirmed", 200, paid_payment)

        my_reservations = expect_status(
            "My reservations loaded",
            request_json(
                step="My reservations loaded",
                method="GET",
                path="/api/v1/reservations/me",
                token=customer_token,
            ),
            {200},
        )
        if not isinstance(my_reservations, list) or not any(
            item.get("id") == reservation_id and item.get("pickup_code") == pickup_code
            for item in my_reservations
        ):
            raise SmokeTestError("My reservations loaded", 200, my_reservations)

        merchant_token = login("merchant@breadgo.test", "Merchant login")

        picked_up = expect_status(
            "Pickup confirmed",
            request_json(
                step="Pickup confirmed",
                method="POST",
                path="/api/v1/reservations/pickup/confirm",
                token=merchant_token,
                payload={"pickup_code": pickup_code},
            ),
            {200},
        )
        reservation_body = picked_up.get("reservation") if isinstance(picked_up, dict) else None
        if not isinstance(reservation_body, dict) or reservation_body.get("status") != "PICKED_UP":
            raise SmokeTestError("Pickup confirmed", 200, picked_up)

        inventory_events = expect_status(
            "Merchant inventory events loaded",
            request_json(
                step="Merchant inventory events loaded",
                method="GET",
                path="/api/v1/merchant/pro/inventory-events?limit=10",
                token=merchant_token,
            ),
            {200},
        )
        if not isinstance(inventory_events, list):
            raise SmokeTestError("Merchant inventory events loaded", 200, inventory_events)
        if not any(
            isinstance(item, dict)
            and item.get("product_id") == product["id"]
            and item.get("source_type") == "RESERVATION"
            for item in inventory_events
        ):
            raise SmokeTestError(
                "Merchant inventory events loaded",
                200,
                {
                    "expected": "reservation-related inventory event for smoke product",
                    "actual_events": inventory_events,
                },
            )

        admin_token = login("admin@breadgo.test", "Admin login")

        applications = expect_status(
            "Admin merchant applications loaded",
            request_json(
                step="Admin merchant applications loaded",
                method="GET",
                path="/api/v1/admin/merchant-applications",
                token=admin_token,
            ),
            {200},
        )
        if not isinstance(applications, list) or not any(item.get("id") == application_id for item in applications):
            raise SmokeTestError("Admin merchant applications loaded", 200, applications)

        application_detail = expect_status(
            "Admin merchant application detail loaded",
            request_json(
                step="Admin merchant application detail loaded",
                method="GET",
                path=f"/api/v1/admin/merchant-applications/{application_id}",
                token=admin_token,
            ),
            {200},
        )
        expect_dict_with_keys(
            "Admin merchant application detail loaded",
            application_detail,
            {"id", "store_name", "status"},
        )

        approved_application = expect_status(
            "Admin merchant application approved",
            request_json(
                step="Admin merchant application approved",
                method="POST",
                path=f"/api/v1/admin/merchant-applications/{application_id}/approve",
                token=admin_token,
            ),
            {200},
        )
        approved_body = expect_dict_with_keys(
            "Admin merchant application approved",
            approved_application,
            {"application", "merchant"},
        )
        if approved_body["application"].get("status") != "APPROVED" or approved_body["merchant"].get("status") != "APPROVED":
            raise SmokeTestError("Admin merchant application approved", 200, approved_application)
        approved_merchant_login = expect_status(
            "Approved merchant application login",
            request_json(
                step="Approved merchant application login",
                method="POST",
                path="/api/v1/auth/login",
                payload={"email": application_payload["email"], "password": PASSWORD},
            ),
            {200},
        )
        approved_merchant_body = expect_dict_with_keys(
            "Approved merchant application login",
            approved_merchant_login,
            {"access_token", "user"},
        )
        if str(approved_merchant_body["user"].get("role")).lower() != "merchant":
            raise SmokeTestError("Approved merchant application login", 200, approved_merchant_login)
        approved_merchant_token = approved_merchant_body["access_token"]
        approved_merchant_stores = expect_status(
            "Approved merchant default store loaded",
            request_json(
                step="Approved merchant default store loaded",
                method="GET",
                path="/api/v1/stores/me",
                token=approved_merchant_token,
            ),
            {200},
        )
        if not isinstance(approved_merchant_stores, list) or len(approved_merchant_stores) != 1:
            raise SmokeTestError("Approved merchant default store loaded", 200, approved_merchant_stores)
        approved_store = approved_merchant_stores[0]
        if approved_store.get("name") != application_payload["store_name"] or approved_store.get("address") != application_payload["address"]:
            raise SmokeTestError("Approved merchant default store loaded", 200, approved_merchant_stores)

        rejected_application = expect_status(
            "Admin merchant application rejected",
            request_json(
                step="Admin merchant application rejected",
                method="POST",
                path=f"/api/v1/admin/merchant-applications/{rejection_application_id}/reject",
                token=admin_token,
                payload={"reason": "Smoke test rejection"},
            ),
            {200},
        )
        if not isinstance(rejected_application, dict) or rejected_application.get("status") != "REJECTED":
            raise SmokeTestError("Admin merchant application rejected", 200, rejected_application)

        summary = expect_status(
            "Admin summary loaded",
            request_json(
                step="Admin summary loaded",
                method="GET",
                path="/api/v1/admin/summary",
                token=admin_token,
            ),
            {200},
        )
        if not isinstance(summary, dict) or "total_users" not in summary:
            raise SmokeTestError("Admin summary loaded", 200, summary)

        operations_summary = expect_status(
            "Admin Pro Operations summary loaded",
            request_json(
                step="Admin Pro Operations summary loaded",
                method="GET",
                path="/api/v1/admin/pro/operations/summary",
                token=admin_token,
            ),
            {200},
        )
        expect_dict_with_keys(
            "Admin Pro Operations summary loaded",
            operations_summary,
            {"batch", "delivery", "notifications", "attention"},
        )

        operations_health = expect_status(
            "Admin Pro Operations health loaded",
            request_json(
                step="Admin Pro Operations health loaded",
                method="GET",
                path="/api/v1/admin/pro/operations/health",
                token=admin_token,
            ),
            {200},
        )
        expect_dict_with_keys(
            "Admin Pro Operations health loaded",
            operations_health,
            {"overall_status", "checked_at", "health_messages"},
        )

        external_readiness = expect_status(
            "Admin external integration readiness loaded",
            request_json(
                step="Admin external integration readiness loaded",
                method="GET",
                path="/api/v1/admin/pro/operations/external-integrations/readiness",
                token=admin_token,
            ),
            {200},
        )
        readiness_body = expect_dict_with_keys(
            "Admin external integration readiness loaded",
            external_readiness,
            {"overall_status", "external_calls_enabled", "items", "dry_runs"},
        )
        if readiness_body.get("external_calls_enabled") is not False:
            raise SmokeTestError("Admin external integration readiness loaded", 200, external_readiness)
        readiness_areas = {
            item.get("area")
            for item in readiness_body.get("items", [])
            if isinstance(item, dict) and item.get("external_calls_enabled") is False
        }
        if not {"PAYMENT", "DELIVERY", "NOTIFICATION", "POS"}.issubset(readiness_areas):
            raise SmokeTestError("Admin external integration readiness loaded", 200, external_readiness)

        health_alerts = expect_status(
            "Admin Pro Health Alerts list loaded",
            request_json(
                step="Admin Pro Health Alerts list loaded",
                method="GET",
                path="/api/v1/admin/pro/operations/health/alerts",
                token=admin_token,
            ),
            {200},
        )
        expect_dict_with_keys(
            "Admin Pro Health Alerts list loaded",
            health_alerts,
            {"alerts", "total_count"},
        )

        batch_runs = expect_status(
            "Admin Weekly Report batch runs loaded",
            request_json(
                step="Admin Weekly Report batch runs loaded",
                method="GET",
                path="/api/v1/admin/pro/weekly-report/batch-runs",
                token=admin_token,
            ),
            {200},
        )
        batch_runs_body = expect_dict_with_keys(
            "Admin Weekly Report batch runs loaded",
            batch_runs,
            {"summary", "batch_runs"},
        )
        batch_run_items = batch_runs_body.get("batch_runs")
        if not isinstance(batch_run_items, list):
            raise SmokeTestError("Admin Weekly Report batch runs loaded", 200, batch_runs)

        if batch_run_items:
            batch_run_id = batch_run_items[0].get("id") if isinstance(batch_run_items[0], dict) else None
            if not batch_run_id:
                raise SmokeTestError("Admin Weekly Report batch detail loaded", 200, batch_runs)
            batch_run_detail = expect_status(
                "Admin Weekly Report batch detail loaded",
                request_json(
                    step=f"Admin Weekly Report batch detail loaded ({batch_run_id})",
                    method="GET",
                    path=f"/api/v1/admin/pro/weekly-report/batch-runs/{batch_run_id}",
                    token=admin_token,
                ),
                {200},
            )
            expect_dict_with_keys(
                "Admin Weekly Report batch detail loaded",
                batch_run_detail,
                {"id", "run_type", "status", "items"},
            )
        else:
            print_pass("Admin Weekly Report batch detail skipped (no batch runs)")

        expect_http_error_status(
            "Merchant blocked from Admin Pro Operations summary",
            "GET",
            "/api/v1/admin/pro/operations/summary",
            merchant_token,
            {403},
        )

        expect_http_error_status(
            "Merchant blocked from Admin merchant applications",
            "GET",
            "/api/v1/admin/merchant-applications",
            merchant_token,
            {403},
        )

        expect_http_error_status(
            "Merchant blocked from Admin external integration readiness",
            "GET",
            "/api/v1/admin/pro/operations/external-integrations/readiness",
            merchant_token,
            {403},
        )

        print("[PASS] BreadGo MVP smoke test completed")
        return 0
    except SmokeTestError as exc:
        print_fail(exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
