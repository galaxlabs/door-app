import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../auth/data/auth_repository.dart';
import '../../../doors/models/door_models.dart';
import '../../../doors/repositories/door_repository.dart';
import '../../../profile/presentation/screens/profile_tab.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;
  bool _generalNotifications = true;
  bool _hasSession = false;
  String _language = 'English';
  String _themeMode = 'Midnight amber';

  @override
  void initState() {
    super.initState();
    _loadSessionState();
    _loadProfilePrefs();
  }

  Future<void> _loadSessionState() async {
    final hasSession = await context.read<AuthRepository>().hasSession();
    if (!mounted) return;
    setState(() => _hasSession = hasSession);
  }

  Future<void> _loadProfilePrefs() async {
    final prefs = await SharedPreferences.getInstance();
    final locale = (prefs.getString('profile_locale') ?? 'en').toLowerCase();
    final theme = (prefs.getString('app_theme_mode') ?? 'midnight').toLowerCase();
    if (!mounted) return;
    setState(() {
      _language = switch (locale) {
        'ur' => 'اردو',
        'ar' => 'العربية',
        _ => 'English',
      };
      _themeMode = switch (theme) {
        'system' => 'System',
        'dark' => 'Dark',
        _ => 'Midnight amber',
      };
    });
  }

  void _showNote(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final pages = [
      _HomeTab(showNote: _showNote),
      _DoorsTab(showNote: _showNote, enableLive: _hasSession),
      _QrTab(showNote: _showNote),
      ProfileTab(
        generalNotifications: _generalNotifications,
        onNotificationsChanged: (value) => setState(() => _generalNotifications = value),
        language: _language,
        onOpenLanguages: () => context.push('/language').then((_) => _loadProfilePrefs()),
        themeMode: _themeMode,
        onOpenTheme: () => context.push('/theme').then((_) => _loadProfilePrefs()),
        onGoToDoors: () => setState(() => _currentIndex = 1),
        onOpenQuickGuide: () => context.push('/quick-guide'),
      ),
    ];

    const titles = ['Home', 'Doors', 'QR Codes', 'Profile'];

    return Scaffold(
      appBar: AppBar(
        title: Text(titles[_currentIndex]),
        actions: [
          IconButton(
            onPressed: () => _showNote('Notifications center is next in line.'),
            icon: Icon(
              _generalNotifications ? Icons.notifications_active_outlined : Icons.notifications_off_outlined,
            ),
          ),
        ],
      ),
      body: SafeArea(
        child: AnimatedSwitcher(
          duration: const Duration(milliseconds: 220),
          child: KeyedSubtree(
            key: ValueKey(_currentIndex),
            child: pages[_currentIndex],
          ),
        ),
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) => setState(() => _currentIndex = index),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home_rounded), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.door_front_door_outlined), selectedIcon: Icon(Icons.door_front_door_rounded), label: 'Doors'),
          NavigationDestination(icon: Icon(Icons.qr_code_2_outlined), selectedIcon: Icon(Icons.qr_code_2_rounded), label: 'QR'),
          NavigationDestination(icon: Icon(Icons.person_outline_rounded), selectedIcon: Icon(Icons.person_rounded), label: 'Profile'),
        ],
      ),
    );
  }
}

class _HomeTab extends StatelessWidget {
  final void Function(String message) showNote;

  const _HomeTab({required this.showNote});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(28),
            gradient: const LinearGradient(
              colors: [Color(0x33F6B94A), Color(0x1137D6C5)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            border: Border.all(color: const Color(0x33F6B94A)),
          ),
          child: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Mobile command center',
                style: TextStyle(
                  color: Color(0xFFB8B0A0),
                  fontSize: 12,
                  letterSpacing: 0.3,
                ),
              ),
              SizedBox(height: 10),
              Text(
                'Home, Doors, QR Codes, and Profile now live in one clean mobile shell.',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.w700),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        const Row(
          children: [
            Expanded(child: _StatCard(label: 'QR Codes', value: 'Ready', tone: Color(0xFFF6B94A))),
            SizedBox(width: 12),
            Expanded(child: _StatCard(label: 'Doors', value: '4 Tabs', tone: Color(0xFF37D6C5))),
            SizedBox(width: 12),
            Expanded(child: _StatCard(label: 'Profile', value: 'Polished', tone: Color(0xFF4ECB71))),
          ],
        ),
        const SizedBox(height: 20),
        Text('Quick actions', style: theme.textTheme.titleLarge),
        const SizedBox(height: 12),
        _NavCard(
          title: 'Scan QR now',
          subtitle: 'Open the scanner for door, queue, and visitor actions',
          icon: Icons.qr_code_scanner_rounded,
          accent: const Color(0xFFF6B94A),
          onTap: () => context.push('/scan'),
        ),
        _NavCard(
          title: 'Queue control',
          subtitle: 'Open live queue state and join flow',
          icon: Icons.confirmation_number_rounded,
          accent: const Color(0xFF37D6C5),
          onTap: () => context.push('/queue/demo-queue'),
        ),
        _NavCard(
          title: 'Sync center',
          subtitle: 'Push and pull offline changes',
          icon: Icons.sync_rounded,
          accent: const Color(0xFF4ECB71),
          onTap: () => context.push('/sync-center'),
        ),
        const SizedBox(height: 12),
        const _InfoPanel(
          title: 'Why this layout works',
          body: 'The main mobile app is now focused around just four anchors: Home, Doors, QR Codes, and Profile.',
        ),
        const SizedBox(height: 12),
        _InfoPanel(
          title: 'Next recommended action',
          body: 'Tap the QR tab to scan or manage entry flows, then use the profile tab to adjust personal and visitor settings.',
          onTap: () => showNote('You can continue with QR and profile improvements next.'),
        ),
      ],
    );
  }
}

