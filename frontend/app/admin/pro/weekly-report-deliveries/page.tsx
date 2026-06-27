"use client";

import { useCallback, useEffect, useState } from "react";
import { Badge, EmptyState, PageHeader, StatCard } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type {
  AdminProWeeklyReportDeliveryRunHistory,
  AdminProWeeklyReportNotificationList,
  AdminProWeeklyReportNotificationSummary,
  ProWeeklyReportDeliveryRun,
} from "@/lib/types";

function formatDate(value: string) {
  return new Date(`${value}T00:00:00`).toLocaleDateString("ko-KR", {
    month: "numeric",
    day: "numeric",
  });
}

function formatDateTime(value: string | null) {
  if (!value) return "-";
  return new Date(value).toLocaleString("ko-KR");
}

function statusTone(status: string): "success" | "warning" | "danger" | "muted" {
  if (status === "COMPLETED" || status === "READY" || status === "SENT") return "success";
  if (status === "FAILED") return "danger";
  if (status === "PARTIAL" || status === "PENDING") return "warning";
  return "muted";
}

const runTypeLabels: Record<string, string> = {
  PREVIEW: "발송 미리보기",
  DRY_RUN: "Dry-run",
  IN_APP_MOCK: "내부 알림 Mock 발송",
  IN_APP_REMINDER: "미확인 리마인드",
};

const itemStatusLabels: Record<string, string> = {
  READY: "발송 가능",
  SENT: "내부 알림 생성",
  SKIPPED: "제외",
  FAILED: "실패",
  COMPLETED: "완료",
  PARTIAL: "부분 성공",
};

function displayRunType(runType: string) {
  return runTypeLabels[runType] ? `${runTypeLabels[runType]} · ${runType}` : runType;
}

function displayStatus(status: string) {
  return itemStatusLabels[status] ? `${itemStatusLabels[status]} · ${status}` : status;
}

