import 'package:flutter/material.dart';

import '../state/auth_controller.dart';
import '../state/reservation_controller.dart';
import '../widgets/empty_state.dart';
import '../widgets/reservation_card.dart';

class ReservationsScreen extends StatefulWidget {
  const ReservationsScreen({
    super.key,
    required this.authController,
    required this.reservationController,
  });

  final AuthController authController;
  final ReservationController reservationController;

  @override
  State<ReservationsScreen> createState() => _ReservationsScreenState();
}

class _ReservationsScreenState extends State<ReservationsScreen> {
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
        widget.reservationController.reservations.isEmpty) {
      widget.reservationController.loadMyReservations();
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.authController.isLoggedIn) {
      return const EmptyState(
        title: '로그인이 필요합니다.',
        description: '내 예약을 보려면 고객 계정으로 로그인해 주세요.',
        icon: Icons.lock_outline,
      );
    }

    return AnimatedBuilder(
      animation: widget.reservationController,
      builder: (context, _) {
        return RefreshIndicator(
          onRefresh: widget.reservationController.loadMyReservations,
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Row(
                children: [
                  const Expanded(
                    child: Text(
                      '내 예약',
                      style: TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ),
                  IconButton(
                    onPressed: widget.reservationController.loadMyReservations,
                    icon: const Icon(Icons.refresh),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              if (widget.reservationController.loading)
                const Padding(
                  padding: EdgeInsets.only(top: 80),
                  child: Center(child: CircularProgressIndicator()),
                )
              else if (widget.reservationController.errorMessage != null)
                EmptyState(
                  title: '예약 내역을 불러오지 못했습니다.',
                  description: widget.reservationController.errorMessage,
                  icon: Icons.receipt_long_outlined,
                )
              else if (widget.reservationController.reservations.isEmpty)
                const EmptyState(
                  title: '예약 내역이 없습니다.',
                  description: '상품 탭에서 마감 할인 상품을 둘러보세요.',
                  icon: Icons.receipt_long_outlined,
                )
              else
                ...widget.reservationController.reservations.map(
                  (reservation) => ReservationCard(reservation: reservation),
                ),
            ],
          ),
        );
      },
    );
  }
}
