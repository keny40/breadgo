"use client";

import { useCallback, useEffect, useState } from "react";
import { Badge, EmptyState, PageHeader, StatCard } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { AdminProWeeklyReportBatchRunMonitor, ProWeeklyReportBatchRun } from "@/lib/types";

const statuses = ["", "STARTED", "COMPLETED", "FAILED", "PARTIAL"];
const runTypes = ["", "MANUAL_TEST", "SCHEDULE_PREP"];

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
  if (status === "COMPLETED" || status === "SUCCESS") return "success";
  if (status === "FAILED") return "danger";
  if (status === "PARTIAL" || status === "STARTED") return "warning";
  return "muted";
}

function BatchRunCard({ run }: { run: ProWeeklyReportBatchRun }) {
  return (
    <article className="panel">
      <div className="card-title-row">
        <div>
          <p className="eyebrow">{run.run_type}</p>
          <h2>
            {formatDate(run.start_date)} - {formatDate(run.end_date)}
          </h2>
          <p>{run.message || "Weekly Report batch run"}</p>
        </div>
        <Badge tone={statusTone(run.status)}>{run.status}</Badge>
      </div>

      <div className="summary-grid compact">
        <StatCard label="대상" value={run.target_merchant_count} />
        <StatCard label="성공" value={run.success_count} />
        <StatCard label="실패" value={run.failed_count} />
        <StatCard label="스킵" value={run.skipped_count} />
        <StatCard label="실행" value={formatDateTime(run.created_at)} />
        <StatCard label="완료" value={formatDateTime(run.completed_at)} />
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Merchant</th>
              <th>Snapshot</th>
              <th>Status</th>
              <th>Message</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {run.items.map((item) => (
              <tr key={item.id}>
                <td>{item.merchant_id}</td>
                <td>{item.snapshot_id || "-"}</td>
                <td>
                  <Badge tone={statusTone(item.status)}>{item.status}</Badge>
                </td>
                <td>{item.message || "-"}</td>
                <td>{formatDateTime(item.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </article>
  );
}

export default function AdminWeeklyReportBatchMonitorPage() {
  const guard = useRoleGuard("ADMIN");
  const [data, setData] = useState<AdminProWeeklyReportBatchRunMonitor | null>(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [runType, setRunType] = useState("");
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  const loadBatchRuns = useCallback(async () => {
    setLoading(true);
    setMessage("");
    setIsError(false);
    try {
      const params = new URLSearchParams();
      if (statusFilter) params.set("status", statusFilter);
      if (runType) params.set("run_type", runType);
      const query = params.toString();
      const result = await apiFetch<AdminProWeeklyReportBatchRunMonitor>(
        `/api/v1/admin/pro/weekly-report/batch-runs${query ? `?${query}` : ""}`,
        {},
        true,
      );
      setData(result);
      setMessage("Weekly Report batch run 이력을 불러왔습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }, [runType, statusFilter]);

  useEffect(() => {
    if (!guard.allowed) return;
    queueMicrotask(() => {
      void loadBatchRuns();
    });
  }, [guard.allowed, loadBatchRuns]);

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
        title="Weekly Report Batch Monitor"
        description="BreadGo Pro 주간 리포트 자동 생성 준비 작업의 실행 이력과 merchant별 결과를 확인합니다."
        actions={
          <button type="button" onClick={loadBatchRuns} disabled={loading}>
            {loading ? "불러오는 중" : "새로고침"}
          </button>
        }
      />

      <p className="message">
        실제 cron/scheduler는 아직 연결하지 않았습니다. 현재는 점주 화면의 자동 생성 테스트 실행 이력을 모니터링합니다.
      </p>

      {message && <div className={isError ? "notice error" : "notice success"}>{message}</div>}

      <section className="panel">
        <div className="form-grid">
          <label>
            상태
            <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
              {statuses.map((status) => (
                <option key={status || "ALL"} value={status}>
                  {status || "전체"}
                </option>
              ))}
            </select>
          </label>
          <label>
            실행 유형
            <select value={runType} onChange={(event) => setRunType(event.target.value)}>
              {runTypes.map((type) => (
                <option key={type || "ALL"} value={type}>
                  {type || "전체"}
                </option>
              ))}
            </select>
          </label>
          <button type="button" onClick={loadBatchRuns} disabled={loading}>
            필터 적용
          </button>
        </div>
      </section>

      {data && (
        <div className="summary-grid">
          <StatCard label="전체 실행" value={data.summary.total_runs} />
          <StatCard label="완료" value={data.summary.completed_count} />
          <StatCard label="실패" value={data.summary.failed_count} />
          <StatCard label="부분 성공" value={data.summary.partial_count} />
          <StatCard label="최근 상태" value={data.summary.latest_run_status || "-"} />
          <StatCard label="최근 실행" value={formatDateTime(data.summary.latest_run_at)} />
        </div>
      )}

      {data && data.batch_runs.length > 0 ? (
        <div className="stacked-list">
          {data.batch_runs.map((run) => (
            <BatchRunCard key={run.id} run={run} />
          ))}
        </div>
      ) : (
        <EmptyState title="표시할 batch run 이력이 없습니다." />
      )}
    </section>
  );
}
