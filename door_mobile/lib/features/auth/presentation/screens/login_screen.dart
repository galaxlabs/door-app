import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../data/auth_repository.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0D0D0D),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 28),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Spacer(flex: 2),
              // Brand
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                decoration: BoxDecoration(
                  color: const Color(0x29F6B94A),
                  borderRadius: BorderRadius.circular(999),
                  border: Border.all(color: const Color(0x55F6B94A)),
                ),
                child: const Text('Door App',
                    style: TextStyle(
                        color: Color(0xFFF6B94A),
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                        letterSpacing: 0.6)),
              ),
              const SizedBox(height: 24),
              const Text('Welcome back',
                  style: TextStyle(
                      fontSize: 36,
                      fontWeight: FontWeight.w900,
                      height: 1.1)),
              const SizedBox(height: 10),
              const Text(
                'Sign in to manage your doors, visitors, and QR codes.',
                style: TextStyle(color: Color(0xFF888888), height: 1.5, fontSize: 15),
              ),
              const Spacer(flex: 1),

              // ── Google sign-in ──────────────────────────────────────────────
              _GoogleSignInButton(),

              const SizedBox(height: 14),

              // ── Divider ─────────────────────────────────────────────────────
              Row(children: const [
                Expanded(child: Divider(color: Color(0xFF2A2A2A))),
                Padding(
                  padding: EdgeInsets.symmetric(horizontal: 14),
                  child: Text('or',
                      style: TextStyle(color: Color(0xFF555555), fontSize: 13)),
                ),
                Expanded(child: Divider(color: Color(0xFF2A2A2A))),
              ]),

              const SizedBox(height: 14),

              // ── Email / password ────────────────────────────────────────────
              const _EmailLoginCard(),

              const Spacer(flex: 2),

              // ── Footer ──────────────────────────────────────────────────────
              Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                const Text('New here? ',
                    style: TextStyle(color: Color(0xFF666666), fontSize: 13)),
                GestureDetector(
                  onTap: () => context.go('/register'),
                  child: const Text('Create account',
                      style: TextStyle(
                          color: Color(0xFFF6B94A),
                          fontSize: 13,
                          fontWeight: FontWeight.w700)),
                ),
              ]),
              const SizedBox(height: 8),
              Center(
                child: TextButton(
                  onPressed: () => context.go('/home'),
                  child: const Text('Skip for now',
                      style: TextStyle(color: Color(0xFF555555), fontSize: 13)),
                ),
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }
}

// ── Google Sign-In Button ────────────────────────────────────────────────────

class _GoogleSignInButton extends StatefulWidget {
  @override
  State<_GoogleSignInButton> createState() => _GoogleSignInButtonState();
}

class _GoogleSignInButtonState extends State<_GoogleSignInButton> {
  bool _loading = false;
  String? _error;

  Future<void> _signIn() async {
    setState(() { _loading = true; _error = null; });
    try {
      await context.read<AuthRepository>().signInWithGoogle();
      if (!mounted) return;
      context.go('/home');
    } catch (e) {
      if (!mounted) return;
      final msg = e.toString();
      if (!msg.contains('cancelled')) {
        setState(() => _error = 'Google sign-in failed. Please try again.');
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        SizedBox(
          width: double.infinity,
          height: 56,
          child: ElevatedButton(
            onPressed: _loading ? null : _signIn,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.white,
              foregroundColor: const Color(0xFF1A1A1A),
              elevation: 0,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16)),
            ),
            child: _loading
                ? const SizedBox(
                    width: 22,
                    height: 22,
                    child: CircularProgressIndicator(strokeWidth: 2.5, color: Color(0xFF4285F4)),
                  )
                : Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                    _GoogleLogo(),
                    const SizedBox(width: 12),
                    const Text('Continue with Google',
                        style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 0.2)),
                  ]),
          ),
        ),
        if (_error != null) ...[
          const SizedBox(height: 8),
          Text(_error!,
              style: const TextStyle(color: Color(0xFFFF6D6D), fontSize: 13),
              textAlign: TextAlign.center),
        ],
      ],
    );
  }
}

