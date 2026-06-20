"use client";

import { useEffect, useState } from "react";
import { Badge, EmptyState, PageHeader, StatCard } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { MerchantProPlan } from "@/lib/types";

const planCards = [
  {
    key: "FREE",
    name: "Free",
    badge: "기본",
    description: "기본 상품 등록과 예약 확인을 시작하는 무료 운영 플랜입니다.",
    features: ["상품 등록", "예약 확인", "기본 주문 관리", "Pro 기능 미리보기"],
    cta: "현재 데모에서는 준비 중",
  },
  {
    key: "PRO",
    name: "BreadGo Pro",
    badge: "Pro",
    description: "점주용 수율 관리 플랜입니다. 반복 등록, ESG, 추천, 전환 분석을 제공합니다.",
    features: ["수율 대시보드", "반복 상품 등록", "요일별 템플릿", "CSV 일괄 등록", "ESG 리포트", "추천 재고/할인가", "고객 전환 분석"],
    cta: "현재 MVP 기본 플랜",
  },
  {
    key: "ENTERPRISE",
    name: "Enterprise",
    badge: "Enterprise",
    description: "다중 매장/프랜차이즈 운영을 위한 확장 플랜입니다.",
    features: ["매장 통합 대시보드", "프랜차이즈/본사 리포트", "CSV 일괄 등록 고도화", "POS/API 연동 준비", "전담 운영 리포트"],
    cta: "도입 문의 준비 중",
  },
];

const featureLabels: Record<keyof MerchantProPlan["features"], string> = {
  yield_dashboard: "수율 대시보드",
  relist_products: "반복 상품 등록",
  product_templates: "요일별 상품 템플릿",
  csv_product_import: "CSV 일괄 등록 / POS 연동 준비",
  esg_report: "ESG 리포트",
  recommendations: "추천 재고/할인",
  recommendation_performance: "추천 성과 분석",
  product_funnel: "고객 전환 퍼널",
  multi_store_dashboard: "다중 매장 통합",
  pos_api_integration: "POS/API 연동 준비",
};

function planTone(plan: string): "success" | "warning" | "muted" {
  if (plan === "PRO") return "success";
  if (plan === "ENTERPRISE") return "warning";
  return "muted";
}

export default function MerchantProPlanPage() {
  const guard = useRoleGuard("MERCHANT");
  const [plan, setPlan] = useState<MerchantProPlan | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!guard.allowed) return;
    void loadPlan();
  }, [guard.allowed]);

  async function loadPlan() {
    setLoading(true);
    setMessage("");
    setIsError(false);

    try {
      const result = await apiFetch<MerchantProPlan>("/api/v1/merchant/pro/plan", {}, true);
      setPlan(result);
      setMessage("BreadGo Pro 플랜 정보를 불러왔습니다.");
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

  const enabledFeatureCount = plan
    ? Object.values(plan.features).filter(Boolean).length
    : 0;

  return (
    <section className="section">
      <PageHeader
        title="BreadGo Pro 플랜"
        description="Free / Pro / Enterprise 구조로 BreadGo Pro 기능을 SaaS 플랜으로 확장할 준비를 합니다."
        actions={
          <button type="button" onClick={loadPlan} disabled={loading}>
            {loading ? "불러오는 중" : "플랜 새로고침"}
          </button>
        }
      />

      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      {!plan ? (
        <EmptyState title="플랜 정보를 불러오세요." />
      ) : (
        <>
          <div className="pro-hero panel">
            <div>
              <p className="eyebrow">점주용 수율 관리 플랜</p>
              <h2>{plan.business_name}</h2>
              <p>{plan.upgrade_message}</p>
            </div>
            <div className="pro-score">
              <span>현재 플랜</span>
              <strong>{plan.plan_label}</strong>
              <small>{plan.is_pro_active ? "Pro 기능 활성" : "기본 기능만 활성"}</small>
            </div>
          </div>

          <div className="summary-grid">
            <StatCard label="현재 플랜" value={plan.plan_label} />
            <StatCard label="활성 기능" value={`${enabledFeatureCount}개`} />
            <StatCard label="Pro 활성 상태" value={plan.is_pro_active ? "활성" : "비활성"} />
            <StatCard label="과금 연동" value="준비 중" helper="실제 결제/구독 과금 없음" />
          </div>

          <section className="panel">
            <div className="card-title-row">
              <div>
                <p className="eyebrow">현재 사용 가능 기능</p>
                <h2>플랜별 기능 플래그</h2>
              </div>
              <Badge tone={planTone(plan.current_plan)}>{plan.current_plan}</Badge>
            </div>
            <div className="pro-product-grid">
              {(Object.keys(featureLabels) as Array<keyof MerchantProPlan["features"]>).map((featureKey) => (
                <article className="item" key={featureKey}>
                  <div className="card-title-row">
                    <h3>{featureLabels[featureKey]}</h3>
                    <Badge tone={plan.features[featureKey] ? "success" : "muted"}>
                      {plan.features[featureKey] ? "사용 가능" : "플랜 업그레이드"}
                    </Badge>
                  </div>
                </article>
              ))}
            </div>
          </section>

          <section className="panel">
            <div className="card-title-row">
              <div>
                <p className="eyebrow">플랜 비교</p>
                <h2>Free / Pro / Enterprise</h2>
              </div>
              <Badge tone="muted">실제 과금 연동 준비 중</Badge>
            </div>
            <div className="pro-product-grid">
              {planCards.map((card) => (
                <article className="item pro-product-card" key={card.key}>
                  <div className="card-title-row">
                    <div>
                      <p className="eyebrow">{card.badge}</p>
                      <h3>{card.name}</h3>
                    </div>
                    {plan.current_plan === card.key && <Badge tone="success">현재 플랜</Badge>}
                  </div>
                  <p>{card.description}</p>
                  <ul className="compact-list">
                    {card.features.map((feature) => (
                      <li key={feature}>{feature}</li>
                    ))}
                  </ul>
                  <button type="button" className="secondary" disabled>
                    {card.cta}
                  </button>
                </article>
              ))}
            </div>
          </section>
        </>
      )}
    </section>
  );
}
