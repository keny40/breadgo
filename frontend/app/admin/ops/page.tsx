"use client";

import { useCallback, useEffect, useState } from "react";
import { EmptyState, PageHeader, StatCard, StatusBadge } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { OpsComponentStatus, OpsStatus } from "@/lib/types";

function statusForBadge(status: string) {
  const normalized = status.toUpperCase();
  if (normalized === "OK" || normalized === "ENABLED") return "ACTIVE";
  if (normalized === "DEGRADED" || normalized === "SKELETON" || normalized === "PLANNED") return "PENDING";
  if (normalized === "ERROR") return "FAILED";
  return status;
}

function StatusCardList({ title, items }: { title: string; items: OpsComponentStatus[] }) {
  return (
    <section className="panel form-grid">
      <h2>{title}</h2>
      <div className="ops-grid">
        {items.map((item) => (
          <article className="ops-card" key={`${title}-${item.name}`}>
            <div className="card-title-row">
              <strong>{item.name}</strong>
              <StatusBadge status={statusForBadge(item.status)} />
            </div>
            <p>{item.message || "상태 메시지가 없습니다."}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

export default function AdminOpsPage() {
  const guard = useRoleGuard("ADMIN");
  const [opsStatus, setOpsStatus] = useState<OpsStatus | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  const loadOpsStatus = useCallback(async () => {
    setMessage("");
    setIsError(false);
    setLoading(true);

    try {
      const data = await apiFetch<OpsStatus>("/api/v1/ops/status", {}, true);
      setOpsStatus(data);
      setMessage("운영 상태를 불러왔습니다.");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!guard.allowed) return;
    queueMicrotask(() => {
      void loadOpsStatus();
    });
  }, [guard.allowed, loadOpsStatus]);

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
        title="운영 점검"
        description="백엔드 상태, DB 연결, 결제 Provider, 알림 Channel, 장애 알림 준비 상태를 확인합니다."
        actions={
          <button type="button" onClick={loadOpsStatus} disabled={loading}>
            {loading ? "확인 중" : "상태 새로고침"}
          </button>
        }
      />
      <p className="message">
        현재는 실제 Sentry, Slack, 외부 모니터링 서비스를 호출하지 않습니다. 운영 전환을 위한 skeleton 상태만 표시합니다.
      </p>
      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      {!opsStatus ? (
        <EmptyState title="운영 상태를 불러오지 않았습니다." description="상태 새로고침을 눌러 확인해 주세요." />
      ) : (
        <>
          <div className="summary-grid">
            <StatCard label="App" value={opsStatus.app_status.toUpperCase()} helper={opsStatus.app_name} />
            <StatCard label="Environment" value={opsStatus.environment} helper={`API ${opsStatus.api_version}`} />
            <StatCard label="Database" value={opsStatus.database.status.toUpperCase()} helper={opsStatus.database.name} />
            <StatCard label="Checked" value={new Date(opsStatus.checked_at).toLocaleTimeString()} />
          </div>

          <StatusCardList title="결제 Provider" items={opsStatus.payment_providers} />
          <StatusCardList title="알림 Channel" items={opsStatus.notification_channels} />
          <StatusCardList title="장애 알림 Notifier" items={opsStatus.incident_notifiers} />
        </>
      )}
    </section>
  );
}
