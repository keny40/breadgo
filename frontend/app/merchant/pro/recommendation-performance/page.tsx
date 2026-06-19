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

function adoptionTypeLabel(value: string | null) {
  if (value === "EXACT_ACCEPTED") return "그대로 채택";
  if (value === "MODIFIED_ACCEPTED") return "수정 후 채택";
  return "채택 방식 미기록";
}

function funnelStatusLabel(usage: RecommendationUsage) {
  if (usage.first_picked_up_at) return "픽업 완료";
  if (usage.first_paid_at) return "결제 발생";
  if (usage.first_reserved_at) return "예약 발생";
  if (usage.draft_product_status === "PUBLISHED") return "판매 노출됨";
  if (usage.draft_product_status === "ARCHIVED") return "초안 보관됨";
  return "초안 상태";
}

function funnelStatusTone(usage: RecommendationUsage): "success" | "warning" | "muted" {
  if (usage.first_picked_up_at || usage.first_paid_at || usage.first_reserved_at) return "success";
  if (usage.draft_product_status === "PUBLISHED") return "warning";
  return "muted";
}

function formatSignedNumber(value: number | null) {
  if (value === null) return "-";
  if (value > 0) return `+${value}`;
  return `${value}`;
}

function formatSignedMoney(value: string | null) {
  if (value === null) return "-";
  const numberValue = Number(value);
  if (numberValue > 0) return `+${numberValue.toLocaleString()}원`;
  return `${numberValue.toLocaleString()}원`;
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
        추천 초안 생성, 실제 노출 전환, 노출 이후 예약/결제/픽업 흐름을 추적합니다.
        데이터가 쌓일수록 추천 품질을 개선할 수 있습니다.
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
            <StatCard label="초안 생성 수" value={`${performance.draft_created_count}건`} />
            <StatCard
              label="실제 노출 전환 수"
              value={`${performance.published_from_recommendation_count}건`}
              helper={formatPercent(performance.publish_conversion_rate)}
            />
            <StatCard label="노출 후 예약" value={`${performance.reserved_after_publish_count}건`} />
            <StatCard label="노출 후 결제" value={`${performance.paid_after_publish_count}건`} />
            <StatCard label="노출 후 픽업" value={`${performance.picked_up_after_publish_count}건`} />
            <StatCard
              label="평균 노출 소요 시간"
              value={`${performance.average_time_to_publish_minutes.toFixed(1)}분`}
            />
            <StatCard
              label="추천 그대로 채택"
              value={`${performance.exact_accept_count}건`}
              helper={formatPercent(performance.exact_accept_rate)}
            />
            <StatCard
              label="수정 후 채택"
              value={`${performance.modified_accept_count}건`}
              helper={formatPercent(performance.modified_accept_rate)}
            />
            <StatCard
              label="평균 재고 수정폭"
              value={`${formatSignedNumber(performance.average_stock_delta)}개`}
            />
            <StatCard
              label="평균 가격 수정폭"
              value={formatSignedMoney(performance.average_discount_price_delta)}
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
          <Badge tone={usage.adoption_type === "MODIFIED_ACCEPTED" ? "warning" : "success"}>
            {adoptionTypeLabel(usage.adoption_type)}
          </Badge>
          <Badge tone={funnelStatusTone(usage)}>{funnelStatusLabel(usage)}</Badge>
          <Badge tone="muted">{usage.action_type}</Badge>
        </div>
      </div>
      <div className="detail-grid">
        <Metric label="추천 재고" value={`${usage.recommended_stock_quantity}개`} />
        <Metric label="추천 할인가" value={formatMoney(usage.recommended_discount_price)} />
        <Metric
          label="실제 채택 재고"
          value={usage.accepted_stock_quantity === null ? "-" : `${usage.accepted_stock_quantity}개`}
        />
        <Metric
          label="실제 채택 할인가"
          value={usage.accepted_discount_price ? formatMoney(usage.accepted_discount_price) : "-"}
        />
        <Metric label="추천 대비 재고 수정폭" value={`${formatSignedNumber(usage.stock_delta)}개`} />
        <Metric label="추천 대비 가격 수정폭" value={formatSignedMoney(usage.discount_price_delta)} />
        <Metric label="초안 전환 상태" value={usage.draft_product_status || "HIDDEN_DRAFT"} />
        <Metric label="노출 시각" value={usage.published_at ? formatDate(usage.published_at) : "-"} />
        <Metric label="첫 예약" value={usage.first_reserved_at ? formatDate(usage.first_reserved_at) : "-"} />
        <Metric label="첫 결제" value={usage.first_paid_at ? formatDate(usage.first_paid_at) : "-"} />
        <Metric label="첫 픽업" value={usage.first_picked_up_at ? formatDate(usage.first_picked_up_at) : "-"} />
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
