import 'package:flutter_test/flutter_test.dart';

import 'package:breadgo_mobile/core/api_client.dart';
import 'package:breadgo_mobile/core/session_store.dart';
import 'package:breadgo_mobile/main.dart';
import 'package:breadgo_mobile/state/auth_controller.dart';
import 'package:breadgo_mobile/state/notification_controller.dart';
import 'package:breadgo_mobile/state/product_controller.dart';
import 'package:breadgo_mobile/state/reservation_controller.dart';

void main() {
  testWidgets('BreadGo app renders product tab', (WidgetTester tester) async {
    final sessionStore = SessionStore();
    final apiClient = ApiClient(
      baseUrl: 'http://127.0.0.1:8000',
      sessionStore: sessionStore,
    );

    await tester.pumpWidget(
      BreadGoApp(
        authController: AuthController(apiClient: apiClient),
        productController: ProductController(apiClient: apiClient),
        reservationController: ReservationController(apiClient: apiClient),
        notificationController: NotificationController(apiClient: apiClient),
      ),
    );

    expect(find.text('BreadGo'), findsOneWidget);
    expect(find.text('상품 보기'), findsOneWidget);
  });
}
