"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Badge, EmptyState, PageHeader, StatCard } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type { MerchantProDailyBrief, ProDailyBriefTask } from "@/lib/types";

function formatMoney(value: string) {
  return `${Number(value).toLocaleString()}원`;
}

function formatDateTime(value: string | null) {
  if (!value) return "동기화 기록 없음";
  return new Date(value).toLocaleString("ko-KR", {
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function priorityTone(priority: string): "success" | "warning" | "danger" | "muted" {
  if (priority === "HIGH") return "danger";
  if (priority === "MEDIUM") return "warning";
  if (priority === "LOW") return "success";
  return "muted";
}

function priorityLabel(priority: string) {
  const labels: Record<string, string> = {
    HIGH: "높음",
    MEDIUM: "보통",
    LOW: "낮음",
  };
  return labels[priority] || priority;
}

function taskTypeLabel(type: string) {
  const labels: Record<string, string> = {
    INVENTORY_ALERT: "재고 알림",
    RECOMMENDATION_ACTION: "추천 액션",
    POS_SYNC_CHECK: "POS 확인",
    CSV_IMPORT_REVIEW: "CSV 확인",
    LOW_STOCK_HIGH_DEMAND: "수요 높음",
  };
  return labels[type] || type;
}

function TaskCard({ task }: { task: ProDailyBriefTask }) {
  return (
    <article className="panel compact-card">
      <div className="card-title-row">
        <div>
          <p className="eyebrow">{taskTypeLabel(task.task_type)}</p>
          <h3>{task.title}</h3>
        </div>
        <Badge tone={priorityTone(task.priority)}>우선순위 {priorityLabel(task.priority)}</Badge>
      </div>
      <p>{task.message}</p>
      <Link className="button-link secondary" href={task.action_href}>
        {task.action_label}
      </Link>
    </article>
  );
}

export default function MerchantProDailyBriefPage() {
  const guard = useRoleGuard("MERCHANT");
  const [brief, setBrief] = useState<MerchantProDailyBrief | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!guard.allowed) return;
    void loadBrief();
  }, [guard.allowed]);

  const hasTasks = useMemo(() => Boolean(brief?.tasks.length), [brief?.tasks.length]);

  async function loadBrief() {
    setLoading(true);
    setMessage("");
    setIsError(false);
    try {
      const data = await apiFetch<MerchantProDailyBrief>("/api/v1/merchant/pro/daily-brief", {}, true);
      setBrief(data);
      setMessage("오늘의 운영 브리프를 불러왔습니다.");
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
        title="오늘의 운영 브리프"
        description="BreadGo Pro가 오늘 먼저 확인할 운영 이슈, 추천 액션, POS/CSV 상태를 한 화면에 정리합니다."
        actions={
          <button type="button" onClick={loadBrief} disabled={loading}>
            {loading ? "불러오는 중" : "브리프 새로고침"}
          </button>
        }
      />

      {message && <div className={isError ? "notice error" : "notice success"}>{message}</div>}

      <div className="pro-hero panel">
        <div>
          <p className="eyebrow">Daily Pro Brief</p>
          <h2>{brief?.date || "오늘"} 운영 요약</h2>
          <p>
            오늘 매출, 픽업, 취소, 미해결 재고 알림과 추천 액션을 빠르게 확인하세요. 실제 AI 요약이 아닌
            현재 데이터 기반 MVP 운영 브리프입니다.
          </p>
        </div>
        <div className="pro-score">
          <span>미해결 알림</span>
          <strong>{brief?.unresolved_alert_count ?? 0}</strong>
          <small>HIGH {brief?.high_severity_alert_count ?? 0}건</small>
        </div>
      </div>

      <div className="summary-grid">
        <StatCard label="오늘 결제금액" value={brief ? formatMoney(brief.today_sales_amount) : "0원"} helper="Mock 결제 기준" />
        <StatCard label="오늘 예약 수량" value={brief?.today_reservation_count ?? 0} helper="예약된 마감 상품" />
        <StatCard label="픽업 완료" value={brief?.today_picked_up_count ?? 0} helper="폐기 절감 수량 기준" />
        <StatCard label="취소" value={brief?.today_cancelled_count ?? 0} helper="Mock 환불 포함" />
        <StatCard label="폐기 절감" value={`${brief?.saved_quantity_today ?? 0}개`} helper="픽업 완료 수량 기준" />
        <StatCard label="재고 변경" value={brief?.inventory_event_count_today ?? 0} helper="오늘 기록된 이력" />
      </div>

      <section className="panel">
        <div className="card-title-row">
          <div>
            <p className="eyebrow">오늘 먼저 확인할 일</p>
            <h2>운영 To-do</h2>
            <p>미해결 재고 알림, 추천 액션, POS/CSV 상태를 우선순위 순서로 보여줍니다.</p>
          </div>
          <Badge tone={(brief?.high_severity_alert_count || 0) > 0 ? "danger" : "success"}>
            HIGH {brief?.high_severity_alert_count || 0}
          </Badge>
        </div>

        {hasTasks ? (
          <div className="stacked-list">
            {brief?.tasks.map((task, index) => (
              <TaskCard key={`${task.task_type}-${task.title}-${index}`} task={task} />
            ))}
          </div>
        ) : (
          <EmptyState title="오늘 할 일이 없습니다." description="데이터가 쌓이면 운영 이슈와 추천 액션이 표시됩니다." />
        )}
      </section>

      <div className="grid-two">
        <section className="panel">
          <p className="eyebrow">재고 알림 요약</p>
          <h2>미해결 재고 알림</h2>
          <div className="summary-grid compact">
            <StatCard label="미해결" value={brief?.unresolved_alert_count ?? 0} />
            <StatCard label="조치 중" value={brief?.action_started_alert_count ?? 0} />
            <StatCard label="HIGH" value={brief?.high_severity_alert_count ?? 0} />
          </div>
          <Link className="button-link secondary" href="/merchant/pro/inventory-alerts">
            재고 알림 보기
          </Link>
        </section>

        <section className="panel">
          <p className="eyebrow">추천 액션 요약</p>
          <h2>오늘 확인할 추천</h2>
          <div className="summary-grid compact">
            <StatCard label="추천 액션" value={brief?.recommendation_action_count ?? 0} />
            <StatCard label="CSV 업로드" value={brief?.csv_recent_import_count ?? 0} />
            <StatCard label="CSV 오류" value={brief?.csv_recent_failed_count ?? 0} />
          </div>
          <Link className="button-link secondary" href="/merchant/pro/recommendations">
            추천 화면으로 이동
          </Link>
        </section>
      </div>

      <section className="panel">
        <div className="card-title-row">
          <div>
            <p className="eyebrow">POS/CSV 동기화 상태</p>
            <h2>외부 재고 반영 상태</h2>
            <p>
              마지막 POS 상태는 {brief?.pos_last_sync_status || "기록 없음"}이며, 마지막 동기화 시각은{" "}
              {formatDateTime(brief?.pos_last_synced_at || null)}입니다.
            </p>
          </div>
          <Badge tone={brief?.pos_last_sync_status === "COMPLETED" ? "success" : "warning"}>
            {brief?.pos_last_sync_status || "NOT_SYNCED"}
          </Badge>
        </div>
        <div className="actions">
          <Link className="button-link secondary" href="/merchant/pro/pos">
            POS 연동 확인
          </Link>
          <Link className="button-link secondary" href="/merchant/products/import">
            CSV 등록 확인
          </Link>
          <Link className="button-link secondary" href="/merchant/pro/inventory-ledger">
            재고 이력 확인
          </Link>
        </div>
      </section>
    </section>
  );
}
