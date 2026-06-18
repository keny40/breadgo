import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/auth_user.dart';
import '../models/notification_item.dart';
import '../models/payment.dart';
import '../models/product.dart';
import '../models/reservation.dart';
import 'session_store.dart';

class ApiException implements Exception {
  ApiException(this.message);

  final String message;

  @override
  String toString() => message;
}

class LoginResult {
  LoginResult({required this.accessToken, required this.user});

  final String accessToken;
  final AuthUser user;
}

class ApiClient {
  ApiClient({required String baseUrl, required this.sessionStore})
    : baseUrl = _normalizeBaseUrl(baseUrl);

  final String baseUrl;
  final SessionStore sessionStore;

  static String _normalizeBaseUrl(String value) =>
      value.replaceAll(RegExp(r'/+$'), '');

  Uri _uri(String path, [Map<String, String>? queryParameters]) {
    final normalizedPath = path.startsWith('/') ? path : '/$path';
    return Uri.parse(
      '$baseUrl$normalizedPath',
    ).replace(queryParameters: queryParameters);
  }

  Map<String, String> _headers({bool auth = false}) {
    final headers = {'Content-Type': 'application/json'};
    final token = sessionStore.accessToken;
    if (auth && token != null) {
      headers['Authorization'] = 'Bearer $token';
    }
    return headers;
  }

  Future<dynamic> _decodeResponse(http.Response response) async {
    if (response.statusCode < 200 || response.statusCode >= 300) {
      var message = '요청 처리에 실패했습니다. (${response.statusCode})';
      if (response.body.isNotEmpty) {
        try {
          final body = jsonDecode(utf8.decode(response.bodyBytes));
          if (body is Map<String, dynamic> && body['detail'] is String) {
            message = body['detail'] as String;
          }
        } catch (_) {
          message = utf8.decode(response.bodyBytes);
        }
      }
      throw ApiException(message);
    }

    if (response.bodyBytes.isEmpty) {
      return null;
    }
    return jsonDecode(utf8.decode(response.bodyBytes));
  }

  Future<LoginResult> login({
    required String email,
    required String password,
  }) async {
    final response = await http.post(
      _uri('/api/v1/auth/login'),
      headers: _headers(),
      body: jsonEncode({'email': email, 'password': password}),
    );
    final body = await _decodeResponse(response) as Map<String, dynamic>;
    return LoginResult(
      accessToken: body['access_token'] as String,
      user: AuthUser.fromJson(body['user'] as Map<String, dynamic>),
    );
  }

  Future<AuthUser> me() async {
    final response = await http.get(
      _uri('/api/v1/auth/me'),
      headers: _headers(auth: true),
    );
    final body = await _decodeResponse(response) as Map<String, dynamic>;
    return AuthUser.fromJson(body);
  }

  Future<List<Product>> fetchRegionProducts({
    String sido = '서울특별시',
    String sigungu = '강남구',
    String dong = '역삼동',
  }) async {
    final response = await http.get(
      _uri('/api/v1/regions/products', {
        'sido': sido,
        'sigungu': sigungu,
        'dong': dong,
      }),
      headers: _headers(),
    );
    final body = await _decodeResponse(response) as List<dynamic>;
    return body
        .map((item) => Product.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<List<Reservation>> fetchMyReservations() async {
    final response = await http.get(
      _uri('/api/v1/reservations/me'),
      headers: _headers(auth: true),
    );
    final body = await _decodeResponse(response) as List<dynamic>;
    return body
        .map((item) => Reservation.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<Reservation> createReservation({
    required String productId,
    required int quantity,
    required String fulfillmentMethod,
    String? recipientName,
    String? recipientPhone,
    String? deliveryAddress,
    String? deliveryRequestMemo,
    double deliveryFee = 0,
  }) async {
    final response = await http.post(
      _uri('/api/v1/reservations'),
      headers: _headers(auth: true),
      body: jsonEncode({
        'product_id': productId,
        'quantity': quantity,
        'fulfillment_method': fulfillmentMethod,
        'recipient_name': recipientName,
        'recipient_phone': recipientPhone,
        'delivery_address': deliveryAddress,
        'delivery_request_memo': deliveryRequestMemo,
        'delivery_fee': deliveryFee,
      }),
    );
    final body = await _decodeResponse(response) as Map<String, dynamic>;
    return Reservation.fromJson(body);
  }

  Future<Reservation> cancelReservation({required String reservationId}) async {
    final response = await http.post(
      _uri('/api/v1/reservations/$reservationId/cancel'),
      headers: _headers(auth: true),
    );
    final body = await _decodeResponse(response) as Map<String, dynamic>;
    return Reservation.fromJson(body);
  }

  Future<Payment> createMockPaymentReady({
    required String reservationId,
    String method = 'MOCK_CARD',
  }) async {
    final response = await http.post(
      _uri('/api/v1/payments/mock/ready'),
      headers: _headers(auth: true),
      body: jsonEncode({'reservation_id': reservationId, 'method': method}),
    );
    final body = await _decodeResponse(response) as Map<String, dynamic>;
    return Payment.fromJson(body);
  }

  Future<Payment> confirmMockPayment({required String paymentId}) async {
    final response = await http.post(
      _uri('/api/v1/payments/mock/confirm'),
      headers: _headers(auth: true),
      body: jsonEncode({'payment_id': paymentId}),
    );
    final body = await _decodeResponse(response) as Map<String, dynamic>;
    return Payment.fromJson(body);
  }

  Future<List<NotificationItem>> fetchMyNotifications() async {
    final response = await http.get(
      _uri('/api/v1/notifications/me'),
      headers: _headers(auth: true),
    );
    final body = await _decodeResponse(response) as List<dynamic>;
    return body
        .map((item) => NotificationItem.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<NotificationItem> markNotificationAsRead({
    required String notificationId,
  }) async {
    final response = await http.patch(
      _uri('/api/v1/notifications/$notificationId/read'),
      headers: _headers(auth: true),
    );
    final body = await _decodeResponse(response) as Map<String, dynamic>;
    return NotificationItem.fromJson(body);
  }

  Future<List<NotificationItem>> markAllNotificationsAsRead() async {
    final response = await http.patch(
      _uri('/api/v1/notifications/read-all'),
      headers: _headers(auth: true),
    );
    final body = await _decodeResponse(response) as List<dynamic>;
    return body
        .map((item) => NotificationItem.fromJson(item as Map<String, dynamic>))
        .toList();
  }
}
