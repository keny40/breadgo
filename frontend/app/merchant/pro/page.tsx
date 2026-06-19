"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Badge, EmptyState, PageHeader, StatCard, StatusBadge } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { MerchantProDashboard, ProDailySummary, ProProductSummary } from "@/lib/types";

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

function maxRecentValue(days: ProDailySummary[]) {
  return Math.max(1, ...days.map((day) => day.registered_quantity));
}

export default function MerchantProDashboardPage() {
  const guard = useRoleGuard("MERCHANT");
  const [dashboard, setDashboard] = useState<MerchantProDashboard | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!guard.allowed) return;
    void loadDashboard();
  }, [guard.allowed]);

  const recentMax = useMemo(
    () => maxRecentValue(dashboard?.recent_7_days || []),
    [dashboard?.recent_7_days],
  );

  async function loadDashboard() {
    setLoading(true);
    setMessage("");
    setIsError(false);

    try {
      const data = await apiFetch<MerchantProDashboard>("/api/v1/merchant/pro/dashboard", {}, true);
      setDashboard(data);
      setMessage("BreadGo Pro 수율 데이터를 불러왔습니다.");
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
        title="BreadGo Pro 대시보드"
        description="오늘의 수율, 남은 재고, 픽업 완료, 취소, 예상 정산금과 폐기 절감을 한 화면에서 확인합니다."
        actions={
          <button type="button" onClick={loadDashboard} disabled={loading}>
            {loading ? "불러오는 중" : "수율 데이터 새로고침"}
          </button>
        }
      />

      <div className="pro-hero panel">
        <div>
          <p className="eyebrow">오늘의 수율 관리</p>
          <h2>{dashboard?.business_name || "BreadGo Pro"}</h2>
          <p>
            BreadGo Pro는 마감 할인 판매를 단순 주문 처리에서 끝내지 않고, 점주가 매일 재고 회수율과
            정산 가능 금액을 확인하는 운영 도구로 확장합니다.
          </p>
        </div>
        <div className="pro-score">
          <span>판매율</span>
          <strong>{dashboard ? formatPercent(dashboard.sell_through_rate) : "0.0%"}</strong>
          <small>예약 수량 / 오늘 등록 추정 수량</small>
        </div>
      </div>

      <div className="panel pro-relist-card">
        <div>
          <p className="eyebrow">점주 운영 자동화</p>
          <h2>어제 남은 빵 그대로 올리기</h2>
          <p>
            기존 상품 정보는 유지하고 오늘 재고만 입력하세요. 마감 시간만 바꿔 빠르게 재등록할 수 있습니다.
          </p>
        </div>
        <div className="actions">
          <Link className="button-link" href="/merchant/products">
            상품관리에서 다시 올리기
          </Link>
          <Link className="button-link secondary" href="/merchant/product-templates">
            오늘 템플릿으로 한 번에 등록
          </Link>
        </div>
      </div>

      <div className="panel pro-relist-card">
        <div>
          <p className="eyebrow">AI 추천 준비 단계</p>
          <h2>오늘 추천 확인하기</h2>
          <p>최근 7일 판매 데이터를 기준으로 추천 재고와 추천 할인가를 참고하세요.</p>
        </div>
        <Link className="button-link" href="/merchant/pro/recommendations">
          Pro 추천 보기
        </Link>
      </div>

      <div className="panel pro-relist-card">
        <div>
          <p className="eyebrow">폐기 감소 리포트</p>
          <h2>이번 달 폐기 방지 성과 보기</h2>
          <p>BreadGo로 판매 전환된 마감 상품과 폐기 방지 금액을 확인하세요.</p>
        </div>
        <Link className="button-link" href="/merchant/pro/esg">
          ESG 리포트 보기
        </Link>
      </div>

      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      {!dashboard ? (
        <EmptyState title="수율 데이터를 불러오세요." description="가맹점 상품과 예약 데이터가 있으면 오늘의 운영 지표를 확인할 수 있습니다." />
      ) : (
        <>
          <div className="summary-grid">
            <StatCard label="오늘 등록 추정 수량" value={`${dashboard.today_registered_quantity}개`} helper="현재 재고 + 유효 예약" />
            <StatCard label="오늘 예약 수량" value={`${dashboard.today_reserved_quantity}개`} />
            <StatCard label="남은 재고" value={`${dashboard.today_remaining_quantity}개`} />
            <StatCard label="픽업 완료율" value={formatPercent(dashboard.pickup_completion_rate)} helper={`${dashboard.today_picked_up_count}건 완료`} />
            <StatCard label="취소율" value={formatPercent(dashboard.cancellation_rate)} helper={`${dashboard.today_cancelled_count}건 취소`} />
            <StatCard label="오늘 매출" value={formatMoney(dashboard.today_gross_sales)} helper={`${dashboard.today_paid_count}건 결제`} />
            <StatCard label="예상 정산금" value={formatMoney(dashboard.today_estimated_settlement)} />
            <StatCard label="폐기 절감" value={`${dashboard.today_estimated_saved_items}개`} helper={formatMoney(dashboard.today_estimated_waste_prevented_amount)} />
          </div>

          <section className="panel">
            <div className="card-title-row">
              <div>
                <p className="eyebrow">최근 7일</p>
                <h2>수율 흐름</h2>
              </div>
              <Badge tone="muted">MVP 추정 지표</Badge>
            </div>
            <div className="pro-chart" aria-label="최근 7일 판매율">
              {dashboard.recent_7_days.map((day) => (
                <DayBar key={day.date} day={day} maxValue={recentMax} />
              ))}
            </div>
          </section>

          <section className="panel">
            <div className="card-title-row">
              <div>
                <p className="eyebrow">상품별 판매율</p>
                <h2>오늘 상품 수율</h2>
              </div>
              <span className="field-help">판매율이 높은 상품부터 표시됩니다.</span>
            </div>

            {dashboard.product_summaries.length === 0 ? (
              <EmptyState
                title="오늘 집계할 상품이 없습니다."
                description="오늘 픽업 상품을 등록하거나 예약이 발생하면 BreadGo Pro 지표가 표시됩니다."
              />
            ) : (
              <div className="pro-product-grid">
                {dashboard.product_summaries.map((product) => (
                  <ProductYieldCard key={product.product_id} product={product} />
                ))}
              </div>
            )}
          </section>

          <p className="message">
            폐기 절감은 픽업 완료 수량과 픽업 완료 상품 금액을 기준으로 한 MVP 추정치입니다. 실제 중량,
            탄소 배출 절감량, POS 폐기 데이터 연동은 다음 단계에서 고도화합니다.
          </p>
        </>
      )}
    </section>
  );
}

