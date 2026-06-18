import 'package:flutter/material.dart';

import '../state/auth_controller.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key, required this.authController});

  final AuthController authController;

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController(text: 'customer@breadgo.test');
  final _passwordController = TextEditingController(text: '12345678');

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: widget.authController,
      builder: (context, _) {
        final user = widget.authController.user;
        return ListView(
          padding: const EdgeInsets.all(20),
          children: [
            const Text(
              '우리 동네 마감 할인 빵을 예약하고 픽업하세요.',
              style: TextStyle(
                fontSize: 26,
                fontWeight: FontWeight.w900,
                height: 1.25,
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              '모바일 MVP는 고객 로그인, 상품 조회, 내 예약 조회를 먼저 연결합니다.',
              style: TextStyle(color: Colors.black54),
            ),
            const SizedBox(height: 24),
            if (user != null)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '로그인됨: ${user.email}',
                        style: const TextStyle(fontWeight: FontWeight.w800),
                      ),
                      const SizedBox(height: 12),
                      OutlinedButton(
                        onPressed: widget.authController.logout,
                        child: const Text('로그아웃'),
                      ),
                    ],
                  ),
                ),
              )
            else
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      TextField(
                        controller: _emailController,
                        keyboardType: TextInputType.emailAddress,
                        decoration: const InputDecoration(labelText: '이메일'),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _passwordController,
                        obscureText: true,
                        decoration: const InputDecoration(labelText: '비밀번호'),
                      ),
                      const SizedBox(height: 18),
                      FilledButton(
                        onPressed: widget.authController.loading
                            ? null
                            : _login,
                        child: Text(
                          widget.authController.loading ? '로그인 중' : '로그인',
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            if (widget.authController.errorMessage != null) ...[
              const SizedBox(height: 12),
              Text(
                widget.authController.errorMessage!,
                style: const TextStyle(color: Colors.red),
              ),
            ],
          ],
        );
      },
    );
  }

  void _login() {
    widget.authController.login(
      _emailController.text.trim(),
      _passwordController.text,
    );
  }
}
