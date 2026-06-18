"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Badge, EmptyState, PageHeader } from "@/components/UI";
import { apiFetch, clearToken, friendlyErrorMessage, getToken } from "@/lib/api";
import type { Notification } from "@/lib/types";

function notificationTypeLabel(value: string) {
  const labels: Record<string, string> = {
    RESERVATION_CREATED: "예약 생성",
    PAYMENT_COMPLETED: "결제 완료",
    PICKUP_CONFIRMED: "픽업 완료",
    DELIVERY_STATUS_CHANGED: "배송 상태 변경",
    RESERVATION_CANCELLED: "예약 취소",
    MOCK_REFUNDED: "Mock 환불",
    SETTLEMENT_READY: "정산 가능",
    SETTLEMENT_PAID: "정산 완료",
    SETTLEMENT_HOLD: "정산 보류",
  };
  return labels[value] || value;
}

export default function NotificationsPage() {
  const router = useRouter();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const loadNotifications = useCallback(async () => {
    setMessage("");
    setIsError(false);
    setLoading(true);

    try {
      const data = await apiFetch<Notification[]>("/api/v1/notifications/me", {}, true);
      setNotifications(data);
      setMessage(data.length > 0 ? `${data.length}개 알림을 불러왔습니다.` : "");
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
      if (friendlyErrorMessage(error) === "로그인이 필요합니다.") {
        clearToken();
        router.replace("/login");
      }
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
      return;
    }

    queueMicrotask(() => {
      void loadNotifications();
    });
  }, [loadNotifications, router]);

  async function markAsRead(notificationId: string) {
    setUpdatingId(notificationId);
    setMessage("");
    setIsError(false);

    try {
      const updated = await apiFetch<Notification>(
        `/api/v1/notifications/${notificationId}/read`,
        { method: "PATCH" },
        true,
      );
      setNotifications((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      window.dispatchEvent(new Event("breadgo-notifications-changed"));
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setUpdatingId(null);
    }
  }

  async function markAllAsRead() {
    setUpdatingId("all");
    setMessage("");
    setIsError(false);

    try {
      const updated = await apiFetch<Notification[]>(
        "/api/v1/notifications/read-all",
        { method: "PATCH" },
        true,
      );
      setNotifications(updated);
      setMessage("모든 알림을 읽음 처리했습니다.");
      window.dispatchEvent(new Event("breadgo-notifications-changed"));
    } catch (error) {
      setIsError(true);
      setMessage(friendlyErrorMessage(error));
    } finally {
      setUpdatingId(null);
    }
  }

  const unreadCount = notifications.filter((notification) => !notification.is_read).length;

  return (
    <section className="section">
      <PageHeader
        title="알림"
        description="예약, 결제, 픽업, 배송, 정산 상태 변경을 BreadGo 안에서 확인합니다."
        actions={
          <div className="actions">
            <button type="button" onClick={loadNotifications} disabled={loading}>
              {loading ? "불러오는 중" : "새로고침"}
            </button>
            <button
              type="button"
              className="secondary"
              onClick={markAllAsRead}
              disabled={updatingId === "all" || unreadCount === 0}
            >
              모두 읽음 처리
            </button>
          </div>
        }
      />
      <p className="message">현재는 SMS, 카카오톡, 이메일, 푸시가 아닌 MVP용 인앱 알림입니다.</p>
      {message && <div className={`message ${isError ? "error" : "success"}`}>{message}</div>}

      {notifications.length === 0 && !isError ? (
        <EmptyState title="알림이 없습니다." />
      ) : (
        <div className="list">
          {notifications.map((notification) => (
            <article className={`item ${notification.is_read ? "" : "notification-unread"}`} key={notification.id}>
              <div className="card-title-row">
                <div>
                  <p className="eyebrow">{notificationTypeLabel(notification.notification_type)}</p>
                  <h3>{notification.title}</h3>
                </div>
                <Badge tone={notification.is_read ? "muted" : "warning"}>
                  {notification.is_read ? "읽음" : "읽지 않음"}
                </Badge>
              </div>
              <p>{notification.message}</p>
              <div className="meta">
                <span>{new Date(notification.created_at).toLocaleString()}</span>
                {notification.related_reservation_id && <span>예약 관련 알림</span>}
                {notification.related_payment_id && <span>결제 관련 알림</span>}
                {notification.related_settlement_id && <span>정산 관련 알림</span>}
              </div>
              {!notification.is_read && (
                <div className="actions">
                  <button
                    type="button"
                    className="secondary"
                    onClick={() => markAsRead(notification.id)}
                    disabled={updatingId === notification.id}
                  >
                    {updatingId === notification.id ? "처리 중" : "읽음 처리"}
                  </button>
                </div>
              )}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
