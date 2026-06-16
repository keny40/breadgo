"use client";

import { FormEvent, useEffect, useState } from "react";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import type { Product, Store } from "@/lib/types";

export default function MerchantProductsPage() {
  const [stores, setStores] = useState<Store[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [storeId, setStoreId] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
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
      <h1>상품 관리</h1>
      <div className="actions">
        <button type="button" onClick={loadProducts}>
          상품 불러오기
        </button>
      </div>
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
          Name
          <input value={name} onChange={(event) => setName(event.target.value)} required />
        </label>
        <label>
          Description
          <textarea value={description} onChange={(event) => setDescription(event.target.value)} />
        </label>
        <div className="two-column">
          <label>
            Original price
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
            Discount price
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
          Quantity
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
            Pickup start
            <input
              type="datetime-local"
              value={pickupStartTime}
              onChange={(event) => setPickupStartTime(event.target.value)}
              required
            />
          </label>
          <label>
            Pickup end
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
        {products.length === 0 && !isError && <div className="empty-state">상품이 없습니다.</div>}
        {products.map((product) => (
          <article className="item" key={product.id}>
            <h3>{product.name}</h3>
            <div className="meta">
              <span>ID {product.id}</span>
              <span>Store {product.store_id}</span>
              <span>할인가 {product.discount_price}</span>
              <span>수량 {product.quantity}</span>
              <span>상태 {product.status}</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
