"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import type { MerchantApplication } from "@/lib/types";

export default function MerchantApplyPage() {
  const initialForm = {
    store_name: "",
    owner_name: "",
    email: "",
    password: "",
    password_confirm: "",
    phone: "",
    business_registration_number: "",
    address: "",
    product_category: "",
    pickup_available_time: "",
    note: "",
  };
  const [form, setForm] = useState({
    ...initialForm,
  });
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  function updateField(field: keyof typeof form, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function submitApplication(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    setIsError(false);

    if (form.password.length < 8) {
      setLoading(false);
      setIsError(true);
      setMessage("비밀번호는 8자 이상 입력해 주세요.");
      return;
    }

    if (form.password !== form.password_confirm) {
      setLoading(false);
      setIsError(true);
      setMessage("비밀번호와 비밀번호 확인이 일치하지 않습니다.");
      return;
    }

    const payload = {
      store_name: form.store_name,
      owner_name: form.owner_name,
      email: form.email,
      password: form.password,
      phone: form.phone,
      business_registration_number: form.business_registration_number,
      address: form.address,
      product_category: form.product_category,
      pickup_available_time: form.pickup_available_time,
      note: form.note,
    };

    try {
      await apiFetch<MerchantApplication>("/api/v1/merchants/apply", {
        method: "POST",
        body: JSON.stringify({
          ...payload,
          region_sido: "",
          region_sigungu: "",
          region_dong: "",
        }),
      });
      setForm({ ...initialForm });
      setSubmitted(true);
      setMessage("입점 신청이 접수되었습니다. 관리자 승인 후 로그인할 수 있습니다.");
    } catch (error) {
      const errorMessage = friendlyErrorMessage(error);
      const normalized = errorMessage.toLowerCase();
      setIsError(true);
      if (normalized.includes("pending merchant application") || normalized.includes("already used")) {
        setMessage("이미 사용 중인 이메일이거나 접수된 입점 신청이 있습니다.");
      } else {
        setMessage("입점 신청을 접수하지 못했습니다. 입력 정보를 확인해 주세요.");
      }
    } finally {
      setLoading(false);
    }
  }

  if (submitted) {
    return (
      <section className="section">
        <div className="panel">
          <p className="eyebrow">Merchant Application</p>
          <h1>입점 신청 접수 완료</h1>
          <p className="message success">
            입점 신청이 접수되었습니다. 관리자 승인 후 로그인 이메일과 비밀번호로 가맹점 관리 화면에 로그인할 수 있습니다.
          </p>
          <p>
            승인 전에는 가맹점 관리 화면에 접근할 수 없습니다. 관리자 공개 가입이나 Google 가입으로는 가맹점 권한이 생성되지
            않습니다.
          </p>
          <div className="button-row">
            <Link className="button-link" href="/login">
              로그인 화면으로 이동
            </Link>
            <Link className="button-link secondary" href="/">
              홈으로 이동
            </Link>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="section">
      <div className="card-title-row">
        <div>
          <p className="eyebrow">Merchant Application</p>
          <h1>가맹점 입점 신청</h1>
          <p>
            상품을 등록하고 판매하려는 매장은 이 신청서를 제출해 주세요. 고객 회원가입이나 Google 가입으로는
            가맹점 권한이 생성되지 않으며, 관리자 승인 전에는 가맹점 관리 화면에 접근할 수 없습니다.
          </p>
        </div>
        <Link className="button-link secondary" href="/register">
          고객 회원가입으로 돌아가기
        </Link>
      </div>

      <p className="message">
        이 신청은 계정을 즉시 활성화하지 않습니다. 관리자가 신청 정보를 검토하고 승인해야 merchant 계정과 프로필이 활성화됩니다.
        이미 고객 계정으로 가입한 이메일이라도 가맹점 권한은 자동으로 부여되지 않습니다.
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
          로그인 이메일
          <input type="email" value={form.email} onChange={(event) => updateField("email", event.target.value)} required />
        </label>
        <label>
          비밀번호
          <input
            type="password"
            minLength={8}
            value={form.password}
            onChange={(event) => updateField("password", event.target.value)}
            required
          />
          <span className="help-text">관리자 승인 후 이 비밀번호로 가맹점 로그인에 사용됩니다. 8자 이상 입력해 주세요.</span>
        </label>
        <label>
          비밀번호 확인
          <input
            type="password"
            minLength={8}
            value={form.password_confirm}
            onChange={(event) => updateField("password_confirm", event.target.value)}
            required
          />
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
          매장 주소
          <input value={form.address} onChange={(event) => updateField("address", event.target.value)} required />
        </label>
        <label>
          주요 판매 상품
          <input value={form.product_category} onChange={(event) => updateField("product_category", event.target.value)} />
          <span className="help-text">예: 빵, 샌드위치, 케이크, 도시락, 샐러드 등</span>
        </label>
        <label>
          픽업 가능 시간
          <input value={form.pickup_available_time} onChange={(event) => updateField("pickup_available_time", event.target.value)} />
          <span className="help-text">예: 매일 18:00~21:00</span>
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
