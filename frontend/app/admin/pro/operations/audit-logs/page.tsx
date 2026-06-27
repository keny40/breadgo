"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";
import { Badge, EmptyState, PageHeader, StatCard } from "@/components/UI";
import { apiFetch, buildApiUrl, friendlyErrorMessage, getToken } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { ProOperationsAuditLogList, ProOperationsAuditLogSummary } from "@/lib/types";

const actionTypes = [
  "",
  "RUN_WEEKLY_REPORT_BATCH",
  "CREATE_DELIVERY_PREVIEW",
  "RUN_IN_APP_MOCK_DELIVERY",
  "RUN_UNREAD_REMINDER",
  "RETRY_FAILED_BATCH_ITEMS",
  "EXPORT_AUDIT_LOG_CSV",
  "PURGE_AUDIT_LOGS",
];

const targetTypes = ["", "BATCH_RUN", "DELIVERY_RUN", "NOTIFICATION", "OPERATIONS", "WEEKLY_REPORT", "AUDIT_LOG"];
const statuses = ["", "SUCCESS", "FAILED"];

function formatDateTime(value: string | null) {
  if (!value) return "-";
  return new Date(value).toLocaleString("ko-KR");
}

function statusTone(status: string): "success" | "danger" | "warning" | "muted" {
  if (status === "SUCCESS") return "success";
  if (status === "FAILED") return "danger";
  return "muted";
}

function targetHref(targetType: string, targetId: string | null) {
  if (targetType === "BATCH_RUN") return "/admin/pro/weekly-report-batches";
  if (targetType === "DELIVERY_RUN") return "/admin/pro/weekly-report-deliveries";
  if (targetType === "OPERATIONS") return "/admin/pro/operations";
  return targetId ? null : "/admin/pro/operations";
}

function buildQuery(filters: AuditLogFilters, includeLimit = true) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });
  if (includeLimit) {
    params.set("limit", "100");
  }
  return params.toString();
}

type AuditLogFilters = {
  action_type: string;
  status: string;
  target_type: string;
  target_id: string;
  date_from: string;
  date_to: string;
};

type AuditLogPurgePreview = {
  retention_days: number;
  cutoff_date: string;
  matched_count: number;
  oldest_created_at: string | null;
  newest_created_at: string | null;
  status_counts: Record<string, number>;
  action_type_counts: Record<string, number>;
  message: string;
  deleted_count?: number;
};

const emptyFilters: AuditLogFilters = {
  action_type: "",
  status: "",
  target_type: "",
  target_id: "",
  date_from: "",
  date_to: "",
};

