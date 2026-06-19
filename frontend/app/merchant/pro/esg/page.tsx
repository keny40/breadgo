"use client";

import { useEffect, useMemo, useState } from "react";
import { Badge, EmptyState, PageHeader, StatCard } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { MerchantProEsgReport, ProEsgDailyTrend, ProEsgProductSummary } from "@/lib/types";

function formatMoney(value: string) {
  return `${Number(value).toLocaleString()}원`;
}

function formatPercent(value: number) {
  return `${value.toFixed(1)}%`;
}

function formatDate(value: string) {
  return new Date(`${value}T00:00:00`).toLocaleDateString("ko-KR", {
    month: "numeric",
    day: "numeric",
  });
}

function maxSavedItems(days: ProEsgDailyTrend[]) {
  return Math.max(1, ...days.map((day) => day.saved_items));
}

export default function MerchantProEsgPage() {
  const guard = useRoleGuard("MERCHANT");
  const [report, setReport] = useState<MerchantProEsgReport | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!guard.allowed) return;
    void loadReport();
  }, [guard.allowed]);

  const trendMax = useMemo(() => maxSavedItems(report?.daily_esg_trend || []), [report?.daily_esg_trend]);

  async function loadReport() {
    setLoading(true);
    setMessage("");
    setIsError(false);

    try {
      const data = await apiFetch<MerchantProEsgReport>("/api/v1/merchant/pro/esg-report", {}, true);
      setReport(data);
      setMessage("폐기 감소 리포트를 불러왔습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setLoading(false);
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
        title="폐기 감소 리포트"
        description="BreadGo로 판매 전환된 마감 상품, 폐기 방지 금액, 상품별 절감 기여도를 확인합니다."
        actions={
          <button type="button" onClick={loadReport} disabled={loading}>
            {loading ? "불러오는 중" : "ESG 리포트 새로고침"}
          </button>
        }
      />

      <div className="pro-hero panel">
        <div>
          <p className="eyebrow">BreadGo Pro ESG</p>
          <h2>{report?.business_name || "폐기 감소 성과"}</h2>
          <p>
            절감 수량은 픽업 완료된 예약 상품 수량 기준입니다. 취소된 예약은 제외하고, 폐기 방지 금액은
            픽업 완료 예약의 상품 금액 기준으로 계산합니다.
          </p>
        </div>
        <div className="pro-score">
          <span>이번 달 절감 수량</span>
          <strong>{report ? `${report.month_saved_items}개` : "0개"}</strong>
          <small>판매로 전환된 마감 상품</small>
        </div>
      </div>

      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      {!report ? (
        <EmptyState title="ESG 리포트를 불러오세요." description="픽업 완료된 예약이 있으면 폐기 감소 성과가 표시됩니다." />
      ) : (
        <>
          <div className="summary-grid">
            <StatCard label="오늘 절감 수량" value={`${report.today_saved_items}개`} helper={formatMoney(report.today_saved_amount)} />
            <StatCard label="최근 7일 절감 수량" value={`${report.week_saved_items}개`} helper={formatMoney(report.week_saved_amount)} />
            <StatCard label="이번 달 절감 수량" value={`${report.month_saved_items}개`} helper={formatMoney(report.month_saved_amount)} />
            <StatCard label="폐기 방지 금액" value={formatMoney(report.estimated_waste_prevention_amount)} helper="이번 달 누적" />
            <StatCard label="픽업 완료 건수" value={`${report.pickup_completed_count}건`} />
            <StatCard label="취소 건수" value={`${report.cancelled_count}건`} />
            <StatCard label="판매율" value={formatPercent(report.sell_through_rate)} helper="예약 수량 / 등록 추정 수량" />
          </div>

          <section className="panel">
            <div className="card-title-row">
              <div>
                <p className="eyebrow">최근 7일</p>
                <h2>폐기 감소 추이</h2>
              </div>
              <Badge tone="muted">MVP 계산 기준</Badge>
            </div>
            <div className="pro-chart" aria-label="최근 7일 폐기 감소 추이">
              {report.daily_esg_trend.map((day) => (
                <EsgDayBar key={day.date} day={day} maxValue={trendMax} />
              ))}
            </div>
          </section>

          <section className="panel">
            <div className="card-title-row">
              <div>
                <p className="eyebrow">상품별 절감 기여도</p>
                <h2>판매로 전환된 마감 상품</h2>
              </div>
              <span className="field-help">이번 달 절감 수량이 높은 상품부터 표시됩니다.</span>
            </div>

            {report.product_esg_summaries.length === 0 ? (
              <EmptyState
                title="아직 폐기 감소 데이터가 없습니다."
                description="픽업 완료된 예약이 생기면 상품별 절감 기여도가 표시됩니다."
              />
            ) : (
              <div className="pro-product-grid">
                {report.product_esg_summaries.map((product) => (
                  <ProductEsgCard key={product.product_id} product={product} />
                ))}
              </div>
            )}
          </section>

          <p className="message">
            {report.carbon_reduction_note} 실제 POS 폐기 데이터, 상품 중량, 품목별 탄소 배출계수 연동 전까지는
            CO2 절감량을 확정값으로 표시하지 않습니다.
          </p>
        </>
      )}
    </section>
  );
}

function EsgDayBar({ day, maxValue }: { day: ProEsgDailyTrend; maxValue: number }) {
  const height = day.saved_items > 0 ? Math.max(8, (day.saved_items / maxValue) * 100) : 4;

  return (
    <div className="pro-day-bar">
      <div className="pro-bar-track">
        <span className="pro-bar reserved" style={{ height: `${height}%` }} />
      </div>
      <strong>{day.saved_items}개</strong>
      <span>{formatDate(day.date)}</span>
      <small>{formatMoney(day.saved_amount)}</small>
    </div>
  );
}

function ProductEsgCard({ product }: { product: ProEsgProductSummary }) {
  return (
    <article className="item pro-product-card">
      <div className="card-title-row">
        <div>
          <p className="eyebrow">{product.store_name}</p>
          <h3>{product.product_name}</h3>
        </div>
        <Badge tone="success">{formatPercent(product.contribution_rate)}</Badge>
      </div>
      <div className="pro-meter" aria-label={`${product.product_name} 절감 기여도`}>
        <span style={{ width: `${Math.min(100, product.contribution_rate)}%` }} />
      </div>
      <div className="detail-grid">
        <Metric label="절감 수량" value={`${product.saved_items}개`} />
        <Metric label="폐기 방지 금액" value={formatMoney(product.saved_amount)} />
        <Metric label="픽업 완료" value={`${product.pickup_completed_count}건`} />
        <Metric label="취소" value={`${product.cancelled_count}건`} />
      </div>
    </article>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

