"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { EmptyState, PageHeader, StatCard, StatusBadge } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { Settlement, SettlementAccount, SettlementSummary } from "@/lib/types";

function formatMoney(value: string) {
  return `${Number(value).toLocaleString()}원`;
}

function formatDate(value: string | null) {
  return value ? new Date(value).toLocaleString() : "-";
}

function hasAccount(account: SettlementAccount | null) {
  return Boolean(account?.bank_name && account.bank_account_number && account.bank_account_holder);
}

export default function MerchantSettlementsPage() {
  const guard = useRoleGuard("MERCHANT");
  const [settlements, setSettlements] = useState<Settlement[]>([]);
  const [account, setAccount] = useState<SettlementAccount | null>(null);
  const [summary, setSummary] = useState<SettlementSummary | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    if (!guard.allowed) {
      return;
    }

    let cancelled = false;

    async function loadSettlements() {
      setMessage("");
      setIsError(false);

      try {
        const [settlementData, summaryData, accountData] = await Promise.all([
          apiFetch<Settlement[]>("/api/v1/merchant/settlements", {}, true),
          apiFetch<SettlementSummary>("/api/v1/merchant/settlements/summary", {}, true),
          apiFetch<SettlementAccount>("/api/v1/merchant/settlement-account", {}, true),
        ]);
        if (cancelled) return;
        setSettlements(settlementData);
        setSummary(summaryData);
        setAccount(accountData);
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
  }, [guard.allowed]);

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
        title="정산 내역"
        description="판매 결제 건의 수수료와 점주 정산금을 확인합니다."
      />
      <p className="message">
        고객 결제금액에서 BreadGo 수수료와 PG 수수료를 차감한 금액이 점주 정산금입니다.
        현재는 실제 송금이 아닌 MVP용 정산 상태 관리입니다.
      </p>

      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      <div className="panel">
        <div className="card-title-row">
          <div>
            <p className="eyebrow">정산 계좌</p>
            <h3>{account?.business_name || "가맹점 계좌 정보"}</h3>
          </div>
          <Link className="secondary button-link" href="/merchant/settlement-account">
            {hasAccount(account) ? "정산 계좌 관리" : "정산 계좌 등록"}
          </Link>
        </div>
        {hasAccount(account) ? (
          <div className="detail-grid">
            <div>
              <span>은행명</span>
              <strong>{account?.bank_name}</strong>
            </div>
            <div>
              <span>계좌번호</span>
              <strong>{account?.bank_account_number}</strong>
            </div>
            <div>
              <span>예금주</span>
              <strong>{account?.bank_account_holder}</strong>
            </div>
            <div>
              <span>정산 주기</span>
              <strong>{account?.settlement_cycle || "-"}</strong>
            </div>
          </div>
        ) : (
          <EmptyState
            title="정산 계좌가 등록되지 않았습니다."
            description="정산 계좌를 등록하면 관리자 정산 화면에서도 계좌 요약을 확인할 수 있습니다."
          />
        )}
        {account?.settlement_memo && <p className="meta">정산 메모: {account.settlement_memo}</p>}
      </div>

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
                <span>수령 방법 {settlement.fulfillment_method || "-"}</span>
                <span>배송비 {settlement.delivery_fee ? formatMoney(settlement.delivery_fee) : "0원"}</span>
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
