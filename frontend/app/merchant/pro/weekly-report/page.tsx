"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Badge, EmptyState, PageHeader, StatCard } from "@/components/UI";
import { apiFetch, buildApiUrl, friendlyErrorMessage, getToken } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type {
  MerchantProWeeklyReport,
  MerchantProWeeklyReportBatchRunHistory,
  ProWeeklyReportAutoSnapshotPreview,
  ProWeeklyReportAutoSnapshotRun,
  ProWeeklyReportDailyTrend,
  ProWeeklyReportInsight,
  ProWeeklyReportSnapshot,
} from "@/lib/types";

function formatMoney(value: string) {
  return `${Number(value).toLocaleString()}원`;
}

function formatDate(value: string) {
  return new Date(`${value}T00:00:00`).toLocaleDateString("ko-KR", {
    month: "numeric",
    day: "numeric",
  });
}

function insightTone(severity: string): "success" | "warning" | "danger" | "muted" {
  if (severity === "POSITIVE") return "success";
  if (severity === "WARNING") return "warning";
  if (severity === "DANGER") return "danger";
  return "muted";
}

function maxTrendValue(trends: ProWeeklyReportDailyTrend[]) {
  return Math.max(
    1,
    ...trends.map((trend) =>
      Math.max(
        Number(trend.sales_amount) / 10000,
        trend.reservation_count,
        trend.picked_up_count,
        trend.saved_quantity,
        trend.unresolved_alert_count,
      ),
    ),
  );
}

function InsightCard({ insight }: { insight: ProWeeklyReportInsight }) {
  return (
    <article className="item compact-card">
      <div className="card-title-row">
        <strong>{insight.title}</strong>
        <Badge tone={insightTone(insight.severity)}>{insight.severity}</Badge>
      </div>
      <p>{insight.message}</p>
    </article>
  );
}

