import 'package:flutter/material.dart';

import '../models/reservation.dart';
import 'status_badge.dart';

class ReservationCard extends StatelessWidget {
  const ReservationCard({
    super.key,
    required this.reservation,
    this.onCancel,
    this.onShowHistory,
    this.isCancelling = false,
    this.isLoadingHistory = false,
  });

  final Reservation reservation;
  final VoidCallback? onCancel;
  final VoidCallback? onShowHistory;
  final bool isCancelling;
  final bool isLoadingHistory;

  @override
  Widget build(BuildContext context) {
    final isPickup = reservation.fulfillmentMethod == 'PICKUP';
    return Card(
      margin: const EdgeInsets.only(bottom: 14),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    reservation.productName,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ),
                StatusBadge(label: reservation.status),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              reservation.storeName,
              style: const TextStyle(fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                StatusBadge(label: reservation.paymentStatus ?? '결제 상태 없음'),
                StatusBadge(
                  label: _fulfillmentLabel(reservation.fulfillmentMethod),
                  color: Colors.orange.shade700,
                ),
                if (!isPickup)
                  StatusBadge(
                    label: reservation.deliveryStatus,
                    color: Colors.blue.shade700,
                  ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              '수량 ${reservation.quantity}개 · 상품 ${reservation.productAmount.toStringAsFixed(0)}원 · 배송비 ${reservation.deliveryFee.toStringAsFixed(0)}원',
            ),
            const SizedBox(height: 4),
            Text(
              '총 고객 결제금액 ${reservation.totalPrice.toStringAsFixed(0)}원',
              style: const TextStyle(fontWeight: FontWeight.w900),
            ),
            if (isPickup) ...[
              const SizedBox(height: 12),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: const Color(0xFFE8F5EC),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      '픽업 코드',
                      style: TextStyle(fontWeight: FontWeight.w700),
                    ),
                    Text(
                      reservation.pickupCode,
                      style: const TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 2,
                      ),
                    ),
                  ],
                ),
              ),
            ],
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: isLoadingHistory ? null : onShowHistory,
              icon: const Icon(Icons.history),
              label: Text(isLoadingHistory ? '이력 불러오는 중' : '상태 이력 보기'),
            ),
            const SizedBox(height: 8),
            if (reservation.canCancel)
              OutlinedButton.icon(
                onPressed: isCancelling ? null : onCancel,
                icon: const Icon(Icons.cancel_outlined),
                label: Text(isCancelling ? '취소 처리 중' : '예약 취소'),
              )
            else
              Text(
                _cancelGuide(reservation),
                style: const TextStyle(color: Colors.black54, fontSize: 12),
              ),
          ],
        ),
      ),
    );
  }

  String _fulfillmentLabel(String value) {
    switch (value) {
      case 'QUICK_DELIVERY':
        return '퀵배달';
      case 'PARCEL_DELIVERY':
        return '택배';
      default:
        return '매장 픽업';
    }
  }

  String _cancelGuide(Reservation reservation) {
    if (reservation.status == 'CANCELLED') {
      return '취소된 예약입니다. Mock 환불 상태를 확인해 주세요.';
    }
    if (reservation.status == 'PICKED_UP') {
      return '픽업 완료된 예약은 취소할 수 없습니다.';
    }
    if (reservation.deliveryStatus == 'SENT' ||
        reservation.deliveryStatus == 'DELIVERED') {
      return '배송이 시작되었거나 완료되어 취소할 수 없습니다.';
    }
    if (reservation.paymentStatus != 'PAID') {
      return '결제 완료 후 취소할 수 있습니다.';
    }
    return '현재 상태에서는 취소할 수 없습니다.';
  }
}
