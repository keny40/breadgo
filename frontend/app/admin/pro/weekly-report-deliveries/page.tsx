"use client";

import { useCallback, useEffect, useState } from "react";
import { Badge, EmptyState, PageHeader, StatCard } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { AdminProWeeklyReportDeliveryRunHistory, ProWeeklyReportDeliveryRun } from "@/lib/types";

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
  if (status === "COMPLETED" || status === "READY") return "success";
  if (status === "FAILED") return "danger";
  if (status === "PARTIAL" || status === "PENDING") return "warning";
  return "muted";
}

function DeliveryRunCard({ run }: { run: ProWeeklyReportDeliveryRun }) {
  return (
    <article className="panel">
      <div className="card-title-row">
        <div>
          <p className="eyebrow">
            {run.run_type} · {run.channel}
          </p>
          <h2>
            {formatDate(run.period_start)} - {formatDate(run.period_end)}
          </h2>
          <p>{run.message || "Weekly Report delivery preview"}</p>
        </div>
        <Badge tone={statusTone(run.status)}>{run.status}</Badge>
      </div>

      <div className="summary-grid compact">
        <StatCard label="전체" value={run.total_count} />
        <StatCard label="READY" value={run.ready_count} />
        <StatCard label="SKIPPED" value={run.skipped_count} />
        <StatCard label="FAILED" value={run.failed_count} />
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
                  <Badge tone={statusTone(item.status)}>{item.status}</Badge>
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
  const [lastPreview, setLastPreview] = useState<ProWeeklyReportDeliveryRun | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);

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
      setHistory(result);
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
        description="실제 이메일/카카오/Push 발송 전, 발송 가능한 Weekly Report snapshot과 제외 대상을 확인합니다."
        actions={
          <>
            <button type="button" onClick={createPreview} disabled={creating}>
              {creating ? "생성 중" : "발송 미리보기 생성"}
            </button>
            <button type="button" onClick={loadDeliveryRuns} disabled={loading}>
              {loading ? "불러오는 중" : "이력 새로고침"}
            </button>
          </>
        }
      />

      <p className="message">
        이번 Phase는 preview/dry-run 단계입니다. 이메일, 카카오, Push, 외부 발송 API를 호출하지 않으며
        수신자 이메일/전화번호/주소/token을 저장하지 않습니다.
      </p>

      {message && <div className={isError ? "notice error" : "notice success"}>{message}</div>}

      {lastPreview && (
        <section className="panel">
          <div className="card-title-row">
            <div>
              <p className="eyebrow">최근 미리보기 결과</p>
              <h2>
                {formatDate(lastPreview.period_start)} - {formatDate(lastPreview.period_end)}
              </h2>
            </div>
            <Badge tone={statusTone(lastPreview.status)}>{lastPreview.status}</Badge>
          </div>
          <div className="summary-grid compact">
            <StatCard label="READY" value={lastPreview.ready_count} />
            <StatCard label="SKIPPED" value={lastPreview.skipped_count} />
            <StatCard label="FAILED" value={lastPreview.failed_count} />
            <StatCard label="Channel" value={lastPreview.channel} />
          </div>
        </section>
      )}

      {history && history.delivery_runs.length > 0 ? (
        <div className="stacked-list">
          {history.delivery_runs.map((run) => (
            <DeliveryRunCard key={run.id} run={run} />
          ))}
        </div>
      ) : (
        <EmptyState
          title="발송 미리보기 이력이 없습니다."
          description="발송 미리보기 생성을 누르면 READY/SKIPPED 대상이 기록됩니다."
        />
      )}
    </section>
  );
}
