"use client";

/* eslint-disable @next/next/no-img-element */

import { ChangeEvent, Fragment, useEffect, useState } from "react";
import type { ReactNode } from "react";
import Link from "next/link";
import { EmptyState, PageHeader, StatCard, StatusBadge } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import {
  deliveryStatusLabel,
  deliveryStatuses,
  type AdminSummary,
  type AuthUser,
  type Merchant,
  type Payment,
  type Product,
  type Reservation,
  type ReservationHistory,
  type Store,
} from "@/lib/types";

const merchantStatuses = ["PENDING", "APPROVED", "REJECTED", "SUSPENDED"];

function historyEventLabel(value: string) {
  const labels: Record<string, string> = {
    RESERVATION_CREATED: "예약 생성",
    PAYMENT_COMPLETED: "결제 완료",
    PICKUP_CONFIRMED: "픽업 완료",
    DELIVERY_STATUS_CHANGED: "배송 상태 변경",
    RESERVATION_CANCELLED: "예약 취소",
    MOCK_REFUND_PROCESSED: "Mock 환불 처리",
    SETTLEMENT_STATUS_CHANGED: "정산 상태 변경",
    RESERVATION_STATUS_CHANGED: "예약 상태 변경",
  };
  return labels[value] || value;
}

export default function AdminPage() {
  const guard = useRoleGuard("ADMIN");
  const [summary, setSummary] = useState<AdminSummary | null>(null);
  const [users, setUsers] = useState<AuthUser[]>([]);
  const [merchants, setMerchants] = useState<Merchant[]>([]);
  const [stores, setStores] = useState<Store[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [historyByReservation, setHistoryByReservation] = useState<Record<string, ReservationHistory[]>>({});
  const [expandedHistoryId, setExpandedHistoryId] = useState<string | null>(null);
  const [historyLoadingId, setHistoryLoadingId] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    if (!guard.allowed) {
      return;
    }

    let cancelled = false;

    async function loadAdminDashboard() {
      setMessage("");
      setIsError(false);

      try {
        const me = await apiFetch<AuthUser>("/api/v1/auth/me", {}, true);
        if (cancelled) {
          return;
        }

        if (me.role.toLowerCase() !== "admin") {
          setIsError(true);
          setMessage("관리자 권한이 필요합니다.");
          return;
        }

        const [summaryData, userData, merchantData, storeData, productData, reservationData, paymentData] =
          await Promise.all([
            apiFetch<AdminSummary>("/api/v1/admin/summary", {}, true),
            apiFetch<AuthUser[]>("/api/v1/admin/users", {}, true),
            apiFetch<Merchant[]>("/api/v1/admin/merchants", {}, true),
            apiFetch<Store[]>("/api/v1/admin/stores", {}, true),
            apiFetch<Product[]>("/api/v1/admin/products", {}, true),
            apiFetch<Reservation[]>("/api/v1/admin/reservations", {}, true),
            apiFetch<Payment[]>("/api/v1/admin/payments", {}, true),
          ]);

        if (cancelled) {
          return;
        }

        setSummary(summaryData);
        setUsers(userData);
        setMerchants(merchantData);
        setStores(storeData);
        setProducts(productData);
        setReservations(reservationData);
        setPayments(paymentData);
        setMessage("관리자 데이터를 불러왔습니다.");
      } catch (error) {
        if (cancelled) {
          return;
        }
        setIsError(true);
        setMessage(friendlyErrorMessage(error));
      }
    }

    void loadAdminDashboard();
    return () => {
      cancelled = true;
    };
  }, [guard.allowed]);

  async function updateMerchantStatus(merchantId: string, event: ChangeEvent<HTMLSelectElement>) {
    const nextStatus = event.target.value;
    setMessage("");
    setIsError(false);

    try {
      const updated = await apiFetch<Merchant>(
        `/api/v1/admin/merchants/${merchantId}/status`,
        {
          method: "PATCH",
          body: JSON.stringify({ status: nextStatus }),
        },
        true,
      );
      setMerchants((current) =>
        current.map((merchant) => (merchant.id === merchantId ? updated : merchant)),
      );
      setMessage(`${updated.business_name} 상태가 ${updated.status}(으)로 변경되었습니다.`);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  async function updateReservationDeliveryStatus(
    reservationId: string,
    event: ChangeEvent<HTMLSelectElement>,
  ) {
    const nextStatus = event.target.value;
    setMessage("");
    setIsError(false);

    try {
      const updated = await apiFetch<Reservation>(
        `/api/v1/admin/reservations/${reservationId}/delivery-status`,
        {
          method: "PATCH",
          body: JSON.stringify({ delivery_status: nextStatus }),
        },
        true,
      );
      setReservations((current) =>
        current.map((reservation) => (reservation.id === reservationId ? updated : reservation)),
      );
      setMessage(`배송 상태가 ${deliveryStatusLabel(nextStatus)}(으)로 변경되었습니다.`);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  async function toggleReservationHistory(reservationId: string) {
    if (expandedHistoryId === reservationId) {
      setExpandedHistoryId(null);
      return;
    }

    setExpandedHistoryId(reservationId);
    if (historyByReservation[reservationId]) {
      return;
    }

    setHistoryLoadingId(reservationId);
    try {
      const history = await apiFetch<ReservationHistory[]>(
        `/api/v1/admin/reservations/${reservationId}/history`,
        {},
        true,
      );
      setHistoryByReservation((current) => ({ ...current, [reservationId]: history }));
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setHistoryLoadingId(null);
    }
  }

  const blocked = !guard.allowed;

  if (!guard.allowed) {
    return (
      <section className="section">
        <EmptyState title={guard.message || "권한을 확인하고 있습니다."} />
      </section>
    );
  }

  return (
    <section className="section">
      <PageHeader
        title="Admin Dashboard"
        description="BreadGo MVP의 사용자, 가맹점, 매장, 상품, 예약, 결제 현황을 모니터링합니다."
        actions={
          <>
            <Link className="button-link secondary" href="/admin/pro/operations">
              Pro Operations
            </Link>
            <Link className="button-link secondary" href="/admin/pro/operations/audit-logs">
              Pro 감사 로그
            </Link>
            <Link className="button-link secondary" href="/admin/pro/weekly-report-batches">
              Weekly Batch Monitor
            </Link>
            <Link className="button-link secondary" href="/admin/pro/weekly-report-deliveries">
              Delivery Preview
            </Link>
          </>
        }
      />
      {process.env.NODE_ENV === "development" && (
        <p className="message">
          로컬 개발 환경에서는 seed_demo.py 또는 직접 SQL로 관리자 계정을 준비할 수 있습니다.
        </p>
      )}

      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      {blocked ? (
        <EmptyState
          title={message || "로그인이 필요합니다."}
          description="관리자 계정으로 로그인한 뒤 다시 열어주세요."
        />
      ) : (
        <>
          {summary && (
            <div className="summary-grid">
              <StatCard label="Users" value={summary.total_users} />
              <StatCard label="Merchants" value={summary.total_merchants} />
              <StatCard label="Stores" value={summary.total_stores} />
              <StatCard label="Products" value={summary.total_products} helper={`${summary.active_products} active`} />
              <StatCard label="Reservations" value={summary.total_reservations} />
              <StatCard label="Picked Up" value={summary.picked_up_reservations} />
              <StatCard label="Cancelled" value={summary.cancelled_reservations} />
              <StatCard label="Payments" value={summary.total_payments} />
              <StatCard label="Paid" value={summary.paid_payments} />
              <StatCard label="Cancelled Pay" value={summary.cancelled_payments} />
              <StatCard label="Failed Pay" value={summary.failed_payments} />
              <StatCard label="Paid Amount" value={`${Number(summary.total_paid_amount).toLocaleString()}원`} />
            </div>
          )}

          <AdminTable title="Users">
            <thead>
              <tr>
                <th>Email</th>
                <th>Name</th>
                <th>Role</th>
                <th>Active</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td>{user.email}</td>
                  <td>{user.full_name}</td>
                  <td><StatusBadge status={user.role} /></td>
                  <td><StatusBadge status={user.is_active ? "ACTIVE" : "HIDDEN"} /></td>
                </tr>
              ))}
            </tbody>
          </AdminTable>

          <AdminTable title="Merchants">
            <thead>
              <tr>
                <th>Business</th>
                <th>Representative</th>
                <th>Phone</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {merchants.map((merchant) => (
                <tr key={merchant.id}>
                  <td>{merchant.business_name}</td>
                  <td>{merchant.representative_name}</td>
                  <td>{merchant.phone_number}</td>
                  <td>
                    <select
                      value={merchant.status}
                      onChange={(event) => updateMerchantStatus(merchant.id, event)}
                      aria-label={`${merchant.business_name} status`}
                    >
                      {merchantStatuses.map((status) => (
                        <option key={status} value={status}>
                          {status}
                        </option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </AdminTable>

          <AdminTable title="Stores">
            <thead>
              <tr>
                <th>Name</th>
                <th>Region</th>
                <th>Address</th>
                <th>Phone</th>
                <th>Active</th>
              </tr>
            </thead>
            <tbody>
              {stores.map((store) => (
                <tr key={store.id}>
                  <td>{store.name}</td>
                  <td>{[store.sido, store.sigungu, store.dong].filter(Boolean).join(" ") || "-"}</td>
                  <td>{store.address}</td>
                  <td>{store.phone_number}</td>
                  <td><StatusBadge status={store.is_active ? "ACTIVE" : "HIDDEN"} /></td>
                </tr>
              ))}
            </tbody>
          </AdminTable>

          <AdminTable title="Products">
            <thead>
              <tr>
                <th>Image</th>
                <th>Name</th>
                <th>Store</th>
                <th>Price</th>
                <th>Fulfillment</th>
                <th>Qty</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {products.map((product) => (
                <tr key={product.id}>
                  <td>
                    {product.image_url ? (
                      <img className="table-product-image" src={product.image_url} alt={`${product.name} 대표 이미지`} />
                    ) : (
                      <span className="badge muted">No image</span>
                    )}
                  </td>
                  <td>{product.name}</td>
                  <td>{product.store_id}</td>
                  <td>{product.discount_price}</td>
                  <td>
                    픽업 {product.allow_pickup ? "가능" : "불가"}
                    <br />
                    퀵 {product.allow_quick_delivery ? `${Number(product.quick_delivery_fee).toLocaleString()}원` : "불가"}
                    <br />
                    택배 {product.allow_parcel_delivery ? `${Number(product.parcel_delivery_fee).toLocaleString()}원` : "불가"}
                  </td>
                  <td>{product.quantity}</td>
                  <td><StatusBadge status={product.status} /></td>
                </tr>
              ))}
            </tbody>
          </AdminTable>

          <AdminTable title="Reservations">
            <thead>
              <tr>
                <th>Pickup</th>
                <th>User</th>
                <th>Product</th>
                <th>Fulfillment</th>
                <th>Total</th>
                <th>Status</th>
                <th>History</th>
              </tr>
            </thead>
            <tbody>
              {reservations.map((reservation) => (
                <Fragment key={reservation.id}>
                  <tr>
                    <td>{reservation.pickup_code}</td>
                    <td>{reservation.user_id}</td>
                    <td>{reservation.product_id}</td>
                    <td>
                      {reservation.fulfillment_method}
                      <br />
                      {reservation.fulfillment_method === "PICKUP"
                        ? `Pickup ${reservation.pickup_code}`
                        : reservation.delivery_address || "-"}
                      <br />
                      {reservation.fulfillment_method === "PICKUP" ? (
                        <span>배송 상태 {deliveryStatusLabel(reservation.delivery_status)}</span>
                      ) : (
                        <select
                          value={reservation.delivery_status}
                          onChange={(event) => updateReservationDeliveryStatus(reservation.id, event)}
                          aria-label={`${reservation.id} delivery status`}
                        >
                          {deliveryStatuses.map((status) => (
                            <option key={status} value={status}>
                              {deliveryStatusLabel(status)}
                            </option>
                          ))}
                        </select>
                      )}
                    </td>
                    <td>{reservation.total_price}</td>
                    <td><StatusBadge status={reservation.status} /></td>
                    <td>
                      <button type="button" className="secondary" onClick={() => toggleReservationHistory(reservation.id)}>
                        {expandedHistoryId === reservation.id ? "닫기" : "이력"}
                      </button>
                    </td>
                  </tr>
                  {expandedHistoryId === reservation.id && (
                    <tr>
                      <td colSpan={7}>
                        <div className="timeline">
                          {historyLoadingId === reservation.id && <p className="field-help">상태 이력을 불러오는 중입니다.</p>}
                          {(historyByReservation[reservation.id] || []).map((event) => (
                            <div className="timeline-item" key={event.id}>
                              <strong>{historyEventLabel(event.event_type)}</strong>
                              <span>{event.message}</span>
                              <small>
                                {[event.actor_email || event.actor_role, event.from_status && event.to_status
                                  ? `${event.from_status} → ${event.to_status}`
                                  : null, new Date(event.created_at).toLocaleString()]
                                  .filter(Boolean)
                                  .join(" · ")}
                              </small>
                            </div>
                          ))}
                          {!historyLoadingId && (historyByReservation[reservation.id] || []).length === 0 && (
                            <p className="field-help">상태 이력이 없습니다.</p>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </AdminTable>

          <AdminTable title="Payments">
            <thead>
              <tr>
                <th>Payment</th>
                <th>Reservation</th>
                <th>User</th>
                <th>Amount</th>
                <th>Method</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {payments.map((payment) => (
                <tr key={payment.id}>
                  <td>{payment.id}</td>
                  <td>{payment.reservation_id}</td>
                  <td>{payment.user_id}</td>
                  <td>{payment.amount}</td>
                  <td>{payment.method}</td>
                  <td><StatusBadge status={payment.status} /></td>
                </tr>
              ))}
            </tbody>
          </AdminTable>
        </>
      )}
    </section>
  );
}

function AdminTable({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="section">
      <h2>{title}</h2>
      <div className="table-wrap">
        <table>{children}</table>
      </div>
    </section>
  );
}
