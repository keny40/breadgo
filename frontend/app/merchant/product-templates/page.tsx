"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { EmptyState, PageHeader, StatusBadge } from "@/components/UI";
import { apiFetch, buildApiUrl, friendlyErrorMessage, getToken } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { Product, ProductTemplate, ProductTemplateCreateProductsResponse } from "@/lib/types";

const dayLabels = ["월", "화", "수", "목", "금", "토", "일"];

function todayDayOfWeek() {
  const day = new Date().getDay();
  return day === 0 ? 6 : day - 1;
}

function formatTime(value: string) {
  return value.slice(0, 5);
}

export default function MerchantProductTemplatesPage() {
  const guard = useRoleGuard("MERCHANT");
  const [products, setProducts] = useState<Product[]>([]);
  const [templates, setTemplates] = useState<ProductTemplate[]>([]);
  const [sourceProductId, setSourceProductId] = useState("");
  const [templateName, setTemplateName] = useState("");
  const [dayOfWeek, setDayOfWeek] = useState(todayDayOfWeek());
  const [defaultStockQuantity, setDefaultStockQuantity] = useState(1);
  const [startTime, setStartTime] = useState("18:00");
  const [endTime, setEndTime] = useState("21:00");
  const [isActive, setIsActive] = useState(true);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  const sourceProducts = useMemo(
    () => products.filter((product) => product.status !== "HIDDEN"),
    [products],
  );

  useEffect(() => {
    if (!guard.allowed) return;
    void loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [guard.allowed]);

  async function loadData(successMessage = "") {
    setLoading(true);
    setMessage("");
    setIsError(false);

    try {
      const [productData, templateData] = await Promise.all([
        apiFetch<Product[]>("/api/v1/products/me", {}, true),
        apiFetch<ProductTemplate[]>("/api/v1/merchant/product-templates", {}, true),
      ]);
      setProducts(productData);
      setTemplates(templateData);
      if (!sourceProductId && productData.length > 0) {
        setSourceProductId(productData[0].id);
      }
      if (successMessage) {
        setMessage(successMessage);
      }
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  async function createTemplate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    setIsError(false);

    try {
      await apiFetch<ProductTemplate>(
        "/api/v1/merchant/product-templates",
        {
          method: "POST",
          body: JSON.stringify({
            source_product_id: sourceProductId,
            template_name: templateName,
            day_of_week: dayOfWeek,
            default_stock_quantity: defaultStockQuantity,
            start_time: startTime,
            end_time: endTime,
            is_active: isActive,
          }),
        },
        true,
      );
      setTemplateName("");
      await loadData("요일별 반복 등록 템플릿을 저장했습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  async function toggleTemplate(template: ProductTemplate) {
    setMessage("");
    setIsError(false);

    try {
      await apiFetch<ProductTemplate>(
        `/api/v1/merchant/product-templates/${template.id}`,
        {
          method: "PATCH",
          body: JSON.stringify({ is_active: !template.is_active }),
        },
        true,
      );
      await loadData(template.is_active ? "템플릿을 비활성화했습니다." : "템플릿을 활성화했습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  async function deleteTemplate(template: ProductTemplate) {
    if (!window.confirm(`${template.template_name} 템플릿을 삭제할까요?`)) {
      return;
    }
    setMessage("");
    setIsError(false);

    try {
      const token = getToken();
      const response = await fetch(buildApiUrl(`/api/v1/merchant/product-templates/${template.id}`), {
        method: "DELETE",
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      });
      if (!response.ok) {
        const body = await response.text();
        throw new Error(body || "템플릿 삭제에 실패했습니다.");
      }
      await loadData("템플릿을 삭제했습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  async function createProductFromTemplate(template: ProductTemplate) {
    setMessage("");
    setIsError(false);

    try {
      const product = await apiFetch<Product>(
        `/api/v1/merchant/product-templates/${template.id}/create-product`,
        {
          method: "POST",
          body: JSON.stringify({ is_visible: true, name_suffix: template.template_name }),
        },
        true,
      );
      await loadData(`${product.name} 상품을 오늘 판매 상품으로 등록했습니다.`);
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    }
  }

  async function createTodayProducts() {
    setMessage("");
    setIsError(false);

    try {
      const result = await apiFetch<ProductTemplateCreateProductsResponse>(
        "/api/v1/merchant/product-templates/create-today-products",
        {
          method: "POST",
          body: JSON.stringify({ is_visible: true }),
        },
        true,
      );
      await loadData(
        result.created_products.length > 0
          ? `오늘 요일 템플릿 ${result.created_products.length}개를 상품으로 등록했습니다.`
          : "오늘 요일에 활성화된 템플릿이 없습니다.",
      );
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
        title="상품 템플릿"
        description="자주 올리는 마감 상품을 요일별 템플릿으로 저장하고 오늘 판매 상품으로 한 번에 등록합니다."
        actions={
          <div className="actions">
            <button type="button" onClick={createTodayProducts} disabled={loading}>
              오늘 템플릿으로 한 번에 등록
            </button>
            <button type="button" className="secondary" onClick={() => loadData("템플릿을 새로고침했습니다.")}>
              새로고침
            </button>
          </div>
        }
      />
      <div className="message">
        <strong>요일별 반복 등록</strong>
        <br />
        재고와 마감 시간만 바꾸면 바로 판매 시작할 수 있도록 자주 올리는 마감 상품을 템플릿으로 저장하세요.
        추천 재고가 필요하면 Pro 추천 화면에서 최근 7일 데이터 기반 제안을 참고할 수 있습니다.
      </div>
      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      <form className="panel form-grid" onSubmit={createTemplate}>
        <h2>템플릿 생성</h2>
        {sourceProducts.length === 0 ? (
          <EmptyState
            title="원본 상품이 필요합니다."
            description="먼저 상품관리에서 반복 등록의 기준이 될 상품을 등록해 주세요."
          />
        ) : (
          <>
            <label>
              원본 상품
              <select value={sourceProductId} onChange={(event) => setSourceProductId(event.target.value)} required>
                {sourceProducts.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              템플릿 이름
              <input
                value={templateName}
                onChange={(event) => setTemplateName(event.target.value)}
                placeholder="예) 월요일 식빵 마감 세트"
                required
              />
            </label>
            <div className="three-column">
              <label>
                요일
                <select value={dayOfWeek} onChange={(event) => setDayOfWeek(Number(event.target.value))}>
                  {dayLabels.map((label, index) => (
                    <option key={label} value={index}>
                      {label}요일
                    </option>
                  ))}
                </select>
              </label>
              <label>
                기본 재고
                <input
                  type="number"
                  min={0}
                  value={defaultStockQuantity}
                  onChange={(event) => setDefaultStockQuantity(Number(event.target.value))}
                  required
                />
              </label>
              <label>
                활성화
                <select value={isActive ? "true" : "false"} onChange={(event) => setIsActive(event.target.value === "true")}>
                  <option value="true">사용</option>
                  <option value="false">중지</option>
                </select>
              </label>
            </div>
            <div className="two-column">
              <label>
                기본 판매 시작
                <input type="time" value={startTime} onChange={(event) => setStartTime(event.target.value)} required />
              </label>
              <label>
                기본 판매 종료
                <input type="time" value={endTime} onChange={(event) => setEndTime(event.target.value)} required />
              </label>
            </div>
            <button type="submit">템플릿 저장</button>
          </>
        )}
      </form>

      {templates.length === 0 ? (
        <EmptyState
          title="등록된 상품 템플릿이 없습니다."
          description="자주 올리는 마감 상품을 템플릿으로 저장하면 오늘 상품 등록을 더 빠르게 할 수 있습니다."
        />
      ) : (
        <div className="list">
          {templates.map((template) => (
            <article className="item" key={template.id}>
              <div className="card-title-row">
                <div>
                  <p className="eyebrow">{dayLabels[template.day_of_week]}요일 반복 등록</p>
                  <h3>{template.template_name}</h3>
                  <p>{template.source_product_name || "원본 상품"} · {template.source_store_name || "매장 정보 없음"}</p>
                </div>
                <StatusBadge status={template.is_active ? "ACTIVE" : "HIDDEN"} />
              </div>
              <div className="detail-grid">
                <Metric label="기본 재고" value={`${template.default_stock_quantity}개`} />
                <Metric label="판매 시간" value={`${formatTime(template.start_time)} - ${formatTime(template.end_time)}`} />
                <Metric label="요일" value={`${dayLabels[template.day_of_week]}요일`} />
              </div>
              <div className="actions">
                <button type="button" onClick={() => createProductFromTemplate(template)}>
                  오늘 상품 생성
                </button>
                <button type="button" className="secondary" onClick={() => toggleTemplate(template)}>
                  {template.is_active ? "비활성화" : "활성화"}
                </button>
                <button type="button" className="danger" onClick={() => deleteTemplate(template)}>
                  삭제
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