function DayBar({ day, maxValue }: { day: ProDailySummary; maxValue: number }) {
  const registeredHeight = Math.max(8, (day.registered_quantity / maxValue) * 100);
  const reservedHeight = day.registered_quantity > 0
    ? Math.max(4, (day.reserved_quantity / maxValue) * 100)
    : 0;

  return (
    <div className="pro-day-bar">
      <div className="pro-bar-track">
        <span className="pro-bar registered" style={{ height: `${registeredHeight}%` }} />
        <span className="pro-bar reserved" style={{ height: `${reservedHeight}%` }} />
      </div>
      <strong>{formatPercent(day.sell_through_rate)}</strong>
      <span>{formatDate(day.date)}</span>
      <small>{day.reserved_quantity}/{day.registered_quantity}개</small>
    </div>
  );
}

function ProductYieldCard({ product }: { product: ProProductSummary }) {
  return (
    <article className="item pro-product-card">
      <div className="card-title-row">
        <div>
          <p className="eyebrow">{product.store_name}</p>
          <h3>{product.product_name}</h3>
        </div>
        <StatusBadge status={product.status} />
      </div>

      <div className="pro-meter" aria-label={`${product.product_name} 판매율`}>
        <span style={{ width: `${Math.min(100, product.sell_through_rate)}%` }} />
      </div>

      <div className="detail-grid">
        <Metric label="판매율" value={formatPercent(product.sell_through_rate)} />
        <Metric label="등록 추정" value={`${product.registered_quantity}개`} />
        <Metric label="예약" value={`${product.reserved_quantity}개`} />
        <Metric label="픽업 완료" value={`${product.picked_up_quantity}개`} />
        <Metric label="남은 재고" value={`${product.remaining_quantity}개`} />
        <Metric label="예상 정산금" value={formatMoney(product.estimated_settlement)} />
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
