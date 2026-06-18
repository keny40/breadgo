class SessionStore {
  String? _accessToken;

  String? get accessToken => _accessToken;
  bool get isLoggedIn => _accessToken != null && _accessToken!.isNotEmpty;

  Future<void> saveAccessToken(String token) async {
    _accessToken = token;
  }

  Future<void> clear() async {
    _accessToken = null;
  }
}
