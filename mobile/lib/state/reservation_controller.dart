import 'package:flutter/foundation.dart';

import '../core/api_client.dart';
import '../models/payment.dart';
import '../models/reservation.dart';

class ReservationController extends ChangeNotifier {
  ReservationController({required this.apiClient});

  final ApiClient apiClient;

  List<Reservation> reservations = [];
  bool loading = false;
  bool submitting = false;
  final Set<String> cancellingReservationIds = {};
  String? errorMessage;
  String? successMessage;
  Reservation? lastReservation;
  Payment? lastPayment;

  Future<void> loadMyReservations() async {
    loading = true;
    errorMessage = null;
    notifyListeners();

    try {
      reservations = await apiClient.fetchMyReservations();
    } on ApiException catch (error) {
      errorMessage = error.message;
    } catch (_) {
      errorMessage = '예약 내역을 불러오지 못했습니다.';
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  Future<bool> createReservationAndPay({
    required String productId,
    required int quantity,
    required String fulfillmentMethod,
    String? recipientName,
    String? recipientPhone,
    String? deliveryAddress,
    String? deliveryRequestMemo,
    double deliveryFee = 0,
  }) async {
    submitting = true;
    errorMessage = null;
    successMessage = null;
    lastReservation = null;
    lastPayment = null;
    notifyListeners();

    try {
      final reservation = await apiClient.createReservation(
        productId: productId,
        quantity: quantity,
        fulfillmentMethod: fulfillmentMethod,
        recipientName: recipientName,
        recipientPhone: recipientPhone,
        deliveryAddress: deliveryAddress,
        deliveryRequestMemo: deliveryRequestMemo,
        deliveryFee: deliveryFee,
      );
      final readyPayment = await apiClient.createMockPaymentReady(
        reservationId: reservation.id,
      );
      final paidPayment = await apiClient.confirmMockPayment(
        paymentId: readyPayment.id,
      );

      lastReservation = reservation;
      lastPayment = paidPayment;
      successMessage = '예약과 Mock 결제가 완료되었습니다.';
      await loadMyReservations();
      return true;
    } on ApiException catch (error) {
      errorMessage = _friendlyError(error.message);
      return false;
    } catch (_) {
      errorMessage = '예약 또는 Mock 결제 처리에 실패했습니다.';
      return false;
    } finally {
      submitting = false;
      notifyListeners();
    }
  }

  bool isCancelling(String reservationId) {
    return cancellingReservationIds.contains(reservationId);
  }

  Future<bool> cancelReservation(String reservationId) async {
    cancellingReservationIds.add(reservationId);
    errorMessage = null;
    successMessage = null;
    notifyListeners();

    try {
      final cancelledReservation = await apiClient.cancelReservation(
        reservationId: reservationId,
      );
      reservations = reservations
          .map(
            (reservation) => reservation.id == reservationId
                ? cancelledReservation
                : reservation,
          )
          .toList();
      successMessage = '예약이 취소되었습니다. MVP에서는 Mock 환불 상태로 처리됩니다.';
      await loadMyReservations();
      return true;
    } on ApiException catch (error) {
      errorMessage = _friendlyError(error.message);
      return false;
    } catch (_) {
      errorMessage = '예약 취소에 실패했습니다.';
      return false;
    } finally {
      cancellingReservationIds.remove(reservationId);
      notifyListeners();
    }
  }

  String _friendlyError(String message) {
    final lower = message.toLowerCase();
    if (lower.contains('authentication') || lower.contains('401')) {
      return '로그인이 필요합니다. 다시 로그인해 주세요.';
    }
    if (lower.contains('insufficient product quantity')) {
      return '예약 가능한 수량이 부족합니다.';
    }
    if (lower.contains('not available')) {
      return '선택한 수령 방식은 이 상품에서 사용할 수 없습니다.';
    }
    if (lower.contains('recipient')) {
      return '배송 수령자, 연락처, 주소를 입력해 주세요.';
    }
    if (lower.contains('reservation cannot be cancelled')) {
      return '취소할 수 없는 예약입니다.';
    }
    if (lower.contains('delivery is already in progress')) {
      return '이미 배송이 시작되었거나 완료되어 취소할 수 없습니다.';
    }
    if (lower.contains('only paid reservations')) {
      return '결제 완료된 예약만 취소할 수 있습니다.';
    }
    return message;
  }
}
