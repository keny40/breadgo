"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Badge, EmptyState, PageHeader, StatCard } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { MerchantProInventoryAlerts, ProInventoryAlert } from "@/lib/types";

const alertTypeLabels: Record<string, string> = {
  NEGATIVE_STOCK: "음수 재고",
  EXPIRED_WITH_STOCK: "마감 후 재고",
  HIGH_VIEW_LOW_RESERVATION: "조회 대비 낮은 예약",
  LARGE_STOCK_CHANGE: "큰 재고 변동",
  CANCEL_RESTORED_HIDDEN: "취소 복구 숨김 재고",
  LOW_STOCK_HIGH_DEMAND: "높은 수요 낮은 재고",
};

function severityTone(severity: string): "success" | "warning" | "danger" | "muted" {
  if (severity === "HIGH") return "danger";
  if (severity === "MEDIUM") return "warning";
  if (severity === "LOW") return "muted";
  return "muted";
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString("ko-KR", {
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function MerchantProInventoryAlertsPage() {
  const guard = useRoleGuard("MERCHANT");
  const [data, setData] = useState<MerchantProInventoryAlerts | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!guard.allowed) return;
    void Promise.resolve().then(() => loadAlerts());
  }, [guard.allowed]);

  async function loadAlerts() {
    setLoading(true);
    setMessage("");
    setIsError(false);
    try {
      const result = await apiFetch<MerchantProInventoryAlerts>(
        "/api/v1/merchant/pro/inventory-alerts",
        {},
        true,
      );
      setData(result);
      setMessage("재고 이상 알림을 확인했습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setLoading(false);
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
        title="재고 이상 알림"
        description="마감 후 재고, 낮은 예약 전환, 큰 재고 변동처럼 점주가 바로 확인해야 할 운영 신호를 보여줍니다."
        actions={
          <button type="button" onClick={loadAlerts} disabled={loading}>
            {loading ? "확인 중" : "알림 새로고침"}
          </button>
        }
      />

      <div className="pro-hero panel">
        <div>
          <p className="eyebrow">Inventory Anomaly</p>
          <h2>문제가 될 수 있는 재고 상태를 자동 확인합니다</h2>
          <p>실제 외부 알림 발송은 하지 않고, BreadGo Pro 안에서 점주가 조치할 운영 신호를 계산합니다.</p>
        </div>
        <div className="pro-score">
          <span>전체 알림</span>
          <strong>{data?.total_alerts || 0}건</strong>
          <small>최근 7일 및 현재 상품 기준</small>
        </div>
      </div>

      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      <div className="summary-grid">
        <StatCard label="전체 알림" value={`${data?.total_alerts || 0}건`} />
        <StatCard label="HIGH" value={`${data?.high_count || 0}건`} />
        <StatCard label="MEDIUM" value={`${data?.medium_count || 0}건`} />
        <StatCard label="LOW" value={`${data?.low_count || 0}건`} />
      </div>

      <section className="panel">
        <div className="card-title-row">
          <div>
            <p className="eyebrow">운영 알림</p>
            <h2>조치가 필요한 재고 신호</h2>
          </div>
          <Badge tone="muted">외부 발송 없음</Badge>
        </div>

        {!data || data.alerts.length === 0 ? (
          <EmptyState
            title="현재 감지된 재고 이상 알림이 없습니다."
            description="상품 조회, 예약, 취소, CSV/POS 변경 이력이 쌓이면 운영 신호가 표시됩니다."
          />
        ) : (
          <div className="pro-product-grid">
            {data.alerts.map((alert) => (
              <InventoryAlertCard key={`${alert.product_id}-${alert.alert_type}`} alert={alert} />
            ))}
          </div>
        )}
      </section>
    </section>
  );
}

function InventoryAlertCard({ alert }: { alert: ProInventoryAlert }) {
  return (
    <article className="item pro-product-card">
      <div className="card-title-row">
        <div>
          <p className="eyebrow">{alert.store_name}</p>
          <h3>{alert.product_name}</h3>
        </div>
        <Badge tone={severityTone(alert.severity)}>{alert.severity}</Badge>
      </div>
      <div className="actions">
        <Badge tone="muted">{alertTypeLabels[alert.alert_type] || alert.alert_type}</Badge>
      </div>
      <h4>{alert.title}</h4>
      <p>{alert.message}</p>
      <div className="detail-grid">
        <div>
          <span>현재 재고</span>
          <strong>{alert.current_stock_quantity}개</strong>
        </div>
        <div>
          <span>관련 지표</span>
          <strong>{alert.related_metric || "-"}</strong>
        </div>
        <div>
          <span>감지 시각</span>
          <strong>{formatDateTime(alert.detected_at)}</strong>
        </div>
      </div>
      {alert.recent_inventory_note && <p className="field-help">{alert.recent_inventory_note}</p>}
      <p className="guidance-text">
        <strong>추천 조치</strong>
        <br />
        {alert.suggested_action}
      </p>
      <div className="actions">
        <Link className="button-link secondary" href="/merchant/products">
          상품관리
        </Link>
        <Link className="button-link secondary" href="/merchant/pro/inventory-ledger">
          재고 이력
        </Link>
        <Link className="button-link secondary" href="/merchant/pro/product-funnel">
          고객 전환
        </Link>
        <Link className="button-link secondary" href="/merchant/pro/recommendations">
          추천 화면
        </Link>
      </div>
    </article>
  );
}
