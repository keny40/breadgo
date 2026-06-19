"use client";

import { useEffect, useState } from "react";
import { Badge, EmptyState, PageHeader, StatCard } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { MerchantProProductFunnel, ProProductFunnelSummary } from "@/lib/types";

function formatMoney(value: string) {
  return `${Number(value).toLocaleString()}원`;
}

function formatPercent(value: number) {
  return `${value.toFixed(1)}%`;
}

function attentionTone(value: string): "success" | "warning" | "muted" {
  if (value.includes("우수")) return "success";
  if (value.includes("낮은")) return "warning";
  return "muted";
}

export default function MerchantProProductFunnelPage() {
  const guard = useRoleGuard("MERCHANT");
  const [data, setData] = useState<MerchantProProductFunnel | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!guard.allowed) return;
    void loadFunnel();
  }, [guard.allowed]);

  async function loadFunnel() {
    setLoading(true);
    setMessage("");
    setIsError(false);

    try {
      const result = await apiFetch<MerchantProProductFunnel>("/api/v1/merchant/pro/product-funnel", {}, true);
      setData(result);
      setMessage("상품 전환 퍼널을 불러왔습니다.");
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

  const lowConversionProducts =
    data?.product_funnel_summaries.filter((item) => item.attention_label.includes("낮은")).length || 0;

  return (
    <section className="section">
      <PageHeader
        title="고객 전환 퍼널"
        description="상품 조회에서 예약, 결제, 픽업까지 이어지는 고객 반응 데이터를 확인합니다."
        actions={
          <button type="button" onClick={loadFunnel} disabled={loading}>
            {loading ? "불러오는 중" : "전환 데이터 새로고침"}
          </button>
        }
      />

      <div className="message">
        <Badge tone="success">BreadGo Pro 기능</Badge>
        <br />
        <strong>최근 7일 기준</strong>
        <br />
        상품 상세 조회와 예약 데이터를 연결해 예약 전환율을 계산합니다. 데이터가 쌓이면 추천 품질 개선에
        활용됩니다.
      </div>
      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      {!data ? (
        <EmptyState title="고객 전환 데이터를 불러오세요." />
      ) : (
        <>
          <div className="summary-grid">
            <StatCard label="상품 조회" value={`${data.total_detail_views}회`} />
            <StatCard label="예약 시작" value={`${data.total_reservation_starts}회`} />
            <StatCard label="예약 생성" value={`${data.total_reservations}건`} />
            <StatCard label="결제 완료" value={`${data.total_paid_count}건`} />
            <StatCard label="픽업 완료" value={`${data.total_picked_up_count}건`} />
            <StatCard label="예약 전환율" value={formatPercent(data.detail_to_reservation_rate)} />
            <StatCard label="조회 대비 예약 낮음" value={`${lowConversionProducts}개`} />
          </div>

          {data.product_funnel_summaries.length === 0 ? (
            <EmptyState
              title="상품 전환 데이터가 없습니다."
              description="고객이 상품을 조회하고 예약하면 전환 퍼널이 표시됩니다."
            />
          ) : (
            <div className="pro-product-grid">
              {data.product_funnel_summaries.map((item) => (
                <FunnelCard item={item} key={item.product_id} />
              ))}
            </div>
          )}
        </>
      )}
    </section>
  );
}

function FunnelCard({ item }: { item: ProProductFunnelSummary }) {
  return (
    <article className="item pro-product-card">
      <div className="card-title-row">
        <div>
          <p className="eyebrow">{item.store_name}</p>
          <h3>{item.product_name}</h3>
        </div>
        <div className="actions">
          {item.from_recommendation && <Badge tone="success">추천 상품</Badge>}
          <Badge tone={attentionTone(item.attention_label)}>{item.attention_label}</Badge>
        </div>
      </div>

      <div className="detail-grid">
        <Metric label="상품 조회" value={`${item.detail_views}회`} />
        <Metric label="예약 시작" value={`${item.reservation_started_count}회`} />
        <Metric label="예약 생성" value={`${item.reservations}건`} />
        <Metric label="결제 완료" value={`${item.paid_count}건`} />
        <Metric label="픽업 완료" value={`${item.picked_up_count}건`} />
        <Metric label="예약 전환율" value={formatPercent(item.conversion_rate)} />
        <Metric label="결제 전환율" value={formatPercent(item.paid_conversion_rate)} />
        <Metric label="픽업 전환율" value={formatPercent(item.pickup_conversion_rate)} />
        <Metric label="결제 금액" value={formatMoney(item.paid_amount)} />
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
