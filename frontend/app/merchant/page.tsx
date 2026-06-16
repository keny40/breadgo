"use client";

import { FormEvent, useEffect, useState } from "react";
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
      <h1>가맹점 대시보드</h1>
      <div className="actions">
        <button type="button" onClick={loadMerchant}>
          내 가맹점 정보 확인
        </button>
      </div>
      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      {merchant ? (
        <article className="item">
          <h3>{merchant.business_name}</h3>
          <div className="meta">
            <span>상태 {merchant.status}</span>
            <span>사업자번호 {merchant.business_registration_number}</span>
            <span>대표자 {merchant.representative_name}</span>
            <span>전화 {merchant.phone_number}</span>
          </div>
        </article>
      ) : (
        <form className="panel form-grid" onSubmit={registerMerchant}>
          <h2>가맹점 등록</h2>
          <label>
            Business name
            <input value={businessName} onChange={(event) => setBusinessName(event.target.value)} required />
          </label>
          <label>
            Business registration number
            <input
              value={businessRegistrationNumber}
              onChange={(event) => setBusinessRegistrationNumber(event.target.value)}
              required
            />
          </label>
          <label>
            Representative name
            <input
              value={representativeName}
              onChange={(event) => setRepresentativeName(event.target.value)}
              required
            />
          </label>
          <label>
            Phone number
            <input value={phoneNumber} onChange={(event) => setPhoneNumber(event.target.value)} required />
          </label>
          <button type="submit">가맹점 등록</button>
        </form>
      )}
    </section>
  );
}
