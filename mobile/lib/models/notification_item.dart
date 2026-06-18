class NotificationItem {
  NotificationItem({
    required this.id,
    required this.title,
    required this.message,
    required this.notificationType,
    required this.isRead,
    required this.createdAt,
    this.relatedReservationId,
    this.relatedPaymentId,
    this.relatedSettlementId,
    this.readAt,
  });

  final String id;
  final String title;
  final String message;
  final String notificationType;
  final bool isRead;
  final DateTime createdAt;
  final String? relatedReservationId;
  final String? relatedPaymentId;
  final String? relatedSettlementId;
  final DateTime? readAt;

  factory NotificationItem.fromJson(Map<String, dynamic> json) {
    return NotificationItem(
      id: json['id'] as String? ?? '',
      title: json['title'] as String? ?? '',
      message: json['message'] as String? ?? '',
      notificationType: json['notification_type'] as String? ?? '',
      isRead: json['is_read'] as bool? ?? false,
      createdAt: _toDateTime(json['created_at']),
      relatedReservationId: json['related_reservation_id'] as String?,
      relatedPaymentId: json['related_payment_id'] as String?,
      relatedSettlementId: json['related_settlement_id'] as String?,
      readAt: json['read_at'] == null ? null : _toDateTime(json['read_at']),
    );
  }
}

DateTime _toDateTime(dynamic value) {
  return DateTime.tryParse(value?.toString() ?? '') ??
      DateTime.fromMillisecondsSinceEpoch(0);
}
