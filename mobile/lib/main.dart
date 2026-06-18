import 'package:flutter/material.dart';

import 'core/api_client.dart';
import 'core/app_config.dart';
import 'core/session_store.dart';
import 'screens/login_screen.dart';
import 'screens/notifications_screen.dart';
import 'screens/product_list_screen.dart';
import 'screens/reservations_screen.dart';
import 'state/auth_controller.dart';
import 'state/notification_controller.dart';
import 'state/product_controller.dart';
import 'state/reservation_controller.dart';

void main() {
  final sessionStore = SessionStore();
  final apiClient = ApiClient(
    baseUrl: AppConfig.apiBaseUrl,
    sessionStore: sessionStore,
  );
  runApp(
    BreadGoApp(
      authController: AuthController(apiClient: apiClient),
      productController: ProductController(apiClient: apiClient),
      reservationController: ReservationController(apiClient: apiClient),
      notificationController: NotificationController(apiClient: apiClient),
    ),
  );
}

class BreadGoApp extends StatefulWidget {
  const BreadGoApp({
    super.key,
    required this.authController,
    required this.productController,
    required this.reservationController,
    required this.notificationController,
  });

  final AuthController authController;
  final ProductController productController;
  final ReservationController reservationController;
  final NotificationController notificationController;

  @override
  State<BreadGoApp> createState() => _BreadGoAppState();
}

class _BreadGoAppState extends State<BreadGoApp> {
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'BreadGo',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF087A3A),
          primary: const Color(0xFF087A3A),
          secondary: const Color(0xFFFFB84D),
          surface: const Color(0xFFFFFCF5),
        ),
        scaffoldBackgroundColor: const Color(0xFFFFFCF5),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFFFFFCF5),
          foregroundColor: Color(0xFF092018),
          elevation: 0,
          centerTitle: false,
        ),
        cardTheme: CardThemeData(
          color: Colors.white,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side: const BorderSide(color: Color(0xFFE3E8DE)),
          ),
        ),
        filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
            backgroundColor: const Color(0xFF087A3A),
            foregroundColor: Colors.white,
            minimumSize: const Size.fromHeight(48),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),
      ),
      home: AnimatedBuilder(
        animation: Listenable.merge([
          widget.authController,
          widget.notificationController,
        ]),
        builder: (context, _) {
          final pages = [
            ProductListScreen(
              authController: widget.authController,
              productController: widget.productController,
              reservationController: widget.reservationController,
              onOpenReservations: () => setState(() => _selectedIndex = 1),
            ),
            ReservationsScreen(
              authController: widget.authController,
              reservationController: widget.reservationController,
            ),
            NotificationsScreen(
              authController: widget.authController,
              notificationController: widget.notificationController,
            ),
            LoginScreen(authController: widget.authController),
          ];

          return Scaffold(
            appBar: AppBar(
              title: const Text('BreadGo'),
              actions: [
                Padding(
                  padding: const EdgeInsets.only(right: 16),
                  child: Center(
                    child: Text(
                      widget.authController.user?.email ?? '고객 앱 MVP',
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                  ),
                ),
              ],
            ),
            body: SafeArea(child: pages[_selectedIndex]),
            bottomNavigationBar: NavigationBar(
              selectedIndex: _selectedIndex,
              onDestinationSelected: (index) =>
                  setState(() => _selectedIndex = index),
              destinations: [
                const NavigationDestination(
                  icon: Icon(Icons.storefront_outlined),
                  label: '상품',
                ),
                const NavigationDestination(
                  icon: Icon(Icons.receipt_long_outlined),
                  label: '내 예약',
                ),
                NavigationDestination(
                  icon: _NotificationIcon(
                    unreadCount: widget.authController.isLoggedIn
                        ? widget.notificationController.unreadCount
                        : 0,
                  ),
                  label: '알림',
                ),
                const NavigationDestination(
                  icon: Icon(Icons.person_outline),
                  label: '로그인',
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}

class _NotificationIcon extends StatelessWidget {
  const _NotificationIcon({required this.unreadCount});

  final int unreadCount;

  @override
  Widget build(BuildContext context) {
    return Badge(
      isLabelVisible: unreadCount > 0,
      label: Text(unreadCount > 99 ? '99+' : '$unreadCount'),
      child: const Icon(Icons.notifications_outlined),
    );
  }
}