class _DoorsTab extends StatelessWidget {
  final void Function(String message) showNote;
  final bool enableLive;

  const _DoorsTab({required this.showNote, required this.enableLive});

  Color _accentFor(String slug) {
    switch (slug) {
      case 'hospital':   return const Color(0xFFFF6D6D);
      case 'shop':       return const Color(0xFF37D6C5);
      case 'office':     return const Color(0xFF4D9EFF);
      case 'education':  return const Color(0xFFA78BFA);
      case 'trip':       return const Color(0xFF4ECB71);
      case 'checkpoint': return const Color(0xFFFF9A3C);
      case 'emergency':  return const Color(0xFFFF4444);
      default:           return const Color(0xFFF6B94A);
    }
  }

  @override
  Widget build(BuildContext context) {
    final uid = FirebaseAuth.instance.currentUser?.uid;
    final repo = DoorRepository();

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _InfoPanel(
          title: 'Your Doors',
          body: enableLive
              ? 'Live doors are loaded from Firebase below.'
              : 'Guest mode. Sign in to see your real doors.',
        ),
        const SizedBox(height: 12),
        _NavCard(
          title: 'Add Door',
          subtitle: enableLive ? 'Create a new door and generate a QR' : 'Sign in to create your first door',
          icon: Icons.add_circle_outline,
          accent: const Color(0xFFF6B94A),
          onTap: enableLive ? () => context.push('/doors/create') : () => context.go('/login'),
        ),
        _NavCard(
          title: 'Emergency',
          subtitle: 'Create an emergency card door preset',
          icon: Icons.warning_amber_rounded,
          accent: const Color(0xFFFF6D6D),
          onTap: enableLive ? () => context.push('/doors/create') : () => context.go('/login'),
        ),
        _NavCard(
          title: 'Join Door',
          subtitle: 'Scan a QR to open the visitor flow',
          icon: Icons.qr_code_scanner_rounded,
          accent: const Color(0xFF37D6C5),
          onTap: () => context.push('/scan'),
        ),
        const SizedBox(height: 12),
        if (enableLive && uid != null)
          StreamBuilder<List<Door>>(
            stream: repo.watchMyDoors(uid),
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(
                  child: Padding(
                    padding: EdgeInsets.all(24),
                    child: CircularProgressIndicator(),
                  ),
                );
              }
              final doors = snapshot.data ?? [];
              if (doors.isEmpty) {
                return Container(
                  margin: const EdgeInsets.only(top: 4),
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(20),
                    color: const Color(0xFF1A1A1A),
                  ),
                  child: Column(
                    children: [
                      const Icon(Icons.door_front_door_rounded,
                          size: 40, color: Color(0xFF444444)),
                      const SizedBox(height: 12),
                      const Text('No doors yet',
                          style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
                      const SizedBox(height: 6),
                      const Text('Create your first door and it will appear here.',
                          style: TextStyle(color: Color(0xFF888888)),
                          textAlign: TextAlign.center),
                      const SizedBox(height: 16),
                      OutlinedButton.icon(
                        onPressed: () => context.push('/doors/create'),
                        icon: const Icon(Icons.add_circle_outline),
                        label: const Text('Create door'),
                      ),
                    ],
                  ),
                );
              }
              return Column(
                children: doors.take(10).map((door) {
                  final accent = _accentFor(door.typeSlug);
                  final statusLabel = door.status == DoorStatus.active ? 'Active' : 'Inactive';
                  return _DoorCard(
                    title: door.name,
                    subtitle: door.typeSlug.replaceAll('_', ' '),
                    status: statusLabel,
                    accent: accent,
                    onTap: () => context.push('/doors/${door.id}'),
                  );
                }).toList(),
              );
            },
          ),
        if (!enableLive || uid == null) ...[
          _DoorCard(
            title: 'Home Entrance',
            subtitle: 'Bell mode • family notifications on',
            status: 'Active',
            accent: const Color(0xFFF6B94A),
            onTap: () => showNote('Sign in to open real door settings.'),
          ),
          _DoorCard(
            title: 'Clinic Queue Door',
            subtitle: 'Queue join • waiting room live',
            status: 'Live',
            accent: const Color(0xFF37D6C5),
            onTap: () => context.push('/queue/demo-queue'),
          ),
          _DoorCard(
            title: 'Office Visitor Door',
            subtitle: 'Chat + notify members',
            status: 'Online',
            accent: const Color(0xFF6FA8FF),
            onTap: () => showNote('Office visitor routing is ready for the next backend hookup.'),
          ),
          _DoorCard(
            title: 'Emergency Door',
            subtitle: 'Priority route with backup alerts',
            status: 'Standby',
            accent: const Color(0xFF4ECB71),
            onTap: () => showNote('Emergency escalation can be expanded next.'),
          ),
        ],
      ],
    );
  }
}