export default function MerchantProWeeklyReportPage() {
  const guard = useRoleGuard("MERCHANT");
  const router = useRouter();
  const [report, setReport] = useState<MerchantProWeeklyReport | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [autoSnapshotLoading, setAutoSnapshotLoading] = useState(false);
  const [autoSnapshotPreview, setAutoSnapshotPreview] = useState<ProWeeklyReportAutoSnapshotPreview | null>(null);
  const [batchLoading, setBatchLoading] = useState(false);
  const [batchHistory, setBatchHistory] = useState<MerchantProWeeklyReportBatchRunHistory | null>(null);

  const trendMax = useMemo(() => maxTrendValue(report?.daily_trends || []), [report?.daily_trends]);

  const loadReport = useCallback(async () => {
    setLoading(true);
    setMessage("");
    setIsError(false);
    try {
      const query = reportQuery();
      const data = await apiFetch<MerchantProWeeklyReport>(`/api/v1/merchant/pro/weekly-report${query}`, {}, true);
      setReport(data);
      setMessage("주간 운영 리포트를 불러왔습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }, []);

  const loadBatchRuns = useCallback(async () => {
    try {
      const data = await apiFetch<MerchantProWeeklyReportBatchRunHistory>(
        "/api/v1/merchant/pro/weekly-report/batch-runs",
        {},
        true,
      );
      setBatchHistory(data);
    } catch {
      setBatchHistory(null);
    }
  }, []);

  useEffect(() => {
    if (!guard.allowed) return;
    void Promise.resolve().then(async () => {
      await loadReport();
      await loadBatchRuns();
    });
  }, [guard.allowed, loadBatchRuns, loadReport]);

  function reportQuery() {
    const params = new URLSearchParams();
    const currentParams = typeof window === "undefined" ? new URLSearchParams() : new URLSearchParams(window.location.search);
    const startDate = currentParams.get("start_date");
    const endDate = currentParams.get("end_date");
    if (startDate) params.set("start_date", startDate);
    if (endDate) params.set("end_date", endDate);
    const query = params.toString();
    return query ? `?${query}` : "";
  }

  async function fetchExport(format: "csv" | "text") {
    const token = getToken();
    if (!token) {
      throw new Error("로그인이 필요합니다.");
    }
    const params = new URLSearchParams(reportQuery().replace(/^\?/, ""));
    params.set("format", format);
    const response = await fetch(buildApiUrl(`/api/v1/merchant/pro/weekly-report/export?${params.toString()}`), {
      headers: {
        Accept: format === "csv" ? "text/csv" : "text/plain",
        Authorization: `Bearer ${token}`,
      },
    });
    if (!response.ok) {
      throw new Error(await response.text());
    }
    return response;
  }

  async function downloadCsv() {
    setExporting(true);
    setMessage("");
    setIsError(false);
    try {
      const response = await fetchExport("csv");
      const csv = await response.text();
      const blob = new Blob(["\uFEFF", csv], { type: "text/csv;charset=utf-8" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "breadgo-weekly-report.csv";
      link.click();
      window.URL.revokeObjectURL(url);
      setMessage("주간 리포트 CSV를 다운로드했습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setExporting(false);
    }
  }

  async function copySummary() {
    setExporting(true);
    setMessage("");
    setIsError(false);
    try {
      const response = await fetchExport("text");
      const text = await response.text();
      await navigator.clipboard.writeText(text);
      setMessage("공유용 주간 리포트 요약을 클립보드에 복사했습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setExporting(false);
    }
  }

  async function saveWeeklyReport() {
    setSaving(true);
    setMessage("");
    setIsError(false);
    try {
      const snapshot = await apiFetch<ProWeeklyReportSnapshot>(
        `/api/v1/merchant/pro/weekly-report/snapshot${reportQuery()}`,
        { method: "POST" },
        true,
      );
      setMessage("이번 주 리포트를 저장했습니다. 동일 기간 리포트는 최신 값으로 업데이트됩니다.");
      router.push(`/merchant/pro/weekly-report/history?snapshot=${snapshot.id}`);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setSaving(false);
    }
  }

  async function previewAutoSnapshot() {
    setAutoSnapshotLoading(true);
    setMessage("");
    setIsError(false);
    try {
      const preview = await apiFetch<ProWeeklyReportAutoSnapshotPreview>(
        `/api/v1/merchant/pro/weekly-report/auto-snapshot-preview${reportQuery()}`,
        { method: "POST" },
        true,
      );
      setAutoSnapshotPreview(preview);
      setMessage(
        preview.would_create_new
          ? "자동 저장 시 새 주간 리포트 snapshot이 생성됩니다."
          : "자동 저장 시 기존 주간 리포트 snapshot이 최신 값으로 업데이트됩니다.",
      );
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setAutoSnapshotLoading(false);
    }
  }

  async function runAutoSnapshot() {
    setAutoSnapshotLoading(true);
    setMessage("");
    setIsError(false);
    try {
      const result = await apiFetch<ProWeeklyReportAutoSnapshotRun>(
        `/api/v1/merchant/pro/weekly-report/auto-snapshot${reportQuery()}`,
        { method: "POST" },
        true,
      );
      setMessage(result.message);
      router.push(`/merchant/pro/weekly-report/history?snapshot=${result.snapshot_id}`);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setAutoSnapshotLoading(false);
    }
  }

  async function runBatchTest() {
    setBatchLoading(true);
    setMessage("");
    setIsError(false);
    try {
      const result = await apiFetch<MerchantProWeeklyReportBatchRunHistory["batch_runs"][number]>(
        `/api/v1/merchant/pro/weekly-report/batch-test-run${reportQuery()}`,
        { method: "POST" },
        true,
      );
      const item = result.items[0];
      setMessage(
        item?.snapshot_id
          ? `자동 생성 테스트가 완료되었습니다. snapshot: ${item.snapshot_id}`
          : result.message || "자동 생성 테스트가 완료되었습니다.",
      );
      await loadBatchRuns();
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setBatchLoading(false);
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
        title="주간 운영 리포트"
        description="최근 7일 기준 매출, 예약, 픽업, 폐기 절감, 미해결 알림과 추천 액션 흐름을 확인합니다."
        actions={
          <>
            <button type="button" onClick={loadReport} disabled={loading}>
              {loading ? "불러오는 중" : "리포트 새로고침"}
            </button>
            <button type="button" onClick={downloadCsv} disabled={exporting}>
              {exporting ? "처리 중" : "CSV 다운로드"}
            </button>
            <button type="button" onClick={copySummary} disabled={exporting}>
              요약 복사
            </button>
            <button type="button" onClick={saveWeeklyReport} disabled={saving}>
              {saving ? "저장 중" : "이번 주 리포트 저장"}
            </button>
            <Link className="button-link secondary" href="/merchant/pro/daily-brief/history">
              Daily Brief 이력
            </Link>
            <Link className="button-link secondary" href="/merchant/pro/weekly-report/history">
              저장 이력 보기
            </Link>
          </>
        }
      />

      {message && <div className={isError ? "notice error" : "notice success"}>{message}</div>}

      <div className="pro-hero panel">
        <div>
          <p className="eyebrow">Weekly Pro Report</p>
          <h2>
            {report ? `${formatDate(report.start_date)} - ${formatDate(report.end_date)}` : "최근 7일"} 운영 요약
          </h2>
          <p>
            전일 브리프가 쌓일수록 더 정확해집니다. 저장된 snapshot이 없는 날짜는 0으로 표시하고,
            오늘 snapshot이 없으면 실시간 Daily Brief를 임시로 반영합니다.
          </p>
        </div>
        <div className="pro-score">
          <span>저장된 브리프</span>
          <strong>{report?.snapshot_days_count ?? 0}</strong>
          <small>최근 기간 내 반영 일수</small>
        </div>
      </div>

      <section className="panel">
        <div className="card-title-row">
          <div>
            <p className="eyebrow">Auto Snapshot MVP</p>
            <h2>주간 리포트 자동 저장 준비</h2>
            <p>
              실제 cron은 아직 연결하지 않았습니다. 향후 매주 자동 저장될 리포트의 기간과 핵심 지표를
              미리 확인하고, 같은 로직으로 snapshot을 생성합니다.
            </p>
          </div>
          <Badge tone="muted">수동/자동 공통 저장 이력</Badge>
        </div>
        <div className="actions">
          <button type="button" onClick={previewAutoSnapshot} disabled={autoSnapshotLoading}>
            {autoSnapshotLoading ? "확인 중" : "자동 저장 미리보기"}
          </button>
          <button type="button" onClick={runAutoSnapshot} disabled={autoSnapshotLoading}>
            {autoSnapshotLoading ? "저장 중" : "이번 주 리포트 자동 저장"}
          </button>
          <Link className="button-link secondary" href="/merchant/pro/weekly-report/history">
            저장 이력 보기
          </Link>
        </div>
        {autoSnapshotPreview && (
          <div className="summary-grid compact-grid">
            <StatCard
              label="저장될 기간"
              value={`${formatDate(autoSnapshotPreview.start_date)} - ${formatDate(autoSnapshotPreview.end_date)}`}
              helper={autoSnapshotPreview.would_create_new ? "새 snapshot 생성 예정" : "기존 snapshot 업데이트 예정"}
            />
            <StatCard label="총 매출" value={formatMoney(autoSnapshotPreview.report_summary.total_sales_amount)} />
            <StatCard label="예약" value={autoSnapshotPreview.report_summary.total_reservation_count} />
            <StatCard label="픽업" value={autoSnapshotPreview.report_summary.total_picked_up_count} />
            <StatCard label="폐기 절감" value={`${autoSnapshotPreview.report_summary.total_saved_quantity}개`} />
            <StatCard label="인사이트" value={`${autoSnapshotPreview.insights.length}개`} />
          </div>
        )}
      </section>

      <section className="panel">
        <div className="card-title-row">
          <div>
            <p className="eyebrow">Batch Run Log</p>
            <h2>자동 생성 테스트 실행 이력</h2>
            <p>
              실제 cron은 아직 없지만, 운영자가 나중에 실행할 자동 생성 작업의 성공/실패와 대상 기간을
              기록하는 MVP 로그입니다.
            </p>
          </div>
          <Badge tone="muted">MANUAL_TEST</Badge>
        </div>
        <div className="actions">
          <button type="button" onClick={runBatchTest} disabled={batchLoading}>
            {batchLoading ? "실행 중" : "자동 생성 테스트 실행"}
          </button>
          <button type="button" onClick={loadBatchRuns} disabled={batchLoading}>
            이력 새로고침
          </button>
        </div>
        {batchHistory && batchHistory.batch_runs.length > 0 ? (
          <div className="stacked-list">
            {batchHistory.batch_runs.slice(0, 5).map((run) => {
              const item = run.items[0];
              return (
                <article className="item compact-card" key={run.id}>
                  <div className="card-title-row">
                    <div>
                      <strong>
                        {formatDate(run.start_date)} - {formatDate(run.end_date)}
                      </strong>
                      <p>{run.message || "Weekly Report batch run"}</p>
                    </div>
                    <Badge tone={run.status === "COMPLETED" ? "success" : run.status === "FAILED" ? "danger" : "warning"}>
                      {run.status}
                    </Badge>
                  </div>
                  <p>
                    성공 {run.success_count} · 실패 {run.failed_count} · 건너뜀 {run.skipped_count}
                  </p>
                  {item?.snapshot_id && (
                    <Link className="button-link secondary" href={`/merchant/pro/weekly-report/history?snapshot=${item.snapshot_id}`}>
                      저장 이력에서 확인
                    </Link>
                  )}
                </article>
              );
            })}
          </div>
        ) : (
          <EmptyState title="아직 자동 생성 테스트 이력이 없습니다." />
        )}
      </section>

      <div className="summary-grid">
        <StatCard label="총 매출" value={report ? formatMoney(report.total_sales_amount) : "0원"} helper="Mock 결제 기준" />
        <StatCard label="예약" value={report?.total_reservation_count ?? 0} />
        <StatCard label="픽업" value={report?.total_picked_up_count ?? 0} />
        <StatCard label="취소" value={report?.total_cancelled_count ?? 0} />
        <StatCard label="폐기 절감" value={`${report?.total_saved_quantity ?? 0}개`} />
        <StatCard label="평균 미해결 알림" value={report?.average_unresolved_alert_count.toFixed(1) ?? "0.0"} />
        <StatCard label="HIGH 알림" value={report?.high_severity_alert_count ?? 0} />
        <StatCard label="추천 액션" value={report?.total_recommendation_action_count ?? 0} />
        <StatCard label="재고 변경" value={report?.total_inventory_event_count ?? 0} />
        <StatCard label="POS 이슈" value={report?.pos_sync_issue_count ?? 0} />
        <StatCard label="CSV 오류" value={report?.csv_import_error_count ?? 0} />
      </div>

      <section className="panel">
        <div className="card-title-row">
          <div>
            <p className="eyebrow">운영 인사이트</p>
            <h2>이번 주 운영 신호</h2>
            <p>실제 AI 요약이 아닌 rule-based 운영 인사이트입니다.</p>
          </div>
          <Badge tone="muted">최근 7일 기준</Badge>
        </div>
        {report && report.insights.length > 0 ? (
          <div className="stacked-list">
            {report.insights.map((insight) => (
              <InsightCard key={`${insight.title}-${insight.message}`} insight={insight} />
            ))}
          </div>
        ) : (
          <EmptyState title="아직 표시할 인사이트가 없습니다." />
        )}
      </section>

      <section className="panel">
        <div className="card-title-row">
          <div>
            <p className="eyebrow">일자별 추이</p>
            <h2>매출 · 예약 · 알림 흐름</h2>
            <p>막대는 날짜별 매출, 예약, 픽업, 폐기 절감, 미해결 알림을 비교하기 위한 MVP 시각화입니다.</p>
          </div>
        </div>
        <div className="weekly-trend-grid">
          {(report?.daily_trends || []).map((trend) => {
            const salesUnits = Number(trend.sales_amount) / 10000;
            const barHeight = Math.max(8, (Math.max(salesUnits, trend.reservation_count, trend.picked_up_count, trend.saved_quantity, trend.unresolved_alert_count) / trendMax) * 120);
            return (
              <article className="weekly-trend-card" key={trend.date}>
                <div className="weekly-trend-bar" style={{ height: `${barHeight}px` }} />
                <strong>{formatDate(trend.date)}</strong>
                <span>매출 {formatMoney(trend.sales_amount)}</span>
                <span>예약 {trend.reservation_count} · 픽업 {trend.picked_up_count}</span>
                <span>절감 {trend.saved_quantity} · 알림 {trend.unresolved_alert_count}</span>
              </article>
            );
          })}
        </div>
      </section>

      <section className="panel">
        <p className="eyebrow">관련 화면 바로가기</p>
        <h2>운영 원인 확인</h2>
        <div className="actions">
          <Link className="button-link secondary" href="/merchant/pro/daily-brief/history">
            Daily Brief 이력
          </Link>
          <Link className="button-link secondary" href="/merchant/pro/inventory-alerts">
            재고 알림
          </Link>
          <Link className="button-link secondary" href="/merchant/pro/recommendation-performance">
            추천 성과
          </Link>
          <Link className="button-link secondary" href="/merchant/pro/pos">
            POS 연동
          </Link>
          <Link className="button-link secondary" href="/merchant/products/import">
            CSV import
          </Link>
        </div>
      </section>
    </section>
  );
}
