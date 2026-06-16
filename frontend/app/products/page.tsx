"use client";

import { FormEvent, useEffect, useState } from "react";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import type { Payment, RegionProduct, Reservation } from "@/lib/types";

const paymentMethods = [
  { value: "MOCK_CARD", label: "카드 모의결제" },
  { value: "MOCK_KAKAO_PAY", label: "카카오페이 모의결제" },
  { value: "MOCK_NAVER_PAY", label: "네이버페이 모의결제" },
];
const demoRegions = [
  { label: "서울특별시 강남구 역삼동", sido: "서울특별시", sigungu: "강남구", dong: "역삼동" },
  { label: "서울특별시 강남구 삼성동", sido: "서울특별시", sigungu: "강남구", dong: "삼성동" },
  { label: "경기도 안산시 고잔동", sido: "경기도", sigungu: "안산시", dong: "고잔동" },
];

export default function ProductsPage() {
  const [sido, setSido] = useState("서울특별시");
  const [sigungu, setSigungu] = useState("강남구");
  const [dong, setDong] = useState("역삼동");
  const [products, setProducts] = useState<RegionProduct[]>([]);
  const [quantities, setQuantities] = useState<Record<string, number>>({});
  const [pickupCode, setPickupCode] = useState("");
  const [latestReservation, setLatestReservation] = useState<Reservation | null>(null);
  const [paymentMethod, setPaymentMethod] = useState("MOCK_CARD");
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadInitialProducts() {
      try {
        const params = new URLSearchParams({
          sido: "서울특별시",
          sigungu: "강남구",
          dong: "역삼동",
        });
        const data = await apiFetch<RegionProduct[]>(`/api/v1/regions/products?${params.toString()}`);
        if (cancelled) {
          return;
        }
        setProducts(data);
        setMessage(
          data.length > 0
            ? `${data.length}개 상품을 불러왔습니다.`
            : "선택한 지역에 판매 중인 상품이 없습니다.",
        );
      } catch (error) {
        if (cancelled) {
          return;
        }
        setIsError(true);
        setMessage(friendlyErrorMessage(error));
      }
    }

    void loadInitialProducts();
    return () => {
      cancelled = true;
    };
  }, []);

  function buildRegionQuery() {
    const params = new URLSearchParams();
    if (sido.trim()) params.set("sido", sido.trim());
    if (sigungu.trim()) params.set("sigungu", sigungu.trim());
    if (dong.trim()) params.set("dong", dong.trim());
    return params.toString();
  }

  async function loadProducts(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault();
    setMessage("");
    setIsError(false);
    setPickupCode("");
    setLatestReservation(null);

    try {
      const data = await apiFetch<RegionProduct[]>(`/api/v1/regions/products?${buildRegionQuery()}`);
      setProducts(data);
      setMessage(
        data.length > 0
          ? `${data.length}개 상품을 불러왔습니다.`
          : "선택한 지역에 판매 중인 상품이 없습니다.",
      );
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  async function reserveProduct(productId: string) {
    setMessage("");
    setIsError(false);
    setPickupCode("");
    const quantity = quantities[productId] || 1;

    try {
      const reservation = await apiFetch<Reservation>(
        "/api/v1/reservations",
        {
          method: "POST",
          body: JSON.stringify({ product_id: productId, quantity }),
        },
        true,
      );
      setPickupCode(reservation.pickup_code);
      setLatestReservation(reservation);
      setMessage("예약이 완료되었습니다.");
      const data = await apiFetch<RegionProduct[]>(`/api/v1/regions/products?${buildRegionQuery()}`);
      setProducts(data);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  async function payLatestReservation() {
    if (!latestReservation) {
      setIsError(true);
      setMessage("먼저 상품을 예약하세요.");
      return;
    }

    setMessage("");
    setIsError(false);

    try {
      const ready = await apiFetch<Payment>(
        "/api/v1/payments/mock/ready",
        {
          method: "POST",
          body: JSON.stringify({
            reservation_id: latestReservation.id,
            method: paymentMethod,
          }),
        },
        true,
      );
      const paid = await apiFetch<Payment>(
        "/api/v1/payments/mock/confirm",
        {
          method: "POST",
          body: JSON.stringify({ payment_id: ready.id }),
        },
        true,
      );
      setMessage(`결제 완료. 상태: ${paid.status}`);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  function applyDemoRegion(region: (typeof demoRegions)[number]) {
    setSido(region.sido);
    setSigungu(region.sigungu);
    setDong(region.dong);
    setMessage(`${region.label} 지역이 선택되었습니다.`);
    setIsError(false);
  }

  const productsByStore = products.reduce<Record<string, RegionProduct[]>>((groups, product) => {
    groups[product.store_id] = groups[product.store_id] || [];
    groups[product.store_id].push(product);
    return groups;
  }, {});

  return (
    <section className="section">
      <h1>상품 보기</h1>
      <form className="panel form-grid" onSubmit={loadProducts}>
        <div className="two-column">
          <label>
            시/도
            <input value={sido} onChange={(event) => setSido(event.target.value)} placeholder="서울특별시" />
          </label>
          <label>
            시/군/구
            <input value={sigungu} onChange={(event) => setSigungu(event.target.value)} placeholder="강남구" />
          </label>
        </div>
        <label>
          동/읍/면
          <input value={dong} onChange={(event) => setDong(event.target.value)} placeholder="역삼동" />
        </label>
        <div className="actions">
          {demoRegions.map((region) => (
            <button type="button" className="secondary" key={region.label} onClick={() => applyDemoRegion(region)}>
              {region.label}
            </button>
          ))}
        </div>
        <button type="submit">지역 상품 찾기</button>
      </form>

      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}
      {products.length === 0 && !isError && (
        <div className="empty-state">선택한 지역에 판매 중인 상품이 없습니다.</div>
      )}

      <div className="list">
        {Object.entries(productsByStore).map(([storeId, storeProducts]) => (
          <section className="panel" key={storeId}>
            <div className="section">
              <h2>{storeProducts[0].store_name}</h2>
              <div className="meta">
                <span>
                  {[storeProducts[0].sido, storeProducts[0].sigungu, storeProducts[0].dong]
                    .filter(Boolean)
                    .join(" ")}
                </span>
                <span>{storeProducts[0].store_address}</span>
              </div>
            </div>
            <div className="list">
              {storeProducts.map((product) => (
                <article className="item" key={product.id}>
                  <h3>{product.name}</h3>
                  <p>{product.description || "설명 없음"}</p>
                  <div className="meta">
                    <span>정가 {product.original_price}</span>
                    <span>할인가 {product.discount_price}</span>
                    <span>수량 {product.quantity}</span>
                    <span>상태 {product.status}</span>
                  </div>
                  <div className="meta">
                    <span>픽업 시작 {new Date(product.pickup_start_time).toLocaleString()}</span>
                    <span>픽업 종료 {new Date(product.pickup_end_time).toLocaleString()}</span>
                  </div>
                  <div className="actions">
                    <input
                      type="number"
                      min={1}
                      max={product.quantity}
                      value={quantities[product.id] || 1}
                      onChange={(event) =>
                        setQuantities((current) => ({
                          ...current,
                          [product.id]: Number(event.target.value),
                        }))
                      }
                      aria-label={`${product.name} reservation quantity`}
                    />
                    <button type="button" onClick={() => reserveProduct(product.id)}>
                      이 상품 예약하기
                    </button>
                  </div>
                </article>
              ))}
            </div>
          </section>
        ))}
      </div>

      {pickupCode && (
        <div className="panel">
          <h2>픽업코드</h2>
          <p className="pickup-code">{pickupCode}</p>
          <div className="form-grid">
            <label>
              Mock payment method
              <select value={paymentMethod} onChange={(event) => setPaymentMethod(event.target.value)}>
                {paymentMethods.map((method) => (
                  <option key={method.value} value={method.value}>
                    {method.label}
                  </option>
                ))}
              </select>
            </label>
            <button type="button" onClick={payLatestReservation}>
              결제하기
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
