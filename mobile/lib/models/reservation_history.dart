class ReservationHistoryItem {
  ReservationHistoryItem({
    required this.id,
    required this.reservationId,
    required this.eventType,
    required this.message,
    required this.createdAt,
    this.actorUserId,
    this.actorRole,
    this.actorEmail,
    this.fromStatus,
    this.toStatus,
  });

  final String id;
  final String reservationId;
  final String? actorUserId;
  final String? actorRole;
  final String? actorEmail;
  final String eventType;
  final String? fromStatus;
  final String? toStatus;
  final String message;
  final DateTime createdAt;

  factory ReservationHistoryItem.fromJson(Map<String, dynamic> json) {
    return ReservationHistoryItem(
      id: json['id'] as String? ?? '',
      reservationId: json['reservation_id'] as String? ?? '',
      actorUserId: json['actor_user_id'] as String?,
      actorRole: json['actor_role'] as String?,
      actorEmail: json['actor_email'] as String?,
      eventType: json['event_type'] as String? ?? '',
      fromStatus: json['from_status'] as String?,
      toStatus: json['to_status'] as String?,
      message: json['message'] as String? ?? '',
      createdAt: _toDateTime(json['created_at']),
    );
  }

  String get eventLabel {
    switch (eventType) {
      case 'RESERVATION_CREATED':
        return '예약 생성';
      case 'PAYMENT_COMPLETED':
        return '결제 완료';
      case 'PICKUP_CONFIRMED':
        return '픽업 완료';
      case 'DELIVERY_STATUS_CHANGED':
        return '배송 상태 변경';
      case 'RESERVATION_CANCELLED':
        return '예약 취소';
      case 'MOCK_REFUND_PROCESSED':
        return 'Mock 환불 처리';
      case 'SETTLEMENT_STATUS_CHANGED':
        return '정산 상태 변경';
      default:
        return eventType;
    }
  }

  String get actorLabel {
    if (actorEmail != null && actorEmail!.isNotEmpty) {
      return actorEmail!;
    }
    if (actorRole != null && actorRole!.isNotEmpty) {
      return actorRole!;
    }
    return '시스템';
  }
}

DateTime _toDateTime(dynamic value) {
  return DateTime.tryParse(value?.toString() ?? '') ??
      DateTime.fromMillisecondsSinceEpoch(0);
}
