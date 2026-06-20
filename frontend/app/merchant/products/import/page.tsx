"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { Badge, EmptyState, PageHeader, StatCard } from "@/components/UI";
import { buildApiUrl, friendlyErrorMessage, getToken } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { ProductCsvImportResult, Store } from "@/lib/types";

const sampleCsv = [
  "name,description,original_price,discount_price,stock_quantity,sale_starts_at,sale_ends_at,pickup_available,quick_delivery_available,parcel_delivery_available,quick_delivery_fee,parcel_delivery_fee",
  "식빵 마감 세트,오늘 남은 식빵 세트,12000,7900,5,2026-06-20 18:00,2026-06-20 21:00,true,false,false,0,0",
  "크루아상 세트,버터 크루아상 묶음,15000,9900,3,2026-06-20 18:00,2026-06-20 21:00,true,true,false,3000,0",
].join("\n");

function resultTitle(result: ProductCsvImportResult) {
  if (result.failed_count === 0) {
    return "CSV 검증이 완료되었습니다.";
  }
  return `${result.failed_count}개 행을 확인해 주세요.`;
}

async function parseUploadResponse(response: Response): Promise<ProductCsvImportResult> {
  const text = await response.text();
  let data: ProductCsvImportResult | { detail?: unknown };
  try {
    data = JSON.parse(text) as ProductCsvImportResult | { detail?: unknown };
  } catch {
    throw new Error(text || "CSV 업로드에 실패했습니다.");
  }

  if (!response.ok) {
    const detail = "detail" in data ? data.detail : null;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail || data));
  }

  return data as ProductCsvImportResult;
}

export default function MerchantProductCsvImportPage() {
  const guard = useRoleGuard("MERCHANT");
  const [stores, setStores] = useState<Store[]>([]);
  const [storeId, setStoreId] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<ProductCsvImportResult | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  async function loadStores() {
    setMessage("");
    setIsError(false);
    try {
      const token = getToken();
      if (!token) throw new Error("로그인이 필요합니다.");
      const response = await fetch(buildApiUrl("/api/v1/stores/me"), {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error(await response.text());
      const data = (await response.json()) as Store[];
      setStores(data);
      if (data.length > 0) {
        setStoreId(data[0].id);
      }
      setMessage(data.length > 0 ? "매장 목록을 불러왔습니다." : "매장이 없습니다. 먼저 매장을 등록하세요.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  useEffect(() => {
    if (!guard.allowed) return;
    const timer = window.setTimeout(() => {
      void loadStores();
    }, 0);
    return () => window.clearTimeout(timer);
  }, [guard.allowed]);

  function downloadSampleCsv() {
    const blob = new Blob([`\uFEFF${sampleCsv}`], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "breadgo-product-import-sample.csv";
    anchor.click();
    URL.revokeObjectURL(url);
  }

  async function uploadCsv(preview: boolean) {
    setMessage("");
    setIsError(false);
    setResult(null);

    if (!storeId) {
      setIsError(true);
      setMessage("상품을 등록할 매장을 선택하세요.");
      return;
    }
    if (!file) {
      setIsError(true);
      setMessage("업로드할 CSV 파일을 선택하세요.");
      return;
    }

    const token = getToken();
    if (!token) {
      setIsError(true);
      setMessage("로그인이 필요합니다.");
      return;
    }

    const formData = new FormData();
    formData.append("store_id", storeId);
    formData.append("file", file);
    setLoading(true);

    try {
      const endpoint = preview
        ? "/api/v1/merchant/products/import-csv/preview"
        : "/api/v1/merchant/products/import-csv";
      const response = await fetch(buildApiUrl(endpoint), {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      const uploadResult = await parseUploadResponse(response);
      setResult(uploadResult);
      setMessage(
        preview
          ? resultTitle(uploadResult)
          : `${uploadResult.success_count}개 상품을 HIDDEN 상태로 등록했습니다.`,
      );
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void uploadCsv(false);
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
        title="CSV 상품 일괄 등록"
        description="POS 연동 전 단계로, 엑셀에서 저장한 CSV 파일로 마감 상품을 한 번에 등록합니다."
        actions={
          <div className="actions">
            <button type="button" className="secondary" onClick={downloadSampleCsv}>
              샘플 CSV 다운로드
            </button>
            <Link className="button-link secondary" href="/merchant/products">
              상품관리로 이동
            </Link>
          </div>
        }
      />

      <div className="message">
        <Badge tone="warning">Pro 고급 기능</Badge>
        <br />
        실제 POS API 연동 전, CSV로 상품명/가격/재고/판매 시간을 일괄 등록하는 MVP 기능입니다.
        업로드된 상품은 기본적으로 숨김 상태로 생성되며, 상품관리에서 확인 후 판매 상태로 변경할 수 있습니다.
      </div>
      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      <form className="panel form-grid" onSubmit={handleSubmit}>
        <h2>CSV 업로드</h2>
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
        <label>
          CSV 파일
          <input
            type="file"
            accept=".csv,text/csv"
            onChange={(event) => setFile(event.target.files?.[0] || null)}
            required
          />
          <span className="field-help">UTF-8 또는 엑셀 CSV(cp949) 파일을 지원합니다.</span>
        </label>
        <div className="actions">
          <button type="button" className="secondary" onClick={() => uploadCsv(true)} disabled={loading}>
            {loading ? "검증 중" : "업로드 전 검증"}
          </button>
          <button type="submit" disabled={loading}>
            {loading ? "등록 중" : "CSV 일괄 등록"}
          </button>
        </div>
      </form>

      <section className="panel">
        <div className="card-title-row">
          <div>
            <p className="eyebrow">CSV 컬럼</p>
            <h2>필수 컬럼과 예시</h2>
          </div>
          <Badge tone="muted">개인정보 입력 금지</Badge>
        </div>
        <pre className="code-block">{sampleCsv}</pre>
      </section>

      {result && (
        <section className="panel">
          <div className="card-title-row">
            <div>
              <p className="eyebrow">업로드 결과</p>
              <h2>{resultTitle(result)}</h2>
            </div>
            <Badge tone={result.failed_count > 0 ? "warning" : "success"}>
              성공 {result.success_count} / 실패 {result.failed_count}
            </Badge>
          </div>

          <div className="summary-grid">
            <StatCard label="전체 행" value={`${result.total_rows}개`} />
            <StatCard label="성공" value={`${result.success_count}개`} />
            <StatCard label="실패" value={`${result.failed_count}개`} />
            <StatCard label="생성된 상품" value={`${result.created_product_ids.length}개`} />
          </div>

          {result.errors.length === 0 ? (
            <EmptyState title="실패한 행이 없습니다." description="등록된 상품은 상품관리에서 판매 상태로 변경할 수 있습니다." />
          ) : (
            <div className="list">
              {result.errors.map((error) => (
                <article className="item" key={`${error.row_number}-${error.field}-${error.message}`}>
                  <div className="card-title-row">
                    <h3>{error.row_number}행</h3>
                    <Badge tone="danger">{error.field}</Badge>
                  </div>
                  <p>{error.message}</p>
                </article>
              ))}
            </div>
          )}

          {result.created_product_ids.length > 0 && (
            <div className="actions">
              <Link className="button-link" href="/merchant/products">
                상품관리에서 확인
              </Link>
            </div>
          )}
        </section>
      )}
    </section>
  );
}