class _QrTab extends StatelessWidget {
  final void Function(String message) showNote;

  const _QrTab({required this.showNote});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('QR Codes', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
                const SizedBox(height: 8),
                const Text('Scan a code, manage the flow, and notify the right members from one mobile area.'),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () => context.push('/scan'),
                    icon: const Icon(Icons.qr_code_scanner_rounded),
                    label: const Text('Open scanner'),
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        _NavCard(
          title: 'Home bell QR',
          subtitle: 'Rings the owner and backup members',
          icon: Icons.doorbell_outlined,
          accent: const Color(0xFFF6B94A),
          onTap: () => showNote('Member-notify routing is ready from the mobile QR area.'),
        ),
        _NavCard(
          title: 'Queue join QR',
          subtitle: 'Issues a ticket and opens the queue screen',
          icon: Icons.confirmation_number_outlined,
          accent: const Color(0xFF37D6C5),
          onTap: () => context.push('/queue/demo-queue'),
        ),
        _NavCard(
          title: 'Broadcast QR',
          subtitle: 'Subscribes people to urgent update channels',
          icon: Icons.campaign_outlined,
          accent: const Color(0xFF4ECB71),
          onTap: () => context.push('/broadcast/demo-channel'),
        ),
      ],
    );
  }
}

class _StatCard extends StatelessWidget {
  final String label;
  final String value;
  final Color tone;

  const _StatCard({
    required this.label,
    required this.value,
    required this.tone,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 10,
              height: 10,
              decoration: BoxDecoration(
                color: tone,
                borderRadius: BorderRadius.circular(999),
              ),
            ),
            const SizedBox(height: 12),
            Text(
              value,
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 4),
            Text(label),
          ],
        ),
      ),
    );
  }
}

class _DoorCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final String status;
  final Color accent;
  final VoidCallback onTap;

  const _DoorCard({
    required this.title,
    required this.subtitle,
    required this.status,
    required this.accent,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
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
          child: Icon(Icons.door_front_door_rounded, color: accent),
        ),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w700)),
        subtitle: Text(subtitle),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(status, style: TextStyle(color: accent, fontWeight: FontWeight.w700)),
            const Icon(Icons.chevron_right),
          ],
        ),
      ),
    );
  }
}

class _InfoPanel extends StatelessWidget {
  final String title;
  final String body;
  final VoidCallback? onTap;

  const _InfoPanel({
    required this.title,
    required this.body,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(24),
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
              const SizedBox(height: 8),
              Text(body, style: Theme.of(context).textTheme.bodyMedium),
            ],
          ),
        ),
      ),
    );
  }
}

class _NavCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final IconData icon;
  final Color accent;
  final VoidCallback onTap;

  const _NavCard({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.accent,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        borderRadius: BorderRadius.circular(24),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Row(
            children: [
              Container(
                width: 52,
                height: 52,
                decoration: BoxDecoration(
                  color: accent.withValues(alpha: 0.14),
                  borderRadius: BorderRadius.circular(18),
                ),
                child: Icon(icon, color: accent),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: const TextStyle(fontWeight: FontWeight.w700)),
                    const SizedBox(height: 4),
                    Text(subtitle),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right),
            ],
          ),
        ),
      ),
    );
  }
}
