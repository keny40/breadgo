import 'package:flutter/material.dart';

import '../models/product.dart';
import '../state/reservation_controller.dart';
import '../widgets/status_badge.dart';

class ProductDetailScreen extends StatefulWidget {
  const ProductDetailScreen({
    super.key,
    required this.product,
    required this.isLoggedIn,
    required this.reservationController,
    required this.onOpenReservations,
  });

  final Product product;
  final bool isLoggedIn;
  final ReservationController reservationController;
  final VoidCallback onOpenReservations;

  @override
  State<ProductDetailScreen> createState() => _ProductDetailScreenState();
}

class _ProductDetailScreenState extends State<ProductDetailScreen> {
  final _recipientNameController = TextEditingController();
  final _recipientPhoneController = TextEditingController();
  final _deliveryAddressController = TextEditingController();
  final _deliveryMemoController = TextEditingController();
  int _quantity = 1;
  late String _fulfillmentMethod;
  String? _localMessage;

  @override
  void initState() {
    super.initState();
    final availableMethods = widget.product.availableFulfillmentMethods;
    _fulfillmentMethod = availableMethods.isNotEmpty
        ? availableMethods.first
        : 'PICKUP';
    _recordProductEvent('DETAIL_VIEW');
  }

  @override
  void dispose() {
    _recipientNameController.dispose();
    _recipientPhoneController.dispose();
    _deliveryAddressController.dispose();
    _deliveryMemoController.dispose();
    super.dispose();
  }

  bool get _requiresDeliveryInfo => _fulfillmentMethod != 'PICKUP';
  double get _deliveryFee => widget.product.deliveryFeeFor(_fulfillmentMethod);
  double get _productAmount => widget.product.discountPrice * _quantity;
  double get _totalAmount => _productAmount + _deliveryFee;

