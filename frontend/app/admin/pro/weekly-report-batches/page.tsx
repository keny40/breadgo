"use client";

import { useCallback, useEffect, useState } from "react";
import { Badge, EmptyState, PageHeader, StatCard } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type {
  AdminProWeeklyReportBatchRunMonitor,
  AdminWeeklyReportBatchPreview,
  ProWeeklyReportBatchRun,
} from "@/lib/types";

const statuses = ["", "STARTED", "COMPLETED", "FAILED", "PARTIAL", "SKIPPED"];
const runTypes = ["", "MANUAL_TEST", "SCHEDULE_PREP", "SCHEDULED", "RETRY"];
const runTypeLabels: Record<string, string> = {
  MANUAL_TEST: "관리자 수동 테스트",
  SCHEDULE_PREP: "자동 생성 준비",
  SCHEDULED: "Scheduler 자동 실행",
  RETRY: "실패 건 재실행",
};
const statusLabels: Record<string, string> = {
  STARTED: "실행 중",
  COMPLETED: "완료",
  FAILED: "실패",
  PARTIAL: "부분 성공",
  SKIPPED: "건너뜀",
  SUCCESS: "성공",
};

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
  if (status === "SKIPPED") return "muted";
  return "muted";
}

function displayRunType(runType: string) {
  return runTypeLabels[runType] ? `${runTypeLabels[runType]} · ${runType}` : runType;
}

function displayStatus(status: string) {
  return statusLabels[status] ? `${statusLabels[status]} · ${status}` : status;
}

