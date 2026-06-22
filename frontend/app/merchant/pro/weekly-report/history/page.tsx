"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Badge, EmptyState, PageHeader, StatCard } from "@/components/UI";
import { apiFetch, buildApiUrl, friendlyErrorMessage, getToken } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { MerchantProWeeklyReportHistory, ProWeeklyReportSnapshot, ProWeeklyReportSnapshotInsight } from "@/lib/types";

function formatMoney(value: string) {
  return `${Number(value).toLocaleString()}원`;
}

function formatDate(value: string) {
  return new Date(`${value}T00:00:00`).toLocaleDateString("ko-KR", {
    month: "numeric",
    day: "numeric",
  });
}

function insightTone(severity: string | null): "success" | "warning" | "danger" | "muted" {
  if (severity === "POSITIVE") return "success";
  if (severity === "WARNING") return "warning";
  if (severity === "DANGER") return "danger";
  return "muted";
}

function InsightRow({ insight }: { insight: ProWeeklyReportSnapshotInsight }) {
  return (
    <div className="item compact-card">
      <div className="card-title-row">
        <strong>{insight.title || "운영 인사이트"}</strong>
        <Badge tone={insightTone(insight.severity)}>{insight.severity || "INFO"}</Badge>
      </div>
      <p>{insight.message}</p>
    </div>
  );
}

function SnapshotCard({
  snapshot,
  exportingId,
  onCopySummary,
  onDownloadCsv,
}: {
  snapshot: ProWeeklyReportSnapshot;
  exportingId: string | null;
  onCopySummary: (snapshotId: string) => void;
  onDownloadCsv: (snapshotId: string) => void;
}) {
  const weeklyReportHref = `/merchant/pro/weekly-report?start_date=${snapshot.start_date}&end_date=${snapshot.end_date}`;
  const isExporting = exportingId === snapshot.id;

  return (
    <article className="panel">
      <div className="card-title-row">
        <div>
          <p className="eyebrow">저장된 리포트</p>
          <h2>
            {formatDate(snapshot.start_date)} - {formatDate(snapshot.end_date)}
          </h2>
          <p>수동 저장과 자동 저장 준비 흐름이 함께 사용하는 공통 이력입니다.</p>
        </div>
        <Badge tone={snapshot.high_severity_alert_count > 0 ? "danger" : "success"}>
          HIGH {snapshot.high_severity_alert_count}
        </Badge>
      </div>

      <div className="summary-grid compact">
        <StatCard label="총 매출" value={formatMoney(snapshot.total_sales_amount)} />
        <StatCard label="예약" value={snapshot.total_reservation_count} />
        <StatCard label="픽업" value={snapshot.total_picked_up_count} />
        <StatCard label="폐기 절감" value={`${snapshot.total_saved_quantity}개`} />
        <StatCard label="평균 미해결 알림" value={Number(snapshot.average_unresolved_alert_count).toFixed(1)} />
        <StatCard label="추천 액션" value={snapshot.total_recommendation_action_count} />
      </div>

      <div className="stacked-list">
        {snapshot.insights.length > 0 ? (
          snapshot.insights.map((insight) => <InsightRow key={insight.id} insight={insight} />)
        ) : (
          <EmptyState title="저장된 인사이트가 없습니다." />
        )}
      </div>

      {snapshot.text_summary && (
        <details className="compact-card">
          <summary>공유용 텍스트 요약 보기</summary>
          <pre className="text-export-preview">{snapshot.text_summary}</pre>
        </details>
      )}

      <div className="actions">
        <button type="button" onClick={() => onDownloadCsv(snapshot.id)} disabled={isExporting}>
          {isExporting ? "처리 중" : "CSV 다운로드"}
        </button>
        <button type="button" onClick={() => onCopySummary(snapshot.id)} disabled={isExporting}>
          요약 복사
        </button>
        <Link className="button-link secondary" href={weeklyReportHref}>
          현재 기간으로 열기
        </Link>
        <Link className="button-link secondary" href="/merchant/pro/weekly-report">
          최신 주간 리포트
        </Link>
      </div>
    </article>
  );
}

export default function MerchantProWeeklyReportHistoryPage() {
  const guard = useRoleGuard("MERCHANT");
  const [history, setHistory] = useState<MerchantProWeeklyReportHistory | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);
  const [exportingId, setExportingId] = useState<string | null>(null);

  useEffect(() => {
    if (!guard.allowed) return;
    void loadHistory();
  }, [guard.allowed]);

  async function loadHistory() {
    setLoading(true);
    setMessage("");
    setIsError(false);
    try {
      const data = await apiFetch<MerchantProWeeklyReportHistory>("/api/v1/merchant/pro/weekly-report/history", {}, true);
      setHistory(data);
      setMessage("저장된 주간 리포트 이력을 불러왔습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  async function fetchSnapshotExport(snapshotId: string, format: "csv" | "text") {
    const token = getToken();
    if (!token) {
      throw new Error("로그인이 필요합니다.");
    }
    const response = await fetch(
      buildApiUrl(`/api/v1/merchant/pro/weekly-report/history/${snapshotId}/export?format=${format}`),
      {
        headers: {
          Accept: format === "csv" ? "text/csv" : "text/plain",
          Authorization: `Bearer ${token}`,
        },
      },
    );
    if (!response.ok) {
      throw new Error(await response.text());
    }
    return response;
  }

  async function downloadSnapshotCsv(snapshotId: string) {
    setExportingId(snapshotId);
    setMessage("");
    setIsError(false);
    try {
      const response = await fetchSnapshotExport(snapshotId, "csv");
      const csv = await response.text();
      const blob = new Blob(["\uFEFF", csv], { type: "text/csv;charset=utf-8" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "breadgo-saved-weekly-report.csv";
      link.click();
      window.URL.revokeObjectURL(url);
      setMessage("저장된 리포트 CSV를 다운로드했습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setExportingId(null);
    }
  }

  async function copySnapshotSummary(snapshotId: string) {
    setExportingId(snapshotId);
    setMessage("");
    setIsError(false);
    try {
      const response = await fetchSnapshotExport(snapshotId, "text");
      const text = await response.text();
      await navigator.clipboard.writeText(text);
      setMessage("저장된 리포트 요약을 클립보드에 복사했습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setExportingId(null);
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
        title="주간 리포트 이력"
        description="수동 저장 또는 자동 저장 준비 흐름으로 저장된 주간 운영 리포트를 다시 확인합니다."
        actions={
          <>
            <button type="button" onClick={loadHistory} disabled={loading}>
              {loading ? "불러오는 중" : "이력 새로고침"}
            </button>
            <Link className="button-link secondary" href="/merchant/pro/weekly-report">
              주간 리포트
            </Link>
          </>
        }
      />

      {message && <div className={isError ? "notice error" : "notice success"}>{message}</div>}

      {history && history.snapshots.length > 0 ? (
        <div className="stacked-list">
          {history.snapshots.map((snapshot) => (
            <SnapshotCard
              key={snapshot.id}
              snapshot={snapshot}
              exportingId={exportingId}
              onCopySummary={copySnapshotSummary}
              onDownloadCsv={downloadSnapshotCsv}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          title="저장된 주간 리포트가 없습니다."
          description="주간 리포트 화면에서 수동 저장 또는 자동 저장 버튼을 누르면 이력이 생성됩니다."
        />
      )}
    </section>
  );
}