  @override
  Widget build(BuildContext context) {
    final product = widget.product;
    return Scaffold(
      appBar: AppBar(title: const Text('상품 상세')),
      body: AnimatedBuilder(
        animation: widget.reservationController,
        builder: (context, _) {
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              _ProductHero(product: product),
              const SizedBox(height: 18),
              Row(
                children: [
                  Expanded(
                    child: Text(
                      product.name,
                      style: const TextStyle(
                        fontSize: 26,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ),
                  StatusBadge(label: '${product.discountPercent}% 할인'),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                product.storeName,
                style: const TextStyle(fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 4),
              Text(
                product.regionLabel,
                style: const TextStyle(color: Colors.black54),
              ),
              const SizedBox(height: 18),
              _PriceCard(product: product),
              const SizedBox(height: 16),
              _reservationCard(),
            ],
          );
        },
      ),
    );
  }

  Widget _reservationCard() {
    final controller = widget.reservationController;
    final availableMethods = widget.product.availableFulfillmentMethods;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '수령 방법을 선택해 주세요.',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
            ),
            const SizedBox(height: 12),
            if (availableMethods.isEmpty)
              const Text('이 상품은 현재 선택 가능한 수령 방식이 없습니다.')
            else
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: availableMethods
                    .map(
                      (method) => ChoiceChip(
                        label: Column(
                          mainAxisSize: MainAxisSize.min,
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(_fulfillmentLabel(method)),
                            Text(
                              _fulfillmentDescription(method),
                              style: const TextStyle(fontSize: 11),
                            ),
                          ],
                        ),
                        selected: _fulfillmentMethod == method,
                        onSelected: controller.submitting
                            ? null
                            : (_) =>
                                  setState(() => _fulfillmentMethod = method),
                      ),
                    )
                    .toList(),
              ),
            const Divider(height: 28),
            Row(
              children: [
                const Expanded(
                  child: Text(
                    '수량',
                    style: TextStyle(fontWeight: FontWeight.w800),
                  ),
                ),
                IconButton(
                  onPressed: controller.submitting || _quantity <= 1
                      ? null
                      : () => setState(() => _quantity--),
                  icon: const Icon(Icons.remove_circle_outline),
                ),
                Text(
                  '$_quantity',
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                IconButton(
                  onPressed:
                      controller.submitting ||
                          _quantity >= widget.product.quantity
                      ? null
                      : () => setState(() => _quantity++),
                  icon: const Icon(Icons.add_circle_outline),
                ),
              ],
            ),
            if (_requiresDeliveryInfo) ...[
              const SizedBox(height: 12),
              const Text(
                '배송 요청 정보',
                style: TextStyle(fontWeight: FontWeight.w900),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _recipientNameController,
                enabled: !controller.submitting,
                decoration: const InputDecoration(labelText: '받는 사람'),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _recipientPhoneController,
                enabled: !controller.submitting,
                keyboardType: TextInputType.phone,
                decoration: const InputDecoration(labelText: '받는 사람 연락처'),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _deliveryAddressController,
                enabled: !controller.submitting,
                decoration: const InputDecoration(labelText: '주소'),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _deliveryMemoController,
                enabled: !controller.submitting,
                maxLines: 2,
                decoration: const InputDecoration(labelText: '배송 요청사항'),
              ),
              const SizedBox(height: 8),
              const Text(
                '현재는 실제 배송 연동이 아닌 요청 정보 저장 단계입니다.',
                style: TextStyle(color: Colors.black54),
              ),
            ],
            const SizedBox(height: 16),
            _AmountRow(label: '상품 금액', amount: _productAmount),
            _AmountRow(label: '배송비', amount: _deliveryFee),
            const Divider(height: 22),
            _AmountRow(
              label: '총 고객 결제금액',
              amount: _totalAmount,
              emphasized: true,
            ),
            const SizedBox(height: 16),
            if (_localMessage != null)
              Text(_localMessage!, style: const TextStyle(color: Colors.red)),
            if (controller.errorMessage != null) ...[
              const SizedBox(height: 8),
              Text(
                controller.errorMessage!,
                style: const TextStyle(color: Colors.red),
              ),
            ],
            if (controller.successMessage != null &&
                controller.lastReservation != null) ...[
              const SizedBox(height: 8),
              _SuccessPanel(
                fulfillmentMethod:
                    controller.lastReservation!.fulfillmentMethod,
                pickupCode: controller.lastReservation!.pickupCode,
                paymentStatus: controller.lastPayment?.status,
                onOpenReservations: _openReservations,
              ),
            ],
            const SizedBox(height: 16),
            if (!widget.isLoggedIn)
              const Text(
                '예약하려면 로그인 탭에서 고객 계정으로 로그인해 주세요.',
                style: TextStyle(fontWeight: FontWeight.w700),
              )
            else
              FilledButton(
                onPressed: controller.submitting || availableMethods.isEmpty
                    ? null
                    : _submit,
                child: Text(
                  controller.submitting ? '예약/결제 처리 중' : '예약 생성 후 Mock 결제',
                ),
              ),
          ],
        ),
      ),
    );
  }

  Future<void> _submit() async {
    setState(() => _localMessage = null);

    if (_requiresDeliveryInfo) {
      final missingDeliveryInfo =
          _recipientNameController.text.trim().isEmpty ||
          _recipientPhoneController.text.trim().isEmpty ||
          _deliveryAddressController.text.trim().isEmpty;
      if (missingDeliveryInfo) {
        setState(() => _localMessage = '배송 수령자, 연락처, 주소를 입력해 주세요.');
        return;
      }
    }

    await _recordProductEvent('RESERVATION_STARTED');
    await widget.reservationController.createReservationAndPay(
      productId: widget.product.id,
      quantity: _quantity,
      fulfillmentMethod: _fulfillmentMethod,
      recipientName: _requiresDeliveryInfo
          ? _recipientNameController.text.trim()
          : null,
      recipientPhone: _requiresDeliveryInfo
          ? _recipientPhoneController.text.trim()
          : null,
      deliveryAddress: _requiresDeliveryInfo
          ? _deliveryAddressController.text.trim()
          : null,
      deliveryRequestMemo: _requiresDeliveryInfo
          ? _deliveryMemoController.text.trim()
          : null,
      deliveryFee: _deliveryFee,
    );
  }

  Future<void> _recordProductEvent(String eventType) async {
    try {
      await widget.reservationController.apiClient.recordProductEvent(
        productId: widget.product.id,
        eventType: eventType,
      );
    } catch (_) {
      // Product analytics should not block browsing or reservations.
    }
  }

  void _openReservations() {
    Navigator.of(context).pop();
    widget.onOpenReservations();
  }

  String _fulfillmentLabel(String method) {
    switch (method) {
      case 'QUICK_DELIVERY':
        return '퀵배달 요청';
      case 'PARCEL_DELIVERY':
        return '택배 배송';
      default:
        return '매장 직접 픽업';
    }
  }

  String _fulfillmentDescription(String method) {
    switch (method) {
      case 'QUICK_DELIVERY':
        return '배송비 ${widget.product.quickDeliveryFee.toStringAsFixed(0)}원 · MVP 요청 정보 저장';
      case 'PARCEL_DELIVERY':
        return '배송비 ${widget.product.parcelDeliveryFee.toStringAsFixed(0)}원 · 배송 가능 상품만 선택';
      default:
        return '배송비 0원 · 매장에서 픽업 코드를 보여주세요';
    }
  }
}

