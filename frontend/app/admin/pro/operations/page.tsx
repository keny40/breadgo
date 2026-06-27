"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { Badge, EmptyState, PageHeader, StatCard } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type {
  AdminProOperationsHealth,
  AdminProOperationsSummary,
  ProHealthAlertList,
  ProHealthAlertGenerateResult,
  ProOperationsAuditLogList,
  ProOperationsAuditLogSummary,
} from "@/lib/types";

function formatDateTime(value: string | null) {
  if (!value) return "-";
  return new Date(value).toLocaleString("ko-KR");
}

function statusTone(status: string | null): "success" | "warning" | "danger" | "muted" {
  if (!status) return "muted";
  if (status === "COMPLETED" || status === "SUCCESS" || status === "OK") return "success";
  if (status === "FAILED" || status === "CRITICAL") return "danger";
  if (status === "PARTIAL" || status === "STARTED" || status === "PENDING" || status === "WARNING") return "warning";
  return "muted";
}

function healthStatusLabel(status: string | null) {
  if (status === "OK") return "정상";
  if (status === "WARNING") return "주의 필요";
  if (status === "CRITICAL") return "즉시 확인";
  return status || "확인 전";
}

const healthCards: Array<{ key: keyof Pick<
  AdminProOperationsHealth,
  | "scheduler_health"
  | "batch_health"
  | "delivery_health"
  | "notification_health"
  | "audit_log_health"
  | "purge_policy_health"
>; label: string }> = [
  { key: "scheduler_health", label: "Scheduler 실행" },
  { key: "batch_health", label: "Batch 생성" },
  { key: "delivery_health", label: "Delivery 준비" },
  { key: "notification_health", label: "내부 알림" },
  { key: "audit_log_health", label: "Audit Log" },
  { key: "purge_policy_health", label: "Purge 정책" },
];

