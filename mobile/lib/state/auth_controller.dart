import 'package:flutter/foundation.dart';

import '../core/api_client.dart';
import '../models/auth_user.dart';

class AuthController extends ChangeNotifier {
  AuthController({required this.apiClient});

  final ApiClient apiClient;

  AuthUser? user;
  bool loading = false;
  String? errorMessage;

  bool get isLoggedIn => user != null && apiClient.sessionStore.isLoggedIn;

  Future<void> login(String email, String password) async {
    loading = true;
    errorMessage = null;
    notifyListeners();

    try {
      final result = await apiClient.login(email: email, password: password);
      await apiClient.sessionStore.saveAccessToken(result.accessToken);
      user = result.user;
    } on ApiException catch (error) {
      errorMessage = _friendlyError(error.message);
    } catch (_) {
      errorMessage = '로그인에 실패했습니다. API 주소와 네트워크 연결을 확인한 뒤 다시 시도해 주세요.';
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    await apiClient.sessionStore.clear();
    user = null;
    errorMessage = null;
    notifyListeners();
  }

  String _friendlyError(String message) {
    final lower = message.toLowerCase();
    if (lower.contains('invalid email or password') || lower.contains('401')) {
      return '이메일 또는 비밀번호를 확인해 주세요.';
    }
    if (lower.contains('failed') || lower.contains('network')) {
      return '서버에 연결하지 못했습니다. API 주소와 네트워크 상태를 확인해 주세요.';
    }
    return message;
  }
}
