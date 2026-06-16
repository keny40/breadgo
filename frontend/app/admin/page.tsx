"use client";

import { ChangeEvent, useEffect, useState } from "react";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import type { AdminSummary, AuthUser, Merchant, Payment, Product, Reservation, Store } from "@/lib/types";

const merchantStatuses = ["PENDING", "APPROVED", "REJECTED", "SUSPENDED"];

export default function AdminPage() {
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [summary, setSummary] = useState<AdminSummary | null>(null);
  const [users, setUsers] = useState<AuthUser[]>([]);
  const [merchants, setMerchants] = useState<Merchant[]>([]);
  const [stores, setStores] = useState<Store[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadAdminDashboard() {
      setMessage("");
      setIsError(false);

      try {
        const me = await apiFetch<AuthUser>("/api/v1/auth/me", {}, true);
        if (cancelled) {
          return;
        }
        setCurrentUser(me);

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
  }, []);

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

  const blocked = !currentUser || currentUser.role.toLowerCase() !== "admin";

  return (
    <section className="section">
      <h1>Admin Dashboard</h1>
      <p className="message">
        로컬 데모 관리자 승격 SQL:
        <br />
        <code>UPDATE users SET role = &apos;ADMIN&apos; WHERE email = &apos;owner@test.com&apos;;</code>
      </p>

      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      {blocked ? (
        <div className="empty-state">
          {message || "로그인이 필요합니다. 관리자 계정으로 로그인한 뒤 다시 열어주세요."}
        </div>
      ) : (
        <>
          {summary && (
            <div className="summary-grid">
              <SummaryCard label="Users" value={summary.total_users} />
              <SummaryCard label="Merchants" value={summary.total_merchants} />
              <SummaryCard label="Stores" value={summary.total_stores} />
              <SummaryCard label="Products" value={summary.total_products} />
              <SummaryCard label="Active Products" value={summary.active_products} />
              <SummaryCard label="Reservations" value={summary.total_reservations} />
              <SummaryCard label="Picked Up" value={summary.picked_up_reservations} />
              <SummaryCard label="Cancelled" value={summary.cancelled_reservations} />
              <SummaryCard label="Payments" value={summary.total_payments} />
              <SummaryCard label="Paid" value={summary.paid_payments} />
              <SummaryCard label="Cancelled Pay" value={summary.cancelled_payments} />
              <SummaryCard label="Failed Pay" value={summary.failed_payments} />
              <SummaryCard label="Paid Amount" value={summary.total_paid_amount} />
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
                  <td>{user.role}</td>
                  <td>{user.is_active ? "Y" : "N"}</td>
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
                  <td>{store.is_active ? "Y" : "N"}</td>
                </tr>
              ))}
            </tbody>
          </AdminTable>

          <AdminTable title="Products">
            <thead>
              <tr>
                <th>Name</th>
                <th>Store</th>
                <th>Price</th>
                <th>Qty</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {products.map((product) => (
                <tr key={product.id}>
                  <td>{product.name}</td>
                  <td>{product.store_id}</td>
                  <td>{product.discount_price}</td>
                  <td>{product.quantity}</td>
                  <td>{product.status}</td>
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
                <th>Total</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {reservations.map((reservation) => (
                <tr key={reservation.id}>
                  <td>{reservation.pickup_code}</td>
                  <td>{reservation.user_id}</td>
                  <td>{reservation.product_id}</td>
                  <td>{reservation.total_price}</td>
                  <td>{reservation.status}</td>
                </tr>
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
                  <td>{payment.status}</td>
                </tr>
              ))}
            </tbody>
          </AdminTable>
        </>
      )}
    </section>
  );
}

function SummaryCard({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="summary-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function AdminTable({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="section">
      <h2>{title}</h2>
      <div className="table-wrap">
        <table>{children}</table>
      </div>
    </section>
  );
}