export default function AdminProOperationsPage() {
  const guard = useRoleGuard("ADMIN");
  const [summary, setSummary] = useState<AdminProOperationsSummary | null>(null);
  const [health, setHealth] = useState<AdminProOperationsHealth | null>(null);
  const [healthAlerts, setHealthAlerts] = useState<ProHealthAlertList>({ alerts: [], total_count: 0 });
  const [auditSummary, setAuditSummary] = useState<ProOperationsAuditLogSummary | null>(null);
  const [auditLogs, setAuditLogs] = useState<ProOperationsAuditLogList>({ audit_logs: [], total_count: 0 });
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const loadSummary = useCallback(async (nextMessage = "BreadGo Pro 운영 상태를 불러왔습니다.") => {
    setLoading(true);
    setMessage("");
    setIsError(false);
    try {
      const [result, healthResult, alertsResult, auditSummaryResult, auditLogsResult] = await Promise.all([
        apiFetch<AdminProOperationsSummary>("/api/v1/admin/pro/operations/summary", {}, true),
        apiFetch<AdminProOperationsHealth>("/api/v1/admin/pro/operations/health", {}, true),
        apiFetch<ProHealthAlertList>("/api/v1/admin/pro/operations/health/alerts?limit=10", {}, true),
        apiFetch<ProOperationsAuditLogSummary>("/api/v1/admin/pro/operations/audit-logs/summary", {}, true),
        apiFetch<ProOperationsAuditLogList>("/api/v1/admin/pro/operations/audit-logs?limit=10", {}, true),
      ]);
      setSummary(result);
      setHealth(healthResult);
      setHealthAlerts(alertsResult);
      setAuditSummary(auditSummaryResult);
      setAuditLogs(auditLogsResult);
      setMessage(nextMessage);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!guard.allowed) return;
    queueMicrotask(() => {
      void loadSummary();
    });
  }, [guard.allowed, loadSummary]);

  async function runQuickAction(action: "batch" | "preview" | "mock" | "reminder") {
    setActionLoading(action);
    setMessage("");
    setIsError(false);
    try {
      if (action === "batch") {
        await apiFetch("/api/v1/admin/pro/weekly-report/batch-runs", { method: "POST" }, true);
        setMessage("전체 Weekly Report batch 실행을 완료했습니다.");
      }
      if (action === "preview") {
        await apiFetch("/api/v1/admin/pro/weekly-report/delivery-runs/preview", { method: "POST" }, true);
        setMessage("Delivery preview를 생성했습니다.");
      }
      if (action === "mock") {
        if (!summary?.delivery.latest_ready_delivery_run_id) {
          setIsError(true);
          setMessage("READY item이 있는 delivery preview가 없어 In-app mock delivery를 실행할 수 없습니다.");
          return;
        }
        await apiFetch(
          `/api/v1/admin/pro/weekly-report/delivery-runs/${summary.delivery.latest_ready_delivery_run_id}/mock-send`,
          { method: "POST" },
          true,
        );
        setMessage("In-app mock delivery를 실행했습니다.");
      }
      if (action === "reminder") {
        await apiFetch("/api/v1/admin/pro/weekly-report/notifications/remind-unread", { method: "POST" }, true);
        setMessage("미확인 Weekly Report 리마인드를 생성했습니다.");
      }
      await loadSummary(
        action === "batch"
          ? "전체 Weekly Report batch 실행 후 운영 상태를 새로고침했습니다."
          : action === "preview"
            ? "Delivery preview 생성 후 운영 상태를 새로고침했습니다."
            : action === "mock"
              ? "In-app mock delivery 실행 후 운영 상태를 새로고침했습니다."
              : "미확인 Weekly Report 리마인드 생성 후 운영 상태를 새로고침했습니다.",
      );
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setActionLoading(null);
    }
  }

  async function generateHealthAlerts() {
    setActionLoading("health-alerts");
    setMessage("");
    setIsError(false);
    try {
      const result = await apiFetch<ProHealthAlertGenerateResult>(
        "/api/v1/admin/pro/operations/health/alerts/generate",
        { method: "POST" },
        true,
      );
      await loadSummary(`${result.generated_count}건 생성, ${result.skipped_count}건 중복 skip 처리했습니다.`);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setActionLoading(null);
    }
  }

  async function updateHealthAlert(alertId: string, action: "acknowledge" | "resolve") {
    setActionLoading(`${action}-${alertId}`);
    setMessage("");
    setIsError(false);
    try {
      await apiFetch(`/api/v1/admin/pro/operations/health/alerts/${alertId}/${action}`, { method: "POST" }, true);
      await loadSummary(action === "acknowledge" ? "Health Alert를 확인 처리했습니다." : "Health Alert를 해결 처리했습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setActionLoading(null);
    }
  }

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
        title="Pro 운영 대시보드"
        description="Weekly Report batch, delivery, 내부 알림, audit trail, health alert 상태를 한눈에 확인합니다."
        actions={
          <>
            <Link className="button-link secondary" href="/admin/pro/weekly-report-batches">
              Batch Monitor로 이동
            </Link>
            <Link className="button-link secondary" href="/admin/pro/weekly-report-deliveries">
              Delivery Preview로 이동
            </Link>
            <button type="button" onClick={() => loadSummary()} disabled={loading}>
              {loading ? "불러오는 중" : "새로고침"}
            </button>
          </>
        }
      />

      <p className="message">
        이 화면은 내부 운영 상태만 집계합니다. 이메일, 전화번호, 주소, 외부 발송 토큰은 저장하거나 표시하지 않습니다.
      </p>

      {message && <div className={isError ? "notice error" : "notice success"}>{message}</div>}

      {summary ? (
        <>
          {health && (
            <section className="panel">
              <div className="card-title-row">
                <div>
                  <p className="eyebrow">Pro Health Check</p>
                  <h2>현재 Pro 운영 상태</h2>
                  <p>{health.summary_message}</p>
                </div>
                <div className="actions">
                  <Badge tone={statusTone(health.overall_status)}>
                    {healthStatusLabel(health.overall_status)} · {health.overall_status}
                  </Badge>
                  <button type="button" onClick={() => loadSummary("Pro Health Check를 다시 점검했습니다.")} disabled={loading}>
                    {loading ? "점검 중" : "상태 다시 점검"}
                  </button>
                </div>
              </div>
              <div className="summary-grid compact">
                <StatCard label="전체 상태" value={healthStatusLabel(health.overall_status)} helper={formatDateTime(health.checked_at)} />
                {healthCards.map(({ key, label }) => {
                  const item = health[key];
                  return (
                    <StatCard
                      key={key}
                      label={label}
                      value={healthStatusLabel(item.status)}
                      helper={item.message}
                    />
                  );
                })}
              </div>
              {health.health_messages.length > 0 ? (
                <div className="stacked-list">
                  {health.health_messages.map((healthMessage) => (
                    <article className="item compact-card highlight-card" key={healthMessage}>
                      <strong>{healthMessage}</strong>
                    </article>
                  ))}
                </div>
              ) : (
                <EmptyState title="현재 Health Check 경고가 없습니다." />
              )}
            </section>
          )}

          <section className="panel">
            <div className="card-title-row">
              <div>
                <p className="eyebrow">Health Alerts</p>
                <h2>내부 상태 알림</h2>
                <p>WARNING 또는 CRITICAL Health Check 결과를 내부 관리자 알림으로 기록합니다.</p>
              </div>
              <div className="actions">
                <Badge tone={healthAlerts.alerts.some((alert) => alert.status !== "RESOLVED") ? "warning" : "success"}>
                  미해결 {healthAlerts.alerts.filter((alert) => alert.status !== "RESOLVED").length}
                </Badge>
                <button type="button" onClick={generateHealthAlerts} disabled={actionLoading !== null}>
                  {actionLoading === "health-alerts" ? "생성 중" : "Health Alert 생성"}
                </button>
              </div>
            </div>
            {healthAlerts.alerts.length > 0 ? (
              <div className="stacked-list">
                {healthAlerts.alerts.map((alert) => (
                  <article className="item compact-card" key={alert.id}>
                    <div className="card-title-row">
                      <div>
                        <strong>{alert.title}</strong>
                        <p>{alert.message}</p>
                        <small>
                          {alert.source_key} · {formatDateTime(alert.created_at)}
                        </small>
                      </div>
                      <div className="actions">
                        <Badge tone={statusTone(alert.severity)}>{alert.severity}</Badge>
                        <Badge tone={alert.status === "RESOLVED" ? "success" : "warning"}>{alert.status}</Badge>
                      </div>
                    </div>
                    <div className="actions">
                      <button
                        type="button"
                        className="secondary"
                        onClick={() => updateHealthAlert(alert.id, "acknowledge")}
                        disabled={actionLoading !== null || alert.status !== "OPEN"}
                      >
                        확인
                      </button>
                      <button
                        type="button"
                        onClick={() => updateHealthAlert(alert.id, "resolve")}
                        disabled={actionLoading !== null || alert.status === "RESOLVED"}
                      >
                        해결 처리
                      </button>
                    </div>
                  </article>
                ))}
              </div>
            ) : (
              <EmptyState title="아직 Health Alert가 없습니다." description="Health Alert 생성 버튼으로 현재 경고 상태를 내부 알림으로 기록할 수 있습니다." />
            )}
          </section>

          <div className="summary-grid">
            <StatCard label="최근 Batch" value={summary.batch.latest_status || "-"} helper={summary.batch.latest_run_type || "-"} />
            <StatCard label="최근 Delivery" value={summary.delivery.latest_status || "-"} helper={summary.delivery.latest_run_type || "-"} />
            <StatCard label="알림 읽음률" value={`${summary.notifications.read_rate}%`} helper={`미확인 ${summary.notifications.unread_count}건`} />
            <StatCard
              label="주의 필요"
              value={summary.attention.needs_attention ? "확인 필요" : "정상"}
              helper={`${summary.attention.attention_messages.length}개 메시지`}
            />
          </div>

          <section className="panel">
            <div className="card-title-row">
              <div>
                <p className="eyebrow">운영 Quick Actions</p>
                <h2>필요한 조치를 바로 실행</h2>
                <p>기존 Weekly Report 운영 API를 재사용합니다. 실제 외부 발송은 수행하지 않습니다.</p>
              </div>
              <Badge tone={summary.attention.needs_attention ? "warning" : "success"}>
                {summary.attention.needs_attention ? "조치 확인" : "정상"}
              </Badge>
            </div>
            <div className="actions">
              <button
                type="button"
                onClick={() => runQuickAction("batch")}
                disabled={actionLoading !== null}
              >
                {actionLoading === "batch" ? "실행 중" : "전체 Weekly Report 생성"}
              </button>
              <button
                type="button"
                onClick={() => runQuickAction("preview")}
                disabled={actionLoading !== null}
              >
                {actionLoading === "preview" ? "생성 중" : "Delivery 미리보기 생성"}
              </button>
              <button
                type="button"
                onClick={() => runQuickAction("mock")}
                disabled={actionLoading !== null || !summary.can_run_mock_delivery}
              >
                {actionLoading === "mock" ? "실행 중" : "내부 알림 Mock 발송"}
              </button>
              <button
                type="button"
                onClick={() => runQuickAction("reminder")}
                disabled={actionLoading !== null || !summary.can_run_unread_reminder}
              >
                {actionLoading === "reminder" ? "생성 중" : "미확인 리마인드 생성"}
              </button>
              <Link className="button-link secondary" href="/admin/pro/weekly-report-batches">
                Batch Monitor로 이동
              </Link>
              <Link className="button-link secondary" href="/admin/pro/weekly-report-deliveries">
                Delivery Preview로 이동
              </Link>
            </div>
            {summary.quick_action_messages.length > 0 ? (
              <div className="stacked-list">
                {summary.quick_action_messages.map((quickActionMessage) => (
                  <article className="item compact-card" key={quickActionMessage}>
                    <p>{quickActionMessage}</p>
                  </article>
                ))}
              </div>
            ) : (
              <EmptyState title="현재 실행을 막는 Quick Action 안내가 없습니다." />
            )}
          </section>

          <section className="panel">
            <div className="card-title-row">
              <div>
                <p className="eyebrow">Audit Trail</p>
                <h2>최근 운영 액션 이력</h2>
                <p>Quick Action과 주요 Weekly Report 운영 액션 실행 결과를 기록합니다.</p>
              </div>
              <div className="actions">
                <Badge tone={(auditSummary?.failed_count || 0) > 0 ? "warning" : "success"}>
                  실패 {auditSummary?.failed_count || 0}
                </Badge>
                <Link className="button-link secondary" href="/admin/pro/operations/audit-logs">
                  전체 Audit Log 보기
                </Link>
              </div>
            </div>
            <div className="summary-grid compact">
              <StatCard label="전체 액션" value={auditSummary?.total_count || 0} />
              <StatCard label="성공" value={auditSummary?.success_count || 0} />
              <StatCard label="실패" value={auditSummary?.failed_count || 0} />
              <StatCard label="최근 액션" value={formatDateTime(auditSummary?.latest_action_at || null)} />
              <StatCard label="최근 실패" value={formatDateTime(auditSummary?.latest_failed_action_at || null)} />
            </div>
            {auditLogs.audit_logs.length > 0 ? (
              <div className="table-wrap">
                <table className="table">
                  <thead>
                    <tr>
                      <th>액션</th>
                      <th>상태</th>
                      <th>대상</th>
                      <th>메시지</th>
                      <th>실행 시각</th>
                    </tr>
                  </thead>
                  <tbody>
                    {auditLogs.audit_logs.map((log) => (
                      <tr key={log.id}>
                        <td>{log.action_type}</td>
                        <td>
                          <Badge tone={statusTone(log.status)}>{log.status}</Badge>
                        </td>
                        <td>{log.target_type}</td>
                        <td>{log.message || "-"}</td>
                        <td>{formatDateTime(log.created_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <EmptyState title="아직 기록된 운영 액션이 없습니다." />
            )}
          </section>

          <section className="panel">
            <div className="card-title-row">
              <div>
                <p className="eyebrow">Weekly Report Batch</p>
                <h2>최근 batch run 요약</h2>
              </div>
              <Badge tone={statusTone(summary.batch.latest_status)}>{summary.batch.latest_status || "NO DATA"}</Badge>
            </div>
            <div className="summary-grid compact">
              <StatCard label="Run Type" value={summary.batch.latest_run_type || "-"} />
              <StatCard label="생성일" value={formatDateTime(summary.batch.latest_created_at)} />
              <StatCard label="대상" value={summary.batch.latest_total_count} />
              <StatCard label="성공" value={summary.batch.latest_success_count} />
              <StatCard label="실패" value={summary.batch.latest_failed_count} />
              <StatCard label="스킵" value={summary.batch.latest_skipped_count} />
              <StatCard label="최근 7일 실행" value={summary.batch.recent_7_days_run_count} />
              <StatCard label="최근 7일 실패/부분실패" value={summary.batch.recent_7_days_failed_or_partial_count} />
            </div>
          </section>

          <section className="panel">
            <div className="card-title-row">
              <div>
                <p className="eyebrow">Delivery</p>
                <h2>최근 delivery run 요약</h2>
              </div>
              <Badge tone={statusTone(summary.delivery.latest_status)}>{summary.delivery.latest_status || "NO DATA"}</Badge>
            </div>
            <div className="summary-grid compact">
              <StatCard label="Run Type" value={summary.delivery.latest_run_type || "-"} />
              <StatCard label="Channel" value={summary.delivery.latest_channel || "-"} />
              <StatCard label="생성일" value={formatDateTime(summary.delivery.latest_created_at)} />
              <StatCard label="전체" value={summary.delivery.latest_total_count} />
              <StatCard label="READY" value={summary.delivery.latest_ready_count} />
              <StatCard label="SENT" value={summary.delivery.latest_sent_count} />
              <StatCard label="SKIPPED" value={summary.delivery.latest_skipped_count} />
              <StatCard label="FAILED" value={summary.delivery.latest_failed_count} />
            </div>
          </section>

          <section className="panel">
            <div className="card-title-row">
              <div>
                <p className="eyebrow">Notification</p>
                <h2>Weekly Report 내부 알림 요약</h2>
              </div>
              <Badge tone={summary.notifications.unread_count > 0 ? "warning" : "success"}>
                미확인 {summary.notifications.unread_count}
              </Badge>
            </div>
            <div className="summary-grid compact">
              <StatCard label="전체" value={summary.notifications.total_count} />
              <StatCard label="읽음" value={summary.notifications.read_count} />
              <StatCard label="미확인" value={summary.notifications.unread_count} />
              <StatCard label="읽음률" value={`${summary.notifications.read_rate}%`} />
              <StatCard label="최근 알림" value={formatDateTime(summary.notifications.latest_created_at)} />
              <StatCard label="최근 읽음" value={formatDateTime(summary.notifications.latest_read_at)} />
              <StatCard label="최근 리마인드" value={formatDateTime(summary.notifications.latest_reminder_at)} />
              <StatCard label="미확인 리마인드" value={summary.notifications.unread_reminder_count} />
            </div>
          </section>

          <section className="panel">
            <div className="card-title-row">
              <div>
                <p className="eyebrow">Attention</p>
                <h2>주의 필요 항목</h2>
              </div>
              <Badge tone={summary.attention.needs_attention ? "danger" : "success"}>
                {summary.attention.needs_attention ? "확인 필요" : "정상"}
              </Badge>
            </div>
            <div className="summary-grid compact">
              <StatCard label="실패 Batch" value={summary.attention.failed_batch_count} />
              <StatCard label="부분 실패 Batch" value={summary.attention.partial_batch_count} />
              <StatCard label="실패 Delivery" value={summary.attention.failed_delivery_count} />
              <StatCard label="미확인 알림" value={summary.attention.unread_notification_count} />
            </div>
            {summary.attention.attention_messages.length > 0 ? (
              <div className="stacked-list">
                {summary.attention.attention_messages.map((attentionMessage) => (
                  <article className="item compact-card highlight-card" key={attentionMessage}>
                    <strong>{attentionMessage}</strong>
                  </article>
                ))}
              </div>
            ) : (
              <EmptyState title="현재 주의가 필요한 운영 항목이 없습니다." />
            )}
          </section>
        </>
      ) : (
        <EmptyState title="운영 상태를 불러오고 있습니다." />
      )}
    </section>
  );
}
