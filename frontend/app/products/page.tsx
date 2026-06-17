"use client";

/* eslint-disable @next/next/no-img-element */

import { FormEvent, useEffect, useState } from "react";
import { Badge, EmptyState, PageHeader, StatusBadge } from "@/components/UI";
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

function formatMoney(value: string) {
  return `${Number(value).toLocaleString()}원`;
}

function discountPercent(product: RegionProduct) {
  const original = Number(product.original_price);
  const discount = Number(product.discount_price);
  if (!original || discount >= original) {
    return 0;
  }
  return Math.round(((original - discount) / original) * 100);
}

function paymentMethodLabel(value: string) {
  return paymentMethods.find((method) => method.value === value)?.label || value;
}

function ProductImage({ imageUrl, name }: { imageUrl: string | null | undefined; name: string }) {
  if (!imageUrl) {
    return <div className="product-image-placeholder">이미지 없음</div>;
  }

  return <img className="product-image" src={imageUrl} alt={`${name} 대표 이미지`} loading="lazy" />;
}

export default function ProductsPage() {
  const [sido, setSido] = useState("서울특별시");
  const [sigungu, setSigungu] = useState("강남구");
  const [dong, setDong] = useState("역삼동");
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [discoveryMode, setDiscoveryMode] = useState<"region" | "nearby">("region");
  const [products, setProducts] = useState<RegionProduct[]>([]);
  const [quantities, setQuantities] = useState<Record<string, number>>({});
  const [pickupCode, setPickupCode] = useState("");
  const [latestReservation, setLatestReservation] = useState<Reservation | null>(null);
  const [latestReservedProduct, setLatestReservedProduct] = useState<RegionProduct | null>(null);
  const [latestPayment, setLatestPayment] = useState<Payment | null>(null);
  const [paymentMethod, setPaymentMethod] = useState("MOCK_CARD");
  const [paymentMessage, setPaymentMessage] = useState("");
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [isPaymentError, setIsPaymentError] = useState(false);
  const [locating, setLocating] = useState(false);

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
    setLatestReservedProduct(null);
    setLatestPayment(null);
    setPaymentMessage("");
    setIsPaymentError(false);
    setDiscoveryMode("region");

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

  function getBrowserPosition(): Promise<GeolocationPosition> {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error("이 브라우저에서는 위치 기능을 사용할 수 없습니다."));
        return;
      }

      navigator.geolocation.getCurrentPosition(resolve, reject, {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000,
      });
    });
  }

  async function loadNearbyProducts(lat: number, lng: number, announce = true) {
    const params = new URLSearchParams({
      lat: String(lat),
      lng: String(lng),
    });
    const data = await apiFetch<RegionProduct[]>(`/api/v1/regions/products/nearby?${params.toString()}`);
    setProducts(data);
    setDiscoveryMode("nearby");
    setUserLocation({ lat, lng });
    if (announce) {
      setMessage(
        data.length > 0
          ? `내 위치 기준 가까운 상품 ${data.length}개를 불러왔습니다.`
          : "내 위치 주변에 판매 중인 상품이 없습니다.",
      );
    }
  }

  async function findProductsNearMe() {
    setMessage("");
    setIsError(false);
    setPickupCode("");
    setLatestReservation(null);
    setLatestReservedProduct(null);
    setLatestPayment(null);
    setPaymentMessage("");
    setIsPaymentError(false);
    setLocating(true);

    try {
      const position = await getBrowserPosition();
      await loadNearbyProducts(position.coords.latitude, position.coords.longitude);
    } catch (error) {
      setIsError(true);
      const isGeolocationError =
        typeof error === "object" && error !== null && "code" in error && "message" in error;
      const message = isGeolocationError
        ? "위치 권한을 허용해야 내 위치로 상품을 찾을 수 있습니다."
        : friendlyErrorMessage(error);
      setMessage(message);
    } finally {
      setLocating(false);
    }
  }

  async function reserveProduct(productId: string) {
    setMessage("");
    setIsError(false);
    setPickupCode("");
    setLatestPayment(null);
    setPaymentMessage("");
    setIsPaymentError(false);
    const quantity = quantities[productId] || 1;
    const reservedProduct = products.find((product) => product.id === productId) || null;

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
      setLatestReservedProduct(reservedProduct);
      setMessage("예약이 완료되었습니다. 픽업코드를 확인하고 Mock 결제를 진행해 보세요.");
      if (discoveryMode === "nearby" && userLocation) {
        await loadNearbyProducts(userLocation.lat, userLocation.lng, false);
      } else {
        const data = await apiFetch<RegionProduct[]>(`/api/v1/regions/products?${buildRegionQuery()}`);
        setProducts(data);
      }
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
    setPaymentMessage("");
    setIsPaymentError(false);

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
      setLatestPayment(paid);
      setPaymentMessage(`${paymentMethodLabel(paymentMethod)} 결제가 완료되었습니다.`);
    } catch (error) {
      setIsPaymentError(true);
      setPaymentMessage(friendlyErrorMessage(error));
    }
  }

  function continueBrowsing() {
    setPickupCode("");
    setLatestReservation(null);
    setLatestReservedProduct(null);
    setLatestPayment(null);
    setPaymentMessage("");
    setIsPaymentError(false);
    setMessage("");
    setIsError(false);
  }

  function applyDemoRegion(region: (typeof demoRegions)[number]) {
    setSido(region.sido);
    setSigungu(region.sigungu);
    setDong(region.dong);
    setMessage(`${region.label} 지역이 선택되었습니다.`);
    setIsError(false);
    setDiscoveryMode("region");
  }

  const productsByStore = products.reduce<Record<string, RegionProduct[]>>((groups, product) => {
    groups[product.store_id] = groups[product.store_id] || [];
    groups[product.store_id].push(product);
    return groups;
  }, {});

  return (
    <section className="section">
      <PageHeader
        title="상품 보기"
        description="지역을 선택하면 오늘 픽업 가능한 마감 할인 상품을 매장별로 확인할 수 있습니다."
      />
      <form className="panel form-grid" onSubmit={loadProducts}>
        <h2>지역 선택</h2>
        <div className="three-column">
          <label>
            시/도
            <input value={sido} onChange={(event) => setSido(event.target.value)} placeholder="서울특별시" />
          </label>
          <label>
            시/군/구
            <input value={sigungu} onChange={(event) => setSigungu(event.target.value)} placeholder="강남구" />
          </label>
          <label>
            동/읍/면
            <input value={dong} onChange={(event) => setDong(event.target.value)} placeholder="역삼동" />
          </label>
        </div>
        <div className="chip-row">
          {demoRegions.map((region) => (
            <button
              type="button"
              className={`chip ${
                sido === region.sido && sigungu === region.sigungu && dong === region.dong ? "active" : ""
              }`}
              key={region.label}
              onClick={() => applyDemoRegion(region)}
            >
              {region.label}
            </button>
          ))}
        </div>
        <div className="actions">
          <button type="submit">지역 상품 찾기</button>
          <button type="button" className="secondary" onClick={findProductsNearMe} disabled={locating}>
            {locating ? "위치 확인 중" : "내 위치로 찾기"}
          </button>
        </div>
      </form>

      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}
      {products.length === 0 && !isError && (
        <EmptyState title="선택한 지역에 판매 중인 상품이 없습니다." description="다른 데모 지역을 선택해 보세요." />
      )}

      <div className="list">
        {Object.entries(productsByStore).map(([storeId, storeProducts]) => (
          <section className="panel" key={storeId}>
            <div className="section">
              <div className="card-title-row">
                <h2>{storeProducts[0].store_name}</h2>
                <div className="actions">
                  {storeProducts[0].distance_km != null && (
                    <Badge tone="warning">{storeProducts[0].distance_km.toFixed(2)}km</Badge>
                  )}
                  <Badge tone="success">{storeProducts.length}개 상품</Badge>
                </div>
              </div>
              <div className="meta">
                <span>
                  {[storeProducts[0].sido, storeProducts[0].sigungu, storeProducts[0].dong]
                    .filter(Boolean)
                    .join(" ")}
                </span>
                <span>{storeProducts[0].store_address}</span>
              </div>
            </div>
            <div className="product-grid">
              {storeProducts.map((product) => (
                <article className="item" key={product.id}>
                  <ProductImage imageUrl={product.image_url} name={product.name} />
                  <div className="card-title-row">
                    <h3>{product.name}</h3>
                    <StatusBadge status={product.status} />
                  </div>
                  <p>{product.description || "설명 없음"}</p>
                  <div className="price-row">
                    <span className="original-price">{formatMoney(product.original_price)}</span>
                    <span className="discount-price">{formatMoney(product.discount_price)}</span>
                    {discountPercent(product) > 0 && <Badge tone="success">{discountPercent(product)}% 할인</Badge>}
                  </div>
                  <div className="meta">
                    <span>
                      남은 수량 <strong>{product.quantity}</strong>
                    </span>
                    <span>
                      매장 <strong>{product.store_name}</strong>
                    </span>
                    {product.distance_km != null && (
                      <span>
                        거리 <strong>{product.distance_km.toFixed(2)}km</strong>
                      </span>
                    )}
                  </div>
                  <div className="meta">
                    <span>픽업 {new Date(product.pickup_start_time).toLocaleString()}</span>
                    <span>- {new Date(product.pickup_end_time).toLocaleString()}</span>
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
        <div className="panel success-panel">
          <div className="card-title-row">
            <div>
              <p className="eyebrow">예약 성공</p>
              <h2>{latestReservedProduct?.name || latestReservation?.product_name || "마감 할인 상품"} 예약 완료</h2>
            </div>
            {latestReservation && <StatusBadge status={latestReservation.status} />}
          </div>
          <p>매장에서 아래 픽업코드를 보여주면 픽업 확인을 받을 수 있습니다.</p>
          <div className="pickup-code-block">
            <span>픽업 코드</span>
            <p className="pickup-code">{pickupCode}</p>
          </div>
          <div className="detail-grid">
            <div>
              <span>매장</span>
              <strong>{latestReservedProduct?.store_name || latestReservation?.store_name || "-"}</strong>
            </div>
            <div>
              <span>예약 수량</span>
              <strong>{latestReservation?.quantity ?? "-"}</strong>
            </div>
            <div>
              <span>총 결제 금액</span>
              <strong>{latestReservation ? formatMoney(latestReservation.total_price) : "-"}</strong>
            </div>
            <div>
              <span>픽업 마감</span>
              <strong>
                {latestReservation ? new Date(latestReservation.pickup_deadline).toLocaleString() : "-"}
              </strong>
            </div>
          </div>
          <div className="payment-box">
            <div className="form-grid">
              <label>
                Mock 결제 수단
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
            {paymentMessage && (
              <div className={`message ${isPaymentError ? "error" : "success"}`}>{paymentMessage}</div>
            )}
            {latestPayment && (
              <div className="meta">
                <span>
                  결제 수단 <strong>{paymentMethodLabel(latestPayment.method)}</strong>
                </span>
                <span>
                  결제 상태 <StatusBadge status={latestPayment.status} />
                </span>
                <span>
                  결제 금액 <strong>{formatMoney(latestPayment.amount)}</strong>
                </span>
              </div>
            )}
          </div>
          <div className="actions">
            <a href="/my-reservations">
              <button type="button">내 예약 보기</button>
            </a>
            <a href="/my-payments">
              <button type="button" className="secondary">
                결제 내역 보기
              </button>
            </a>
            <button type="button" className="secondary" onClick={continueBrowsing}>
              계속 상품 보기
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
