"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";
import { Badge, EmptyState, PageHeader } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { ProHealthAlertList } from "@/lib/types";

const severities = ["", "WARNING", "CRITICAL"];
const statuses = ["", "OPEN", "ACKNOWLEDGED", "RESOLVED"];

function formatDateTime(value: string | null) {
  if (!value) return "-";
  return new Date(value).toLocaleString("ko-KR");
}

function tone(value: string): "success" | "warning" | "danger" | "muted" {
  if (value === "RESOLVED") return "success";
  if (value === "CRITICAL") return "danger";
  if (value === "WARNING" || value === "OPEN" || value === "ACKNOWLEDGED") return "warning";
  return "muted";
}

function buildQuery(filters: { severity: string; status: string }) {
  const params = new URLSearchParams();
  if (filters.severity) params.set("severity", filters.severity);
  if (filters.status) params.set("status", filters.status);
  params.set("limit", "100");
  return params.toString();
}

export default function AdminProHealthAlertsPage() {
  const guard = useRoleGuard("ADMIN");
  const [filters, setFilters] = useState({ severity: "", status: "" });
  const [appliedFilters, setAppliedFilters] = useState({ severity: "", status: "" });
  const [alerts, setAlerts] = useState<ProHealthAlertList>({ alerts: [], total_count: 0 });
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const loadAlerts = useCallback(async () => {
    setLoading(true);
    setMessage("");
    setIsError(false);
    try {
      const result = await apiFetch<ProHealthAlertList>(
        `/api/v1/admin/pro/operations/health/alerts?${buildQuery(appliedFilters)}`,
        {},
        true,
      );
      setAlerts(result);
      setMessage("Health Alert 목록을 불러왔습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }, [appliedFilters]);

  useEffect(() => {
    if (!guard.allowed) return;
    queueMicrotask(() => {
      void loadAlerts();
    });
  }, [guard.allowed, loadAlerts]);

  function applyFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setAppliedFilters(filters);
  }

  async function updateAlert(alertId: string, action: "acknowledge" | "resolve") {
    setActionLoading(`${action}-${alertId}`);
    setMessage("");
    setIsError(false);
    try {
      await apiFetch(`/api/v1/admin/pro/operations/health/alerts/${alertId}/${action}`, { method: "POST" }, true);
      await loadAlerts();
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
        title="Pro 상태 알림"
        description="Health Check 결과로 생성된 내부 관리자 알림을 확인하고 해결 처리합니다."
        actions={
          <>
            <Link className="button-link secondary" href="/admin/pro/operations">
              Pro Operations
            </Link>
            <button type="button" onClick={loadAlerts} disabled={loading}>
              {loading ? "불러오는 중" : "새로고침"}
            </button>
          </>
        }
      />
      {message && <div className={isError ? "notice error" : "notice success"}>{message}</div>}
      <section className="panel">
        <form className="form-grid" onSubmit={applyFilters}>
          <label>
            Severity
            <select
              value={filters.severity}
              onChange={(event) => setFilters((current) => ({ ...current, severity: event.target.value }))}
            >
              {severities.map((severity) => (
                <option key={severity || "ALL"} value={severity}>{severity || "전체"}</option>
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
                <option key={status || "ALL"} value={status}>{status || "전체"}</option>
              ))}
            </select>
          </label>
          <div className="actions">
            <button type="submit" disabled={loading}>필터 적용</button>
            <button type="button" className="secondary" onClick={() => {
              setFilters({ severity: "", status: "" });
              setAppliedFilters({ severity: "", status: "" });
            }}>
              초기화
            </button>
          </div>
        </form>
      </section>
      <section className="panel">
        <div className="card-title-row">
          <div>
            <p className="eyebrow">Health Alerts</p>
            <h2>최신순 상태 알림</h2>
            <p>현재 조건에서 {alerts.total_count}건이 조회되었습니다.</p>
          </div>
        </div>
        {alerts.alerts.length > 0 ? (
          <div className="stacked-list">
            {alerts.alerts.map((alert) => (
              <article className="item compact-card" key={alert.id}>
                <div className="card-title-row">
                  <div>
                    <strong>{alert.title}</strong>
                    <p>{alert.message}</p>
                    <small>{alert.source_key} · {formatDateTime(alert.created_at)}</small>
                  </div>
                  <div className="actions">
                    <Badge tone={tone(alert.severity)}>{alert.severity}</Badge>
                    <Badge tone={tone(alert.status)}>{alert.status}</Badge>
                  </div>
                </div>
                <div className="actions">
                  <button
                    type="button"
                    className="secondary"
                    onClick={() => updateAlert(alert.id, "acknowledge")}
                    disabled={actionLoading !== null || alert.status !== "OPEN"}
                  >
                    확인
                  </button>
                  <button
                    type="button"
                    onClick={() => updateAlert(alert.id, "resolve")}
                    disabled={actionLoading !== null || alert.status === "RESOLVED"}
                  >
                    해결 처리
                  </button>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <EmptyState title="조건에 맞는 Health Alert가 없습니다." />
        )}
      </section>
    </section>
  );
}
