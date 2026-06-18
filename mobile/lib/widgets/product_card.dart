import 'package:flutter/material.dart';

import '../models/product.dart';
import 'status_badge.dart';

class ProductCard extends StatelessWidget {
  const ProductCard({super.key, required this.product, required this.onTap});

  final Product product;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 14),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: product.imageUrl == null || product.imageUrl!.isEmpty
                    ? Container(
                        width: 88,
                        height: 88,
                        color: const Color(0xFFE8F5EC),
                        child: const Icon(
                          Icons.bakery_dining,
                          color: Color(0xFF087A3A),
                        ),
                      )
                    : Image.network(
                        product.imageUrl!,
                        width: 88,
                        height: 88,
                        fit: BoxFit.cover,
                        errorBuilder: (_, _, _) => Container(
                          width: 88,
                          height: 88,
                          color: const Color(0xFFE8F5EC),
                          child: const Icon(
                            Icons.bakery_dining,
                            color: Color(0xFF087A3A),
                          ),
                        ),
                      ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            product.name,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              fontSize: 17,
                              fontWeight: FontWeight.w900,
                            ),
                          ),
                        ),
                        StatusBadge(label: '${product.discountPercent}%'),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      product.storeName,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      product.regionLabel,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: Colors.black54,
                        fontSize: 12,
                      ),
                    ),
                    const SizedBox(height: 10),
                    Wrap(
                      spacing: 8,
                      runSpacing: 6,
                      crossAxisAlignment: WrapCrossAlignment.center,
                      children: [
                        Text(
                          '${product.discountPrice.toStringAsFixed(0)}원',
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                        Text(
                          '${product.originalPrice.toStringAsFixed(0)}원',
                          style: const TextStyle(
                            color: Colors.black45,
                            decoration: TextDecoration.lineThrough,
                          ),
                        ),
                        Text('남은 수량 ${product.quantity}개'),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