export default function AdminProOperationsAuditLogsPage() {
  const guard = useRoleGuard("ADMIN");
  const [filters, setFilters] = useState<AuditLogFilters>(emptyFilters);
  const [appliedFilters, setAppliedFilters] = useState<AuditLogFilters>(emptyFilters);
  const [summary, setSummary] = useState<ProOperationsAuditLogSummary | null>(null);
  const [logs, setLogs] = useState<ProOperationsAuditLogList>({ audit_logs: [], total_count: 0 });
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [purgeRetentionDays, setPurgeRetentionDays] = useState(180);
  const [purgePreview, setPurgePreview] = useState<AuditLogPurgePreview | null>(null);
  const [purgeLoading, setPurgeLoading] = useState(false);

  const loadAuditLogs = useCallback(async (nextFilters: AuditLogFilters) => {
    setLoading(true);
    setMessage("");
    setIsError(false);
    try {
      const query = buildQuery(nextFilters);
      const [summaryResult, logsResult] = await Promise.all([
        apiFetch<ProOperationsAuditLogSummary>(
          `/api/v1/admin/pro/operations/audit-logs/summary?${query}`,
          {},
          true,
        ),
        apiFetch<ProOperationsAuditLogList>(`/api/v1/admin/pro/operations/audit-logs?${query}`, {}, true),
      ]);
      setSummary(summaryResult);
      setLogs(logsResult);
      setMessage("감사 로그를 불러왔습니다.");
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
      void loadAuditLogs(appliedFilters);
    });
  }, [guard.allowed, appliedFilters, loadAuditLogs]);

  function applyFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setAppliedFilters(filters);
  }

  function resetFilters() {
    setFilters(emptyFilters);
    setAppliedFilters(emptyFilters);
  }

  async function downloadCsv() {
    setExporting(true);
    setMessage("");
    setIsError(false);
    try {
      const token = getToken();
      if (!token) {
        throw new Error("로그인이 필요합니다.");
      }
      const query = buildQuery(appliedFilters, false);
      const response = await fetch(
        buildApiUrl(`/api/v1/admin/pro/operations/audit-logs/export.csv${query ? `?${query}` : ""}`),
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );
      if (!response.ok) {
        const body = await response.text();
        throw new Error(body || `CSV 다운로드에 실패했습니다. (${response.status})`);
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      const yyyymmdd = new Date().toISOString().slice(0, 10).replaceAll("-", "");
      link.href = url;
      link.download = `pro-audit-logs-${yyyymmdd}.csv`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      setMessage("현재 필터 조건으로 CSV를 다운로드했습니다.");
      await loadAuditLogs(appliedFilters);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setExporting(false);
    }
  }

  function purgePayload(confirm = false) {
    return {
      retention_days: purgeRetentionDays,
      confirm,
      status: appliedFilters.status || null,
      action_type: appliedFilters.action_type || null,
    };
  }

  async function previewPurge() {
    if (purgeRetentionDays < 30) {
      setIsError(true);
      setMessage("retention_days는 최소 30일 이상이어야 합니다.");
      return;
    }
    setPurgeLoading(true);
    setMessage("");
    setIsError(false);
    try {
      const result = await apiFetch<AuditLogPurgePreview>(
        "/api/v1/admin/pro/operations/audit-logs/purge/preview",
        {
          method: "POST",
          body: JSON.stringify(purgePayload(false)),
        },
        true,
      );
      setPurgePreview(result);
      setMessage("삭제 대상 미리보기를 확인했습니다. 아직 실제 삭제는 실행하지 않았습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setPurgeLoading(false);
    }
  }

  async function executePurge() {
    if (!purgePreview) {
      setIsError(true);
      setMessage("먼저 삭제 대상 미리보기를 확인해 주세요.");
      return;
    }
    setPurgeLoading(true);
    setMessage("");
    setIsError(false);
    try {
      const result = await apiFetch<AuditLogPurgePreview>(
        "/api/v1/admin/pro/operations/audit-logs/purge",
        {
          method: "POST",
          body: JSON.stringify(purgePayload(true)),
        },
        true,
      );
      setPurgePreview(result);
      setMessage(`오래된 감사 로그 ${result.deleted_count || 0}건을 삭제했습니다.`);
      await loadAuditLogs(appliedFilters);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setPurgeLoading(false);
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
        title="Pro 감사 로그"
        description="관리자 Pro 운영 액션을 필터링하고 실패 이력을 추적합니다."
        actions={
          <>
            <Link className="button-link secondary" href="/admin/pro/operations">
              Pro Operations
            </Link>
            <button type="button" onClick={downloadCsv} disabled={loading || exporting}>
              {exporting ? "다운로드 중" : "감사 로그 CSV 다운로드"}
            </button>
            <button type="button" onClick={() => loadAuditLogs(appliedFilters)} disabled={loading}>
              {loading ? "불러오는 중" : "새로고침"}
            </button>
          </>
        }
      />

      <p className="message">
        감사 로그는 운영 액션, 상태, 대상 id, count 중심으로만 표시합니다. CSV에는 개인정보, 연락처, 주소, 토큰이 포함되지 않습니다.
      </p>

      {message && <div className={isError ? "notice error" : "notice success"}>{message}</div>}

      <div className="summary-grid">
        <StatCard label="전체 건수" value={summary?.total_count || 0} />
        <StatCard label="성공" value={summary?.success_count || 0} />
        <StatCard label="실패" value={summary?.failed_count || 0} />
        <StatCard label="최근 24시간" value={summary?.last_24h_count || 0} />
        <StatCard label="최근 24시간 실패" value={summary?.last_24h_failed_count || 0} />
      </div>

      <section className="panel">
        <div className="card-title-row">
          <div>
            <p className="eyebrow">필터</p>
            <h2>감사 로그 필터</h2>
          </div>
          <Badge tone={(summary?.failed_count || 0) > 0 ? "warning" : "success"}>
            실패 {summary?.failed_count || 0}
          </Badge>
        </div>
        <form className="form-grid" onSubmit={applyFilters}>
          <label>
            액션 유형
            <select
              value={filters.action_type}
              onChange={(event) => setFilters((current) => ({ ...current, action_type: event.target.value }))}
            >
              {actionTypes.map((actionType) => (
                <option key={actionType || "ALL"} value={actionType}>
                  {actionType || "전체"}
                </option>
              ))}
            </select>
          </label>
          <label>
            실행 상태
            <select
              value={filters.status}
              onChange={(event) => setFilters((current) => ({ ...current, status: event.target.value }))}
            >
              {statuses.map((status) => (
                <option key={status || "ALL"} value={status}>
                  {status || "전체"}
                </option>
              ))}
            </select>
          </label>
          <label>
            대상 유형
            <select
              value={filters.target_type}
              onChange={(event) => setFilters((current) => ({ ...current, target_type: event.target.value }))}
            >
              {targetTypes.map((targetType) => (
                <option key={targetType || "ALL"} value={targetType}>
                  {targetType || "전체"}
                </option>
              ))}
            </select>
          </label>
          <label>
            대상 ID
            <input
              value={filters.target_id}
              onChange={(event) => setFilters((current) => ({ ...current, target_id: event.target.value }))}
              placeholder="UUID"
            />
          </label>
          <label>
            시작일
            <input
              type="date"
              value={filters.date_from}
              onChange={(event) => setFilters((current) => ({ ...current, date_from: event.target.value }))}
            />
          </label>
          <label>
            종료일
            <input
              type="date"
              value={filters.date_to}
              onChange={(event) => setFilters((current) => ({ ...current, date_to: event.target.value }))}
            />
          </label>
          <div className="actions">
            <button type="submit" disabled={loading}>
              필터 적용
            </button>
            <button type="button" className="secondary" onClick={resetFilters} disabled={loading}>
              초기화
            </button>
          </div>
        </form>
      </section>

      <section className="panel">
        <div className="card-title-row">
          <div>
            <p className="eyebrow">오래된 감사 로그 정리</p>
            <h2>오래된 감사 로그 정리</h2>
            <p>삭제 전 반드시 Preview로 대상 범위를 확인하세요. 삭제 실행은 되돌릴 수 없습니다.</p>
          </div>
          <Badge tone="warning">ADMIN only</Badge>
        </div>
        <div className="form-grid">
          <label>
            보관 기간(일)
            <input
              type="number"
              min={30}
              value={purgeRetentionDays}
              onChange={(event) => {
                setPurgeRetentionDays(Number(event.target.value));
                setPurgePreview(null);
              }}
            />
          </label>
          <label>
            적용 중인 Status 필터
            <input value={appliedFilters.status || "전체"} readOnly />
          </label>
          <label>
            적용 중인 Action Type 필터
            <input value={appliedFilters.action_type || "전체"} readOnly />
          </label>
          <div className="actions">
            <button type="button" onClick={previewPurge} disabled={purgeLoading || purgeRetentionDays < 30}>
              {purgeLoading ? "확인 중" : "삭제 대상 미리보기"}
            </button>
            <button
              type="button"
              className="danger"
              onClick={executePurge}
              disabled={purgeLoading || !purgePreview || purgePreview.matched_count === 0}
            >
              확인 후 삭제 실행
            </button>
          </div>
        </div>
        {purgePreview && (
          <div className="summary-grid compact">
            <StatCard label="삭제 대상" value={purgePreview.matched_count} />
            <StatCard label="Cutoff" value={formatDateTime(purgePreview.cutoff_date)} />
            <StatCard label="가장 오래된 로그" value={formatDateTime(purgePreview.oldest_created_at)} />
            <StatCard label="가장 최근 대상" value={formatDateTime(purgePreview.newest_created_at)} />
            <StatCard label="삭제 완료" value={purgePreview.deleted_count ?? "-"} />
          </div>
        )}
        {purgePreview && (
          <div className="stacked-list">
            <article className="item compact-card">
              <strong>{purgePreview.message}</strong>
              <p className="field-help">
                삭제 실행 전 대상 수, cutoff, 필터 조건을 다시 확인하세요. 30일 미만 보관 기간은 허용되지 않습니다.
              </p>
              <p>
                Status별: {Object.entries(purgePreview.status_counts).map(([key, count]) => `${key} ${count}`).join(", ") || "-"}
              </p>
              <p>
                Action별:{" "}
                {Object.entries(purgePreview.action_type_counts)
                  .map(([key, count]) => `${key} ${count}`)
                  .join(", ") || "-"}
              </p>
              <p className="field-help">
                삭제 실행은 되돌릴 수 없습니다. 필요한 경우 CSV 다운로드 후 별도 보안 관리 체계에서 보관하세요.
              </p>
            </article>
          </div>
        )}
      </section>

      <section className="panel">
        <div className="card-title-row">
          <div>
            <p className="eyebrow">Audit Logs</p>
            <h2>최신순 감사 로그</h2>
            <p>현재 조건에서 {logs.total_count}건이 조회되었습니다.</p>
          </div>
          <Badge tone="muted">최근 100건</Badge>
        </div>
        {logs.audit_logs.length > 0 ? (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>실행 시각</th>
                  <th>액션</th>
                  <th>상태</th>
                  <th>대상</th>
                  <th>Target ID</th>
                  <th>Actor</th>
                  <th>메시지</th>
                </tr>
              </thead>
              <tbody>
                {logs.audit_logs.map((log) => {
                  const href = targetHref(log.target_type, log.target_id);
                  return (
                    <tr key={log.id} className={log.status === "FAILED" ? "danger-row" : undefined}>
                      <td>{formatDateTime(log.created_at)}</td>
                      <td>{log.action_type}</td>
                      <td>
                        <Badge tone={statusTone(log.status)}>{log.status}</Badge>
                      </td>
                      <td>{log.target_type}</td>
                      <td>
                        {href ? (
                          <Link href={href}>{log.target_id || "바로가기"}</Link>
                        ) : (
                          log.target_id || "-"
                        )}
                      </td>
                      <td>{log.actor_role}</td>
                      <td>{log.message || "-"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState
            title="조건에 맞는 감사 로그가 없습니다."
            description="필터를 초기화하거나 Quick Action을 실행하면 새 감사 로그가 표시됩니다."
          />
        )}
      </section>
    </section>
  );
}
