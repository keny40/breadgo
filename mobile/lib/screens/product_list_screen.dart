import 'package:flutter/material.dart';

import '../models/product.dart';
import '../state/auth_controller.dart';
import '../state/product_controller.dart';
import '../state/reservation_controller.dart';
import '../widgets/empty_state.dart';
import '../widgets/product_card.dart';
import 'product_detail_screen.dart';

class ProductListScreen extends StatefulWidget {
  const ProductListScreen({
    super.key,
    required this.authController,
    required this.productController,
    required this.reservationController,
    required this.onOpenReservations,
  });

  final AuthController authController;
  final ProductController productController;
  final ReservationController reservationController;
  final VoidCallback onOpenReservations;

  @override
  State<ProductListScreen> createState() => _ProductListScreenState();
}

class _ProductListScreenState extends State<ProductListScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(widget.productController.loadProducts);
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: widget.productController,
      builder: (context, _) {
        return RefreshIndicator(
          onRefresh: widget.productController.loadProducts,
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              const Text(
                '상품 보기',
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.w900),
              ),
              const SizedBox(height: 6),
              Text(
                '${widget.productController.sido} ${widget.productController.sigungu} ${widget.productController.dong}',
                style: const TextStyle(color: Colors.black54),
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _RegionChip(
                    label: '역삼동',
                    onTap: () => widget.productController.loadProducts(
                      nextSido: '서울특별시',
                      nextSigungu: '강남구',
                      nextDong: '역삼동',
                    ),
                  ),
                  _RegionChip(
                    label: '삼성동',
                    onTap: () => widget.productController.loadProducts(
                      nextSido: '서울특별시',
                      nextSigungu: '강남구',
                      nextDong: '삼성동',
                    ),
                  ),
                  _RegionChip(
                    label: '고잔동',
                    onTap: () => widget.productController.loadProducts(
                      nextSido: '경기도',
                      nextSigungu: '안산시',
                      nextDong: '고잔동',
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              if (widget.productController.loading)
                const Padding(
                  padding: EdgeInsets.only(top: 80),
                  child: Center(child: CircularProgressIndicator()),
                )
              else if (widget.productController.errorMessage != null)
                EmptyState(
                  title: '상품을 불러오지 못했습니다.',
                  description: widget.productController.errorMessage,
                  icon: Icons.wifi_off_outlined,
                  actionLabel: '다시 불러오기',
                  onAction: widget.productController.loadProducts,
                )
              else if (widget.productController.products.isEmpty)
                EmptyState(
                  title: '선택한 지역에 판매 중인 상품이 없습니다.',
                  description: '다른 지역을 선택하거나 잠시 후 다시 확인해 주세요.',
                  icon: Icons.bakery_dining_outlined,
                  actionLabel: '새로고침',
                  onAction: widget.productController.loadProducts,
                )
              else
                ...widget.productController.products.map(
                  (product) => ProductCard(
                    product: product,
                    onTap: () => _openProductDetail(product),
                  ),
                ),
            ],
          ),
        );
      },
    );
  }

  void _openProductDetail(Product product) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => ProductDetailScreen(
          product: product,
          isLoggedIn: widget.authController.isLoggedIn,
          reservationController: widget.reservationController,
          onOpenReservations: widget.onOpenReservations,
        ),
      ),
    );
  }
}

class _RegionChip extends StatelessWidget {
  const _RegionChip({required this.label, required this.onTap});

  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return ActionChip(
      label: Text(label),
      onPressed: onTap,
      backgroundColor: const Color(0xFFE8F5EC),
      labelStyle: const TextStyle(
        color: Color(0xFF087A3A),
        fontWeight: FontWeight.w800,
      ),
    );
  }
}
