"use client";

import { useState } from "react";
import { API_BASE_URL, buildApiUrl } from "@/lib/api";

type DiagnosticResult = {
  ok: boolean;
  status?: number;
  url: string;
  body: string;
  error?: string;
};

const regionProductsPath =
  "/api/v1/regions/products?sido=서울특별시&sigungu=강남구&dong=역삼동";

async function runDiagnostic(path: string): Promise<DiagnosticResult> {
  const url = buildApiUrl(path);

  try {
    const response = await fetch(url, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
    });
    const body = await response.text();

    return {
      ok: response.ok,
      status: response.status,
      url,
      body: body || "(empty)",
    };
  } catch (error) {
    return {
      ok: false,
      url,
      body: "(no response body)",
      error: error instanceof Error ? error.message : "Unknown fetch error",
    };
  }
}

function ResultPanel({ title, result }: { title: string; result: DiagnosticResult | null }) {
  if (!result) {
    return (
      <div className="empty-state">
        <strong>{title}</strong>
        <span>아직 테스트를 실행하지 않았습니다.</span>
      </div>
    );
  }

  return (
    <article className="item">
      <div className="card-title-row">
        <h3>{title}</h3>
        <span className={`badge ${result.ok ? "success" : "danger"}`}>
          {result.ok ? "OK" : "FAILED"}
        </span>
      </div>
      <div className="meta">
        <span>URL {result.url}</span>
        <span>Status {result.status ?? "N/A"}</span>
      </div>
      {result.error && <div className="message error">{result.error}</div>}
      <pre className="debug-output">{result.body}</pre>
    </article>
  );
}

export default function ApiDebugPage() {
  const [healthResult, setHealthResult] = useState<DiagnosticResult | null>(null);
  const [productsResult, setProductsResult] = useState<DiagnosticResult | null>(null);
  const [healthLoading, setHealthLoading] = useState(false);
  const [productsLoading, setProductsLoading] = useState(false);

  async function testHealth() {
    setHealthLoading(true);
    setHealthResult(await runDiagnostic("/health"));
    setHealthLoading(false);
  }

  async function testRegionProducts() {
    setProductsLoading(true);
    setProductsResult(await runDiagnostic(regionProductsPath));
    setProductsLoading(false);
  }

  return (
    <section className="section">
      <div className="page-header">
        <div>
          <p className="eyebrow">Deployment diagnostics</p>
          <h1>API 연결 진단</h1>
          <p>Vercel 프론트엔드가 어떤 백엔드 URL로 요청하는지 확인합니다.</p>
        </div>
      </div>

      <div className="panel form-grid">
        <h2>현재 API 설정</h2>
        <div className="meta">
          <span>
            NEXT_PUBLIC_API_BASE_URL <strong>{API_BASE_URL}</strong>
          </span>
        </div>
        <div className="meta">
          <span>
            Health URL <strong>{buildApiUrl("/health")}</strong>
          </span>
        </div>
        <div className="actions">
          <button type="button" onClick={testHealth} disabled={healthLoading}>
            {healthLoading ? "테스트 중" : "Test backend health"}
          </button>
          <button type="button" className="secondary" onClick={testRegionProducts} disabled={productsLoading}>
            {productsLoading ? "테스트 중" : "Test region products"}
          </button>
        </div>
      </div>

      <ResultPanel title="GET /health" result={healthResult} />
      <ResultPanel title="GET region products" result={productsResult} />
    </section>
  );
}
