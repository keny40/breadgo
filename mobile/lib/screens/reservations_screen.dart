import 'package:flutter/material.dart';

import '../state/auth_controller.dart';
import '../state/reservation_controller.dart';
import '../widgets/empty_state.dart';
import '../widgets/reservation_card.dart';
import '../widgets/reservation_history_sheet.dart';

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
        description: '내 예약을 보려면 로그인 탭에서 고객 계정으로 로그인해 주세요.',
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
              if (widget.reservationController.successMessage != null) ...[
                Text(
                  widget.reservationController.successMessage!,
                  style: const TextStyle(color: Color(0xFF087A3A)),
                ),
                const SizedBox(height: 12),
              ],
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
                  actionLabel: '다시 불러오기',
                  onAction: widget.reservationController.loadMyReservations,
                )
              else if (widget.reservationController.reservations.isEmpty)
                const EmptyState(
                  title: '예약 내역이 없습니다.',
                  description: '상품 탭에서 마감 할인 상품을 둘러보세요.',
                  icon: Icons.receipt_long_outlined,
                )
              else
                ...widget.reservationController.reservations.map(
                  (reservation) => ReservationCard(
                    reservation: reservation,
                    isCancelling: widget.reservationController.isCancelling(
                      reservation.id,
                    ),
                    isLoadingHistory: widget.reservationController
                        .isLoadingHistory(reservation.id),
                    onShowHistory: () => _showHistory(reservation.id),
                    onCancel: reservation.canCancel
                        ? () => _confirmCancel(reservation.id)
                        : null,
                  ),
                ),
            ],
          ),
        );
      },
    );
  }

  Future<void> _confirmCancel(String reservationId) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('예약 취소'),
        content: const Text('예약을 취소하시겠습니까? MVP에서는 실제 카드 환불이 아닌 Mock 환불 처리입니다.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('아니요'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('예약 취소'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      await widget.reservationController.cancelReservation(reservationId);
    }
  }

  Future<void> _showHistory(String reservationId) async {
    final history = await widget.reservationController.loadReservationHistory(
      reservationId,
    );
    if (!mounted) {
      return;
    }

    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (context) => ReservationHistorySheet(
        history: history,
        errorMessage: widget.reservationController.historyErrorMessage,
      ),
    );
  }
}
