import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../auth/data/auth_repository.dart';

class AccountScreen extends StatefulWidget {
  const AccountScreen({super.key});

  @override
  State<AccountScreen> createState() => _AccountScreenState();
}

class _AccountScreenState extends State<AccountScreen> {
  final _nameCtrl = TextEditingController();
  final _introCtrl = TextEditingController();
  final _ageCtrl = TextEditingController();
  final _phoneCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  bool _loading = true;
  bool _saving = false;
  bool _hasSession = false;
  String _statusText = 'Saved on this device';
  String _publicId = '';

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _introCtrl.dispose();
    _ageCtrl.dispose();
    _phoneCtrl.dispose();
    _emailCtrl.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    final repo = context.read<AuthRepository>();
    final hasSession = await repo.hasSession();
    final data = await repo.fetchProfile();

    if (!mounted) return;
    setState(() {
      _hasSession = hasSession;
      _nameCtrl.text = (data['full_name'] ?? '').toString();
      _introCtrl.text = (data['intro'] ?? '').toString();
      _ageCtrl.text = (data['age'] ?? '').toString();
      _phoneCtrl.text = (data['phone_number'] ?? data['phone'] ?? '').toString();
      _emailCtrl.text = (data['email'] ?? '').toString();
      _publicId = (data['public_id'] ?? '').toString();
      _statusText = hasSession ? 'Live sync enabled' : 'Saved on this device';
      _loading = false;
    });
  }

  Future<void> _save() async {
    setState(() => _saving = true);
    try {
      final repo = context.read<AuthRepository>();
      final parsedAge = int.tryParse(_ageCtrl.text.trim());
      final data = await repo.updateProfile(
        fullName: _nameCtrl.text.trim().isEmpty ? 'Guest' : _nameCtrl.text.trim(),
        intro: _introCtrl.text.trim(),
        age: parsedAge,
        phoneNumber: _phoneCtrl.text.trim().isEmpty ? '+92' : _phoneCtrl.text.trim(),
        email: _emailCtrl.text.trim(),
      );
      if (!mounted) return;
      final remote = (data['source'] ?? 'local') == 'remote';
      setState(() => _statusText = remote ? 'Live sync enabled' : 'Saved on this device');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(remote ? 'Profile saved.' : 'Profile saved locally.'),
          behavior: SnackBarBehavior.floating,
        ),
      );
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Account')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Profile details',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                  ),
                  const SizedBox(height: 6),
                  Text(_hasSession ? 'Connected to backend' : 'Local-only draft', style: Theme.of(context).textTheme.bodyMedium),
                  const SizedBox(height: 14),
                  if (_loading) ...[
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 12),
                      child: Center(child: CircularProgressIndicator()),
                    ),
                  ] else ...[
                    TextField(
                      controller: _nameCtrl,
                      decoration: const InputDecoration(labelText: 'Name'),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _introCtrl,
                      decoration: const InputDecoration(labelText: 'Intro'),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _ageCtrl,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(labelText: 'Age'),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _phoneCtrl,
                      keyboardType: TextInputType.phone,
                      decoration: InputDecoration(
                        labelText: 'Phone',
                        helperText: _hasSession ? 'Phone is locked for now (saved locally only).' : null,
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _emailCtrl,
                      keyboardType: TextInputType.emailAddress,
                      decoration: InputDecoration(
                        labelText: 'Email',
                        helperText: _hasSession ? 'Email is locked for now (saved locally only).' : null,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: const Color(0x1FFFFFFF)),
                        color: const Color(0x141D1D1D),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Random ID', style: Theme.of(context).textTheme.bodyMedium),
                          const SizedBox(height: 6),
                          Text(_publicId.isEmpty ? '—' : _publicId, style: const TextStyle(fontWeight: FontWeight.w700)),
                        ],
                      ),
                    ),
                    const SizedBox(height: 14),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(18),
                        border: Border.all(color: const Color(0x1FFFFFFF)),
                        color: const Color(0x141D1D1D),
                      ),
                      child: Text(_statusText),
                    ),
                    const SizedBox(height: 14),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: _saving ? null : _save,
                        icon: _saving
                            ? const SizedBox(
                                width: 18,
                                height: 18,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Icon(Icons.save_outlined),
                        label: Text(_saving ? 'Saving…' : 'Save'),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
