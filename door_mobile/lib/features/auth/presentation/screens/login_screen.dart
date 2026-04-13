import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import '../../data/auth_repository.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _phoneCtrl = TextEditingController();
  bool _loading = false;

  Future<void> _submit() async {
    setState(() => _loading = true);
    try {
      final repo = RepositoryProvider.of<AuthRepository>(context);
      await repo.requestOtp(_phoneCtrl.text.trim());
      if (mounted) context.push('/otp', extra: _phoneCtrl.text.trim());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      body: SafeArea(
        child: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: [Color(0xFF050505), Color(0xFF0D0D0D)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                  decoration: BoxDecoration(
                    color: const Color(0x29F6B94A),
                    borderRadius: BorderRadius.circular(999),
                    border: Border.all(color: const Color(0x66F6B94A)),
                  ),
                  child: const Text(
                    'Phase 1 smart QR coordination',
                    style: TextStyle(
                      color: Color(0xFFB8B0A0),
                      fontSize: 12,
                      letterSpacing: 0.4,
                    ),
                  ),
                ),
                const SizedBox(height: 28),
                Text(
                  'Door App',
                  style: theme.textTheme.headlineMedium?.copyWith(fontSize: 38),
                ),
                const SizedBox(height: 12),
                const Text(
                  'Sign in to manage queues, QR interactions, messaging, and offline-ready coordination flows.',
                  style: TextStyle(height: 1.5),
                ),
                const SizedBox(height: 28),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Phone number'),
                        const SizedBox(height: 12),
                        TextField(
                          controller: _phoneCtrl,
                          keyboardType: TextInputType.phone,
                          decoration: const InputDecoration(
                            hintText: '+92 300 0000000',
                          ),
                          textDirection: TextDirection.ltr,
                        ),
                        const SizedBox(height: 18),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton(
                            onPressed: _loading ? null : _submit,
                            child: _loading
                                ? const SizedBox(
                                    width: 22,
                                    height: 22,
                                    child: CircularProgressIndicator(strokeWidth: 2),
                                  )
                                : const Text('Send OTP'),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const Spacer(),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
