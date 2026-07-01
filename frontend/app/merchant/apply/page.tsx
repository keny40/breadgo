"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import type { MerchantApplication } from "@/lib/types";

export default function MerchantApplyPage() {
  const [form, setForm] = useState({
    store_name: "",
    owner_name: "",
    email: "",
    phone: "",
    business_registration_number: "",
    address: "",
    region_sido: "",
    region_sigungu: "",
    region_dong: "",
    product_category: "",
    pickup_available_time: "",
    note: "",
  });
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  function updateField(field: keyof typeof form, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function submitApplication(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    setIsError(false);

    try {
      const application = await apiFetch<MerchantApplication>("/api/v1/merchants/apply", {
        method: "POST",
        body: JSON.stringify(form),
      });
      setMessage(`입점 신청이 접수되었습니다. 신청 상태: ${application.status}`);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="section">
      <div className="card-title-row">
        <div>
          <p className="eyebrow">Merchant Application</p>
          <h1>가맹점 입점 신청</h1>
          <p>가맹점은 입점 신청 후 관리자 승인 절차를 거칩니다. 승인 전에는 가맹점 관리 화면에 접근할 수 없습니다.</p>
        </div>
        <Link className="button-link secondary" href="/register">
          고객 회원가입으로 돌아가기
        </Link>
      </div>

      <p className="message">
        이 신청은 계정을 즉시 생성하지 않습니다. 관리자가 신청 정보를 검토하고 승인해야 merchant 계정과 프로필이 활성화됩니다.
      </p>

      <form className="panel form-grid" onSubmit={submitApplication}>
        <label>
          매장명
          <input value={form.store_name} onChange={(event) => updateField("store_name", event.target.value)} required />
        </label>
        <label>
          대표자명
          <input value={form.owner_name} onChange={(event) => updateField("owner_name", event.target.value)} required />
        </label>
        <label>
          이메일
          <input type="email" value={form.email} onChange={(event) => updateField("email", event.target.value)} required />
        </label>
        <label>
          연락처
          <input value={form.phone} onChange={(event) => updateField("phone", event.target.value)} required />
        </label>
        <label>
          사업자등록번호
          <input
            value={form.business_registration_number}
            onChange={(event) => updateField("business_registration_number", event.target.value)}
            required
          />
        </label>
        <label>
          주소
          <input value={form.address} onChange={(event) => updateField("address", event.target.value)} required />
        </label>
        <label>
          시/도
          <input value={form.region_sido} onChange={(event) => updateField("region_sido", event.target.value)} />
        </label>
        <label>
          시/군/구
          <input value={form.region_sigungu} onChange={(event) => updateField("region_sigungu", event.target.value)} />
        </label>
        <label>
          동
          <input value={form.region_dong} onChange={(event) => updateField("region_dong", event.target.value)} />
        </label>
        <label>
          주요 상품 카테고리
          <input value={form.product_category} onChange={(event) => updateField("product_category", event.target.value)} />
        </label>
        <label>
          픽업 가능 시간
          <input value={form.pickup_available_time} onChange={(event) => updateField("pickup_available_time", event.target.value)} />
        </label>
        <label>
          메모
          <textarea value={form.note} onChange={(event) => updateField("note", event.target.value)} />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? "신청 중" : "입점 신청 제출"}
        </button>
        {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}
      </form>
    </section>
  );
}
