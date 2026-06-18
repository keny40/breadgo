import 'package:flutter/material.dart';

import '../models/reservation.dart';
import 'status_badge.dart';

class ReservationCard extends StatelessWidget {
  const ReservationCard({super.key, required this.reservation});

  final Reservation reservation;

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
              '수량 ${reservation.quantity}개 · 총 ${reservation.totalPrice.toStringAsFixed(0)}원',
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
}
