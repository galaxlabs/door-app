import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../auth/data/auth_repository.dart';

class LanguageScreen extends StatefulWidget {
  const LanguageScreen({super.key});

  @override
  State<LanguageScreen> createState() => _LanguageScreenState();
}

class _LanguageScreenState extends State<LanguageScreen> {
  String _current = 'en';
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() => _current = prefs.getString('profile_locale') ?? 'en');
  }

  Future<void> _setLocale(String locale) async {
    setState(() => _saving = true);
    try {
      final repo = context.read<AuthRepository>();
      final profile = await repo.fetchProfile();
      await repo.updateProfile(
        fullName: (profile['full_name'] ?? 'Guest').toString(),
        intro: (profile['intro'] ?? '').toString(),
        age: profile['age'] is int ? profile['age'] as int : int.tryParse('${profile['age'] ?? ''}'),
        phoneNumber: (profile['phone_number'] ?? '+92').toString(),
        email: (profile['email'] ?? '').toString(),
        locale: locale,
        timezone: (profile['timezone'] ?? 'UTC').toString(),
      );
      if (!mounted) return;
      setState(() => _current = locale);
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Language')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Column(
              children: [
                _LangTile(
                  title: 'English',
                  value: 'en',
                  current: _current,
                  saving: _saving,
                  onTap: _setLocale,
                ),
                const Divider(height: 1),
                _LangTile(
                  title: 'اردو',
                  value: 'ur',
                  current: _current,
                  saving: _saving,
                  onTap: _setLocale,
                ),
                const Divider(height: 1),
                _LangTile(
                  title: 'العربية',
                  value: 'ar',
                  current: _current,
                  saving: _saving,
                  onTap: _setLocale,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _LangTile extends StatelessWidget {
  final String title;
  final String value;
  final String current;
  final bool saving;
  final void Function(String value) onTap;

  const _LangTile({
    required this.title,
    required this.value,
    required this.current,
    required this.saving,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final selected = value == current;
    return ListTile(
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w700)),
      subtitle: Text(selected ? 'Selected' : 'Tap to select'),
      trailing: selected ? const Icon(Icons.check_circle_rounded, color: Color(0xFF37D6C5)) : null,
      onTap: saving ? null : () => onTap(value),
    );
  }
}

