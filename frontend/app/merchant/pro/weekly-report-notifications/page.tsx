"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { Badge, EmptyState, PageHeader } from "@/components/UI";
import { apiFetch, friendlyErrorMessage } from "@/lib/api";
import { useRoleGuard } from "@/lib/authGuard";
import type {
  MerchantProWeeklyReportReadAllResult,
  MerchantProWeeklyReportNotificationList,
  MerchantProWeeklyReportUnreadCount,
  ProWeeklyReportInAppNotification,
} from "@/lib/types";

function formatDateTime(value: string | null) {
  if (!value) return "-";
  return new Date(value).toLocaleString("ko-KR");
}

function statusTone(status: string): "success" | "warning" | "danger" | "muted" {
  if (status === "READ") return "success";
  if (status === "UNREAD") return "warning";
  return "muted";
}

function NotificationCard({
  notification,
  onRead,
  reading,
}: {
  notification: ProWeeklyReportInAppNotification;
  onRead: (notificationId: string) => void;
  reading: boolean;
}) {
  return (
    <article className={`item compact-card ${notification.status === "UNREAD" ? "highlight-card" : ""}`}>
      <div className="card-title-row">
        <div>
          <p className="eyebrow">BreadGo 내부 알림</p>
          <h2>{notification.title}</h2>
          <p>{notification.message}</p>
        </div>
        <Badge tone={statusTone(notification.status)}>
          {notification.status === "READ" ? "읽음" : "읽지 않음"}
        </Badge>
      </div>
      <dl className="metadata-grid">
        <div>
          <dt>생성 시각</dt>
          <dd>{formatDateTime(notification.created_at)}</dd>
        </div>
        <div>
          <dt>읽음 시각</dt>
          <dd>{formatDateTime(notification.read_at)}</dd>
        </div>
        <div>
          <dt>Snapshot</dt>
          <dd>{notification.snapshot_id}</dd>
        </div>
      </dl>
      <div className="button-row">
        <Link className="button-link secondary" href="/merchant/pro/weekly-report/history">
          저장 리포트 확인
        </Link>
        <button
          type="button"
          disabled={notification.status === "READ" || reading}
          onClick={() => onRead(notification.notification_id)}
        >
          {reading ? "처리 중" : "읽음 처리"}
        </button>
      </div>
    </article>
  );
}

export default function MerchantProWeeklyReportNotificationsPage() {
  const guard = useRoleGuard("MERCHANT");
  const [data, setData] = useState<MerchantProWeeklyReportNotificationList | null>(null);
  const [unreadCount, setUnreadCount] = useState(0);
  const [statusFilter, setStatusFilter] = useState<"ALL" | "UNREAD" | "READ">("ALL");
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);
  const [readingId, setReadingId] = useState<string | null>(null);

  const loadNotifications = useCallback(async () => {
    setLoading(true);
    setMessage("");
    setIsError(false);
    try {
      const result = await apiFetch<MerchantProWeeklyReportNotificationList>(
        "/api/v1/merchant/pro/weekly-report/notifications",
        {},
        true,
      );
      const unread = await apiFetch<MerchantProWeeklyReportUnreadCount>(
        "/api/v1/merchant/pro/weekly-report/notifications/unread-count",
        {},
        true,
      );
      setData(result);
      setUnreadCount(unread.unread_count);
      setMessage("Weekly Report 내부 알림을 불러왔습니다.");
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
      void loadNotifications();
    });
  }, [guard.allowed, loadNotifications]);

  async function markAsRead(notificationId: string) {
    setReadingId(notificationId);
    setMessage("");
    setIsError(false);
    try {
      await apiFetch<ProWeeklyReportInAppNotification>(
        `/api/v1/merchant/pro/weekly-report/notifications/${notificationId}/read`,
        { method: "POST" },
        true,
      );
      setMessage("Weekly Report 알림을 읽음 처리했습니다.");
      await loadNotifications();
      window.dispatchEvent(new Event("breadgo-auth-changed"));
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setReadingId(null);
    }
  }

  async function markAllAsRead() {
    setReadingId("ALL");
    setMessage("");
    setIsError(false);
    try {
      const result = await apiFetch<MerchantProWeeklyReportReadAllResult>(
        "/api/v1/merchant/pro/weekly-report/notifications/read-all",
        { method: "POST" },
        true,
      );
      setMessage(`${result.updated_count}개의 Weekly Report 알림을 모두 읽음 처리했습니다.`);
      await loadNotifications();
      window.dispatchEvent(new Event("breadgo-auth-changed"));
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setReadingId(null);
    }
  }

  if (!guard.allowed) {
    return (
      <section className="section">
        <EmptyState title={guard.message || "권한을 확인하고 있습니다."} />
      </section>
    );
  }

  const notifications = (data?.notifications || []).filter((notification) => {
    if (statusFilter === "ALL") return true;
    return notification.status === statusFilter;
  });

  return (
    <section className="section">
      <PageHeader
        title="Weekly Report 알림"
        description="외부 이메일/카카오/Push가 아니라 BreadGo 내부 알림으로 생성된 Weekly Report 안내를 확인합니다."
        actions={
          <>
            <Badge tone={unreadCount > 0 ? "warning" : "success"}>미확인 {unreadCount}건</Badge>
            <button type="button" onClick={markAllAsRead} disabled={readingId === "ALL" || unreadCount === 0}>
              {readingId === "ALL" ? "처리 중" : "모두 읽음 처리"}
            </button>
            <button type="button" onClick={loadNotifications} disabled={loading}>
              {loading ? "불러오는 중" : "새로고침"}
            </button>
          </>
        }
      />

      <p className="message">
        이 화면은 BreadGo 내부 mock delivery 결과만 보여줍니다. 이메일, 전화번호, 주소, 외부 발송 토큰은 저장하지 않습니다.
      </p>

      {message && <div className={isError ? "notice error" : "notice success"}>{message}</div>}

      <div className="segmented-control" aria-label="Weekly Report 알림 상태 필터">
        {(["ALL", "UNREAD", "READ"] as const).map((status) => (
          <button
            key={status}
            type="button"
            className={statusFilter === status ? "active" : ""}
            onClick={() => setStatusFilter(status)}
          >
            {status === "ALL" ? "전체" : status === "UNREAD" ? "미확인" : "읽음"}
          </button>
        ))}
      </div>

      {notifications.length > 0 ? (
        <div className="stacked-list">
          {notifications.map((notification) => (
            <NotificationCard
              key={notification.notification_id}
              notification={notification}
              onRead={markAsRead}
              reading={readingId === notification.notification_id}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          title="Weekly Report 알림이 없습니다."
          description="관리자가 in-app mock delivery를 실행하면 내부 알림이 표시됩니다."
        />
      )}
    </section>
  );
}
