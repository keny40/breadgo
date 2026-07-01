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
  type ExternalIntegrationReadiness,
  type Merchant,
  type MerchantApplication,
  type MerchantApplicationApproveResponse,
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

const integrationAreaOrder = ["PAYMENT", "DELIVERY", "NOTIFICATION", "POS"];

function integrationAreaLabel(area: string) {
  const labels: Record<string, string> = {
    PAYMENT: "결제",
    DELIVERY: "배송",
    NOTIFICATION: "알림",
    POS: "POS",
  };
  return labels[area] || area;
}

function integrationOffLabel(area: string) {
  const labels: Record<string, string> = {
    PAYMENT: "실제 결제 OFF",
    DELIVERY: "실제 배송 OFF",
    NOTIFICATION: "실제 발송 OFF",
    POS: "실제 POS OFF",
  };
  return labels[area] || "실제 연동 OFF";
}

function integrationSimpleStatus(
  readiness: ExternalIntegrationReadiness,
  area: string,
) {
  const providers = readiness.items.filter((item) => item.area === area);
  const dryRun = readiness.dry_runs.find((item) => item.area === area);
  const hasExternalCalls =
    providers.some((item) => item.external_calls_enabled) || Boolean(dryRun?.external_calls_enabled);
  const hasFailedStatus = providers.some((item) => item.status === "CHECK_FAILED");

  if (hasExternalCalls) {
    return { label: "점검 필요", helper: "외부 호출 ON 감지", badgeClass: "badge danger" };
  }
  if (hasFailedStatus) {
    return { label: "점검 필요", helper: integrationOffLabel(area), badgeClass: "badge danger" };
  }
  if (providers.length === 0) {
    return { label: "설정 전", helper: integrationOffLabel(area), badgeClass: "badge warning" };
  }
  return { label: "준비 완료", helper: integrationOffLabel(area), badgeClass: "badge success" };
}

function readinessStatusLabel(status: string) {
  const labels: Record<string, string> = {
    MOCK_READY: "Mock 준비 완료",
    READY: "준비 완료",
    NOT_ENABLED: "실제 연동 비활성",
    NOT_CONFIGURED: "설정 전",
    CHECK_FAILED: "점검 필요",
  };
  return labels[status] || status;
}

function readinessStatusHelp(status: string) {
  const labels: Record<string, string> = {
    MOCK_READY: "모든 adapter가 mock/noop dry-run 기준으로 준비되어 있습니다.",
    READY: "Mock provider가 내부 dry-run으로 동작합니다.",
    NOT_ENABLED: "실제 provider skeleton은 있지만 운영 연동은 아직 켜지지 않았습니다.",
    NOT_CONFIGURED: "실제 provider 설정과 credential boundary가 아직 준비되지 않았습니다.",
    CHECK_FAILED: "외부 호출 비활성 원칙 또는 dry-run 상태를 다시 확인해야 합니다.",
  };
  return labels[status] || "현재 adapter readiness 상태를 확인합니다.";
}

function readinessBadgeClass(status: string, externalCallsEnabled: boolean) {
  if (externalCallsEnabled || status === "CHECK_FAILED") {
    return "badge danger";
  }
  if (status === "READY" || status === "MOCK_READY") {
    return "badge success";
  }
  if (status === "NOT_ENABLED" || status === "NOT_CONFIGURED") {
    return "badge warning";
  }
  return "badge muted";
}

function dryRunStatusLabel(status: string) {
  if (status.includes("PAID")) {
    return "결제 dry-run 완료";
  }
  if (status.includes("REQUESTED")) {
    return "배송 생성 dry-run 완료";
  }
  if (status.includes("DELIVERED_true")) {
    return "내부 알림 dry-run 완료";
  }
  if (status.includes("ITEMS_")) {
    return "POS sync dry-run 완료";
  }
  return status;
}

