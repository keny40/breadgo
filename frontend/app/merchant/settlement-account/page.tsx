"use client";

import { FormEvent, useEffect, useState } from "react";
import { EmptyState, PageHeader } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import type { SettlementAccount } from "@/lib/types";

type AccountForm = {
  bank_name: string;
  bank_account_number: string;
  bank_account_holder: string;
  settlement_cycle: string;
  settlement_memo: string;
};

const emptyForm: AccountForm = {
  bank_name: "",
  bank_account_number: "",
  bank_account_holder: "",
  settlement_cycle: "",
  settlement_memo: "",
};

function formFromAccount(account: SettlementAccount): AccountForm {
  return {
    bank_name: account.bank_name || "",
    bank_account_number: account.bank_account_number || "",
    bank_account_holder: account.bank_account_holder || "",
    settlement_cycle: account.settlement_cycle || "",
    settlement_memo: account.settlement_memo || "",
  };
}

function hasAccount(account: SettlementAccount | null) {
  return Boolean(account?.bank_name && account.bank_account_number && account.bank_account_holder);
}

export default function MerchantSettlementAccountPage() {
  const [account, setAccount] = useState<SettlementAccount | null>(null);
  const [form, setForm] = useState<AccountForm>(emptyForm);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadAccount() {
      setMessage("");
      setIsError(false);

      try {
        const accountData = await apiFetch<SettlementAccount>(
          "/api/v1/merchant/settlement-account",
          {},
          true,
        );
        if (cancelled) return;
        setAccount(accountData);
        setForm(formFromAccount(accountData));
      } catch (error) {
        if (cancelled) return;
        setIsError(true);
        setMessage(friendlyErrorMessage(error));
      }
    }

    void loadAccount();
    return () => {
      cancelled = true;
    };
  }, []);

  function updateField(field: keyof AccountForm, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function saveAccount(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setMessage("");
    setIsError(false);

    try {
      const updated = await apiFetch<SettlementAccount>(
        "/api/v1/merchant/settlement-account",
        {
          method: "PUT",
          body: JSON.stringify(form),
        },
        true,
      );
      setAccount(updated);
      setForm(formFromAccount(updated));
      setMessage("정산 계좌 정보를 저장했습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="section">
      <PageHeader
        title="정산 계좌"
        description="점주 정산금을 받을 계좌 정보를 등록합니다."
      />
      <p className="message">
        MVP 계좌 등록용 정보입니다. 실제 은행 송금은 아직 발생하지 않습니다.
      </p>

      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      {account && (
        <div className="panel">
          <div className="card-title-row">
            <div>
              <p className="eyebrow">가맹점</p>
              <h3>{account.business_name}</h3>
            </div>
          </div>
          {hasAccount(account) ? (
            <div className="detail-grid">
              <div>
                <span>은행명</span>
                <strong>{account.bank_name}</strong>
              </div>
              <div>
                <span>계좌번호</span>
                <strong>{account.bank_account_number}</strong>
              </div>
              <div>
                <span>예금주</span>
                <strong>{account.bank_account_holder}</strong>
              </div>
              <div>
                <span>정산 주기</span>
                <strong>{account.settlement_cycle || "-"}</strong>
              </div>
            </div>
          ) : (
            <EmptyState
              title="정산 계좌가 등록되지 않았습니다."
              description="아래 양식을 입력하면 정산 내역 화면에서 계좌 요약을 확인할 수 있습니다."
            />
          )}
          {account.settlement_memo && <p className="meta">정산 메모: {account.settlement_memo}</p>}
        </div>
      )}

      <form className="panel form-grid" onSubmit={saveAccount}>
        <label>
          은행명
          <input
            value={form.bank_name}
            onChange={(event) => updateField("bank_name", event.target.value)}
            placeholder="예) 국민은행"
          />
        </label>
        <label>
          계좌번호
          <input
            value={form.bank_account_number}
            onChange={(event) => updateField("bank_account_number", event.target.value)}
            placeholder="예) 123456-01-123456"
          />
        </label>
        <label>
          예금주
          <input
            value={form.bank_account_holder}
            onChange={(event) => updateField("bank_account_holder", event.target.value)}
            placeholder="예) 데모점주"
          />
        </label>
        <label>
          정산 주기
          <select
            value={form.settlement_cycle}
            onChange={(event) => updateField("settlement_cycle", event.target.value)}
          >
            <option value="">선택 안 함</option>
            <option value="WEEKLY">주 1회</option>
            <option value="BIWEEKLY">격주</option>
            <option value="MONTHLY">월 1회</option>
          </select>
        </label>
        <label className="full-width">
          정산 메모
          <textarea
            value={form.settlement_memo}
            onChange={(event) => updateField("settlement_memo", event.target.value)}
            placeholder="운영자에게 전달할 정산 참고사항을 입력하세요."
            rows={4}
          />
        </label>
        <div className="actions">
          <button type="submit" disabled={saving}>
            {saving ? "저장 중..." : "정산 계좌 저장"}
          </button>
        </div>
      </form>
    </section>
  );
}
