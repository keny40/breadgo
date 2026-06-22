"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Badge, EmptyState, PageHeader, StatCard } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { MerchantProDailyBriefHistory, ProDailyBriefSnapshot, ProDailyBriefSnapshotTask } from "@/lib/types";

function formatMoney(value: string | null) {
  return `${Number(value || 0).toLocaleString()}원`;
}

function formatDate(value: string) {
  return new Date(`${value}T00:00:00`).toLocaleDateString("ko-KR", {
    month: "long",
    day: "numeric",
    weekday: "short",
  });
}

function deltaLabel(value: number | string | null, suffix = "") {
  if (value === null || value === undefined) return "기록 없음";
  const numeric = typeof value === "string" ? Number(value) : value;
  if (Number.isNaN(numeric)) return "기록 없음";
  const sign = numeric > 0 ? "+" : "";
  return `${sign}${numeric.toLocaleString()}${suffix}`;
}

function deltaTone(value: number | string | null, lowerIsBetter = false): "success" | "warning" | "danger" | "muted" {
  if (value === null || value === undefined) return "muted";
  const numeric = typeof value === "string" ? Number(value) : value;
  if (Number.isNaN(numeric) || numeric === 0) return "muted";
  const improved = lowerIsBetter ? numeric < 0 : numeric > 0;
  return improved ? "success" : "warning";
}

function priorityTone(priority: string): "success" | "warning" | "danger" | "muted" {
  if (priority === "HIGH") return "danger";
  if (priority === "MEDIUM") return "warning";
  if (priority === "LOW") return "success";
  return "muted";
}

function TaskRow({ task }: { task: ProDailyBriefSnapshotTask }) {
  return (
    <div className="item compact-card">
      <div className="card-title-row">
        <strong>{task.title}</strong>
        <Badge tone={priorityTone(task.priority)}>{task.priority}</Badge>
      </div>
      <p>{task.message}</p>
      {task.action_href && (
        <Link className="button-link secondary" href={task.action_href}>
          {task.action_label || "관련 화면 보기"}
        </Link>
      )}
    </div>
  );
}

function SnapshotCard({ snapshot }: { snapshot: ProDailyBriefSnapshot }) {
  return (
    <article className="panel">
      <div className="card-title-row">
        <div>
          <p className="eyebrow">운영 브리프 이력</p>
          <h2>{formatDate(snapshot.brief_date)}</h2>
          <p>매일의 운영 상태를 기록해 개선 흐름을 확인합니다.</p>
        </div>
        <Badge tone={snapshot.high_severity_alert_count > 0 ? "danger" : "success"}>
          HIGH {snapshot.high_severity_alert_count}
        </Badge>
      </div>

      <div className="summary-grid compact">
        <StatCard label="매출" value={formatMoney(snapshot.today_sales_amount)} />
        <StatCard label="예약" value={snapshot.today_reservation_count} />
        <StatCard label="픽업" value={snapshot.today_picked_up_count} />
        <StatCard label="미해결 알림" value={snapshot.unresolved_alert_count} />
        <StatCard label="폐기 절감" value={`${snapshot.saved_quantity_today}개`} />
        <StatCard label="재고 변경" value={snapshot.inventory_event_count_today} />
      </div>

      <div className="stacked-list">
        {snapshot.tasks.length > 0 ? (
          snapshot.tasks.map((task) => <TaskRow key={task.id} task={task} />)
        ) : (
          <EmptyState title="저장된 할 일이 없습니다." />
        )}
      </div>
    </article>
  );
}

export default function MerchantProDailyBriefHistoryPage() {
  const guard = useRoleGuard("MERCHANT");
  const [history, setHistory] = useState<MerchantProDailyBriefHistory | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!guard.allowed) return;
    void loadHistory();
  }, [guard.allowed]);

  async function loadHistory() {
    setLoading(true);
    setMessage("");
    setIsError(false);
    try {
      const data = await apiFetch<MerchantProDailyBriefHistory>("/api/v1/merchant/pro/daily-brief/history", {}, true);
      setHistory(data);
      setMessage("운영 브리프 이력을 불러왔습니다.");
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
        title="운영 브리프 이력"
        description="저장된 Daily Pro Brief를 날짜별로 확인하고 어제 대비 운영 개선 흐름을 봅니다."
        actions={
          <>
            <button type="button" onClick={loadHistory} disabled={loading}>
              {loading ? "불러오는 중" : "이력 새로고침"}
            </button>
            <Link className="button-link secondary" href="/merchant/pro/daily-brief">
              오늘 브리프
            </Link>
            <Link className="button-link secondary" href="/merchant/pro/weekly-report">
              주간 리포트
            </Link>
          </>
        }
      />

      {message && <div className={isError ? "notice error" : "notice success"}>{message}</div>}

      <section className="panel">
        <div className="card-title-row">
          <div>
            <p className="eyebrow">어제 대비</p>
            <h2>운영 개선 추적</h2>
            <p>최신 브리프와 바로 이전 브리프를 비교합니다. 데이터가 하루뿐이면 증감은 표시하지 않습니다.</p>
          </div>
          <Badge tone="muted">최근 30일</Badge>
        </div>
        <div className="summary-grid">
          <StatCard
            label="미해결 알림 변화"
            value={<Badge tone={deltaTone(history?.delta.unresolved_alert_delta ?? null, true)}>{deltaLabel(history?.delta.unresolved_alert_delta ?? null, "건")}</Badge>}
            helper="줄어들수록 좋음"
          />
          <StatCard
            label="매출 변화"
            value={<Badge tone={deltaTone(history?.delta.sales_delta ?? null)}>{deltaLabel(history?.delta.sales_delta ?? null, "원")}</Badge>}
            helper="Mock 결제 기준"
          />
          <StatCard
            label="예약 변화"
            value={<Badge tone={deltaTone(history?.delta.reservation_delta ?? null)}>{deltaLabel(history?.delta.reservation_delta ?? null, "건")}</Badge>}
          />
          <StatCard
            label="픽업 변화"
            value={<Badge tone={deltaTone(history?.delta.picked_up_delta ?? null)}>{deltaLabel(history?.delta.picked_up_delta ?? null, "건")}</Badge>}
          />
          <StatCard
            label="폐기 절감 변화"
            value={<Badge tone={deltaTone(history?.delta.saved_quantity_delta ?? null)}>{deltaLabel(history?.delta.saved_quantity_delta ?? null, "개")}</Badge>}
          />
        </div>
      </section>

      {history && history.snapshots.length > 0 ? (
        <div className="stacked-list">
          {history.snapshots.map((snapshot) => (
            <SnapshotCard key={snapshot.id} snapshot={snapshot} />
          ))}
        </div>
      ) : (
        <EmptyState
          title="저장된 브리프 이력이 없습니다."
          description="오늘 브리프 화면에서 '오늘 브리프 저장'을 누르면 이력이 생성됩니다."
        />
      )}
    </section>
  );
}
