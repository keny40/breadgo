class Reservation {
  Reservation({
    required this.id,
    required this.productName,
    required this.storeName,
    required this.quantity,
    required this.productAmount,
    required this.deliveryFee,
    required this.totalPrice,
    required this.fulfillmentMethod,
    required this.deliveryStatus,
    required this.status,
    required this.pickupCode,
    required this.pickupDeadline,
    required this.createdAt,
    this.paymentStatus,
  });

  final String id;
  final String productName;
  final String storeName;
  final int quantity;
  final double productAmount;
  final double deliveryFee;
  final double totalPrice;
  final String fulfillmentMethod;
  final String deliveryStatus;
  final String status;
  final String pickupCode;
  final DateTime pickupDeadline;
  final DateTime createdAt;
  final String? paymentStatus;

  factory Reservation.fromJson(Map<String, dynamic> json) {
    return Reservation(
      id: json['id'] as String? ?? '',
      productName: json['product_name'] as String? ?? '상품 정보 없음',
      storeName: json['store_name'] as String? ?? '매장 정보 없음',
      quantity: json['quantity'] as int? ?? 0,
      productAmount: _toDouble(json['product_amount']),
      deliveryFee: _toDouble(json['delivery_fee']),
      totalPrice: _toDouble(json['total_price']),
      fulfillmentMethod: json['fulfillment_method'] as String? ?? 'PICKUP',
      deliveryStatus: json['delivery_status'] as String? ?? 'NOT_REQUIRED',
      status: json['status'] as String? ?? '',
      pickupCode: json['pickup_code'] as String? ?? '',
      pickupDeadline: _toDateTime(json['pickup_deadline']),
      createdAt: _toDateTime(json['created_at']),
      paymentStatus: json['payment_status'] as String?,
    );
  }
}

double _toDouble(dynamic value) {
  if (value is num) {
    return value.toDouble();
  }
  return double.tryParse(value?.toString() ?? '') ?? 0;
}

DateTime _toDateTime(dynamic value) {
  return DateTime.tryParse(value?.toString() ?? '') ??
      DateTime.fromMillisecondsSinceEpoch(0);
}
