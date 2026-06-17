"use client";

import { useEffect, useState } from "react";
import { EmptyState, PageHeader, StatCard, StatusBadge } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import type { Settlement, SettlementSummary } from "@/lib/types";

function formatMoney(value: string) {
  return `${Number(value).toLocaleString()}원`;
}

function formatDate(value: string | null) {
  return value ? new Date(value).toLocaleString() : "-";
}

export default function MerchantSettlementsPage() {
  const [settlements, setSettlements] = useState<Settlement[]>([]);
  const [summary, setSummary] = useState<SettlementSummary | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadSettlements() {
      setMessage("");
      setIsError(false);

      try {
        const [settlementData, summaryData] = await Promise.all([
          apiFetch<Settlement[]>("/api/v1/merchant/settlements", {}, true),
          apiFetch<SettlementSummary>("/api/v1/merchant/settlements/summary", {}, true),
        ]);
        if (cancelled) return;
        setSettlements(settlementData);
        setSummary(summaryData);
        setMessage("정산 내역을 불러왔습니다.");
      } catch (error) {
        if (cancelled) return;
        setIsError(true);
        setMessage(friendlyErrorMessage(error));
      }
    }

    void loadSettlements();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section className="section">
      <PageHeader
        title="정산 내역"
        description="판매 결제 건의 수수료와 점주 정산금을 확인합니다."
      />
      <p className="message">
        고객 결제금액에서 BreadGo 수수료와 PG 수수료를 차감한 금액이 점주 정산금입니다.
        현재는 실제 송금이 아닌 MVP용 정산 상태 관리입니다.
      </p>

      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      {summary && (
        <div className="summary-grid">
          <StatCard label="정산 예정" value={formatMoney(summary.pending_amount)} helper={`${summary.count_by_status.PENDING || 0}건`} />
          <StatCard label="정산 가능" value={formatMoney(summary.ready_amount)} helper={`${summary.count_by_status.READY || 0}건`} />
          <StatCard label="정산 완료" value={formatMoney(summary.paid_amount)} helper={`${summary.count_by_status.PAID || 0}건`} />
          <StatCard label="정산 보류" value={formatMoney(summary.hold_amount)} helper={`${summary.count_by_status.HOLD || 0}건`} />
          <StatCard label="총 결제금액" value={formatMoney(summary.total_gross_amount)} />
          <StatCard label="점주 정산금" value={formatMoney(summary.total_merchant_settlement_amount)} />
        </div>
      )}

      {settlements.length === 0 && !isError ? (
        <EmptyState
          title="정산 내역이 없습니다."
          description="픽업 완료된 결제 건부터 정산 대상이 됩니다."
        />
      ) : (
        <div className="list">
          {settlements.map((settlement) => (
            <article className="item" key={settlement.id}>
              <div className="card-title-row">
                <div>
                  <p className="eyebrow">정산 상품</p>
                  <h3>{settlement.product_name || "마감 할인 상품"}</h3>
                  <p>{settlement.store_name || "매장 정보 없음"}</p>
                </div>
                <StatusBadge status={settlement.status} />
              </div>
              <div className="detail-grid">
                <div>
                  <span>총 결제금액</span>
                  <strong>{formatMoney(settlement.gross_amount)}</strong>
                </div>
                <div>
                  <span>플랫폼 수수료</span>
                  <strong>{formatMoney(settlement.platform_fee_amount)}</strong>
                </div>
                <div>
                  <span>PG 수수료</span>
                  <strong>{formatMoney(settlement.pg_fee_amount)}</strong>
                </div>
                <div>
                  <span>점주 정산금</span>
                  <strong>{formatMoney(settlement.merchant_settlement_amount)}</strong>
                </div>
              </div>
              <div className="meta">
                <span>픽업코드 {settlement.pickup_code || "-"}</span>
                <span>예약 상태 {settlement.reservation_status || "-"}</span>
                <span>결제 상태 {settlement.payment_status || "-"}</span>
                <span>생성일 {formatDate(settlement.created_at)}</span>
                <span>정산일 {formatDate(settlement.settled_at)}</span>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
