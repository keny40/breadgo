import type { ReactNode } from "react";

const successStatuses = new Set(["ACTIVE", "APPROVED", "CONFIRMED", "PAID", "PICKED_UP", "DELIVERED"]);
const warningStatuses = new Set(["PENDING", "READY", "SOLD_OUT", "HOLD", "REFUNDED", "REQUESTED", "PREPARING", "SENT"]);
const dangerStatuses = new Set(["CANCELLED", "FAILED", "REJECTED", "SUSPENDED", "EXPIRED"]);

const statusLabels: Record<string, string> = {
  ACTIVE: "판매중",
  APPROVED: "승인됨",
  CONFIRMED: "예약확정",
  PAID: "결제완료",
  PICKED_UP: "픽업완료",
  DELIVERED: "전달 완료",
  PENDING: "대기중",
  READY: "준비됨",
  SOLD_OUT: "품절",
  HOLD: "보류",
  REFUNDED: "환불 처리됨",
  REQUESTED: "요청 접수",
  PREPARING: "준비중",
  SENT: "발송/배차 완료",
  CANCELLED: "취소됨",
  FAILED: "실패",
  REJECTED: "거절됨",
  SUSPENDED: "중지됨",
  EXPIRED: "만료됨",
};

export function PageHeader({
  title,
  description,
  actions,
}: {
  title: string;
  description?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="page-header">
      <div>
        <p className="eyebrow">BreadGo MVP</p>
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      {actions && <div className="actions">{actions}</div>}
    </div>
  );
}

export function Badge({ children, tone }: { children: ReactNode; tone?: "success" | "warning" | "danger" | "muted" }) {
  return <span className={`badge ${tone || "muted"}`}>{children}</span>;
}

export function StatusBadge({ status }: { status: string }) {
  const normalized = status.toUpperCase();
  let tone: "success" | "warning" | "danger" | "muted" = "muted";

  if (successStatuses.has(normalized)) {
    tone = "success";
  } else if (warningStatuses.has(normalized)) {
    tone = "warning";
  } else if (dangerStatuses.has(normalized)) {
    tone = "danger";
  }

  return <Badge tone={tone}>{statusLabels[normalized] || status}</Badge>;
}

export function EmptyState({ title, description }: { title: string; description?: string }) {
  return (
    <div className="empty-state">
      <strong>{title}</strong>
      {description && <span>{description}</span>}
    </div>
  );
}

export function StatCard({ label, value, helper }: { label: string; value: number | string; helper?: string }) {
  return (
    <div className="summary-card">
      <span>{label}</span>
      <strong>{value}</strong>
      {helper && <small>{helper}</small>}
    </div>
  );
}
