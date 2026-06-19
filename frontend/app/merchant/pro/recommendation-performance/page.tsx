"use client";

import { useEffect, useState } from "react";
import { Badge, EmptyState, PageHeader, StatCard } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { MerchantProRecommendationPerformance, RecommendationUsage } from "@/lib/types";

function formatMoney(value: string) {
  return `${Number(value).toLocaleString()}원`;
}

function formatPercent(value: number) {
  return `${value.toFixed(1)}%`;
}

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}

function recommendationTypeLabel(value: string) {
  const labels: Record<string, string> = {
    KEEP: "유지",
    INCREASE_STOCK: "재고 증가",
    DECREASE_STOCK: "재고 감소",
    LOWER_PRICE: "할인 강화",
    RAISE_PRICE: "가격 조정",
  };
  return labels[value] || value;
}

function confidenceTone(value: string): "success" | "warning" | "muted" {
  if (value === "HIGH") return "success";
  if (value === "MEDIUM") return "warning";
  return "muted";
}

export default function MerchantRecommendationPerformancePage() {
  const guard = useRoleGuard("MERCHANT");
  const [performance, setPerformance] = useState<MerchantProRecommendationPerformance | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!guard.allowed) return;
    void loadPerformance();
  }, [guard.allowed]);

  async function loadPerformance() {
    setLoading(true);
    setMessage("");
    setIsError(false);

    try {
      const data = await apiFetch<MerchantProRecommendationPerformance>(
        "/api/v1/merchant/pro/recommendation-performance",
        {},
        true,
      );
      setPerformance(data);
      setMessage("추천 사용 성과를 불러왔습니다.");
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
        title="추천 사용 성과"
        description="추천으로 만든 상품이 얼마나 판매되고 픽업되었는지 추적합니다."
        actions={
          <button type="button" onClick={loadPerformance} disabled={loading}>
            {loading ? "불러오는 중" : "성과 새로고침"}
          </button>
        }
      />
      <div className="message">
        <strong>추천 후 판매율 추적</strong>
        <br />
        추천 초안 생성 같은 명확한 행동만 기록합니다. 데이터가 쌓일수록 추천 품질을 개선할 수 있습니다.
      </div>
      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      {!performance ? (
        <EmptyState title="추천 성과를 불러오세요." />
      ) : (
        <>
          <div className="summary-grid">
            <StatCard label="추천 초안 생성" value={`${performance.total_recommendation_drafts}건`} />
            <StatCard label="추천 사용 기록" value={`${performance.used_recommendation_count}건`} />
            <StatCard label="추천으로 만든 상품" value={`${performance.recommendation_created_products_count}개`} />
            <StatCard label="추천 상품 픽업 수량" value={`${performance.picked_up_quantity_from_recommendations}개`} />
            <StatCard label="추천 상품 매출" value={formatMoney(performance.paid_amount_from_recommendations)} />
            <StatCard
              label="추천 후 평균 판매율"
              value={formatPercent(performance.average_sell_through_rate_from_recommendations)}
            />
          </div>

          {performance.usage_by_recommendation_type.length > 0 && (
            <section className="panel">
              <div className="card-title-row">
                <div>
                  <p className="eyebrow">추천 타입별 사용 현황</p>
                  <h2>어떤 추천이 사용됐는지 확인하세요</h2>
                </div>
              </div>
              <div className="pro-product-grid">
                {performance.usage_by_recommendation_type.map((item) => (
                  <article className="item" key={item.recommendation_type}>
                    <div className="card-title-row">
                      <h3>{recommendationTypeLabel(item.recommendation_type)}</h3>
                      <Badge tone="muted">{item.count}건</Badge>
                    </div>
                    <div className="detail-grid">
                      <Metric label="픽업 수량" value={`${item.picked_up_quantity}개`} />
                      <Metric label="결제 금액" value={formatMoney(item.paid_amount)} />
                    </div>
                  </article>
                ))}
              </div>
            </section>
          )}

          <section className="panel">
            <div className="card-title-row">
              <div>
                <p className="eyebrow">최근 추천 사용 이력</p>
                <h2>추천으로 만든 상품</h2>
              </div>
            </div>
            {performance.recent_usages.length === 0 ? (
              <EmptyState
                title="추천 사용 이력이 없습니다."
                description="Pro 추천 화면에서 추천 재고로 초안을 생성하면 성과 추적이 시작됩니다."
              />
            ) : (
              <div className="list">
                {performance.recent_usages.map((usage) => (
                  <UsageCard key={usage.id} usage={usage} />
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </section>
  );
}

function UsageCard({ usage }: { usage: RecommendationUsage }) {
  return (
    <article className="item">
      <div className="card-title-row">
        <div>
          <p className="eyebrow">{recommendationTypeLabel(usage.recommendation_type)}</p>
          <h3>{usage.created_product_name || "추천 상품 초안"}</h3>
          <p>원본: {usage.source_product_name || "상품 정보 없음"}</p>
        </div>
        <div className="actions">
          <Badge tone={confidenceTone(usage.confidence_label)}>{usage.confidence_label}</Badge>
          <Badge tone="muted">{usage.action_type}</Badge>
        </div>
      </div>
      <div className="detail-grid">
        <Metric label="추천 재고" value={`${usage.recommended_stock_quantity}개`} />
        <Metric label="추천 할인가" value={formatMoney(usage.recommended_discount_price)} />
        <Metric label="예약 수량" value={`${usage.created_product_reserved_quantity}개`} />
        <Metric label="픽업 수량" value={`${usage.created_product_picked_up_quantity}개`} />
        <Metric label="결제 금액" value={formatMoney(usage.created_product_paid_amount)} />
        <Metric label="추천 후 판매율" value={formatPercent(usage.created_product_sell_through_rate)} />
        <Metric label="기록 시각" value={formatDate(usage.created_at)} />
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

