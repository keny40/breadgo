"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Badge, EmptyState, PageHeader, StatCard } from "@/components/UI";
import { apiFetch, buildApiUrl, friendlyErrorMessage, getToken } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { MerchantProWeeklyReport, ProWeeklyReportDailyTrend, ProWeeklyReportInsight } from "@/lib/types";

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
  const [report, setReport] = useState<MerchantProWeeklyReport | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    if (!guard.allowed) return;
    void loadReport();
  }, [guard.allowed]);

  const trendMax = useMemo(() => maxTrendValue(report?.daily_trends || []), [report?.daily_trends]);

  async function loadReport() {
    setLoading(true);
    setMessage("");
    setIsError(false);
    try {
      const data = await apiFetch<MerchantProWeeklyReport>("/api/v1/merchant/pro/weekly-report", {}, true);
      setReport(data);
      setMessage("주간 운영 리포트를 불러왔습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  async function fetchExport(format: "csv" | "text") {
    const token = getToken();
    if (!token) {
      throw new Error("로그인이 필요합니다.");
    }
    const response = await fetch(buildApiUrl(`/api/v1/merchant/pro/weekly-report/export?format=${format}`), {
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
            <Link className="button-link secondary" href="/merchant/pro/daily-brief/history">
              Daily Brief 이력
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
