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
              {exporting ? "다운로드 중" : "CSV 다운로드"}
            </button>
            <button type="button" onClick={() => loadAuditLogs(appliedFilters)} disabled={loading}>
              {loading ? "불러오는 중" : "새로고침"}
            </button>
          </>
        }
      />

      <p className="message">
        감사 로그는 운영 액션, 상태, 대상 id, count 중심으로만 표시합니다. 이메일, 전화번호, 주소, 외부 발송 토큰은 저장하거나 표시하지 않습니다.
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
            <p className="eyebrow">Filters</p>
            <h2>감사 로그 필터</h2>
          </div>
          <Badge tone={(summary?.failed_count || 0) > 0 ? "warning" : "success"}>
            실패 {summary?.failed_count || 0}
          </Badge>
        </div>
        <form className="form-grid" onSubmit={applyFilters}>
          <label>
            Action Type
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
            Status
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
            Target Type
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
            Target ID
            <input
              value={filters.target_id}
              onChange={(event) => setFilters((current) => ({ ...current, target_id: event.target.value }))}
              placeholder="UUID"
            />
          </label>
          <label>
            Date From
            <input
              type="date"
              value={filters.date_from}
              onChange={(event) => setFilters((current) => ({ ...current, date_from: event.target.value }))}
            />
          </label>
          <label>
            Date To
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
          <EmptyState title="조건에 맞는 감사 로그가 없습니다." />
        )}
      </section>
    </section>
  );
}
