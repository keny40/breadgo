"use client";

/* eslint-disable @next/next/no-img-element */

import { FormEvent, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { EmptyState, PageHeader, StatusBadge } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { Product, Store } from "@/lib/types";

type ProductFormState = {
  name: string;
  description: string;
  imageUrl: string;
  originalPrice: string;
  discountPrice: string;
  quantity: number;
  pickupStartTime: string;
  pickupEndTime: string;
  status: string;
  allowPickup: boolean;
  allowQuickDelivery: boolean;
  allowParcelDelivery: boolean;
  quickDeliveryFee: string;
  parcelDeliveryFee: string;
};

const emptyForm: ProductFormState = {
  name: "",
  description: "",
  imageUrl: "",
  originalPrice: "",
  discountPrice: "",
  quantity: 1,
  pickupStartTime: "",
  pickupEndTime: "",
  status: "ACTIVE",
  allowPickup: true,
  allowQuickDelivery: false,
  allowParcelDelivery: false,
  quickDeliveryFee: "0",
  parcelDeliveryFee: "0",
};

function formatMoney(value: string) {
  return `${Number(value).toLocaleString()}원`;
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString();
}

function toDateTimeLocal(value: string) {
  const date = new Date(value);
  const offsetMs = date.getTimezoneOffset() * 60 * 1000;
  return new Date(date.getTime() - offsetMs).toISOString().slice(0, 16);
}

function dateTimeLocalFromDate(date: Date) {
  const offsetMs = date.getTimezoneOffset() * 60 * 1000;
  return new Date(date.getTime() - offsetMs).toISOString().slice(0, 16);
}

function defaultRelistStart() {
  const date = new Date();
  date.setMinutes(0, 0, 0);
  date.setHours(Math.max(date.getHours() + 1, 18));
  return dateTimeLocalFromDate(date);
}

function defaultRelistEnd(startValue: string) {
  const date = new Date(startValue);
  date.setHours(date.getHours() + 3);
  return dateTimeLocalFromDate(date);
}

function ProductImage({ imageUrl, name }: { imageUrl: string | null | undefined; name: string }) {
  if (!imageUrl) {
    return <div className="product-image-placeholder">이미지 없음</div>;
  }

  return <img className="product-image" src={imageUrl} alt={`${name} 대표 이미지`} loading="lazy" />;
}

export default function MerchantProductsPage() {
  const guard = useRoleGuard("MERCHANT");
  const [stores, setStores] = useState<Store[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [storeId, setStoreId] = useState("");
  const [createForm, setCreateForm] = useState<ProductFormState>(emptyForm);
  const [createImageFile, setCreateImageFile] = useState<File | null>(null);
  const [editingProductId, setEditingProductId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<ProductFormState>(emptyForm);
  const [editImageFile, setEditImageFile] = useState<File | null>(null);
  const [relistingProductId, setRelistingProductId] = useState<string | null>(null);
  const [relistStockQuantity, setRelistStockQuantity] = useState(1);
  const [relistSaleStart, setRelistSaleStart] = useState("");
  const [relistSaleEnd, setRelistSaleEnd] = useState("");
  const [relistVisible, setRelistVisible] = useState(true);
  const [relistNameSuffix, setRelistNameSuffix] = useState("오늘");
  const [uploadingImageTarget, setUploadingImageTarget] = useState<"create" | "edit" | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);

  const storeById = useMemo(() => {
    return stores.reduce<Record<string, Store>>((acc, store) => {
      acc[store.id] = store;
      return acc;
    }, {});
  }, [stores]);

  useEffect(() => {
    if (!guard.allowed) {
      return;
    }

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
  }, [guard.allowed]);

  function updateCreateForm(patch: Partial<ProductFormState>) {
    setCreateForm((current) => ({ ...current, ...patch }));
  }

  function updateEditForm(patch: Partial<ProductFormState>) {
    setEditForm((current) => ({ ...current, ...patch }));
  }

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

  async function loadProducts(successMessage = "상품 목록을 새로고침했습니다.") {
    setMessage("");
    setIsError(false);

    try {
      const data = await apiFetch<Product[]>("/api/v1/products/me", {}, true);
      setProducts(data);
      setMessage(successMessage);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  async function uploadImage(file: File, target: "create" | "edit") {
    setMessage("");
    setIsError(false);

    if (!file.type.startsWith("image/")) {
      setIsError(true);
      setMessage("이미지 파일만 업로드할 수 있습니다.");
      return;
    }

    if (file.size > 3 * 1024 * 1024) {
      setIsError(true);
      setMessage("이미지 용량은 3MB 이하만 가능합니다.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    setUploadingImageTarget(target);

    try {
      const response = await fetch("/api/upload/product-image", {
        method: "POST",
        body: formData,
      });
      const data = (await response.json()) as { url?: string; detail?: string };

      if (!response.ok || !data.url) {
        throw new Error(data.detail || "이미지 업로드에 실패했습니다.");
      }

      if (target === "create") {
        updateCreateForm({ imageUrl: data.url });
      } else {
        updateEditForm({ imageUrl: data.url });
      }
      setMessage("이미지 업로드가 완료되었습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(error instanceof Error ? error.message : "이미지 업로드에 실패했습니다.");
    } finally {
      setUploadingImageTarget(null);
    }
  }

  async function uploadCreateImage() {
    if (!createImageFile) {
      setIsError(true);
      setMessage("업로드할 이미지를 선택하세요.");
      return;
    }
    await uploadImage(createImageFile, "create");
  }

  async function uploadEditImage() {
    if (!editImageFile) {
      setIsError(true);
      setMessage("업로드할 이미지를 선택하세요.");
      return;
    }
    await uploadImage(editImageFile, "edit");
  }

  function productPayload(form: ProductFormState) {
    return {
      name: form.name,
      description: form.description || null,
      image_url: form.imageUrl || null,
      original_price: form.originalPrice,
      discount_price: form.discountPrice,
      quantity: form.quantity,
      pickup_start_time: new Date(form.pickupStartTime).toISOString(),
      pickup_end_time: new Date(form.pickupEndTime).toISOString(),
      status: form.status,
      allow_pickup: form.allowPickup,
      allow_quick_delivery: form.allowQuickDelivery,
      allow_parcel_delivery: form.allowParcelDelivery,
      quick_delivery_fee: form.quickDeliveryFee || "0",
      parcel_delivery_fee: form.parcelDeliveryFee || "0",
    };
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
            ...productPayload(createForm),
          }),
        },
        true,
      );
      setCreateForm(emptyForm);
      setCreateImageFile(null);
      await loadProducts("상품이 등록되었습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  function startEdit(product: Product) {
    setEditingProductId(product.id);
    setEditImageFile(null);
    setEditForm({
      name: product.name,
      description: product.description || "",
      imageUrl: product.image_url || "",
      originalPrice: product.original_price,
      discountPrice: product.discount_price,
      quantity: product.quantity,
      pickupStartTime: toDateTimeLocal(product.pickup_start_time),
      pickupEndTime: toDateTimeLocal(product.pickup_end_time),
      status: product.status,
      allowPickup: product.allow_pickup,
      allowQuickDelivery: product.allow_quick_delivery,
      allowParcelDelivery: product.allow_parcel_delivery,
      quickDeliveryFee: product.quick_delivery_fee,
      parcelDeliveryFee: product.parcel_delivery_fee,
    });
    setMessage(`${product.name} 상품을 편집합니다.`);
    setIsError(false);
  }

  function cancelEdit() {
    setEditingProductId(null);
    setEditForm(emptyForm);
    setEditImageFile(null);
  }

  function startRelist(product: Product) {
    const saleStart = defaultRelistStart();
    setRelistingProductId(product.id);
    setRelistStockQuantity(Math.max(product.quantity, 1));
    setRelistSaleStart(saleStart);
    setRelistSaleEnd(defaultRelistEnd(saleStart));
    setRelistVisible(true);
    setRelistNameSuffix("오늘");
    setMessage(`${product.name} 상품을 그대로 다시 올릴 준비를 합니다.`);
    setIsError(false);
  }

  function cancelRelist() {
    setRelistingProductId(null);
    setRelistStockQuantity(1);
    setRelistSaleStart("");
    setRelistSaleEnd("");
    setRelistVisible(true);
    setRelistNameSuffix("오늘");
  }

  async function updateProduct(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!editingProductId) {
      return;
    }
    setMessage("");
    setIsError(false);

    try {
      await apiFetch<Product>(
        `/api/v1/products/${editingProductId}`,
        {
          method: "PATCH",
          body: JSON.stringify(productPayload(editForm)),
        },
        true,
      );
      cancelEdit();
      await loadProducts("상품 정보가 수정되었습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  async function duplicateProduct(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!relistingProductId) {
      return;
    }
    setMessage("");
    setIsError(false);

    try {
      await apiFetch<Product>(
        `/api/v1/merchant/products/${relistingProductId}/duplicate`,
        {
          method: "POST",
          body: JSON.stringify({
            stock_quantity: relistStockQuantity,
            sale_starts_at: relistSaleStart ? new Date(relistSaleStart).toISOString() : null,
            sale_ends_at: relistSaleEnd ? new Date(relistSaleEnd).toISOString() : null,
            is_visible: relistVisible,
            name_suffix: relistNameSuffix || null,
          }),
        },
        true,
      );
      cancelRelist();
      await loadProducts("기존 상품 정보로 오늘 판매 상품을 다시 올렸습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  async function hideProduct(product: Product) {
    if (!window.confirm(`${product.name} 상품을 숨김 처리할까요? 고객 상품 목록에서 보이지 않게 됩니다.`)) {
      return;
    }
    setMessage("");
    setIsError(false);

    try {
      await apiFetch<Product>(`/api/v1/products/${product.id}`, { method: "DELETE" }, true);
      await loadProducts("상품이 숨김 처리되었습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  async function unhideProduct(product: Product) {
    setMessage("");
    setIsError(false);

    try {
      await apiFetch<Product>(
        `/api/v1/products/${product.id}`,
        {
          method: "PATCH",
          body: JSON.stringify({ status: "ACTIVE" }),
        },
        true,
      );
      await loadProducts("상품을 다시 판매 상태로 변경했습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  if (!guard.allowed) {
    return (
      <section className="section">
        <EmptyState title={guard.message || "권한을 확인하고 있습니다."} />
      </section>
    );
  }

  return (
    <section className="section">
      <PageHeader
        title="상품 관리"
        description="상품 등록, 재고 수정, 이미지 변경, 판매 상태 관리를 한 화면에서 처리합니다."
        actions={
          <div className="actions">
            <button type="button" onClick={() => loadProducts()}>
              상품 불러오기
            </button>
            <Link className="button-link secondary" href="/merchant/products/import">
              CSV 일괄 등록
            </Link>
            <Link className="button-link secondary" href="/merchant/orders">
              예약/주문 확인
            </Link>
            <Link className="button-link secondary" href="/merchant/pro/inventory-ledger">
              재고 이력
            </Link>
          </div>
        }
      />
      <div className="message">
        <strong>어제 남은 빵 그대로 올리기</strong>
        <br />
        반복 상품 등록은 기존 상품 정보는 유지하고 오늘 재고와 마감 시간만 바꿔 빠르게 재등록합니다.
        CSV 일괄 등록은 POS 연동 전 단계의 BreadGo Pro 고급 기능입니다.
        실제 POS API, 배송 provider, 외부 알림 발송은 아직 연결하지 않습니다.
      </div>
      <div className="account-grid">
        <article className="account-card">
          <div className="card-title-row">
            <h3>상품 등록</h3>
            <span className="badge success">Create</span>
          </div>
          <p>상품명, 가격, 할인 가격, 재고, 판매 시간을 입력하면 고객 상품 목록에 노출됩니다.</p>
        </article>
        <article className="account-card">
          <div className="card-title-row">
            <h3>재고 확인</h3>
            <span className="badge warning">Stock</span>
          </div>
          <p>예약/취소/POS mock/CSV import로 바뀐 재고 흐름은 BreadGo Pro 재고 이력에서 추적합니다.</p>
        </article>
        <article className="account-card">
          <div className="card-title-row">
            <h3>예약 연결</h3>
            <span className="badge muted">Orders</span>
          </div>
          <p>상품 등록 후 결제 완료 예약은 주문 관리와 픽업 확인 화면에서 처리합니다.</p>
        </article>
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
        <ProductFields
          form={createForm}
          onChange={updateCreateForm}
          imageFile={createImageFile}
          onImageFileChange={setCreateImageFile}
          onUploadImage={uploadCreateImage}
          uploading={uploadingImageTarget === "create"}
          imageAltName={createForm.name || "상품"}
          showStatus={false}
        />
        <button type="submit">상품 등록</button>
      </form>

      <div className="list">
        {products.length === 0 && !isError && (
          <EmptyState
            title="등록된 상품이 없습니다. 오늘 판매할 마감 할인 상품을 등록해 보세요."
            description="상품을 등록하면 고객 상품 목록과 가맹점 관리 화면에 표시됩니다."
          />
        )}
        {products.map((product) => {
          const store = storeById[product.store_id];
          const isEditing = editingProductId === product.id;

          return (
            <article className="item product-management-card" key={product.id}>
              <ProductImage imageUrl={product.image_url} name={product.name} />
              <div className="card-title-row">
                <div>
                  <h3>{product.name}</h3>
                  <p>{store?.name || "매장 정보 없음"}</p>
                </div>
                <StatusBadge status={product.status} />
              </div>
              <div className="price-row">
                <span className="original-price">{formatMoney(product.original_price)}</span>
                <span className="discount-price">{formatMoney(product.discount_price)}</span>
              </div>
              <div className="meta">
                <span>
                  재고 <strong>{product.quantity}</strong>
                </span>
                <span>픽업 {product.allow_pickup ? "가능" : "불가"}</span>
                <span>퀵 {product.allow_quick_delivery ? `${formatMoney(product.quick_delivery_fee)}` : "불가"}</span>
                <span>택배 {product.allow_parcel_delivery ? `${formatMoney(product.parcel_delivery_fee)}` : "불가"}</span>
                <span>픽업 {formatDateTime(product.pickup_start_time)}</span>
                <span>- {formatDateTime(product.pickup_end_time)}</span>
              </div>
              <div className="actions">
                <button type="button" onClick={() => startRelist(product)}>
                  그대로 다시 올리기
                </button>
                <button type="button" className="secondary" onClick={() => startEdit(product)}>
                  편집
                </button>
                <Link className="button-link secondary" href="/merchant/pro/inventory-ledger">
                  재고 이력 보기
                </Link>
                {product.status === "HIDDEN" ? (
                  <button type="button" onClick={() => unhideProduct(product)}>
                    다시 판매
                  </button>
                ) : (
                  <button type="button" className="danger" onClick={() => hideProduct(product)}>
                    숨김 처리
                  </button>
                )}
              </div>

              {relistingProductId === product.id && (
                <form className="edit-product-form form-grid" onSubmit={duplicateProduct}>
                  <h3>어제 남은 빵 그대로 올리기</h3>
                  <p className="field-help">
                    기존 상품 정보는 유지하고 오늘 재고만 입력하세요. 마감 시간만 바꿔 빠르게 재등록할 수 있습니다.
                  </p>
                  <div className="two-column">
                    <label>
                      오늘 재고 수량
                      <input
                        type="number"
                        min={0}
                        value={relistStockQuantity}
                        onChange={(event) => setRelistStockQuantity(Number(event.target.value))}
                        required
                      />
                    </label>
                    <label>
                      이름 뒤에 붙일 문구
                      <input
                        value={relistNameSuffix}
                        onChange={(event) => setRelistNameSuffix(event.target.value)}
                        placeholder="예) 오늘, 금요일, 저녁"
                      />
                    </label>
                  </div>
                  <div className="two-column">
                    <label>
                      판매 시작 시간
                      <input
                        type="datetime-local"
                        value={relistSaleStart}
                        onChange={(event) => {
                          setRelistSaleStart(event.target.value);
                          if (!relistSaleEnd) {
                            setRelistSaleEnd(defaultRelistEnd(event.target.value));
                          }
                        }}
                      />
                    </label>
                    <label>
                      판매 종료 시간
                      <input
                        type="datetime-local"
                        value={relistSaleEnd}
                        onChange={(event) => setRelistSaleEnd(event.target.value)}
                      />
                    </label>
                  </div>
                  <label>
                    <input
                      type="checkbox"
                      checked={relistVisible}
                      onChange={(event) => setRelistVisible(event.target.checked)}
                    />
                    바로 고객에게 노출하기
                  </label>
                  <div className="actions">
                    <button type="submit">반복 상품 등록</button>
                    <button type="button" className="secondary" onClick={cancelRelist}>
                      취소
                    </button>
                  </div>
                </form>
              )}

              {isEditing && (
                <form className="edit-product-form form-grid" onSubmit={updateProduct}>
                  <h3>상품 수정</h3>
                  <ProductFields
                    form={editForm}
                    onChange={updateEditForm}
                    imageFile={editImageFile}
                    onImageFileChange={setEditImageFile}
                    onUploadImage={uploadEditImage}
                    uploading={uploadingImageTarget === "edit"}
                    imageAltName={editForm.name || product.name}
                    showStatus
                  />
                  <div className="actions">
                    <button type="submit">수정 저장</button>
                    <button type="button" className="secondary" onClick={cancelEdit}>
                      취소
                    </button>
                  </div>
                </form>
              )}
            </article>
          );
        })}
      </div>
    </section>
  );
}

function ProductFields({
  form,
  onChange,
  imageFile,
  onImageFileChange,
  onUploadImage,
  uploading,
  imageAltName,
  showStatus,
}: {
  form: ProductFormState;
  onChange: (patch: Partial<ProductFormState>) => void;
  imageFile: File | null;
  onImageFileChange: (file: File | null) => void;
  onUploadImage: () => void;
  uploading: boolean;
  imageAltName: string;
  showStatus: boolean;
}) {
  return (
    <>
      <label>
        상품명
        <input value={form.name} onChange={(event) => onChange({ name: event.target.value })} required />
      </label>
      <label>
        상품 설명
        <textarea value={form.description} onChange={(event) => onChange({ description: event.target.value })} />
      </label>
      <label>
        이미지 URL
        <input
          type="url"
          value={form.imageUrl}
          onChange={(event) => onChange({ imageUrl: event.target.value })}
          placeholder="https://example.com/product.jpg"
        />
        <span className="field-help">직접 URL을 입력하거나 파일을 업로드할 수 있습니다.</span>
      </label>
      <div className="upload-box form-grid">
        <h3>대표 이미지 업로드</h3>
        <label>
          이미지 파일
          <input
            type="file"
            accept="image/*"
            onChange={(event) => onImageFileChange(event.target.files?.[0] || null)}
          />
        </label>
        <div className="actions">
          <button type="button" className="secondary" onClick={onUploadImage} disabled={uploading || !imageFile}>
            {uploading ? "업로드 중" : "이미지 업로드"}
          </button>
        </div>
        <ProductImage imageUrl={form.imageUrl} name={imageAltName} />
      </div>
      <div className="two-column">
        <label>
          정가
          <input
            type="number"
            min="1"
            step="0.01"
            value={form.originalPrice}
            onChange={(event) => onChange({ originalPrice: event.target.value })}
            required
          />
        </label>
        <label>
          할인가
          <input
            type="number"
            min="1"
            step="0.01"
            value={form.discountPrice}
            onChange={(event) => onChange({ discountPrice: event.target.value })}
            required
          />
        </label>
      </div>
      <label>
        수량
        <input
          type="number"
          min={0}
          value={form.quantity}
          onChange={(event) => onChange({ quantity: Number(event.target.value) })}
          required
        />
      </label>
      <div className="two-column">
        <label>
          픽업 시작
          <input
            type="datetime-local"
            value={form.pickupStartTime}
            onChange={(event) => onChange({ pickupStartTime: event.target.value })}
            required
          />
        </label>
        <label>
          픽업 종료
          <input
            type="datetime-local"
            value={form.pickupEndTime}
            onChange={(event) => onChange({ pickupEndTime: event.target.value })}
            required
          />
        </label>
      </div>
      <div className="payment-box">
        <h3>수령 가능 방식</h3>
        <p className="field-help">신선식품은 매장 직접 픽업이 기본입니다. 택배 배송은 배송 가능한 상품에 한해 선택할 수 있습니다.</p>
        <label>
          <input
            type="checkbox"
            checked={form.allowPickup}
            onChange={(event) => onChange({ allowPickup: event.target.checked })}
          />
          매장 직접 픽업 가능
        </label>
        <label>
          <input
            type="checkbox"
            checked={form.allowQuickDelivery}
            onChange={(event) => onChange({ allowQuickDelivery: event.target.checked })}
          />
          퀵배달 가능
        </label>
        {form.allowQuickDelivery && (
          <label>
            퀵배달비
            <input
              type="number"
              min={0}
              step="100"
              value={form.quickDeliveryFee}
              onChange={(event) => onChange({ quickDeliveryFee: event.target.value })}
            />
          </label>
        )}
        <label>
          <input
            type="checkbox"
            checked={form.allowParcelDelivery}
            onChange={(event) => onChange({ allowParcelDelivery: event.target.checked })}
          />
          택배 배송 가능
        </label>
        {form.allowParcelDelivery && (
          <label>
            택배 배송비
            <input
              type="number"
              min={0}
              step="100"
              value={form.parcelDeliveryFee}
              onChange={(event) => onChange({ parcelDeliveryFee: event.target.value })}
            />
          </label>
        )}
      </div>
      {showStatus && (
        <label>
          상태
          <select value={form.status} onChange={(event) => onChange({ status: event.target.value })}>
            <option value="ACTIVE">ACTIVE</option>
            <option value="SOLD_OUT">SOLD_OUT</option>
            <option value="HIDDEN">HIDDEN</option>
          </select>
        </label>
      )}
    </>
  );
}