function DeliveryRunCard({
  run,
  onMockSend,
  sending,
}: {
  run: ProWeeklyReportDeliveryRun;
  onMockSend: (runId: string) => void;
  sending: boolean;
}) {
  const readyItemCount = run.items.filter((item) => item.status === "READY").length;
  const canMockSend = readyItemCount > 0;
  const successLabel = run.run_type === "IN_APP_MOCK" || run.run_type === "IN_APP_REMINDER" ? "SENT" : "READY";

  return (
    <article className="panel">
      <div className="card-title-row">
        <div>
          <p className="eyebrow">
            {displayRunType(run.run_type)} · {run.channel}
          </p>
          <h2>
            {formatDate(run.period_start)} - {formatDate(run.period_end)}
          </h2>
          <p>{run.message || "Weekly Report delivery preview"}</p>
        </div>
        <div className="button-row">
          <Badge tone={statusTone(run.status)}>{displayStatus(run.status)}</Badge>
          <button
            type="button"
            className="secondary"
            disabled={!canMockSend || sending}
            onClick={() => onMockSend(run.id)}
          >
            {sending ? "처리 중" : "내부 알림 Mock 발송"}
          </button>
        </div>
      </div>

      <div className="summary-grid compact">
        <StatCard label="전체" value={run.total_count} />
        <StatCard label={displayStatus(successLabel)} value={run.ready_count} />
        <StatCard label="제외 · SKIPPED" value={run.skipped_count} />
        <StatCard label="실패 · FAILED" value={run.failed_count} />
        <StatCard label="생성" value={formatDateTime(run.created_at)} />
        <StatCard label="완료" value={formatDateTime(run.completed_at)} />
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Merchant</th>
              <th>Snapshot</th>
              <th>Status</th>
              <th>Reason</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {run.items.map((item) => (
              <tr key={item.id}>
                <td>{item.merchant_id}</td>
                <td>{item.snapshot_id || "-"}</td>
                <td>
                  <Badge tone={statusTone(item.status)}>{displayStatus(item.status)}</Badge>
                </td>
                <td>{item.reason || "-"}</td>
                <td>{formatDateTime(item.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </article>
  );
}

export default function AdminWeeklyReportDeliveriesPage() {
  const guard = useRoleGuard("ADMIN");
  const [history, setHistory] = useState<AdminProWeeklyReportDeliveryRunHistory | null>(null);
  const [notificationSummary, setNotificationSummary] = useState<AdminProWeeklyReportNotificationSummary | null>(null);
  const [notificationList, setNotificationList] = useState<AdminProWeeklyReportNotificationList | null>(null);
  const [lastPreview, setLastPreview] = useState<ProWeeklyReportDeliveryRun | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [sendingRunId, setSendingRunId] = useState<string | null>(null);
  const [reminding, setReminding] = useState(false);

  const loadDeliveryRuns = useCallback(async () => {
    setLoading(true);
    setMessage("");
    setIsError(false);
    try {
      const result = await apiFetch<AdminProWeeklyReportDeliveryRunHistory>(
        "/api/v1/admin/pro/weekly-report/delivery-runs",
        {},
        true,
      );
      const [summary, notifications] = await Promise.all([
        apiFetch<AdminProWeeklyReportNotificationSummary>(
          "/api/v1/admin/pro/weekly-report/notifications/summary",
          {},
          true,
        ),
        apiFetch<AdminProWeeklyReportNotificationList>(
          "/api/v1/admin/pro/weekly-report/notifications",
          {},
          true,
        ),
      ]);
      setHistory(result);
      setNotificationSummary(summary);
      setNotificationList(notifications);
      setMessage("Weekly Report delivery preview 이력을 불러왔습니다.");
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
      void loadDeliveryRuns();
    });
  }, [guard.allowed, loadDeliveryRuns]);

  async function createPreview() {
    setCreating(true);
    setMessage("");
    setIsError(false);
    try {
      const result = await apiFetch<ProWeeklyReportDeliveryRun>(
        "/api/v1/admin/pro/weekly-report/delivery-runs/preview",
        { method: "POST" },
        true,
      );
      setLastPreview(result);
      setMessage("발송 미리보기를 생성했습니다. 실제 외부 발송은 수행하지 않았습니다.");
      await loadDeliveryRuns();
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setCreating(false);
    }
  }

  async function createMockDelivery(runId: string) {
    setSendingRunId(runId);
    setMessage("");
    setIsError(false);
    try {
      const result = await apiFetch<ProWeeklyReportDeliveryRun>(
        `/api/v1/admin/pro/weekly-report/delivery-runs/${runId}/mock-send`,
        { method: "POST" },
        true,
      );
      setLastPreview(result);
      setMessage("BreadGo 내부 알림 mock delivery를 생성했습니다. 실제 외부 발송은 수행하지 않았습니다.");
      await loadDeliveryRuns();
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setSendingRunId(null);
    }
  }

  async function createUnreadReminder() {
    setReminding(true);
    setMessage("");
    setIsError(false);
    try {
      const result = await apiFetch<ProWeeklyReportDeliveryRun>(
        "/api/v1/admin/pro/weekly-report/notifications/remind-unread",
        { method: "POST" },
        true,
      );
      setLastPreview(result);
      setMessage("미확인 Weekly Report 알림 리마인드를 생성했습니다. 실제 외부 발송은 수행하지 않았습니다.");
      await loadDeliveryRuns();
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setReminding(false);
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
        title="Weekly Report Delivery Preview"
        description="실제 이메일/카카오/Push 발송 없이, BreadGo 내부 알림으로 처리할 Weekly Report 대상을 점검합니다."
        actions={
          <>
            <button type="button" onClick={createPreview} disabled={creating}>
              {creating ? "생성 중" : "Delivery 미리보기 생성"}
            </button>
            <button type="button" onClick={createUnreadReminder} disabled={reminding}>
              {reminding ? "생성 중" : "미확인 알림 리마인드 생성"}
            </button>
            <button type="button" onClick={loadDeliveryRuns} disabled={loading}>
              {loading ? "불러오는 중" : "이력 새로고침"}
            </button>
          </>
        }
      />

      <p className="message">
        현재 단계에서는 실제 이메일/카카오/Push를 발송하지 않고 BreadGo 내부 알림만 생성합니다.
        READY는 내부 알림 생성 가능, SENT는 Mock 발송 완료, SKIPPED는 제외 대상을 의미합니다.
      </p>

      {message && <div className={isError ? "notice error" : "notice success"}>{message}</div>}

      {notificationSummary && (
        <section className="panel">
          <div className="card-title-row">
            <div>
              <p className="eyebrow">Weekly Report 내부 알림 현황</p>
              <h2>읽음/미확인 상태</h2>
              <p>실제 외부 발송 없이 BreadGo 내부 알림으로 생성된 리포트 안내의 확인 상태입니다.</p>
            </div>
            <Badge tone={notificationSummary.unread_count > 0 ? "warning" : "success"}>
              미확인 {notificationSummary.unread_count}
            </Badge>
          </div>
          <div className="summary-grid compact">
            <StatCard label="전체 알림" value={notificationSummary.total_count} />
            <StatCard label="읽음" value={notificationSummary.read_count} />
            <StatCard label="미확인" value={notificationSummary.unread_count} />
            <StatCard label="읽음률" value={`${notificationSummary.read_rate}%`} />
            <StatCard label="최근 생성" value={formatDateTime(notificationSummary.latest_created_at)} />
            <StatCard label="최근 읽음" value={formatDateTime(notificationSummary.latest_read_at)} />
          </div>

          {notificationList && notificationList.notifications.length > 0 && (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Merchant</th>
                    <th>Snapshot</th>
                    <th>Delivery Run</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>Read</th>
                  </tr>
                </thead>
                <tbody>
                  {notificationList.notifications.map((notification) => (
                    <tr key={notification.notification_id}>
                      <td>{notification.merchant_id}</td>
                      <td>{notification.snapshot_id}</td>
                      <td>{notification.delivery_run_id}</td>
                      <td>
                        <Badge tone={notification.status === "READ" ? "success" : "warning"}>
                          {notification.status === "READ" ? "읽음 · READ" : "미확인 · UNREAD"}
                        </Badge>
                      </td>
                      <td>{formatDateTime(notification.created_at)}</td>
                      <td>{formatDateTime(notification.read_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      {lastPreview && (
        <section className="panel">
          <div className="card-title-row">
            <div>
              <p className="eyebrow">최근 미리보기 결과</p>
              <h2>
                {formatDate(lastPreview.period_start)} - {formatDate(lastPreview.period_end)}
              </h2>
            </div>
            <Badge tone={statusTone(lastPreview.status)}>{displayStatus(lastPreview.status)}</Badge>
          </div>
          <div className="summary-grid compact">
            <StatCard
              label={lastPreview.run_type === "IN_APP_MOCK" || lastPreview.run_type === "IN_APP_REMINDER" ? "내부 알림 생성 · SENT" : "발송 가능 · READY"}
              value={lastPreview.ready_count}
            />
            <StatCard label="제외 · SKIPPED" value={lastPreview.skipped_count} />
            <StatCard label="실패 · FAILED" value={lastPreview.failed_count} />
            <StatCard label="Channel" value={lastPreview.channel} />
          </div>
        </section>
      )}

      {history && history.delivery_runs.length > 0 ? (
        <div className="stacked-list">
          {history.delivery_runs.map((run) => (
            <DeliveryRunCard
              key={run.id}
              run={run}
              onMockSend={createMockDelivery}
              sending={sendingRunId === run.id}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          title="발송 미리보기 이력이 없습니다."
          description="Delivery 미리보기를 생성하면 READY/SKIPPED 대상과 이후 내부 알림 Mock 발송 결과가 이곳에 표시됩니다."
        />
      )}
    </section>
  );
}
