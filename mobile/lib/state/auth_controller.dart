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
      errorMessage = error.message;
    } catch (_) {
      errorMessage = '로그인에 실패했습니다. 백엔드 연결 상태를 확인해 주세요.';
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
}
