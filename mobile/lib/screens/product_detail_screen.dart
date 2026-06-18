import 'package:flutter/material.dart';

import '../models/product.dart';
import '../widgets/status_badge.dart';

class ProductDetailScreen extends StatelessWidget {
  const ProductDetailScreen({
    super.key,
    required this.product,
    required this.isLoggedIn,
  });

  final Product product;
  final bool isLoggedIn;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('상품 상세')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          ClipRRect(
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
          ),
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
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '${product.discountPrice.toStringAsFixed(0)}원',
                    style: const TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.w900,
                    ),
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
          ),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Text(
                isLoggedIn
                    ? '예약과 Mock 결제는 다음 모바일 Phase에서 연결합니다. 현재는 웹과 동일한 백엔드 상품 조회 구조를 확인하는 단계입니다.'
                    : '예약하려면 로그인 탭에서 고객 계정으로 로그인해 주세요.',
                style: const TextStyle(fontWeight: FontWeight.w700),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