class _GoogleLogo extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    // Simple G logo using text — no svg asset needed
    return Container(
      width: 24,
      height: 24,
      decoration: const BoxDecoration(shape: BoxShape.circle),
      child: const Text('G',
          textAlign: TextAlign.center,
          style: TextStyle(
              fontWeight: FontWeight.w900,
              fontSize: 17,
              color: Color(0xFF4285F4))),
    );
  }
}

// ── Email / Password Card ────────────────────────────────────────────────────

class _EmailLoginCard extends StatefulWidget {
  const _EmailLoginCard();

  @override
  State<_EmailLoginCard> createState() => _EmailLoginCardState();
}

class _EmailLoginCardState extends State<_EmailLoginCard> {
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  bool _loading = false;
  bool _obscure = true;
  String? _error;

  @override
  void dispose() {
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    super.dispose();
  }

  Future<void> _signIn() async {
    final email = _emailCtrl.text.trim();
    final password = _passwordCtrl.text;
    if (email.isEmpty) { setState(() => _error = 'Email is required.'); return; }
    if (password.isEmpty) { setState(() => _error = 'Password is required.'); return; }

    setState(() { _loading = true; _error = null; });
    try {
      await context.read<AuthRepository>().passwordLogin(
        identifier: email,
        password: password,
      );
      if (!mounted) return;
      context.go('/home');
    } catch (_) {
      if (!mounted) return;
      setState(() => _error = 'Incorrect email or password.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        color: const Color(0xFF1A1A1A),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Email & Password',
              style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700,
                  color: Color(0xFF888888), letterSpacing: 0.5)),
          const SizedBox(height: 12),
          TextField(
            controller: _emailCtrl,
            keyboardType: TextInputType.emailAddress,
            textInputAction: TextInputAction.next,
            style: const TextStyle(fontWeight: FontWeight.w600),
            decoration: InputDecoration(
              labelText: 'Email',
              filled: true,
              fillColor: const Color(0xFF111111),
              border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none),
              prefixIcon: const Icon(Icons.email_outlined, size: 18),
            ),
          ),
          const SizedBox(height: 10),
          TextField(
            controller: _passwordCtrl,
            obscureText: _obscure,
            textInputAction: TextInputAction.done,
            onSubmitted: (_) => _loading ? null : _signIn(),
            style: const TextStyle(fontWeight: FontWeight.w600),
            decoration: InputDecoration(
              labelText: 'Password',
              filled: true,
              fillColor: const Color(0xFF111111),
              border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none),
              prefixIcon: const Icon(Icons.lock_outline_rounded, size: 18),
              suffixIcon: IconButton(
                icon: Icon(_obscure ? Icons.visibility_off_outlined : Icons.visibility_outlined, size: 18),
                onPressed: () => setState(() => _obscure = !_obscure),
              ),
            ),
          ),
          if (_error != null) ...[
            const SizedBox(height: 10),
            Row(children: [
              const Icon(Icons.error_outline, color: Color(0xFFFF6D6D), size: 15),
              const SizedBox(width: 6),
              Expanded(child: Text(_error!,
                  style: const TextStyle(color: Color(0xFFFF6D6D), fontSize: 13))),
            ]),
          ],
          const SizedBox(height: 14),
          SizedBox(
            width: double.infinity,
            height: 48,
            child: ElevatedButton(
              onPressed: _loading ? null : _signIn,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFF6B94A),
                foregroundColor: Colors.black,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14)),
              ),
              child: _loading
                  ? const SizedBox(width: 20, height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black))
                  : const Text('Sign in',
                      style: TextStyle(fontSize: 15, fontWeight: FontWeight.w900)),
            ),
          ),
        ],
      ),
    );
  }
}
