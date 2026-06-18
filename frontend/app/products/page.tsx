"use client";

/* eslint-disable @next/next/no-img-element */

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { Badge, EmptyState, PageHeader, StatusBadge } from "@/components/UI";
import { apiFetch, friendlyErrorMessage, getStoredUser, getToken, saveStoredUser } from "@/lib/api";
import type { AuthUser, Payment, RegionProduct, Reservation, Store } from "@/lib/types";

const paymentMethods = [
  { value: "MOCK_CARD", label: "카드 모의결제" },
  { value: "MOCK_KAKAO_PAY", label: "카카오페이 모의결제" },
  { value: "MOCK_NAVER_PAY", label: "네이버페이 모의결제" },
];
const fulfillmentMethods = [
  { value: "PICKUP", label: "매장 직접 픽업" },
  { value: "QUICK_DELIVERY", label: "퀵배달 요청" },
  { value: "PARCEL_DELIVERY", label: "택배 배송" },
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

function fulfillmentMethodLabel(value: string | null | undefined) {
  return fulfillmentMethods.find((method) => method.value === value)?.label || value || "-";
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
  const [mapStores, setMapStores] = useState<Store[]>([]);
  const [selectedMapStoreId, setSelectedMapStoreId] = useState<string | null>(null);
  const [quantities, setQuantities] = useState<Record<string, number>>({});
  const [fulfillmentByProduct, setFulfillmentByProduct] = useState<Record<string, string>>({});
  const [latestReservation, setLatestReservation] = useState<Reservation | null>(null);
  const [latestReservedProduct, setLatestReservedProduct] = useState<RegionProduct | null>(null);
  const [latestPayment, setLatestPayment] = useState<Payment | null>(null);
  const [paymentMethod, setPaymentMethod] = useState("MOCK_CARD");
  const [recipientName, setRecipientName] = useState("");
  const [recipientPhone, setRecipientPhone] = useState("");
  const [deliveryAddress, setDeliveryAddress] = useState("");
  const [deliveryRequestMemo, setDeliveryRequestMemo] = useState("");
  const [paymentMessage, setPaymentMessage] = useState("");
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [isPaymentError, setIsPaymentError] = useState(false);
  const [locating, setLocating] = useState(false);
  const [hasLogin, setHasLogin] = useState(false);
  const [currentRole, setCurrentRole] = useState<string | null>(null);

  const normalizedRole = currentRole?.toUpperCase() || null;
  const isCustomer = normalizedRole === "CUSTOMER";
  const isNonCustomerUser = normalizedRole === "MERCHANT" || normalizedRole === "ADMIN";

  useEffect(() => {
    let cancelled = false;

    async function loadInitialProducts() {
      try {
        const params = new URLSearchParams({
          sido: "서울특별시",
          sigungu: "강남구",
          dong: "역삼동",
        });
        const query = params.toString();
        const [data, storeData] = await Promise.all([
          apiFetch<RegionProduct[]>(`/api/v1/regions/products?${query}`),
          apiFetch<Store[]>(`/api/v1/regions/stores?${query}`),
        ]);
        if (cancelled) {
          return;
        }
        setProducts(data);
        setMapStores(storeData);
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

  useEffect(() => {
    let cancelled = false;

    function applyStoredAuth() {
      const token = getToken();
      const storedUser = getStoredUser();
      setHasLogin(Boolean(token));
      setCurrentRole(storedUser?.role || null);

      if (token && !storedUser?.role) {
        void apiFetch<AuthUser>("/api/v1/auth/me", {}, true)
          .then((user) => {
            if (cancelled) {
              return;
            }
            saveStoredUser(user);
            setHasLogin(true);
            setCurrentRole(user.role || null);
          })
          .catch(() => {
            if (!cancelled) {
              setCurrentRole(null);
            }
          });
      }
    }

    applyStoredAuth();
    window.addEventListener("breadgo-auth-changed", applyStoredAuth);
    window.addEventListener("storage", applyStoredAuth);

    return () => {
      cancelled = true;
      window.removeEventListener("breadgo-auth-changed", applyStoredAuth);
      window.removeEventListener("storage", applyStoredAuth);
    };
  }, []);

  function buildRegionQuery() {
    const params = new URLSearchParams();
    if (sido.trim()) params.set("sido", sido.trim());
    if (sigungu.trim()) params.set("sigungu", sigungu.trim());
    if (dong.trim()) params.set("dong", dong.trim());
    return params.toString();
  }

  async function loadRegionStores(query: string) {
    const data = await apiFetch<Store[]>(`/api/v1/regions/stores?${query}`);
    setMapStores(data);
    setSelectedMapStoreId((current) => {
      if (current && data.some((store) => store.id === current)) {
        return current;
      }
      return null;
    });
  }

  async function loadProducts(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault();
    setMessage("");
    setIsError(false);
    setLatestReservation(null);
    setLatestReservedProduct(null);
    setLatestPayment(null);
    setPaymentMessage("");
    setIsPaymentError(false);
    setDiscoveryMode("region");

    try {
      const query = buildRegionQuery();
      const [data] = await Promise.all([
        apiFetch<RegionProduct[]>(`/api/v1/regions/products?${query}`),
        loadRegionStores(query),
      ]);
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
    if (!isCustomer) {
      setIsError(true);
      setMessage(hasLogin ? "고객 예약은 CUSTOMER 계정에서만 가능합니다." : "예약하려면 로그인해 주세요.");
      return;
    }

    setMessage("");
    setIsError(false);
    setLatestPayment(null);
    setPaymentMessage("");
    setIsPaymentError(false);
    const quantity = quantities[productId] || 1;
    const reservedProduct = products.find((product) => product.id === productId) || null;
    if (!reservedProduct) {
      setIsError(true);
      setMessage("예약할 상품을 찾을 수 없습니다.");
      return;
    }
    const fulfillmentMethod = selectedFulfillmentForProduct(reservedProduct);
    const requiresDeliveryInfo = fulfillmentMethod !== "PICKUP";

    if (requiresDeliveryInfo && (!recipientName.trim() || !recipientPhone.trim() || !deliveryAddress.trim())) {
      setIsError(true);
      setMessage("배송 요청을 위해 받는 사람, 연락처, 주소를 입력해 주세요.");
      return;
    }

    try {
      const reservation = await apiFetch<Reservation>(
        "/api/v1/reservations",
        {
          method: "POST",
          body: JSON.stringify({
            product_id: productId,
            quantity,
            fulfillment_method: fulfillmentMethod,
            recipient_name: requiresDeliveryInfo ? recipientName : null,
            recipient_phone: requiresDeliveryInfo ? recipientPhone : null,
            delivery_address: requiresDeliveryInfo ? deliveryAddress : null,
            delivery_request_memo: requiresDeliveryInfo ? deliveryRequestMemo : null,
            delivery_fee: deliveryFeeForMethod(reservedProduct, fulfillmentMethod),
          }),
        },
        true,
      );
      setLatestReservation(reservation);
      setLatestReservedProduct(reservedProduct);
      setMessage("예약이 완료되었습니다. 수령 방법을 확인하고 Mock 결제를 진행해 보세요.");
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

  function availableFulfillmentMethods(product: RegionProduct) {
    return fulfillmentMethods.filter((method) => {
      if (method.value === "PICKUP") return product.allow_pickup;
      if (method.value === "QUICK_DELIVERY") return product.allow_quick_delivery;
      return product.allow_parcel_delivery;
    });
  }

  function selectedFulfillmentForProduct(product: RegionProduct) {
    const available = availableFulfillmentMethods(product);
    const selected = fulfillmentByProduct[product.id];
    if (selected && available.some((method) => method.value === selected)) {
      return selected;
    }
    return available[0]?.value || "PICKUP";
  }

  function deliveryFeeForMethod(product: RegionProduct, method: string) {
    if (method === "QUICK_DELIVERY") return product.quick_delivery_fee;
    if (method === "PARCEL_DELIVERY") return product.parcel_delivery_fee;
    return "0.00";
  }

  function productAmountFor(product: RegionProduct) {
    return Number(product.discount_price) * (quantities[product.id] || 1);
  }

  function selectedDeliveryFeeFor(product: RegionProduct) {
    return Number(deliveryFeeForMethod(product, selectedFulfillmentForProduct(product)));
  }

  const productsByStore = products.reduce<Record<string, RegionProduct[]>>((groups, product) => {
    groups[product.store_id] = groups[product.store_id] || [];
    groups[product.store_id].push(product);
    return groups;
  }, {});

  const storeById = mapStores.reduce<Record<string, Store>>((stores, store) => {
    stores[store.id] = store;
    return stores;
  }, {});

  const mapStoreSummaries = Object.entries(productsByStore)
    .map(([storeId, storeProducts]) => {
      const store = storeById[storeId];
      if (!store?.latitude || !store.longitude) {
        return null;
      }
      return {
        storeId,
        store,
        products: storeProducts,
        latitude: Number(store.latitude),
        longitude: Number(store.longitude),
        distanceKm: storeProducts.find((product) => product.distance_km != null)?.distance_km ?? null,
      };
    })
    .filter((summary): summary is NonNullable<typeof summary> => Boolean(summary));

  const storesWithoutCoordinates = Object.keys(productsByStore).length - mapStoreSummaries.length;
  const mapLatitudes = [
    ...mapStoreSummaries.map((summary) => summary.latitude),
    ...(userLocation ? [userLocation.lat] : []),
  ];
  const mapLongitudes = [
    ...mapStoreSummaries.map((summary) => summary.longitude),
    ...(userLocation ? [userLocation.lng] : []),
  ];
  const minLatitude = mapLatitudes.length > 0 ? Math.min(...mapLatitudes) : 0;
  const maxLatitude = mapLatitudes.length > 0 ? Math.max(...mapLatitudes) : 0;
  const minLongitude = mapLongitudes.length > 0 ? Math.min(...mapLongitudes) : 0;
  const maxLongitude = mapLongitudes.length > 0 ? Math.max(...mapLongitudes) : 0;
  const latitudeRange = Math.max(maxLatitude - minLatitude, 0.01);
  const longitudeRange = Math.max(maxLongitude - minLongitude, 0.01);

  function mapPosition(latitude: number, longitude: number) {
    return {
      top: `${8 + ((maxLatitude - latitude) / latitudeRange) * 84}%`,
      left: `${8 + ((longitude - minLongitude) / longitudeRange) * 84}%`,
    };
  }

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

      {isCustomer && (
        <section className="panel form-grid">
          <h2>수령 방법 안내</h2>
          <p className="field-help">
            상품마다 가능한 수령 방식이 다릅니다. 각 상품 카드에서 수령 방법을 선택해 주세요. 택배 배송은 배송 가능한 상품에 한해 선택할 수 있습니다.
          </p>
          {products.some((product) => product.allow_quick_delivery || product.allow_parcel_delivery) && (
            <>
              <div className="message">
                현재는 실제 배송 연동이 아닌 요청 정보 저장 단계입니다. 배송 상태는 점주가 수동으로 변경합니다.
              </div>
              <div className="two-column">
                <label>
                  받는 사람
                  <input value={recipientName} onChange={(event) => setRecipientName(event.target.value)} />
                </label>
                <label>
                  받는 사람 연락처
                  <input value={recipientPhone} onChange={(event) => setRecipientPhone(event.target.value)} />
                </label>
              </div>
              <label>
                주소
                <input value={deliveryAddress} onChange={(event) => setDeliveryAddress(event.target.value)} />
              </label>
              <label>
                배송 요청사항
                <textarea
                  value={deliveryRequestMemo}
                  onChange={(event) => setDeliveryRequestMemo(event.target.value)}
                  placeholder="문 앞에 놓아주세요, 도착 전 연락 주세요 등"
                />
              </label>
            </>
          )}
        </section>
      )}

      {!isCustomer && (
        <section className="panel">
          {isNonCustomerUser ? (
            <p className="field-help">고객 예약은 CUSTOMER 계정에서만 가능합니다.</p>
          ) : (
            <div className="card-title-row">
              <p className="field-help">예약하려면 로그인해 주세요.</p>
              <Link className="button-link" href="/login">
                로그인
              </Link>
            </div>
          )}
        </section>
      )}

      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}
      {products.length === 0 && !isError && (
        <EmptyState title="선택한 지역에 판매 중인 상품이 없습니다." description="다른 데모 지역을 선택해 보세요." />
      )}

      <div className="discovery-layout">
        <section className="panel map-panel" aria-label="상품 지도 보기">
          <div className="card-title-row">
            <div>
              <p className="eyebrow">Map View</p>
              <h2>지도 보기</h2>
            </div>
            <Badge tone={discoveryMode === "nearby" ? "success" : "muted"}>
              {discoveryMode === "nearby" ? "내 위치 기준" : "선택 지역 기준"}
            </Badge>
          </div>
          <p className="field-help">
            외부 지도 API 없이 매장 좌표를 시각화한 MVP 지도입니다. 좌표가 등록된 매장만 지도에 표시됩니다.
          </p>
          <div className="mock-map">
            <div className="mock-map-grid" />
            {userLocation && (
              <div className="map-marker user-location" style={mapPosition(userLocation.lat, userLocation.lng)}>
                내 위치
              </div>
            )}
            {mapStoreSummaries.map((summary, index) => (
              <button
                type="button"
                className={`map-marker store-marker ${selectedMapStoreId === summary.storeId ? "active" : ""}`}
                style={mapPosition(summary.latitude, summary.longitude)}
                key={summary.storeId}
                onClick={() => setSelectedMapStoreId(summary.storeId)}
                aria-label={`${summary.store.name} 지도 마커`}
              >
                {index + 1}
              </button>
            ))}
            {mapStoreSummaries.length === 0 && !userLocation && (
              <div className="map-empty">
                <strong>지도에 표시할 좌표가 없습니다.</strong>
                <span>매장에 위도/경도가 등록되면 이곳에 표시됩니다.</span>
              </div>
            )}
          </div>
          <div className="map-store-list">
            {mapStoreSummaries.map((summary, index) => (
              <button
                type="button"
                className={`map-store-summary ${selectedMapStoreId === summary.storeId ? "active" : ""}`}
                key={summary.storeId}
                onClick={() => setSelectedMapStoreId(summary.storeId)}
              >
                <span>{index + 1}</span>
                <strong>{summary.store.name}</strong>
                <small>
                  {summary.products.length}개 상품
                  {summary.distanceKm != null ? ` · ${summary.distanceKm.toFixed(2)}km` : ""}
                </small>
              </button>
            ))}
          </div>
          {storesWithoutCoordinates > 0 && (
            <p className="field-help">
              좌표가 없는 {storesWithoutCoordinates}개 매장은 지도에서 제외되지만 상품 리스트에는 표시됩니다.
            </p>
          )}
        </section>

        <div className="list">
        {Object.entries(productsByStore).map(([storeId, storeProducts]) => (
          <section className={`panel ${selectedMapStoreId === storeId ? "map-selected-panel" : ""}`} key={storeId}>
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
                  {isCustomer && (
                    <>
                      <div className="payment-box">
                        <h3>수령 방법을 선택해 주세요.</h3>
                        <div className="chip-row">
                          {availableFulfillmentMethods(product).map((method) => (
                            <button
                              type="button"
                              className={`chip ${
                                selectedFulfillmentForProduct(product) === method.value ? "active" : ""
                              }`}
                              key={method.value}
                              onClick={() =>
                                setFulfillmentByProduct((current) => ({
                                  ...current,
                                  [product.id]: method.value,
                                }))
                              }
                            >
                              {method.label}
                            </button>
                          ))}
                        </div>
                        <div className="detail-grid">
                          <div>
                            <span>상품 금액</span>
                            <strong>{formatMoney(String(productAmountFor(product)))}</strong>
                          </div>
                          <div>
                            <span>배송비</span>
                            <strong>{formatMoney(String(selectedDeliveryFeeFor(product)))}</strong>
                          </div>
                          <div>
                            <span>총 고객 결제금액</span>
                            <strong>
                              {formatMoney(String(productAmountFor(product) + selectedDeliveryFeeFor(product)))}
                            </strong>
                          </div>
                        </div>
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
                    </>
                  )}
                </article>
              ))}
            </div>
          </section>
        ))}
        </div>
      </div>

      {isCustomer && latestReservation && (
        <div className="panel success-panel">
          <div className="card-title-row">
            <div>
              <p className="eyebrow">예약 성공</p>
              <h2>{latestReservedProduct?.name || latestReservation?.product_name || "마감 할인 상품"} 예약 완료</h2>
            </div>
            {latestReservation && <StatusBadge status={latestReservation.status} />}
          </div>
          {!latestPayment && (
            <p className="message">
              예약 생성 완료. 결제를 완료하면 수령 정보가 확정됩니다.
            </p>
          )}
          {latestPayment?.status === "PAID" && latestReservation.fulfillment_method === "PICKUP" && (
            <>
              <p>매장에서 픽업 코드를 보여주세요.</p>
              <div className="pickup-code-block">
                <span>픽업 코드</span>
                <p className="pickup-code">{latestReservation.pickup_code}</p>
              </div>
            </>
          )}
          {latestPayment?.status === "PAID" && latestReservation.fulfillment_method === "QUICK_DELIVERY" && (
            <p className="message">퀵배달 요청이 접수되었습니다.</p>
          )}
          {latestPayment?.status === "PAID" && latestReservation.fulfillment_method === "PARCEL_DELIVERY" && (
            <p className="message">택배 배송 요청이 접수되었습니다.</p>
          )}
          <div className="detail-grid">
            <div>
              <span>수령 방법</span>
              <strong>{fulfillmentMethodLabel(latestReservation?.fulfillment_method)}</strong>
            </div>
            <div>
              <span>매장</span>
              <strong>{latestReservedProduct?.store_name || latestReservation?.store_name || "-"}</strong>
            </div>
            <div>
              <span>예약 수량</span>
              <strong>{latestReservation?.quantity ?? "-"}</strong>
            </div>
            <div>
              <span>상품 금액</span>
              <strong>{latestReservation ? formatMoney(latestReservation.product_amount) : "-"}</strong>
            </div>
            <div>
              <span>배송비</span>
              <strong>{latestReservation ? formatMoney(latestReservation.delivery_fee) : "0원"}</strong>
            </div>
            <div>
              <span>총 고객 결제금액</span>
              <strong>{latestReservation ? formatMoney(latestReservation.total_price) : "-"}</strong>
            </div>
            <div>
              <span>픽업 마감</span>
              <strong>
                {latestReservation ? new Date(latestReservation.pickup_deadline).toLocaleString() : "-"}
              </strong>
            </div>
          </div>
          {latestReservation.fulfillment_method !== "PICKUP" && (
            <div className="detail-grid">
              <div>
                <span>받는 사람</span>
                <strong>{latestReservation?.recipient_name || "-"}</strong>
              </div>
              <div>
                <span>연락처</span>
                <strong>{latestReservation?.recipient_phone || "-"}</strong>
              </div>
              <div>
                <span>주소</span>
                <strong>{latestReservation?.delivery_address || "-"}</strong>
              </div>
              <div>
                <span>배송 상태</span>
                <strong>{latestReservation?.delivery_status || "-"}</strong>
              </div>
              <div>
                <span>배송 요청사항</span>
                <strong>{latestReservation?.delivery_request_memo || "-"}</strong>
              </div>
            </div>
          )}
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
