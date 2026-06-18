import 'package:flutter/foundation.dart';

import '../core/api_client.dart';
import '../models/reservation.dart';

class ReservationController extends ChangeNotifier {
  ReservationController({required this.apiClient});

  final ApiClient apiClient;

  List<Reservation> reservations = [];
  bool loading = false;
  String? errorMessage;

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
}
