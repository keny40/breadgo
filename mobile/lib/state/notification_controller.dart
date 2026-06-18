import 'package:flutter/foundation.dart';

import '../core/api_client.dart';
import '../models/notification_item.dart';

class NotificationController extends ChangeNotifier {
  NotificationController({required this.apiClient});

  final ApiClient apiClient;

  List<NotificationItem> notifications = [];
  bool loading = false;
  bool updating = false;
  String? errorMessage;
  String? successMessage;

  int get unreadCount =>
      notifications.where((notification) => !notification.isRead).length;

  Future<void> loadNotifications() async {
    loading = true;
    errorMessage = null;
    successMessage = null;
    notifyListeners();

    try {
      notifications = await apiClient.fetchMyNotifications();
    } on ApiException catch (error) {
      errorMessage = _friendlyError(error.message);
    } catch (_) {
      errorMessage = '알림을 불러오지 못했습니다.';
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  Future<void> markAsRead(String notificationId) async {
    updating = true;
    errorMessage = null;
    successMessage = null;
    notifyListeners();

    try {
      final updated = await apiClient.markNotificationAsRead(
        notificationId: notificationId,
      );
      notifications = notifications
          .map((item) => item.id == updated.id ? updated : item)
          .toList();
      successMessage = '알림을 읽음 처리했습니다.';
    } on ApiException catch (error) {
      errorMessage = _friendlyError(error.message);
    } catch (_) {
      errorMessage = '알림 읽음 처리에 실패했습니다.';
    } finally {
      updating = false;
      notifyListeners();
    }
  }

  Future<void> markAllAsRead() async {
    updating = true;
    errorMessage = null;
    successMessage = null;
    notifyListeners();

    try {
      notifications = await apiClient.markAllNotificationsAsRead();
      successMessage = '모든 알림을 읽음 처리했습니다.';
    } on ApiException catch (error) {
      errorMessage = _friendlyError(error.message);
    } catch (_) {
      errorMessage = '전체 읽음 처리에 실패했습니다.';
    } finally {
      updating = false;
      notifyListeners();
    }
  }

  String _friendlyError(String message) {
    final lower = message.toLowerCase();
    if (lower.contains('authentication') || lower.contains('401')) {
      return '로그인이 필요합니다. 다시 로그인해 주세요.';
    }
    return message;
  }
}