class _ProductHero extends StatelessWidget {
  const _ProductHero({required this.product});

  final Product product;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(18),
      child: product.imageUrl == null || product.imageUrl!.isEmpty
          ? Container(
              height: 220,
              color: const Color(0xFFE8F5EC),
              child: const Icon(
                Icons.bakery_dining,
                size: 64,
                color: Color(0xFF087A3A),
              ),
            )
          : Image.network(
              product.imageUrl!,
              height: 220,
              fit: BoxFit.cover,
              errorBuilder: (_, _, _) => Container(
                height: 220,
                color: const Color(0xFFE8F5EC),
                child: const Icon(
                  Icons.bakery_dining,
                  size: 64,
                  color: Color(0xFF087A3A),
                ),
              ),
            ),
    );
  }
}

class _PriceCard extends StatelessWidget {
  const _PriceCard({required this.product});

  final Product product;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '${product.discountPrice.toStringAsFixed(0)}원',
              style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w900),
            ),
            const SizedBox(height: 4),
            Text(
              '정가 ${product.originalPrice.toStringAsFixed(0)}원 · 남은 수량 ${product.quantity}개',
              style: const TextStyle(color: Colors.black54),
            ),
            const SizedBox(height: 12),
            Text(product.description ?? '상품 설명이 없습니다.'),
          ],
        ),
      ),
    );
  }
}

class _AmountRow extends StatelessWidget {
  const _AmountRow({
    required this.label,
    required this.amount,
    this.emphasized = false,
  });

  final String label;
  final double amount;
  final bool emphasized;

  @override
  Widget build(BuildContext context) {
    final style = TextStyle(
      fontSize: emphasized ? 18 : 14,
      fontWeight: emphasized ? FontWeight.w900 : FontWeight.w700,
    );
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        children: [
          Expanded(child: Text(label, style: style)),
          Text('${amount.toStringAsFixed(0)}원', style: style),
        ],
      ),
    );
  }
}

class _SuccessPanel extends StatelessWidget {
  const _SuccessPanel({
    required this.fulfillmentMethod,
    required this.pickupCode,
    required this.paymentStatus,
    required this.onOpenReservations,
  });

  final String fulfillmentMethod;
  final String pickupCode;
  final String? paymentStatus;
  final VoidCallback onOpenReservations;

  @override
  Widget build(BuildContext context) {
    final isPickup = fulfillmentMethod == 'PICKUP';
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFE8F5EC),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('예약과 Mock 결제가 완료되었습니다. 결제 상태: ${paymentStatus ?? 'PAID'}'),
          const SizedBox(height: 8),
          if (isPickup) ...[
            const Text(
              '매장에서 픽업 코드를 보여주세요.',
              style: TextStyle(fontWeight: FontWeight.w800),
            ),
            Text(
              pickupCode,
              style: const TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.w900,
                letterSpacing: 2,
              ),
            ),
          ] else
            const Text('배송 요청이 접수되었습니다. 내 예약에서 상태를 확인해 주세요.'),
          const SizedBox(height: 12),
          OutlinedButton(
            onPressed: onOpenReservations,
            child: const Text('내 예약 보기'),
          ),
        ],
      ),
    );
  }
}
