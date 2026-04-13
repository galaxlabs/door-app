import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Door App'),
        actions: [
          IconButton(
            onPressed: () {},
            icon: const Icon(Icons.notifications_none_rounded),
          ),
        ],
      ),
      body: ListView(
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
                  'Smart QR communication',
                  style: TextStyle(
                    color: Color(0xFFB8B0A0),
                    fontSize: 12,
                    letterSpacing: 0.3,
                  ),
                ),
                SizedBox(height: 10),
                Text(
                  'Turn one code into a doorbell, queue, checkpoint, or coordination point.',
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.w700),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          const Row(
            children: [
              Expanded(
                child: _StatCard(
                  label: 'QR Modes',
                  value: '4',
                  tone: Color(0xFFF6B94A),
                ),
              ),
              SizedBox(width: 12),
              Expanded(
                child: _StatCard(
                  label: 'Queue',
                  value: 'Live',
                  tone: Color(0xFF37D6C5),
                ),
              ),
              SizedBox(width: 12),
              Expanded(
                child: _StatCard(
                  label: 'Sync',
                  value: 'Ready',
                  tone: Color(0xFF4ECB71),
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          Text('Quick actions', style: theme.textTheme.titleLarge),
          const SizedBox(height: 12),
          _NavCard(
            title: 'Scan QR',
            subtitle: 'Door, queue, group, or event action',
            icon: Icons.qr_code_scanner_rounded,
            accent: const Color(0xFFF6B94A),
            onTap: () => context.push('/scan'),
          ),
          _NavCard(
            title: 'Queue',
            subtitle: 'Open live queue state',
            icon: Icons.confirmation_number_rounded,
            accent: const Color(0xFF37D6C5),
            onTap: () => context.push('/queue/demo-queue'),
          ),
          _NavCard(
            title: 'Chat',
            subtitle: 'Open room messaging',
            icon: Icons.forum,
            accent: const Color(0xFF6FA8FF),
            onTap: () => context.push('/chat/demo-room'),
          ),
          _NavCard(
            title: 'Broadcast',
            subtitle: 'Open one-way channel updates',
            icon: Icons.campaign,
            accent: const Color(0xFF4ECB71),
            onTap: () => context.push('/broadcast/demo-channel'),
          ),
          _NavCard(
            title: 'Sync Center',
            subtitle: 'Push/pull offline operations now',
            icon: Icons.sync,
            accent: const Color(0xFFF6B94A),
            onTap: () => context.push('/sync-center'),
          ),
          const SizedBox(height: 20),
          Text('Phase 2', style: theme.textTheme.titleLarge),
          const SizedBox(height: 12),
          _NavCard(
            title: 'Attendance',
            subtitle: 'Roll calls, check-ins, and gather sessions',
            icon: Icons.fact_check_rounded,
            accent: const Color(0xFF37D6C5),
            onTap: () => context.push('/attendance'),
          ),
          _NavCard(
            title: 'Family Coordination',
            subtitle: 'Households, guardians, and regrouping',
            icon: Icons.family_restroom_rounded,
            accent: const Color(0xFFF6B94A),
            onTap: () => context.push('/family'),
          ),
          _NavCard(
            title: 'Safety + Hajj',
            subtitle: 'Emergency cards, Hajj support, missing person flow',
            icon: Icons.health_and_safety_rounded,
            accent: const Color(0xFF4ECB71),
            onTap: () => context.push('/safety-hajj'),
          ),
          const SizedBox(height: 12),
          Text('Today', style: theme.textTheme.titleLarge),
          const SizedBox(height: 12),
          const _InfoPanel(
            title: 'Active product scope',
            body:
                'Phase 1 stays focused on identity, organizations, QR interactions, queues, chat, broadcast, sync, audit, and notifications.',
          ),
          const SizedBox(height: 12),
          const _InfoPanel(
            title: 'Recommended first flow',
            body:
                'Open the scanner, route the QR by mode, then continue into queue join, conversation, or group coordination without leaving the mobile shell.',
          ),
        ],
      ),
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
              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 4),
            Text(label),
          ],
        ),
      ),
    );
  }
}

class _InfoPanel extends StatelessWidget {
  final String title;
  final String body;

  const _InfoPanel({
    required this.title,
    required this.body,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
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
