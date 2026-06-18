import 'package:flutter/material.dart';

import '../state/auth_controller.dart';
import '../widgets/empty_state.dart';

class NotificationsScreen extends StatelessWidget {
  const NotificationsScreen({super.key, required this.authController});

  final AuthController authController;

  @override
  Widget build(BuildContext context) {
    if (!authController.isLoggedIn) {
      return const EmptyState(
        title: '로그인이 필요합니다.',
        description: '알림센터는 다음 Phase에서 API와 연결할 예정입니다.',
        icon: Icons.notifications_none,
      );
    }

    return const EmptyState(
      title: '알림센터 준비 중',
      description: '인앱 알림 API 연동은 다음 모바일 Phase에서 이어갑니다.',
      icon: Icons.notifications_active_outlined,
    );
  }
}
