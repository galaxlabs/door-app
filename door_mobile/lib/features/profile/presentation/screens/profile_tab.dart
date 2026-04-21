import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../auth/data/auth_repository.dart';

class ProfileTab extends StatefulWidget {
  final bool generalNotifications;
  final ValueChanged<bool> onNotificationsChanged;
  final String language;
  final VoidCallback onOpenLanguages;
  final String themeMode;
  final VoidCallback onOpenTheme;
  final VoidCallback onGoToDoors;
  final VoidCallback onOpenQuickGuide;

  const ProfileTab({
    super.key,
    required this.generalNotifications,
    required this.onNotificationsChanged,
    required this.language,
    required this.onOpenLanguages,
    required this.themeMode,
    required this.onOpenTheme,
    required this.onGoToDoors,
    required this.onOpenQuickGuide,
  });

  @override
  State<ProfileTab> createState() => _ProfileTabState();
}

class _ProfileTabState extends State<ProfileTab> {
  bool _loading = true;
  bool _hasSession = false;
  Map<String, dynamic> _me = const {};
  String _visitorCardPhoto = '';

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final repo = context.read<AuthRepository>();
    final prefs = await SharedPreferences.getInstance();
    final hasSession = await repo.hasSession();
    final me = await repo.fetchProfile();

