import 'package:flutter/material.dart';

import '../models/reservation_history.dart';
import 'empty_state.dart';
import 'status_badge.dart';

class ReservationHistorySheet extends StatelessWidget {
  const ReservationHistorySheet({
    super.key,
    required this.history,
    this.errorMessage,
  });

  final List<ReservationHistoryItem> history;
  final String? errorMessage;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: FractionallySizedBox(
        heightFactor: 0.82,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      '상태 이력',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ),
                  IconButton(
                    onPressed: () => Navigator.of(context).pop(),
                    icon: const Icon(Icons.close),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              const Text(
                '예약 생성, 결제, 픽업, 배송, 취소, 환불 흐름을 시간순으로 확인합니다.',
                style: TextStyle(color: Colors.black54),
              ),
              const SizedBox(height: 16),
              if (errorMessage != null)
                Expanded(
                  child: EmptyState(
                    title: '상태 이력을 불러오지 못했습니다.',
                    description: errorMessage,
                    icon: Icons.error_outline,
                  ),
                )
              else if (history.isEmpty)
                const Expanded(
                  child: EmptyState(
                    title: '상태 이력이 없습니다.',
                    description: '예약 상태가 변경되면 이곳에 표시됩니다.',
                    icon: Icons.history,
                  ),
                )
              else
                Expanded(
                  child: ListView.separated(
                    itemCount: history.length,
                    separatorBuilder: (_, _) => const SizedBox(height: 10),
                    itemBuilder: (context, index) {
                      final item = history[index];
                      return _HistoryTile(item: item, isFirst: index == 0);
                    },
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

class _HistoryTile extends StatelessWidget {
  const _HistoryTile({required this.item, required this.isFirst});

  final ReservationHistoryItem item;
  final bool isFirst;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Column(
          children: [
            Container(
              width: 14,
              height: 14,
              decoration: BoxDecoration(
                color: isFirst ? const Color(0xFF087A3A) : Colors.grey,
                shape: BoxShape.circle,
              ),
            ),
            Container(width: 2, height: 72, color: const Color(0xFFE3E8DE)),
          ],
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Card(
            margin: EdgeInsets.zero,
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          item.eventLabel,
                          style: const TextStyle(fontWeight: FontWeight.w900),
                        ),
                      ),
                      StatusBadge(label: _shortTime(item.createdAt)),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(item.message),
                  if (item.fromStatus != null || item.toStatus != null) ...[
                    const SizedBox(height: 6),
                    Text(
                      '${item.fromStatus ?? '-'} → ${item.toStatus ?? '-'}',
                      style: const TextStyle(color: Colors.black54),
                    ),
                  ],
                  const SizedBox(height: 6),
                  Text(
                    '${_shortDate(item.createdAt)} · ${item.actorLabel}',
                    style: const TextStyle(color: Colors.black54, fontSize: 12),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  static String _shortDate(DateTime value) {
    return '${value.year}.${_two(value.month)}.${_two(value.day)}';
  }

  static String _shortTime(DateTime value) {
    return '${_two(value.hour)}:${_two(value.minute)}';
  }

  static String _two(int value) => value.toString().padLeft(2, '0');
}
