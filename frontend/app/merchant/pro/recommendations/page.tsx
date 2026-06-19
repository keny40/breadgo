"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Badge, EmptyState, PageHeader, StatCard } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { MerchantProRecommendations, ProRecommendation, ProRecommendationDraftCreateResponse } from "@/lib/types";

function formatMoney(value: string) {
  return `${Number(value).toLocaleString()}원`;
}

function formatPercent(value: number) {
  return `${value.toFixed(1)}%`;
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

export default function MerchantProRecommendationsPage() {
  const guard = useRoleGuard("MERCHANT");
  const [data, setData] = useState<MerchantProRecommendations | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);
  const [duplicatingId, setDuplicatingId] = useState<string | null>(null);

  useEffect(() => {
    if (!guard.allowed) return;
    void loadRecommendations();
  }, [guard.allowed]);

  async function loadRecommendations() {
    setLoading(true);
    setMessage("");
    setIsError(false);

    try {
      const result = await apiFetch<MerchantProRecommendations>("/api/v1/merchant/pro/recommendations", {}, true);
      setData(result);
      setMessage("BreadGo Pro 추천을 불러왔습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  async function createDraftFromRecommendation(recommendation: ProRecommendation) {
    setMessage("");
    setIsError(false);
    setDuplicatingId(recommendation.product_id);

    try {
      const result = await apiFetch<ProRecommendationDraftCreateResponse>(
        `/api/v1/merchant/pro/recommendations/${recommendation.product_id}/create-draft`,
        {
          method: "POST",
          body: JSON.stringify({
            is_visible: false,
            name_suffix: "추천",
          }),
        },
        true,
      );
      setMessage(
        `${result.created_product.name} 초안을 생성하고 추천 사용 이력을 기록했습니다. 추천 할인가는 ${formatMoney(recommendation.recommended_discount_price)}이며, 상품관리에서 가격을 확인한 뒤 노출하세요.`,
      );
      await loadRecommendations();
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setDuplicatingId(null);
    }
  }

  if (!guard.allowed) {
    return (
      <section className="section">
        <EmptyState title={guard.message || "권한을 확인하고 있습니다."} />
      </section>
    );
  }

  const recommendations = data?.recommendations || [];
  const highCount = recommendations.filter((item) => item.confidence_label === "HIGH").length;
  const mediumCount = recommendations.filter((item) => item.confidence_label === "MEDIUM").length;
  const lowCount = recommendations.filter((item) => item.confidence_label === "LOW").length;

  return (
    <section className="section">
      <PageHeader
        title="BreadGo Pro 추천"
        description="최근 7일 판매 데이터를 기준으로 추천 재고와 추천 할인가를 참고합니다."
        actions={
          <div className="actions">
            <button type="button" onClick={loadRecommendations} disabled={loading}>
              {loading ? "계산 중" : "추천 다시 계산"}
            </button>
            <Link className="button-link secondary" href="/merchant/pro/recommendation-performance">
              추천 성과 확인
            </Link>
          </div>
        }
      />

      <div className="message">
        <strong>AI 추천 준비 단계</strong>
        <br />
        현재는 실제 AI 모델이 아닌 rule-based 추천입니다. 데이터가 적은 상품은 신뢰도가 낮게 표시됩니다.
      </div>
      {data?.note && <div className="message">{data.note}</div>}
      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      <div className="summary-grid">
        <StatCard label="추천 대상 상품" value={`${recommendations.length}개`} />
        <StatCard label="HIGH 신뢰도" value={`${highCount}개`} />
        <StatCard label="MEDIUM 신뢰도" value={`${mediumCount}개`} />
        <StatCard label="LOW 신뢰도" value={`${lowCount}개`} />
      </div>

      {recommendations.length === 0 ? (
        <EmptyState
          title="추천할 상품이 없습니다."
          description="상품과 최근 7일 예약 데이터가 쌓이면 BreadGo Pro 추천이 표시됩니다."
        />
      ) : (
        <div className="pro-product-grid">
          {recommendations.map((recommendation) => (
            <article className="item pro-product-card" key={recommendation.product_id}>
              <div className="card-title-row">
                <div>
                  <p className="eyebrow">{recommendation.store_name}</p>
                  <h3>{recommendation.product_name}</h3>
                </div>
                <div className="actions">
                  <Badge tone={confidenceTone(recommendation.confidence_label)}>
                    {recommendation.confidence_label}
                  </Badge>
                  <Badge tone="muted">{recommendationTypeLabel(recommendation.recommendation_type)}</Badge>
                </div>
              </div>

              <div className="detail-grid">
                <Metric label="최근 예약 수량" value={`${recommendation.recent_reserved_quantity}개`} />
                <Metric label="최근 픽업 수량" value={`${recommendation.recent_picked_up_quantity}개`} />
                <Metric label="최근 취소 수량" value={`${recommendation.recent_cancelled_quantity}개`} />
                <Metric label="현재 재고" value={`${recommendation.current_stock_quantity}개`} />
                <Metric label="판매율" value={formatPercent(recommendation.sell_through_rate)} />
                <Metric label="픽업 완료율" value={formatPercent(recommendation.pickup_completion_rate)} />
                <Metric label="추천 재고" value={`${recommendation.recommended_stock_quantity}개`} />
                <Metric label="현재 할인가" value={formatMoney(recommendation.current_discount_price)} />
                <Metric label="추천 할인가" value={formatMoney(recommendation.recommended_discount_price)} />
              </div>

              <p className="guidance-text">{recommendation.recommendation_message}</p>
              <div className="actions">
                <button
                  type="button"
                  onClick={() => createDraftFromRecommendation(recommendation)}
                  disabled={duplicatingId === recommendation.product_id}
                >
                  {duplicatingId === recommendation.product_id ? "초안 생성 중" : "추천 재고로 초안 생성"}
                </button>
                <Link className="button-link secondary" href="/merchant/products">
                  상품관리에서 가격 반영
                </Link>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
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