function integrationNextStep(area: string) {
  const labels: Record<string, string> = {
    PAYMENT: "실제 PG 연동 전 승인/환불 계약, credential 저장 경계, 실패/환불 audit 정책을 설계합니다.",
    DELIVERY: "실제 배송 provider 연동 전 접수/취소/추적 상태 매핑과 요금 계산 책임을 분리합니다.",
    NOTIFICATION: "실제 외부 발송 전 수신 동의, 재발송 정책, channel별 secret 관리 기준을 정리합니다.",
    POS: "실제 POS API 호출 전 store credential boundary, sync 실패 복구, CSV fallback, external_sku 매핑 기준을 확정합니다.",
  };
  return labels[area] || "실제 provider 연결 전 credential, audit, rollback 기준을 확인합니다.";
}

export default function AdminPage() {
  const guard = useRoleGuard("ADMIN");
  const [summary, setSummary] = useState<AdminSummary | null>(null);
  const [users, setUsers] = useState<AuthUser[]>([]);
  const [merchants, setMerchants] = useState<Merchant[]>([]);
  const [merchantApplications, setMerchantApplications] = useState<MerchantApplication[]>([]);
  const [stores, setStores] = useState<Store[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [externalReadiness, setExternalReadiness] = useState<ExternalIntegrationReadiness | null>(null);
  const [showIntegrationDetails, setShowIntegrationDetails] = useState(false);
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

        const [
          summaryData,
          userData,
          merchantData,
          merchantApplicationData,
          storeData,
          productData,
          reservationData,
          paymentData,
          readinessData,
        ] =
          await Promise.all([
            apiFetch<AdminSummary>("/api/v1/admin/summary", {}, true),
            apiFetch<AuthUser[]>("/api/v1/admin/users", {}, true),
            apiFetch<Merchant[]>("/api/v1/admin/merchants", {}, true),
            apiFetch<MerchantApplication[]>("/api/v1/admin/merchant-applications", {}, true),
            apiFetch<Store[]>("/api/v1/admin/stores", {}, true),
            apiFetch<Product[]>("/api/v1/admin/products", {}, true),
            apiFetch<Reservation[]>("/api/v1/admin/reservations", {}, true),
            apiFetch<Payment[]>("/api/v1/admin/payments", {}, true),
            apiFetch<ExternalIntegrationReadiness>("/api/v1/admin/pro/operations/external-integrations/readiness", {}, true),
          ]);

        if (cancelled) {
          return;
        }

        setSummary(summaryData);
        setUsers(userData);
        setMerchants(merchantData);
        setMerchantApplications(merchantApplicationData);
        setStores(storeData);
        setProducts(productData);
        setReservations(reservationData);
        setPayments(paymentData);
        setExternalReadiness(readinessData);
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

  async function approveMerchantApplication(applicationId: string) {
    setMessage("");
    setIsError(false);

    try {
      const result = await apiFetch<MerchantApplicationApproveResponse>(
        `/api/v1/admin/merchant-applications/${applicationId}/approve`,
        { method: "POST" },
        true,
      );
      setMerchantApplications((current) =>
        current.map((application) => (application.id === applicationId ? result.application : application)),
      );
      setMerchants((current) => {
        const exists = current.some((merchant) => merchant.id === result.merchant.id);
        return exists
          ? current.map((merchant) => (merchant.id === result.merchant.id ? result.merchant : merchant))
          : [result.merchant, ...current];
      });
      setMessage(`${result.application.store_name} 입점 신청을 승인했습니다.`);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  async function rejectMerchantApplication(applicationId: string) {
    const reason = window.prompt("반려 사유를 입력하세요.");
    if (!reason?.trim()) {
      return;
    }

    setMessage("");
    setIsError(false);

    try {
      const application = await apiFetch<MerchantApplication>(
        `/api/v1/admin/merchant-applications/${applicationId}/reject`,
        {
          method: "POST",
          body: JSON.stringify({ reason }),
        },
        true,
      );
      setMerchantApplications((current) =>
        current.map((item) => (item.id === applicationId ? application : item)),
      );
      setMessage(`${application.store_name} 입점 신청을 반려했습니다.`);
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
        description="BreadGo MVP의 사용자, 가맹점, 매장, 상품, 예약, Mock 결제 현황을 모니터링합니다. Pro Operations에서는 v0.1.2 운영 안정화 흐름을 확인합니다."
        actions={
          <>
            <Link className="button-link secondary" href="/admin/pro/operations">
              Pro Operations
            </Link>
            <Link className="button-link secondary" href="/admin/pro/operations/health-alerts">
              Pro 상태 알림
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

      <p className="message">
        데모에서는 실제 PG 결제, 배송 provider, 이메일/카카오/Push 발송을 호출하지 않습니다.
        관리자 운영 시연은 Pro Operations, Weekly Batch Monitor, Delivery Preview 순서로 진행하면 가장 자연스럽습니다.
      </p>

      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      {blocked ? (
        <EmptyState
          title={message || "로그인이 필요합니다."}
          description="관리자 계정으로 로그인한 뒤 다시 열어주세요."
        />
      ) : (
        <>
          {summary && (
            <>
              <section className="panel">
                <div className="card-title-row">
                  <div>
                    <p className="eyebrow">Admin Operations Report</p>
                    <h2>오늘 먼저 확인할 운영 현황</h2>
                    <p>
                      이 화면에서는 MVP 기본 지표를 확인하고, Pro Operations에서 Weekly Report batch,
                      Delivery preview, Health Alert 상태를 이어서 점검합니다.
                    </p>
                  </div>
                  <Link className="button-link secondary" href="/admin/pro/operations">
                    Pro Operations로 이동
                  </Link>
                </div>
                <div className="summary-grid compact">
                  <StatCard label="활성 상품" value={summary.active_products} helper={`${summary.total_products} total`} />
                  <StatCard label="예약" value={summary.total_reservations} helper={`${summary.picked_up_reservations} picked up`} />
                  <StatCard label="취소" value={summary.cancelled_reservations} helper="예약 취소 흐름 점검" />
                  <StatCard label="Mock 결제 완료" value={summary.paid_payments} helper={`${summary.failed_payments} failed`} />
                  <StatCard label="Mock 결제액" value={`${Number(summary.total_paid_amount).toLocaleString()}원`} helper="실제 PG 승인 없음" />
                  <StatCard label="가맹점" value={summary.total_merchants} helper={`${summary.total_stores} stores`} />
                </div>
                <div className="account-grid">
                  <article className="account-card">
                    <div className="card-title-row">
                      <h3>1. MVP 운영 지표</h3>
                      <span className="badge success">PASS</span>
                    </div>
                    <p>상품, 예약, 픽업, Mock 결제 수치가 seed/smoke 흐름과 맞는지 확인합니다.</p>
                  </article>
                  <article className="account-card">
                    <div className="card-title-row">
                      <h3>2. Weekly Report Batch</h3>
                      <span className="badge warning">SKIPPED 가능</span>
                    </div>
                    <p>동일 기간 SCHEDULED batch는 중복 방지로 SKIPPED가 정상일 수 있습니다.</p>
                    <Link href="/admin/pro/weekly-report-batches">
                      <button type="button" className="secondary">Batch Monitor</button>
                    </Link>
                  </article>
                  <article className="account-card">
                    <div className="card-title-row">
                      <h3>3. Delivery / Health</h3>
                      <span className="badge muted">Mock</span>
                    </div>
                    <p>Delivery는 내부 알림 Mock만 생성하고, Health Alert는 외부 Webhook 없이 관리자 내부 알림으로 처리합니다.</p>
                    <div className="actions">
                      <Link href="/admin/pro/weekly-report-deliveries">
                        <button type="button" className="secondary">Delivery Preview</button>
                      </Link>
                      <Link href="/admin/pro/operations/health-alerts">
                        <button type="button" className="secondary">Health Alerts</button>
                      </Link>
                    </div>
                  </article>
                </div>
              </section>

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

              {externalReadiness && (
                <section className="panel">
                  <div className="card-title-row">
                    <div>
                      <p className="eyebrow">External Integration Readiness</p>
                      <h2>외부 연동 준비 상태</h2>
                      <p>
                        실제 외부 연동은 꺼져 있고, 데모/점검용 adapter 준비 상태만 확인합니다.
                        결제, 배송, 알림, POS가 실제 호출 없이 준비되어 있는지 한눈에 봅니다.
                      </p>
                    </div>
                    <div className="actions">
                      <span className={readinessBadgeClass(externalReadiness.overall_status, externalReadiness.external_calls_enabled)}>
                        {readinessStatusLabel(externalReadiness.overall_status)}
                      </span>
                      <button
                        type="button"
                        className="secondary"
                        onClick={() => setShowIntegrationDetails((current) => !current)}
                      >
                        {showIntegrationDetails ? "상세 닫기" : "상세 보기"}
                      </button>
                    </div>
                  </div>

                  <p className="message">
                    현재는 실제 운영 연동 완료가 아니라 안전한 준비 상태입니다. 외부 호출은 모두 OFF입니다.
                  </p>

                  <div className="table-wrap">
                    <table>
                      <thead>
                        <tr>
                          <th>영역</th>
                          <th>준비 상태</th>
                          <th>실제 연동</th>
                        </tr>
                      </thead>
                      <tbody>
                        {integrationAreaOrder.map((area) => {
                          const simpleStatus = integrationSimpleStatus(externalReadiness, area);
                          return (
                            <tr key={area}>
                              <td>{integrationAreaLabel(area)}</td>
                              <td>
                                <span className={simpleStatus.badgeClass}>{simpleStatus.label}</span>
                              </td>
                              <td>{simpleStatus.helper}</td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>

                  <p className="field-help">
                    기술 정보가 필요하면 상세 보기를 열어 Mock / Noop / dry-run / external_calls_enabled 값을 확인하세요.
                  </p>

                  {showIntegrationDetails && (
                    <>
                      <p className="field-help">{readinessStatusHelp(externalReadiness.overall_status)}</p>
                      <p className="message">
                        상세 모드는 개발/운영 점검용입니다. 현재 단계에서는 실제 PG 결제, 배송 provider, POS API,
                        이메일/카카오/Push/Slack/Discord/Webhook을 호출하지 않습니다.
                        모든 provider는 mock/noop dry-run으로만 검증되며 external_calls_enabled=false가 정상입니다.
                      </p>

                      <div className="summary-grid compact">
                        <StatCard
                          label="Overall"
                          value={readinessStatusLabel(externalReadiness.overall_status)}
                          helper={externalReadiness.external_calls_enabled ? "external_calls_enabled=true" : "external_calls_enabled=false"}
                        />
                        <StatCard
                          label="Readiness items"
                          value={externalReadiness.items.length}
                          helper="provider별 준비 상태"
                        />
                        <StatCard
                          label="Dry-run checks"
                          value={externalReadiness.dry_runs.length}
                          helper="외부 호출 없는 mock 실행"
                        />
                        <StatCard
                          label="External calls"
                          value={externalReadiness.external_calls_enabled ? "ON" : "OFF"}
                          helper="OFF가 데모 정상 상태"
                        />
                      </div>

                      <div className="account-grid">
                    {integrationAreaOrder.map((area) => {
                      const providers = externalReadiness.items.filter((item) => item.area === area);
                      const dryRun = externalReadiness.dry_runs.find((item) => item.area === area);
                      const hasExternalCalls =
                        providers.some((item) => item.external_calls_enabled) || Boolean(dryRun?.external_calls_enabled);

                      return (
                        <article className="account-card" key={area}>
                          <div className="card-title-row">
                            <div>
                              <h3>{integrationAreaLabel(area)}</h3>
                              <p className="field-help">{integrationNextStep(area)}</p>
                            </div>
                            <span className={hasExternalCalls ? "badge danger" : "badge success"}>
                              {hasExternalCalls ? "외부 호출 ON" : "외부 호출 OFF"}
                            </span>
                          </div>

                          <div className="timeline">
                            {providers.map((provider) => (
                              <div className="timeline-item" key={`${provider.area}-${provider.provider}`}>
                                <strong>{provider.provider}</strong>
                                <span>
                                  <span className={readinessBadgeClass(provider.status, provider.external_calls_enabled)}>
                                    {readinessStatusLabel(provider.status)}
                                  </span>{" "}
                                  {provider.mode} · external_calls_enabled=
                                  {provider.external_calls_enabled ? "true" : "false"}
                                </span>
                                <small>{provider.message}</small>
                              </div>
                            ))}
                          </div>

                          {dryRun ? (
                            <div className="success-panel">
                              <div className="card-title-row">
                                <strong>Dry-run 결과</strong>
                                <span className={dryRun.external_calls_enabled ? "badge danger" : "badge success"}>
                                  {dryRun.external_calls_enabled ? "실제 호출 감지" : "Mock/Noop"}
                                </span>
                              </div>
                              <p>
                                {dryRun.provider} · {dryRunStatusLabel(dryRun.status)}
                              </p>
                              <p className="field-help">{dryRun.message}</p>
                            </div>
                          ) : (
                            <p className="field-help">아직 dry-run 결과가 없습니다.</p>
                          )}
                        </article>
                      );
                    })}
                      </div>

                      <div className="account-grid">
                        <article className="account-card">
                          <div className="card-title-row">
                            <h3>상태 해석</h3>
                            <span className="badge muted">Guide</span>
                          </div>
                          <p><strong>MOCK_READY</strong>: mock/noop adapter와 dry-run이 모두 외부 호출 없이 통과했습니다.</p>
                          <p><strong>NOT_ENABLED</strong>: 실제 provider skeleton은 있으나 운영 연동은 켜지지 않았습니다.</p>
                          <p><strong>NOT_CONFIGURED</strong>: 실제 provider credential 또는 store 설정이 아직 없습니다.</p>
                        </article>
                        <article className="account-card">
                          <div className="card-title-row">
                            <h3>실제 연동 전 필요 항목</h3>
                            <span className="badge warning">Before live</span>
                          </div>
                          <p>credential 저장 경계, provider별 실패/재시도 정책, audit log, webhook 검증, 운영 secret 관리 기준을 확정한 뒤 실제 연동을 켭니다.</p>
                        </article>
                      </div>
                    </>
                  )}
                </section>
              )}
            </>
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

          <AdminTable title="Merchant Applications">
            <thead>
              <tr>
                <th>Store</th>
                <th>Owner</th>
                <th>Contact</th>
                <th>Region</th>
                <th>Status</th>
                <th>Review</th>
              </tr>
            </thead>
            <tbody>
              {merchantApplications.map((application) => (
                <tr key={application.id}>
                  <td>
                    <strong>{application.store_name}</strong>
                    <br />
                    <small>{application.business_registration_number}</small>
                    <br />
                    <small>{application.product_category || "카테고리 미입력"}</small>
                  </td>
                  <td>{application.owner_name}</td>
                  <td>
                    {application.email}
                    <br />
                    {application.phone}
                  </td>
                  <td>
                    {[application.region_sido, application.region_sigungu, application.region_dong].filter(Boolean).join(" ") || "-"}
                    <br />
                    <small>{application.address}</small>
                  </td>
                  <td>
                    <StatusBadge status={application.status} />
                    {application.rejection_reason && (
                      <>
                        <br />
                        <small>{application.rejection_reason}</small>
                      </>
                    )}
                  </td>
                  <td>
                    {application.status === "PENDING" ? (
                      <div className="actions">
                        <button type="button" className="secondary" onClick={() => approveMerchantApplication(application.id)}>
                          승인
                        </button>
                        <button type="button" className="secondary" onClick={() => rejectMerchantApplication(application.id)}>
                          반려
                        </button>
                      </div>
                    ) : (
                      <span className="field-help">
                        {application.reviewed_at ? new Date(application.reviewed_at).toLocaleString() : "검토 완료"}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
              {merchantApplications.length === 0 && (
                <tr>
                  <td colSpan={6}>접수된 입점 신청이 없습니다.</td>
                </tr>
              )}
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