    if (!mounted) return;
    setState(() {
      _hasSession = hasSession;
      _me = Map<String, dynamic>.from(me);
      _visitorCardPhoto = prefs.getString('visitor_card_photo') ?? '';
      _loading = false;
    });
  }

  String _randomId() {
    final value = (_me['public_id'] ?? _me['anonymous_id'] ?? 'guest').toString();
    if (value.length <= 14) return value;
    return '${value.substring(0, 10)}…${value.substring(value.length - 4)}';
  }

  String _mobile() => (_me['phone_number'] ?? _me['phone'] ?? '+').toString();

  String _email() => (_me['email'] ?? '').toString();

  String _name() => (_me['full_name'] ?? 'Guest').toString();

  String _introText() {
    final value = (_me['intro'] ?? '').toString().trim();
    if (value.isNotEmpty) return value;
    return 'Add a short intro line';
  }

  String _syncStatus() => _hasSession ? 'Synced' : 'Local';

  int? _ageValue() {
    final value = _me['age'];
    if (value is int) return value;
    if (value is num) return value.toInt();
    return int.tryParse('${value ?? ''}');
  }

  Future<void> _editAge() async {
    final repo = context.read<AuthRepository>();
    final ctrl = TextEditingController(text: _ageValue()?.toString() ?? '');
    final result = await showDialog<int?>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Age'),
        content: TextField(
          controller: ctrl,
          keyboardType: TextInputType.number,
          decoration: const InputDecoration(hintText: 'Enter age'),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.of(ctx).pop(null), child: const Text('Cancel')),
          TextButton(
            onPressed: () {
              final parsed = int.tryParse(ctrl.text.trim());
              Navigator.of(ctx).pop(parsed);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );

    if (result == null) return;
    final updated = await repo.updateProfile(
      fullName: _name(),
      intro: (_me['intro'] ?? '').toString(),
      age: result,
      phoneNumber: _mobile(),
      email: _email(),
      locale: (_me['locale'] ?? 'en').toString(),
      timezone: (_me['timezone'] ?? 'UTC').toString(),
    );
    if (!mounted) return;
    setState(() => _me = Map<String, dynamic>.from(updated));
  }

  Future<void> _deleteData() async {
    final repo = context.read<AuthRepository>();
    final yes = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete local data?'),
        content: const Text('This clears local drafts and settings from this device.'),
        actions: [
          TextButton(onPressed: () => Navigator.of(ctx).pop(false), child: const Text('Cancel')),
          TextButton(onPressed: () => Navigator.of(ctx).pop(true), child: const Text('Delete')),
        ],
      ),
    );
    if (yes != true) return;

    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
    await repo.logout();
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Local data cleared.'), behavior: SnackBarBehavior.floating),
    );
    setState(() {
      _me = const {};
      _hasSession = false;
      _visitorCardPhoto = '';
    });
  }

  Future<void> _signOut() async {
    await context.read<AuthRepository>().logout();
    if (!mounted) return;
    context.go('/login');
  }

  Future<void> _copyVisitorCard() async {
    final payload = jsonEncode({
      'name': _name(),
      'phone': _mobile(),
      'email': _email(),
      'id': _randomId(),
    });
    await Clipboard.setData(ClipboardData(text: payload));
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Visitor card copied.'), behavior: SnackBarBehavior.floating),
    );
  }

  Widget _sectionLabel(String text) {
    return Padding(
      padding: const EdgeInsets.only(left: 6, top: 12, bottom: 8),
      child: Text(
        text.toUpperCase(),
        style: const TextStyle(
          color: Color(0xFFB8B0A0),
          fontSize: 12,
          letterSpacing: 0.4,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }

  Widget _actionCard({
    required IconData icon,
    required Color accent,
    required String title,
    required String subtitle,
    VoidCallback? onTap,
    Widget? trailing,
  }) {
    return Card(
      child: ListTile(
        onTap: onTap,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        leading: Container(
          width: 46,
          height: 46,
          decoration: BoxDecoration(
            color: accent.withValues(alpha: 0.14),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Icon(icon, color: accent),
        ),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w700)),
        subtitle: Text(subtitle),
        trailing: trailing ?? (onTap != null ? const Icon(Icons.chevron_right) : null),
      ),
    );
  }

  Widget _onOffToggle() {
    final on = widget.generalNotifications;
    final onStyle = on
        ? const BoxDecoration(
            gradient: LinearGradient(colors: [Color(0xFFF6B94A), Color(0xFFF39C28)]),
            borderRadius: BorderRadius.all(Radius.circular(16)),
          )
        : const BoxDecoration(
            color: Color(0xFF1D1D1D),
            borderRadius: BorderRadius.all(Radius.circular(16)),
          );
    final offStyle = !on
        ? const BoxDecoration(
            color: Color(0xFF2A2A2A),
            borderRadius: BorderRadius.all(Radius.circular(16)),
          )
        : const BoxDecoration(
            color: Color(0xFF1D1D1D),
            borderRadius: BorderRadius.all(Radius.circular(16)),
          );

    return Container(
      padding: const EdgeInsets.all(6),
      decoration: BoxDecoration(
        color: const Color(0xFF151515),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0x1FFFFFFF)),
      ),
      child: Row(
        children: [
          Expanded(
            child: InkWell(
              borderRadius: BorderRadius.circular(16),
              onTap: () => widget.onNotificationsChanged(true),
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 10),
                decoration: onStyle,
                child: const Center(child: Text('On', style: TextStyle(fontWeight: FontWeight.w800))),
              ),
            ),
          ),
          const SizedBox(width: 6),
          Expanded(
            child: InkWell(
              borderRadius: BorderRadius.circular(16),
              onTap: () => widget.onNotificationsChanged(false),
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 10),
                decoration: offStyle,
                child: Center(
                  child: Text(
                    'Off',
                    style: TextStyle(
                      fontWeight: FontWeight.w800,
                      color: on ? const Color(0xFFB8B0A0) : const Color(0xFFF7F0DC),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Row(
              children: [
                GestureDetector(
                  onTap: () => ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Photo picker will be connected next.'), behavior: SnackBarBehavior.floating),
                  ),
                  child: const CircleAvatar(
                    radius: 32,
                    backgroundColor: Color(0x29F6B94A),
                    child: Icon(Icons.person_rounded, size: 30, color: Color(0xFFF6B94A)),
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Text('Intro', style: TextStyle(color: Color(0xFFB8B0A0), fontSize: 12, letterSpacing: 0.3)),
                          const SizedBox(width: 10),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                              color: const Color(0x141D1D1D),
                              borderRadius: BorderRadius.circular(999),
                              border: Border.all(color: const Color(0x1FFFFFFF)),
                            ),
                            child: Text(_syncStatus(), style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800)),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(_introText(), style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800)),
                      const SizedBox(height: 4),
                      Text(_name(), style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w900)),
                      const SizedBox(height: 2),
                      Text(_mobile(), style: Theme.of(context).textTheme.bodyMedium),
                      const SizedBox(height: 10),
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: [
                          _chip(label: 'Age', value: _ageValue()?.toString() ?? '—', onTap: _editAge),
                          _chip(label: 'ID', value: _randomId(), onTap: () async {
                            await Clipboard.setData(ClipboardData(text: (_me['public_id'] ?? _me['anonymous_id'] ?? '').toString()));
                            if (!context.mounted) return;
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('ID copied.'), behavior: SnackBarBehavior.floating),
                            );
                          }),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 12),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => context.push('/doors/create'),
                    icon: const Icon(Icons.add_circle_outline),
                    label: const Text('Create'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: widget.onGoToDoors,
                    icon: const Icon(Icons.door_front_door_outlined),
                    label: const Text('Manage'),
                  ),
                ),
              ],
            ),
          ),
        ),

        _sectionLabel('Quick guide'),
        _actionCard(
          icon: Icons.menu_book_outlined,
          accent: const Color(0xFF4ECB71),
          title: 'Quick guide',
          subtitle: 'How doors, QR, and visitor flows work',
          onTap: widget.onOpenQuickGuide,
        ),

        _sectionLabel('Activity'),
        _actionCard(
          icon: Icons.history_rounded,
          accent: const Color(0xFF37D6C5),
          title: 'All activity',
          subtitle: 'Open activity history and records',
          onTap: () => context.push('/activity'),
        ),
        _actionCard(
          icon: Icons.location_on_outlined,
          accent: const Color(0xFFF6B94A),
          title: 'Meeting points',
          subtitle: 'Create and share a meet link',
          onTap: () => context.push('/meeting-points'),
        ),

        _sectionLabel('My visitor card'),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                Row(
                  children: [
                    GestureDetector(
                      onTap: () => ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Visitor photo picker will be connected next.'), behavior: SnackBarBehavior.floating),
                      ),
                      child: CircleAvatar(
                        radius: 28,
                        backgroundColor: const Color(0xFF1D1D1D),
                        child: _visitorCardPhoto.isEmpty
                            ? const Icon(Icons.camera_alt_outlined, color: Color(0xFFB8B0A0))
                            : const Icon(Icons.check_circle, color: Color(0xFF37D6C5)),
                      ),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Intro', style: TextStyle(color: Color(0xFFB8B0A0), fontSize: 12)),
                          const SizedBox(height: 4),
                          Text(_name(), style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800)),
                          const SizedBox(height: 4),
                          Text(_mobile(), style: Theme.of(context).textTheme.bodyMedium),
                        ],
                      ),
                    ),
                    IconButton(
                      onPressed: _copyVisitorCard,
                      icon: const Icon(Icons.copy_rounded),
                    ),
                  ],
                ),
                const SizedBox(height: 14),
                _readonlyField(label: 'Name', value: _name()),
                const SizedBox(height: 10),
                _readonlyField(label: 'Phone', value: _mobile()),
                const SizedBox(height: 10),
                _readonlyField(label: 'Email', value: _email()),
                const SizedBox(height: 10),
                _readonlyField(label: 'Random ID', value: _randomId()),
              ],
            ),
          ),
        ),

        _sectionLabel('General'),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Notifications', style: TextStyle(fontWeight: FontWeight.w800)),
                const SizedBox(height: 10),
                _onOffToggle(),
                const SizedBox(height: 14),
                ListTile(
                  onTap: widget.onOpenLanguages,
                  leading: const Icon(Icons.language_rounded),
                  title: const Text('Languages', style: TextStyle(fontWeight: FontWeight.w800)),
                  subtitle: Text(widget.language),
                  trailing: const Icon(Icons.chevron_right),
                ),
                ListTile(
                  onTap: widget.onOpenTheme,
                  leading: const Icon(Icons.dark_mode_outlined),
                  title: const Text('Theme', style: TextStyle(fontWeight: FontWeight.w800)),
                  subtitle: Text(widget.themeMode),
                  trailing: const Icon(Icons.chevron_right),
                ),
              ],
            ),
          ),
        ),

        _sectionLabel('Security'),
        _actionCard(
          icon: Icons.privacy_tip_outlined,
          accent: const Color(0xFF4ECB71),
          title: 'Privacy',
          subtitle: 'Save photos, share analytics, policy',
          onTap: () => context.push('/privacy'),
        ),
        Card(
          child: ListTile(
            onTap: _deleteData,
            leading: const Icon(Icons.delete_outline_rounded, color: Color(0xFFFF6D6D)),
            title: const Text('Delete data', style: TextStyle(fontWeight: FontWeight.w800, color: Color(0xFFFF6D6D))),
            subtitle: const Text('Clear local drafts and settings from this device'),
            trailing: const Icon(Icons.chevron_right),
          ),
        ),

        _sectionLabel('Account'),
        Card(
          child: ListTile(
            onTap: _hasSession ? _signOut : () => context.go('/login'),
            leading: Icon(_hasSession ? Icons.logout_rounded : Icons.login_rounded),
            title: Text(_hasSession ? 'Sign out' : 'Sign in', style: const TextStyle(fontWeight: FontWeight.w800)),
            subtitle: Text(_hasSession ? 'Remove session from this device' : 'Connect to the backend'),
            trailing: const Icon(Icons.chevron_right),
          ),
        ),

        _sectionLabel('About'),
        _actionCard(
          icon: Icons.info_outline_rounded,
          accent: const Color(0xFFB8B0A0),
          title: 'Version',
          subtitle: '1.0.0+1',
        ),
        _actionCard(
          icon: Icons.menu_book_outlined,
          accent: const Color(0xFF37D6C5),
          title: 'Guide',
          subtitle: 'Open the quick guide',
          onTap: widget.onOpenQuickGuide,
        ),
        _actionCard(
          icon: Icons.star_outline_rounded,
          accent: const Color(0xFFF6B94A),
          title: 'Rate us',
          subtitle: 'Share feedback (connected later)',
          onTap: () => ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Rating flow will be connected next.'), behavior: SnackBarBehavior.floating),
          ),
        ),
        _actionCard(
          icon: Icons.logout_rounded,
          accent: const Color(0xFFFF6D6D),
          title: 'Sign out',
          subtitle: 'Sign out from this device',
          onTap: _signOut,
        ),
      ],
    );
  }

  Widget _chip({required String label, required String value, VoidCallback? onTap}) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(999),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: const Color(0x141D1D1D),
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: const Color(0x1FFFFFFF)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(label, style: const TextStyle(color: Color(0xFFB8B0A0), fontSize: 12, fontWeight: FontWeight.w700)),
            const SizedBox(width: 8),
            Text(value, style: const TextStyle(fontWeight: FontWeight.w800)),
          ],
        ),
      ),
    );
  }

  Widget _readonlyField({required String label, required String value}) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        color: const Color(0xFF1D1D1D),
        border: Border.all(color: const Color(0x1FFFFFFF)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(color: Color(0xFFB8B0A0), fontSize: 12)),
          const SizedBox(height: 4),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w700)),
        ],
      ),
    );
  }
}
