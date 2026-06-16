"use client";

import { FormEvent, useEffect, useState } from "react";
import { PageHeader, StatusBadge } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import type { Merchant, MerchantMeResponse } from "@/lib/types";

export default function MerchantPage() {
  const [merchant, setMerchant] = useState<Merchant | null>(null);
  const [businessName, setBusinessName] = useState("");
  const [businessRegistrationNumber, setBusinessRegistrationNumber] = useState("");
  const [representativeName, setRepresentativeName] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    void loadMerchant();
  }, []);

  async function loadMerchant() {
    setMessage("");
    setIsError(false);

    try {
      const data = await apiFetch<MerchantMeResponse>("/api/v1/merchants/me", {}, true);
      setMerchant(data.merchant);
      setMessage("가맹점 정보를 불러왔습니다.");
    } catch (error) {
      setMerchant(null);
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  async function registerMerchant(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    setIsError(false);

    try {
      const data = await apiFetch<Merchant>(
        "/api/v1/merchants/register",
        {
          method: "POST",
          body: JSON.stringify({
            business_name: businessName,
            business_registration_number: businessRegistrationNumber,
            representative_name: representativeName,
            phone_number: phoneNumber,
          }),
        },
        true,
      );
      setMerchant(data);
      setMessage("가맹점 등록이 완료되었습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  return (
    <section className="section">
      <PageHeader
        title="가맹점 대시보드"
        description="가맹점 등록 상태와 기본 사업자 정보를 확인합니다."
        actions={
          <button type="button" onClick={loadMerchant}>
            내 가맹점 정보 확인
          </button>
        }
      />
      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      {merchant ? (
        <article className="item">
          <div className="card-title-row">
            <h3>{merchant.business_name}</h3>
            <StatusBadge status={merchant.status} />
          </div>
          <div className="meta">
            <span>사업자번호 {merchant.business_registration_number}</span>
            <span>대표자 {merchant.representative_name}</span>
            <span>전화 {merchant.phone_number}</span>
          </div>
        </article>
      ) : (
        <form className="panel form-grid" onSubmit={registerMerchant}>
          <h2>가맹점 등록</h2>
          <p className="message">매장과 상품을 등록하려면 먼저 가맹점 프로필을 생성해야 합니다.</p>
          <label>
            상호명
            <input value={businessName} onChange={(event) => setBusinessName(event.target.value)} required />
          </label>
          <label>
            사업자등록번호
            <input
              value={businessRegistrationNumber}
              onChange={(event) => setBusinessRegistrationNumber(event.target.value)}
              required
            />
          </label>
          <label>
            대표자명
            <input
              value={representativeName}
              onChange={(event) => setRepresentativeName(event.target.value)}
              required
            />
          </label>
          <label>
            연락처
            <input value={phoneNumber} onChange={(event) => setPhoneNumber(event.target.value)} required />
          </label>
          <button type="submit">가맹점 등록</button>
        </form>
      )}
    </section>
  );
}
