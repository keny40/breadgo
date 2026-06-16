import type { ReactNode } from "react";

const successStatuses = new Set(["ACTIVE", "APPROVED", "CONFIRMED", "PAID", "PICKED_UP"]);
const warningStatuses = new Set(["PENDING", "READY", "SOLD_OUT"]);
const dangerStatuses = new Set(["CANCELLED", "FAILED", "REJECTED", "SUSPENDED", "EXPIRED"]);

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

  return <Badge tone={tone}>{status}</Badge>;
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
