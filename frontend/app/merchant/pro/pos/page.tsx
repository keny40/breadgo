"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Badge, EmptyState, PageHeader, StatCard, StatusBadge } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { MockPosSyncResult, PosIntegration, PosSyncBatch, Store } from "@/lib/types";

const sampleItems = [
  {
    external_sku: "POS-BREAD-001",
    name: "POS 식빵 마감 세트",
    description: "Mock POS 동기화 테스트 상품",
    original_price: "12000",
    discount_price: "7900",
    stock_quantity: 5,
    sale_starts_at: "2026-06-20T18:00:00+09:00",
    sale_ends_at: "2026-06-20T21:00:00+09:00",
    pickup_available: true,
    quick_delivery_available: false,
    parcel_delivery_available: false,
  },
];

function formatDateTime(value: string | null) {
  if (!value) return "-";
  return new Date(value).toLocaleString("ko-KR", {
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function actionTone(action: string): "success" | "warning" | "danger" | "muted" {
  if (action === "CREATED" || action === "UPDATED") return "success";
  if (action === "SKIPPED") return "warning";
  if (action === "FAILED") return "danger";
  return "muted";
}

function reasonLabel(message: string | null) {
  if (!message) return "-";
  const labels: Record<string, string> = {
    EXISTING_PRODUCT_HAS_RESERVATIONS: "예약이 있는 기존 상품이라 건너뜀",
    EXISTING_PRODUCT_SKIPPED_BY_POLICY: "정책에 따라 기존 상품 건너뜀",
    EXISTING_PRODUCT_NOT_HIDDEN: "숨김 상품만 업데이트 정책으로 건너뜀",
    INVALID_PRICE: "가격 오류",
    MISSING_EXTERNAL_SKU: "external_sku 누락",
    GENERIC_POS_PROVIDER_NOT_CONFIGURED: "Generic POS provider 준비 중",
  };
  const code = message.split(":")[0];
  return labels[code] ? `${labels[code]} (${code})` : message;
}

export default function MerchantProPosPage() {
  const guard = useRoleGuard("MERCHANT");
  const [integration, setIntegration] = useState<PosIntegration | null>(null);
  const [stores, setStores] = useState<Store[]>([]);
  const [batches, setBatches] = useState<PosSyncBatch[]>([]);
  const [selectedBatch, setSelectedBatch] = useState<PosSyncBatch | null>(null);
  const [provider, setProvider] = useState("MOCK_POS");
  const [storeId, setStoreId] = useState("");
  const [externalStoreCode, setExternalStoreCode] = useState("");
  const [updateMode, setUpdateMode] = useState("UPDATE_IF_NO_RESERVATIONS");
  const [defaultProductStatus, setDefaultProductStatus] = useState("HIDDEN");
  const [mockJson, setMockJson] = useState(JSON.stringify(sampleItems, null, 2));
  const [syncResult, setSyncResult] = useState<MockPosSyncResult | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    if (!guard.allowed) return;
    void loadPage();
  }, [guard.allowed]);

  const latestBatch = useMemo(() => batches[0] || null, [batches]);

  async function loadPage() {
    setLoading(true);
    setMessage("");
    setIsError(false);
    try {
      const [integrationData, storesData, batchData] = await Promise.all([
        apiFetch<PosIntegration>("/api/v1/merchant/pro/pos-integration", {}, true),
        apiFetch<Store[]>("/api/v1/stores/me", {}, true),
        apiFetch<PosSyncBatch[]>("/api/v1/merchant/pro/pos-integration/sync-batches", {}, true),
      ]);
      setIntegration(integrationData);
      setStores(storesData);
      setBatches(batchData);
      setProvider(integrationData.provider);
      setStoreId(integrationData.store_id || "");
      setExternalStoreCode(integrationData.external_store_code || "");
      setSelectedBatch(batchData[0] || null);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  async function saveIntegration() {
    setLoading(true);
    setMessage("");
    setIsError(false);
    try {
      const result = await apiFetch<PosIntegration>(
        "/api/v1/merchant/pro/pos-integration",
        {
          method: "POST",
          body: JSON.stringify({
            provider,
            store_id: storeId || null,
            external_store_code: externalStoreCode || null,
          }),
        },
        true,
      );
      setIntegration(result);
      setProvider(result.provider);
      setStoreId(result.store_id || "");
      setExternalStoreCode(result.external_store_code || "");
      setMessage("POS 연동 설정을 저장했습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  async function runMockSync() {
    setSyncing(true);
    setMessage("");
    setIsError(false);
    setSyncResult(null);
    try {
      const parsed = JSON.parse(mockJson) as unknown;
      if (!Array.isArray(parsed)) {
        throw new Error("Mock item JSON은 배열 형식이어야 합니다.");
      }
      const result = await apiFetch<MockPosSyncResult>(
        "/api/v1/merchant/pro/pos-integration/mock-sync",
        {
          method: "POST",
          body: JSON.stringify({
            mock_items: parsed,
            update_mode: updateMode,
            default_product_status: defaultProductStatus,
          }),
        },
        true,
      );
      setSyncResult(result);
      setMessage("Mock POS 동기화를 완료했습니다.");
      await loadBatches(result.batch_id);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setSyncing(false);
    }
  }

  async function loadBatches(selectedBatchId?: string) {
    const batchData = await apiFetch<PosSyncBatch[]>("/api/v1/merchant/pro/pos-integration/sync-batches", {}, true);
    setBatches(batchData);
    const nextSelected = selectedBatchId
      ? batchData.find((batch) => batch.id === selectedBatchId)
      : batchData[0];
    setSelectedBatch(nextSelected || null);
  }

  async function loadBatchDetail(batchId: string) {
    try {
      const detail = await apiFetch<PosSyncBatch>(
        `/api/v1/merchant/pro/pos-integration/sync-batches/${batchId}`,
        {},
        true,
      );
      setSelectedBatch(detail);
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
        title="POS 연동 준비"
        description="실제 외부 POS API를 호출하지 않고, external_sku 기반 Mock 동기화로 POS/API 연동 구조를 검증합니다."
        actions={
          <button type="button" onClick={loadPage} disabled={loading}>
            {loading ? "불러오는 중" : "새로고침"}
          </button>
        }
      />

      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      <div className="pro-hero panel">
        <div>
          <p className="eyebrow">Enterprise 준비 기능</p>
          <h2>POS/API 연동 MVP</h2>
          <p>
            CSV 일괄 등록에서 만든 external_sku와 중복 업데이트 기준을 그대로 사용합니다. 현재는 Mock JSON을 BreadGo 내부에서만 처리하며,
            실제 POS API, API key, token, credential은 저장하거나 호출하지 않습니다.
          </p>
        </div>
        <div className="pro-score">
          <span>연동 상태</span>
          <strong>{integration?.status || "DISCONNECTED"}</strong>
          <small>최근 동기화: {formatDateTime(integration?.last_synced_at || null)}</small>
        </div>
      </div>

      <div className="summary-grid">
        <StatCard label="Provider" value={integration?.provider || "MOCK_POS"} />
        <StatCard label="최근 상태" value={integration?.last_sync_status || "-"} />
        <StatCard label="최근 생성" value={`${latestBatch?.created_count || 0}건`} />
        <StatCard label="최근 업데이트" value={`${latestBatch?.updated_count || 0}건`} />
        <StatCard label="외부 POS 호출" value="OFF" helper="Mock dry-run only" />
      </div>

      <div className="account-grid">
        <article className="account-card">
          <div className="card-title-row">
            <h3>현재 단계</h3>
            <span className="badge success">Mock POS</span>
          </div>
          <p>샘플 JSON을 내부 adapter로 정규화해 상품 생성/업데이트 정책을 검증합니다. 외부 POS 서버와 통신하지 않습니다.</p>
        </article>
        <article className="account-card">
          <div className="card-title-row">
            <h3>CSV와의 관계</h3>
            <span className="badge muted">Fallback</span>
          </div>
          <p>CSV import와 Mock POS sync는 모두 external_sku를 기준으로 중복을 판단하고 재고 이력에 원인을 남깁니다. 실제 POS 전에도 CSV fallback을 유지합니다.</p>
          <Link href="/merchant/pro/inventory-ledger">
            <button type="button" className="secondary">재고 이력 보기</button>
          </Link>
        </article>
        <article className="account-card">
          <div className="card-title-row">
            <h3>실제 연동 전 필요</h3>
            <span className="badge warning">Before live</span>
          </div>
          <p>credential boundary, store mapping, 실패 재시도, sync audit, sandbox 검증이 끝난 뒤 실제 POS API를 연결합니다.</p>
        </article>
      </div>

      <section className="panel">
        <div className="card-title-row">
          <div>
            <p className="eyebrow">POS 설정</p>
            <h2>연동 설정 저장</h2>
            <p>현재 설정은 provider readiness와 Mock sync 정책을 위한 값입니다. 실제 credential이나 token은 저장하지 않습니다.</p>
          </div>
          {integration && <StatusBadge status={integration.status} />}
        </div>
        <div className="form-grid">
          <label>
            Provider
            <select value={provider} onChange={(event) => setProvider(event.target.value)}>
              <option value="MOCK_POS">MOCK_POS</option>
              <option value="GENERIC_POS">GENERIC_POS</option>
            </select>
          </label>
          <label>
            매장
            <select value={storeId} onChange={(event) => setStoreId(event.target.value)}>
              <option value="">기본 매장 자동 선택</option>
              {stores.map((store) => (
                <option key={store.id} value={store.id}>
                  {store.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            외부 매장 코드
            <input
              value={externalStoreCode}
              onChange={(event) => setExternalStoreCode(event.target.value)}
              placeholder="예) STORE-GANGNAM-001"
            />
          </label>
        </div>
        <div className="actions">
          <button type="button" onClick={saveIntegration} disabled={loading}>
            연결 설정 저장
          </button>
          <Link className="button-link secondary" href="/merchant/pro/plan">
            Enterprise 플랜 보기
          </Link>
        </div>
      </section>

      <section className="panel">
        <div className="card-title-row">
          <div>
            <p className="eyebrow">Mock POS 동기화</p>
            <h2>external_sku 기준 상품 생성/업데이트</h2>
            <p>업데이트 정책을 선택하고, 기본 생성 상태는 고객에게 바로 노출되지 않는 HIDDEN으로 유지합니다.</p>
          </div>
          <Badge tone="warning">실제 POS 호출 없음</Badge>
        </div>
        <div className="form-grid">
          <label>
            업데이트 정책
            <select value={updateMode} onChange={(event) => setUpdateMode(event.target.value)}>
              <option value="UPDATE_IF_NO_RESERVATIONS">예약 없으면 업데이트</option>
              <option value="SKIP_EXISTING">기존 상품 건너뛰기</option>
              <option value="UPDATE_HIDDEN_ONLY">숨김 상품만 업데이트</option>
            </select>
          </label>
          <label>
            기본 생성 상태
            <select value={defaultProductStatus} onChange={(event) => setDefaultProductStatus(event.target.value)}>
              <option value="HIDDEN">HIDDEN - 상품관리에서 확인 후 노출</option>
            </select>
          </label>
        </div>
        <p className="field-help">
          ACTIVE 생성은 이번 MVP에서 제한합니다. POS에서 들어온 상품은 숨김 상태로 만든 뒤 점주가 상품관리에서 노출합니다.
          Mock POS 동기화는 외부 POS API 호출 없이 내부 dry-run으로만 실행됩니다.
        </p>
        <label>
          Mock item JSON
          <textarea
            className="code-input"
            rows={14}
            value={mockJson}
            onChange={(event) => setMockJson(event.target.value)}
          />
        </label>
        <div className="actions">
          <button type="button" onClick={runMockSync} disabled={syncing}>
            {syncing ? "동기화 중" : "Mock POS 동기화 실행"}
          </button>
          <button type="button" className="secondary" onClick={() => setMockJson(JSON.stringify(sampleItems, null, 2))}>
            샘플 JSON 복원
          </button>
        </div>
      </section>

      {syncResult && (
        <section className="panel">
          <div className="card-title-row">
            <div>
              <p className="eyebrow">동기화 결과</p>
              <h2>Batch {syncResult.batch_id.slice(0, 8)}</h2>
            </div>
            <StatusBadge status={syncResult.status} />
          </div>
          <div className="summary-grid">
            <StatCard label="전체" value={`${syncResult.total_rows}건`} />
            <StatCard label="생성" value={`${syncResult.created_count}건`} />
            <StatCard label="업데이트" value={`${syncResult.updated_count}건`} />
            <StatCard label="건너뜀" value={`${syncResult.skipped_count}건`} />
            <StatCard label="실패" value={`${syncResult.failed_count}건`} />
          </div>
          <SyncRows rows={syncResult.rows} />
        </section>
      )}

      <section className="panel">
        <div className="card-title-row">
          <div>
            <p className="eyebrow">동기화 이력</p>
            <h2>최근 Mock POS sync</h2>
          </div>
        </div>
        {batches.length === 0 ? (
          <EmptyState title="POS 동기화 이력이 없습니다." description="Mock POS 동기화를 실행하면 결과가 이곳에 쌓입니다." />
        ) : (
          <div className="responsive-table">
            <table>
              <thead>
                <tr>
                  <th>일시</th>
                  <th>상태</th>
                  <th>전체</th>
                  <th>생성</th>
                  <th>업데이트</th>
                  <th>건너뜀</th>
                  <th>실패</th>
                  <th>상세</th>
                </tr>
              </thead>
              <tbody>
                {batches.map((batch) => (
                  <tr key={batch.id}>
                    <td>{formatDateTime(batch.created_at)}</td>
                    <td><StatusBadge status={batch.status} /></td>
                    <td>{batch.total_rows}</td>
                    <td>{batch.created_count}</td>
                    <td>{batch.updated_count}</td>
                    <td>{batch.skipped_count}</td>
                    <td>{batch.failed_count}</td>
                    <td>
                      <button type="button" className="secondary compact-button" onClick={() => void loadBatchDetail(batch.id)}>
                        보기
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {selectedBatch && (
        <section className="panel">
          <div className="card-title-row">
            <div>
              <p className="eyebrow">이력 상세</p>
              <h2>{formatDateTime(selectedBatch.created_at)}</h2>
            </div>
            <StatusBadge status={selectedBatch.status} />
          </div>
          <SyncRows rows={selectedBatch.rows} />
        </section>
      )}
    </section>
  );
}

function SyncRows({ rows }: { rows: PosSyncBatch["rows"] }) {
  if (rows.length === 0) {
    return <EmptyState title="row 결과가 없습니다." />;
  }

  return (
    <div className="responsive-table">
      <table>
        <thead>
          <tr>
            <th>SKU</th>
            <th>상품명</th>
            <th>처리</th>
            <th>메시지</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id}>
              <td>{row.external_sku || "-"}</td>
              <td>{row.product_name || "-"}</td>
              <td><Badge tone={actionTone(row.action)}>{row.action}</Badge></td>
              <td>{reasonLabel(row.error_message)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