function BatchRunCard({
  run,
  retryingId,
  onRetryFailed,
}: {
  run: ProWeeklyReportBatchRun;
  retryingId: string | null;
  onRetryFailed: (batchRunId: string) => void;
}) {
  const failedItemCount = run.items.filter((item) => item.status === "FAILED").length;
  return (
    <article className="panel">
      <div className="card-title-row">
        <div>
          <p className="eyebrow">{displayRunType(run.run_type)}</p>
          <h2>
            {formatDate(run.start_date)} - {formatDate(run.end_date)}
          </h2>
          <p>{run.message || "Weekly Report batch run"}</p>
        </div>
        <Badge tone={statusTone(run.status)}>{displayStatus(run.status)}</Badge>
      </div>

      <div className="summary-grid compact">
        <StatCard label="대상" value={run.target_merchant_count} />
        <StatCard label="성공" value={run.success_count} />
        <StatCard label="실패" value={run.failed_count} />
        <StatCard label="스킵" value={run.skipped_count} />
        <StatCard label="실행" value={formatDateTime(run.created_at)} />
        <StatCard label="완료" value={formatDateTime(run.completed_at)} />
      </div>

      <div className="actions">
        {failedItemCount > 0 ? (
          <button type="button" onClick={() => onRetryFailed(run.id)} disabled={retryingId === run.id}>
            {retryingId === run.id ? "재실행 중" : `실패 merchant만 재실행 (${failedItemCount})`}
          </button>
        ) : (
          <span className="field-help">실패 item이 없어 재실행할 대상이 없습니다.</span>
        )}
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
                  <Badge tone={statusTone(item.status)}>{displayStatus(item.status)}</Badge>
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
  const [batchActionLoading, setBatchActionLoading] = useState(false);
  const [preview, setPreview] = useState<AdminWeeklyReportBatchPreview | null>(null);
  const [lastRun, setLastRun] = useState<ProWeeklyReportBatchRun | null>(null);
  const [retryingId, setRetryingId] = useState<string | null>(null);

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

  async function previewFullBatch() {
    setBatchActionLoading(true);
    setMessage("");
    setIsError(false);
    try {
      const result = await apiFetch<AdminWeeklyReportBatchPreview>(
        "/api/v1/admin/pro/weekly-report/batch-runs/preview",
        { method: "POST" },
        true,
      );
      setPreview(result);
      setMessage("전체 가맹점 Weekly Report 배치 미리보기를 확인했습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setBatchActionLoading(false);
    }
  }

  async function runFullBatch() {
    setBatchActionLoading(true);
    setMessage("");
    setIsError(false);
    try {
      const result = await apiFetch<ProWeeklyReportBatchRun>(
        "/api/v1/admin/pro/weekly-report/batch-runs",
        { method: "POST" },
        true,
      );
      setLastRun(result);
      setMessage(`전체 가맹점 리포트 생성 테스트가 완료되었습니다. Batch: ${result.id}`);
      await loadBatchRuns();
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setBatchActionLoading(false);
    }
  }

  async function retryFailedItems(batchRunId: string) {
    setRetryingId(batchRunId);
    setMessage("");
    setIsError(false);
    try {
      const result = await apiFetch<ProWeeklyReportBatchRun>(
        `/api/v1/admin/pro/weekly-report/batch-runs/${batchRunId}/retry-failed`,
        { method: "POST" },
        true,
      );
      setLastRun(result);
      setMessage(`실패 item 재실행이 완료되었습니다. Retry batch: ${result.id}`);
      await loadBatchRuns();
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setRetryingId(null);
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
        <div className="card-title-row">
          <div>
            <p className="eyebrow">Admin Manual Batch</p>
            <h2>전체 가맹점 리포트 생성 테스트</h2>
            <p>
              실행하면 각 가맹점의 동일 기간 Weekly Report snapshot이 생성 또는 업데이트됩니다.
              실제 cron/scheduler와 외부 발송은 아직 연결하지 않습니다.
            </p>
          </div>
          <Badge tone="warning">SCHEDULE_PREP</Badge>
        </div>
        <div className="actions">
          <button type="button" onClick={previewFullBatch} disabled={batchActionLoading}>
            {batchActionLoading ? "확인 중" : "전체 배치 미리보기"}
          </button>
          <button type="button" onClick={runFullBatch} disabled={batchActionLoading}>
            {batchActionLoading ? "실행 중" : "전체 가맹점 리포트 생성 테스트"}
          </button>
        </div>
        {preview && (
          <div className="summary-grid compact">
            <StatCard label="대상 기간" value={`${formatDate(preview.start_date)} - ${formatDate(preview.end_date)}`} />
            <StatCard label="대상 가맹점" value={preview.target_merchant_count} />
            <StatCard label="생성/업데이트 예정" value={preview.would_create_or_update_count} />
            <StatCard label="안내" value={preview.message} />
          </div>
        )}
        {lastRun && (
          <div className="summary-grid compact">
            <StatCard label="최근 실행 Batch" value={lastRun.id} />
            <StatCard label="상태" value={lastRun.status} />
            <StatCard label="성공" value={lastRun.success_count} />
            <StatCard label="실패" value={lastRun.failed_count} />
          </div>
        )}
      </section>

      <section className="panel">
        <div className="card-title-row">
          <div>
            <p className="eyebrow">상태 안내</p>
            <h2>Batch run_type / status 의미</h2>
            <p>
              SCHEDULED는 운영 scheduler 실행, RETRY는 실패 merchant만 재실행, SCHEDULE_PREP는 자동 생성 준비 흐름입니다.
              COMPLETED는 전체 성공, PARTIAL은 일부 실패, SKIPPED는 동일 기간 중복 실행 방지 또는 대상 없음입니다.
              SKIPPED는 조건에 따라 정상적인 안전장치일 수 있습니다.
            </p>
          </div>
        </div>
      </section>

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
          <StatCard label="최근 상태" value={data.summary.latest_run_status ? displayStatus(data.summary.latest_run_status) : "-"} />
          <StatCard label="최근 실행" value={formatDateTime(data.summary.latest_run_at)} />
        </div>
      )}

      {data && data.batch_runs.length > 0 ? (
        <div className="stacked-list">
          {data.batch_runs.map((run) => (
            <BatchRunCard key={run.id} run={run} retryingId={retryingId} onRetryFailed={retryFailedItems} />
          ))}
        </div>
      ) : (
        <EmptyState
          title="표시할 batch run 이력이 없습니다."
          description="전체 가맹점 리포트 생성 테스트 또는 scheduler CLI를 실행하면 이곳에 기록됩니다."
        />
      )}
    </section>
  );
}
