import 'package:flutter/material.dart';

import '../models/notification_item.dart';
import '../state/auth_controller.dart';
import '../state/notification_controller.dart';
import '../widgets/empty_state.dart';
import '../widgets/status_badge.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({
    super.key,
    required this.authController,
    required this.notificationController,
  });

  final AuthController authController;
  final NotificationController notificationController;

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  @override
  void initState() {
    super.initState();
    widget.authController.addListener(_loadAfterLogin);
    _loadAfterLogin();
  }

  @override
  void dispose() {
    widget.authController.removeListener(_loadAfterLogin);
    super.dispose();
  }

  void _loadAfterLogin() {
    if (widget.authController.isLoggedIn &&
        widget.notificationController.notifications.isEmpty) {
      widget.notificationController.loadNotifications();
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.authController.isLoggedIn) {
      return const EmptyState(
        title: '로그인이 필요합니다.',
        description: '알림을 보려면 고객 계정으로 로그인해 주세요.',
        icon: Icons.notifications_none,
      );
    }

    return AnimatedBuilder(
      animation: widget.notificationController,
      builder: (context, _) {
        final controller = widget.notificationController;
        return RefreshIndicator(
          onRefresh: controller.loadNotifications,
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      '알림',
                      style: Theme.of(context).textTheme.headlineSmall
                          ?.copyWith(fontWeight: FontWeight.w900),
                    ),
                  ),
                  TextButton.icon(
                    onPressed:
                        controller.updating || controller.notifications.isEmpty
                        ? null
                        : controller.markAllAsRead,
                    icon: const Icon(Icons.done_all),
                    label: const Text('모두 읽음'),
                  ),
                  IconButton(
                    onPressed: controller.loadNotifications,
                    icon: const Icon(Icons.refresh),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Text(
                '읽지 않은 알림 ${controller.unreadCount}개',
                style: const TextStyle(color: Colors.black54),
              ),
              if (controller.errorMessage != null) ...[
                const SizedBox(height: 12),
                Text(
                  controller.errorMessage!,
                  style: const TextStyle(color: Colors.red),
                ),
              ],
              if (controller.successMessage != null) ...[
                const SizedBox(height: 12),
                Text(
                  controller.successMessage!,
                  style: const TextStyle(color: Color(0xFF087A3A)),
                ),
              ],
              const SizedBox(height: 12),
              if (controller.loading)
                const Padding(
                  padding: EdgeInsets.only(top: 80),
                  child: Center(child: CircularProgressIndicator()),
                )
              else if (controller.notifications.isEmpty)
                const EmptyState(
                  title: '알림이 없습니다.',
                  description: '예약, 결제, 픽업, 환불 상태가 바뀌면 여기에 표시됩니다.',
                  icon: Icons.notifications_active_outlined,
                )
              else
                ...controller.notifications.map(
                  (notification) => _NotificationCard(
                    notification: notification,
                    updating: controller.updating,
                    onMarkAsRead: () => controller.markAsRead(notification.id),
                  ),
                ),
            ],
          ),
        );
      },
    );
  }
}

class _NotificationCard extends StatelessWidget {
  const _NotificationCard({
    required this.notification,
    required this.updating,
    required this.onMarkAsRead,
  });

  final NotificationItem notification;
  final bool updating;
  final VoidCallback onMarkAsRead;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 14),
      color: notification.isRead ? Colors.white : const Color(0xFFF3FFF6),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    notification.title,
                    style: const TextStyle(
                      fontSize: 17,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ),
                StatusBadge(
                  label: notification.isRead ? '읽음' : '읽지 않음',
                  color: notification.isRead
                      ? Colors.grey.shade700
                      : const Color(0xFF087A3A),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(notification.message),
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                StatusBadge(
                  label: _typeLabel(notification.notificationType),
                  color: Colors.orange.shade700,
                ),
                Text(
                  _formatDateTime(notification.createdAt),
                  style: const TextStyle(color: Colors.black54, fontSize: 12),
                ),
              ],
            ),
            if (!notification.isRead) ...[
              const SizedBox(height: 12),
              OutlinedButton(
                onPressed: updating ? null : onMarkAsRead,
                child: const Text('읽음 처리'),
              ),
            ],
          ],
        ),
      ),
    );
  }

  String _typeLabel(String type) {
    switch (type) {
      case 'PAYMENT_COMPLETED':
        return '결제 완료';
      case 'PICKUP_CONFIRMED':
        return '픽업 완료';
      case 'DELIVERY_STATUS_CHANGED':
        return '배송 상태';
      case 'RESERVATION_CANCELLED':
        return '예약 취소';
      case 'MOCK_REFUNDED':
        return 'Mock 환불';
      case 'SETTLEMENT_READY':
        return '정산 가능';
      case 'SETTLEMENT_PAID':
        return '정산 완료';
      case 'SETTLEMENT_HOLD':
        return '정산 보류';
      default:
        return type;
    }
  }

  String _formatDateTime(DateTime value) {
    return '${value.year}.${_twoDigits(value.month)}.${_twoDigits(value.day)} '
        '${_twoDigits(value.hour)}:${_twoDigits(value.minute)}';
  }

  String _twoDigits(int value) => value.toString().padLeft(2, '0');
}
