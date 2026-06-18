class Product {
  Product({
    required this.id,
    required this.storeId,
    required this.name,
    required this.storeName,
    required this.storeAddress,
    required this.originalPrice,
    required this.discountPrice,
    required this.quantity,
    required this.pickupStartTime,
    required this.pickupEndTime,
    required this.status,
    required this.allowPickup,
    required this.allowQuickDelivery,
    required this.allowParcelDelivery,
    required this.quickDeliveryFee,
    required this.parcelDeliveryFee,
    this.description,
    this.imageUrl,
    this.sido,
    this.sigungu,
    this.dong,
    this.distanceKm,
  });

  final String id;
  final String storeId;
  final String name;
  final String? description;
  final String? imageUrl;
  final String storeName;
  final String storeAddress;
  final String? sido;
  final String? sigungu;
  final String? dong;
  final double? distanceKm;
  final double originalPrice;
  final double discountPrice;
  final int quantity;
  final DateTime pickupStartTime;
  final DateTime pickupEndTime;
  final String status;
  final bool allowPickup;
  final bool allowQuickDelivery;
  final bool allowParcelDelivery;
  final double quickDeliveryFee;
  final double parcelDeliveryFee;

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'] as String? ?? '',
      storeId: json['store_id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      description: json['description'] as String?,
      imageUrl: json['image_url'] as String?,
      storeName: json['store_name'] as String? ?? '매장 정보 없음',
      storeAddress: json['store_address'] as String? ?? '',
      sido: json['sido'] as String?,
      sigungu: json['sigungu'] as String?,
      dong: json['dong'] as String?,
      distanceKm: _toNullableDouble(json['distance_km']),
      originalPrice: _toDouble(json['original_price']),
      discountPrice: _toDouble(json['discount_price']),
      quantity: json['quantity'] as int? ?? 0,
      pickupStartTime: _toDateTime(json['pickup_start_time']),
      pickupEndTime: _toDateTime(json['pickup_end_time']),
      status: json['status'] as String? ?? 'ACTIVE',
      allowPickup: json['allow_pickup'] as bool? ?? true,
      allowQuickDelivery: json['allow_quick_delivery'] as bool? ?? false,
      allowParcelDelivery: json['allow_parcel_delivery'] as bool? ?? false,
      quickDeliveryFee: _toDouble(json['quick_delivery_fee']),
      parcelDeliveryFee: _toDouble(json['parcel_delivery_fee']),
    );
  }

  int get discountPercent {
    if (originalPrice <= 0) {
      return 0;
    }
    return ((1 - (discountPrice / originalPrice)) * 100).round();
  }

  String get regionLabel {
    final parts = [
      sido,
      sigungu,
      dong,
    ].where((part) => part != null && part.isNotEmpty).join(' ');
    return parts.isEmpty ? storeAddress : parts;
  }

  List<String> get availableFulfillmentMethods {
    return [
      if (allowPickup) 'PICKUP',
      if (allowQuickDelivery) 'QUICK_DELIVERY',
      if (allowParcelDelivery) 'PARCEL_DELIVERY',
    ];
  }

  double deliveryFeeFor(String fulfillmentMethod) {
    switch (fulfillmentMethod) {
      case 'QUICK_DELIVERY':
        return quickDeliveryFee;
      case 'PARCEL_DELIVERY':
        return parcelDeliveryFee;
      default:
        return 0;
    }
  }
}

double _toDouble(dynamic value) {
  if (value is num) {
    return value.toDouble();
  }
  return double.tryParse(value?.toString() ?? '') ?? 0;
}

double? _toNullableDouble(dynamic value) {
  if (value == null) {
    return null;
  }
  return _toDouble(value);
}

DateTime _toDateTime(dynamic value) {
  return DateTime.tryParse(value?.toString() ?? '') ??
      DateTime.fromMillisecondsSinceEpoch(0);
}
