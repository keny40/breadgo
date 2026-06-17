"use client";

/* eslint-disable @next/next/no-img-element */

import { FormEvent, useEffect, useState } from "react";
import { EmptyState, PageHeader, StatusBadge } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import type { Product, Store } from "@/lib/types";

function formatMoney(value: string) {
  return `${Number(value).toLocaleString()}원`;
}

function ProductImage({ imageUrl, name }: { imageUrl: string | null | undefined; name: string }) {
  if (!imageUrl) {
    return <div className="product-image-placeholder">이미지 없음</div>;
  }

  return <img className="product-image" src={imageUrl} alt={`${name} 대표 이미지`} loading="lazy" />;
}

export default function MerchantProductsPage() {
  const [stores, setStores] = useState<Store[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [storeId, setStoreId] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [originalPrice, setOriginalPrice] = useState("");
  const [discountPrice, setDiscountPrice] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [pickupStartTime, setPickupStartTime] = useState("");
  const [pickupEndTime, setPickupEndTime] = useState("");
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadInitialData() {
      try {
        const [storeData, productData] = await Promise.all([
          apiFetch<Store[]>("/api/v1/stores/me", {}, true),
          apiFetch<Product[]>("/api/v1/products/me", {}, true),
        ]);
        if (cancelled) {
          return;
        }
        setStores(storeData);
        setProducts(productData);
        if (storeData.length > 0) {
          setStoreId(storeData[0].id);
          setMessage(`${productData.length}개 상품을 불러왔습니다.`);
        } else {
          setMessage("매장이 없습니다. 먼저 매장을 등록하세요.");
        }
      } catch (error) {
        if (cancelled) {
          return;
        }
        setIsError(true);
        setMessage(friendlyErrorMessage(error));
      }
    }

    void loadInitialData();
    return () => {
      cancelled = true;
    };
  }, []);

  async function loadStores() {
    setMessage("");
    setIsError(false);

    try {
      const data = await apiFetch<Store[]>("/api/v1/stores/me", {}, true);
      setStores(data);
      if (!storeId && data.length > 0) {
        setStoreId(data[0].id);
      }
      if (data.length === 0) {
        setMessage("매장이 없습니다. 먼저 매장을 등록하세요.");
      }
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  async function loadProducts() {
    setMessage("");
    setIsError(false);

    try {
      const data = await apiFetch<Product[]>("/api/v1/products/me", {}, true);
      setProducts(data);
      setMessage(`${data.length}개 상품을 불러왔습니다.`);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  async function createProduct(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    setIsError(false);

    try {
      await apiFetch<Product>(
        "/api/v1/products",
        {
          method: "POST",
          body: JSON.stringify({
            store_id: storeId,
            name,
            description: description || null,
            image_url: imageUrl || null,
            original_price: originalPrice,
            discount_price: discountPrice,
            quantity,
            pickup_start_time: new Date(pickupStartTime).toISOString(),
            pickup_end_time: new Date(pickupEndTime).toISOString(),
            status: "ACTIVE",
          }),
        },
        true,
      );
      setMessage("상품이 등록되었습니다.");
      await loadProducts();
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  return (
    <section className="section">
      <PageHeader
        title="상품 관리"
        description="매장을 선택하고 오늘 판매할 마감 할인 상품을 등록합니다."
        actions={
          <button type="button" onClick={loadProducts}>
            상품 불러오기
          </button>
        }
      />
      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      <form className="panel form-grid" onSubmit={createProduct}>
        <h2>상품 등록</h2>
        <div className="select-row">
          <label>
            매장 선택
            <select value={storeId} onChange={(event) => setStoreId(event.target.value)} required>
              <option value="">매장을 선택하세요</option>
              {stores.map((store) => (
                <option key={store.id} value={store.id}>
                  {store.name} - {[store.sido, store.sigungu, store.dong].filter(Boolean).join(" ") || store.address}
                </option>
              ))}
            </select>
          </label>
          <button type="button" className="secondary" onClick={loadStores}>
            매장 새로고침
          </button>
        </div>
        <label>
          상품명
          <input value={name} onChange={(event) => setName(event.target.value)} required />
        </label>
        <label>
          상품 설명
          <textarea value={description} onChange={(event) => setDescription(event.target.value)} />
        </label>
        <label>
          대표 이미지 URL
          <input
            type="url"
            value={imageUrl}
            onChange={(event) => setImageUrl(event.target.value)}
            placeholder="https://example.com/product.jpg"
          />
        </label>
        <div className="two-column">
          <label>
            정가
            <input
              type="number"
              min="1"
              step="0.01"
              value={originalPrice}
              onChange={(event) => setOriginalPrice(event.target.value)}
              required
            />
          </label>
          <label>
            할인가
            <input
              type="number"
              min="1"
              step="0.01"
              value={discountPrice}
              onChange={(event) => setDiscountPrice(event.target.value)}
              required
            />
          </label>
        </div>
        <label>
          수량
          <input
            type="number"
            min={0}
            value={quantity}
            onChange={(event) => setQuantity(Number(event.target.value))}
            required
          />
        </label>
        <div className="two-column">
          <label>
            픽업 시작
            <input
              type="datetime-local"
              value={pickupStartTime}
              onChange={(event) => setPickupStartTime(event.target.value)}
              required
            />
          </label>
          <label>
            픽업 종료
            <input
              type="datetime-local"
              value={pickupEndTime}
              onChange={(event) => setPickupEndTime(event.target.value)}
              required
            />
          </label>
        </div>
        <button type="submit">상품 등록</button>
      </form>

      <div className="list">
        {products.length === 0 && !isError && (
          <EmptyState title="상품이 없습니다." description="매장을 선택한 뒤 첫 마감 할인 상품을 등록하세요." />
        )}
        {products.map((product) => (
          <article className="item" key={product.id}>
            <ProductImage imageUrl={product.image_url} name={product.name} />
            <div className="card-title-row">
              <h3>{product.name}</h3>
              <StatusBadge status={product.status} />
            </div>
            <div className="price-row">
              <span className="original-price">{formatMoney(product.original_price)}</span>
              <span className="discount-price">{formatMoney(product.discount_price)}</span>
            </div>
            <div className="meta">
              <span>ID {product.id}</span>
              <span>Store {product.store_id}</span>
              <span>수량 {product.quantity}</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
