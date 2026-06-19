"use client";

import { useEffect, useMemo, useState } from "react";
import { Badge, EmptyState, PageHeader, StatCard } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { MerchantProStoresDashboard, ProStoreDashboardSummary } from "@/lib/types";

function formatMoney(value: string) {
  return `${Number(value).toLocaleString()}원`;
}

function formatPercent(value: number) {
  return `${value.toFixed(1)}%`;
}

function statusLabel(value: string) {
  const labels: Record<string, string> = {
    GOOD: "좋음",
    WATCH: "관찰 필요",
    NEED_ACTION: "조치 필요",
    INSUFFICIENT_DATA: "데이터 부족",
  };
  return labels[value] || value;
}

function statusTone(value: string): "success" | "warning" | "danger" | "muted" {
  if (value === "GOOD") return "success";
  if (value === "NEED_ACTION") return "danger";
  if (value === "WATCH") return "warning";
  return "muted";
}

function locationText(store: ProStoreDashboardSummary) {
  return [store.sido, store.sigungu, store.dong].filter(Boolean).join(" ") || "지역 정보 없음";
}

export default function MerchantProStoresDashboardPage() {
  const guard = useRoleGuard("MERCHANT");
  const [data, setData] = useState<MerchantProStoresDashboard | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!guard.allowed) return;
    void loadStoresDashboard();
  }, [guard.allowed]);

  const needActionCount = useMemo(
    () => data?.stores.filter((store) => store.status_label === "NEED_ACTION").length || 0,
    [data?.stores],
  );
  const watchCount = useMemo(
    () => data?.stores.filter((store) => store.status_label === "WATCH").length || 0,
    [data?.stores],
  );

  async function loadStoresDashboard() {
    setLoading(true);
    setMessage("");
    setIsError(false);

    try {
      const result = await apiFetch<MerchantProStoresDashboard>("/api/v1/merchant/pro/stores-dashboard", {}, true);
      setData(result);
      setMessage("매장 통합 데이터를 불러왔습니다.");
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
        title="매장 통합 대시보드"
        description="최근 7일 기준으로 매장별 수율, 예약 전환, 매출, 폐기 절감 성과를 비교합니다."
        actions={
          <button type="button" onClick={loadStoresDashboard} disabled={loading}>
            {loading ? "불러오는 중" : "매장 통합 데이터 새로고침"}
          </button>
        }
      />

      <div className="message">
        <Badge tone="warning">Enterprise 확장 기능</Badge>
        <br />
        <strong>다중 매장 운영을 위한 BreadGo Pro 기능입니다.</strong>
        <br />
        현재 등록된 매장이 하나뿐이어도 같은 기준으로 집계되며, 매장이 늘어나면 성과 비교 화면으로 확장됩니다.
      </div>
      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      {!data ? (
        <EmptyState title="매장 통합 데이터를 불러오세요." />
      ) : (
        <>
          <div className="summary-grid">
            <StatCard label="등록 매장" value={`${data.total_stores}개`} />
            <StatCard label="전체 예약" value={`${data.total_reservations}건`} />
            <StatCard label="총 결제금액" value={formatMoney(data.total_sales_amount)} />
            <StatCard label="픽업 완료" value={`${data.total_picked_up_count}건`} />
            <StatCard label="폐기 절감 수량" value={`${data.total_saved_quantity}개`} />
            <StatCard label="평균 판매율" value={formatPercent(data.average_sell_through_rate)} />
            <StatCard label="조치 필요 매장" value={`${needActionCount}개`} />
            <StatCard label="관찰 필요 매장" value={`${watchCount}개`} />
          </div>

          {data.stores.length === 0 ? (
            <EmptyState
              title="등록된 매장이 없습니다."
              description="매장을 등록하면 BreadGo Pro 매장 통합 지표를 확인할 수 있습니다."
            />
          ) : (
            <section className="panel">
              <div className="card-title-row">
                <div>
                  <p className="eyebrow">최근 {data.period_days}일 기준</p>
                  <h2>매장별 수율과 예약 전환</h2>
                </div>
                <Badge tone="muted">현재 등록된 매장 기준</Badge>
              </div>

              <div className="pro-product-grid">
                {data.stores.map((store) => (
                  <StorePerformanceCard store={store} key={store.store_id} />
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </section>
  );
}

function StorePerformanceCard({ store }: { store: ProStoreDashboardSummary }) {
  return (
    <article className="item pro-product-card">
      <div className="card-title-row">
        <div>
          <p className="eyebrow">{locationText(store)}</p>
          <h3>{store.store_name}</h3>
        </div>
        <Badge tone={statusTone(store.status_label)}>{statusLabel(store.status_label)}</Badge>
      </div>

      <div className="pro-meter" aria-label={`${store.store_name} 판매율`}>
        <span style={{ width: `${Math.min(100, store.sell_through_rate)}%` }} />
      </div>

      <p className="guidance-text">
        <strong>{store.store_insight_message}</strong>
      </p>

      <div className="detail-grid">
        <Metric label="판매율" value={formatPercent(store.sell_through_rate)} />
        <Metric label="예약 전환율" value={formatPercent(store.reservation_conversion_rate)} />
        <Metric label="상품 조회" value={`${store.detail_views}회`} />
        <Metric label="판매중 상품" value={`${store.active_product_count}개`} />
        <Metric label="예약" value={`${store.reservation_count}건`} />
        <Metric label="결제 완료" value={`${store.paid_count}건`} />
        <Metric label="픽업 완료" value={`${store.picked_up_count}건`} />
        <Metric label="취소" value={`${store.cancelled_count}건`} />
        <Metric label="총 결제금액" value={formatMoney(store.gross_sales_amount)} />
        <Metric label="예상 정산금" value={formatMoney(store.estimated_settlement_amount)} />
        <Metric label="폐기 절감" value={`${store.saved_quantity}개`} />
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
