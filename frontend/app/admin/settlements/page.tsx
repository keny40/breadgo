"use client";

import { ChangeEvent, useEffect, useMemo, useState } from "react";
import { EmptyState, PageHeader, StatCard, StatusBadge } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import type { AuthUser, Settlement, SettlementSummary } from "@/lib/types";

const settlementStatuses = ["ALL", "PENDING", "READY", "PAID", "HOLD", "CANCELLED"];

function formatMoney(value: string) {
  return `${Number(value).toLocaleString()}원`;
}

function statusLabel(status: string) {
  const labels: Record<string, string> = {
    PENDING: "정산 예정",
    READY: "정산 가능",
    PAID: "정산 완료",
    HOLD: "정산 보류",
    CANCELLED: "정산 취소",
  };
  return labels[status] || status;
}

export default function AdminSettlementsPage() {
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [settlements, setSettlements] = useState<Settlement[]>([]);
  const [summary, setSummary] = useState<SettlementSummary | null>(null);
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [holdReasons, setHoldReasons] = useState<Record<string, string>>({});
  const [adminMemos, setAdminMemos] = useState<Record<string, string>>({});
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadInitialData() {
      setMessage("");
      setIsError(false);

      try {
        const me = await apiFetch<AuthUser>("/api/v1/auth/me", {}, true);
        if (cancelled) return;
        setCurrentUser(me);

        if (me.role.toLowerCase() !== "admin") {
          setIsError(true);
          setMessage("관리자 권한이 필요합니다.");
          return;
        }

        const [settlementData, summaryData] = await Promise.all([
          apiFetch<Settlement[]>("/api/v1/admin/settlements", {}, true),
          apiFetch<SettlementSummary>("/api/v1/admin/settlements/summary", {}, true),
        ]);
        if (cancelled) return;
        setSettlements(settlementData);
        setSummary(summaryData);
        setMessage("정산 데이터를 불러왔습니다.");
      } catch (error) {
        if (cancelled) return;
        setIsError(true);
        setMessage(friendlyErrorMessage(error));
      }
    }

    void loadInitialData();
    return () => {
      cancelled = true;
    };
  }, []);

  const filteredSettlements = useMemo(() => {
    if (statusFilter === "ALL") {
      return settlements;
    }
    return settlements.filter((settlement) => settlement.status === statusFilter);
  }, [settlements, statusFilter]);

  async function refreshSettlements() {
    const [settlementData, summaryData] = await Promise.all([
      apiFetch<Settlement[]>("/api/v1/admin/settlements", {}, true),
      apiFetch<SettlementSummary>("/api/v1/admin/settlements/summary", {}, true),
    ]);
    setSettlements(settlementData);
    setSummary(summaryData);
  }

  async function updateSettlementStatus(settlementId: string, status: "PAID" | "HOLD") {
    setMessage("");
    setIsError(false);

    const holdReason = holdReasons[settlementId]?.trim();
    const adminMemo = adminMemos[settlementId]?.trim();

    try {
      await apiFetch<Settlement>(
        `/api/v1/admin/settlements/${settlementId}/status`,
        {
          method: "PATCH",
          body: JSON.stringify({
            status,
            hold_reason: status === "HOLD" ? holdReason || null : undefined,
            admin_memo: adminMemo || undefined,
          }),
        },
        true,
      );
      await refreshSettlements();
      setHoldReasons((current) => ({ ...current, [settlementId]: "" }));
      setAdminMemos((current) => ({ ...current, [settlementId]: "" }));
      setMessage(`정산 상태가 ${statusLabel(status)}(으)로 변경되었습니다.`);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  const blocked = !currentUser || currentUser.role.toLowerCase() !== "admin";

  return (
    <section className="section">
      <PageHeader
        title="정산 관리"
        description="고객 결제금액에서 BreadGo 수수료와 PG 수수료를 차감한 점주 정산금을 확인합니다."
      />
      <p className="message">
        고객 결제금액에서 BreadGo 수수료와 PG 수수료를 차감한 금액이 점주 정산금입니다.
        현재는 실제 송금이 아닌 MVP용 정산 상태 관리입니다.
      </p>

      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      {blocked ? (
        <EmptyState title={message || "로그인이 필요합니다."} description="관리자 계정으로 로그인해 주세요." />
      ) : (
        <>
          {summary && (
            <div className="summary-grid">
              <StatCard label="총 결제금액" value={formatMoney(summary.total_gross_amount)} />
              <StatCard label="플랫폼 수수료" value={formatMoney(summary.total_platform_fee_amount)} />
              <StatCard label="PG 수수료" value={formatMoney(summary.total_pg_fee_amount)} />
              <StatCard label="점주 정산금" value={formatMoney(summary.total_merchant_settlement_amount)} />
              <StatCard label="정산 예정" value={formatMoney(summary.pending_amount)} helper={`${summary.count_by_status.PENDING || 0}건`} />
              <StatCard label="정산 가능" value={formatMoney(summary.ready_amount)} helper={`${summary.count_by_status.READY || 0}건`} />
              <StatCard label="정산 완료" value={formatMoney(summary.paid_amount)} helper={`${summary.count_by_status.PAID || 0}건`} />
              <StatCard label="정산 보류" value={formatMoney(summary.hold_amount)} helper={`${summary.count_by_status.HOLD || 0}건`} />
            </div>
          )}

          <div className="panel form-grid">
            <label>
              상태 필터
              <select value={statusFilter} onChange={(event: ChangeEvent<HTMLSelectElement>) => setStatusFilter(event.target.value)}>
                {settlementStatuses.map((status) => (
                  <option key={status} value={status}>
                    {status === "ALL" ? "전체" : statusLabel(status)}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {filteredSettlements.length === 0 ? (
            <EmptyState
              title="정산 내역이 없습니다."
              description="픽업 완료된 결제 건부터 정산 대상이 됩니다."
            />
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>상품</th>
                    <th>가맹점</th>
                    <th>매장</th>
                    <th>총 결제금액</th>
                    <th>수수료</th>
                    <th>점주 정산금</th>
                    <th>상태</th>
                    <th>관리</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredSettlements.map((settlement) => (
                    <tr key={settlement.id}>
                      <td>
                        <strong>{settlement.product_name || "-"}</strong>
                        <br />
                        픽업 {settlement.pickup_code || "-"}
                      </td>
                      <td>{settlement.merchant_name || settlement.merchant_email || "-"}</td>
                      <td>
                        {settlement.store_name || "-"}
                        <br />
                        <small>
                          계좌{" "}
                          {settlement.bank_name && settlement.bank_account_number && settlement.bank_account_holder
                            ? `${settlement.bank_name} ${settlement.bank_account_number} (${settlement.bank_account_holder})`
                            : "정산 계좌 미등록"}
                        </small>
                        {settlement.settlement_cycle && (
                          <>
                            <br />
                            <small>정산 주기 {settlement.settlement_cycle}</small>
                          </>
                        )}
                      </td>
                      <td>{formatMoney(settlement.gross_amount)}</td>
                      <td>
                        플랫폼 {formatMoney(settlement.platform_fee_amount)}
                        <br />
                        PG {formatMoney(settlement.pg_fee_amount)}
                      </td>
                      <td>{formatMoney(settlement.merchant_settlement_amount)}</td>
                      <td>
                        <StatusBadge status={settlement.status} />
                        <br />
                        예약 {settlement.reservation_status || "-"}
                        <br />
                        결제 {settlement.payment_status || "-"}
                        {settlement.hold_reason && (
                          <>
                            <br />
                            보류 사유 {settlement.hold_reason}
                          </>
                        )}
                        {settlement.admin_memo && (
                          <>
                            <br />
                            관리 메모 {settlement.admin_memo}
                          </>
                        )}
                      </td>
                      <td>
                        <div className="actions">
                          <input
                            value={holdReasons[settlement.id] || ""}
                            onChange={(event) =>
                              setHoldReasons((current) => ({
                                ...current,
                                [settlement.id]: event.target.value,
                              }))
                            }
                            placeholder="보류 사유"
                            aria-label="보류 사유"
                          />
                          <input
                            value={adminMemos[settlement.id] || ""}
                            onChange={(event) =>
                              setAdminMemos((current) => ({
                                ...current,
                                [settlement.id]: event.target.value,
                              }))
                            }
                            placeholder="관리 메모"
                            aria-label="관리 메모"
                          />
                          <button
                            type="button"
                            onClick={() => updateSettlementStatus(settlement.id, "PAID")}
                            disabled={settlement.status === "PAID" || settlement.status === "CANCELLED"}
                          >
                            정산 완료
                          </button>
                          <button
                            type="button"
                            className="secondary"
                            onClick={() => updateSettlementStatus(settlement.id, "HOLD")}
                            disabled={settlement.status === "CANCELLED"}
                          >
                            보류
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </section>
  );
}
