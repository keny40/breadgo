class Payment {
  Payment({
    required this.id,
    required this.reservationId,
    required this.amount,
    required this.method,
    required this.provider,
    required this.status,
  });

  final String id;
  final String reservationId;
  final double amount;
  final String method;
  final String provider;
  final String status;

  factory Payment.fromJson(Map<String, dynamic> json) {
    return Payment(
      id: json['id'] as String? ?? '',
      reservationId: json['reservation_id'] as String? ?? '',
      amount: _toDouble(json['amount']),
      method: json['method'] as String? ?? 'MOCK_CARD',
      provider: json['provider'] as String? ?? 'MOCK',
      status: json['status'] as String? ?? '',
    );
  }
}

double _toDouble(dynamic value) {
  if (value is num) {
    return value.toDouble();
  }
  return double.tryParse(value?.toString() ?? '') ?? 0;
}
