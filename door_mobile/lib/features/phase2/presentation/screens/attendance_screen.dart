import 'package:flutter/material.dart';

class AttendanceScreen extends StatelessWidget {
  const AttendanceScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Attendance')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 28),
        children: [
          const _HeroCard(
            title: 'Attendance and gather control',
            subtitle:
                'Run roll calls, QR check-ins, and regrouping from a single field screen.',
            chips: ['QR check-in', 'Manual mark', 'Missing follow-up'],
          ),
          const SizedBox(height: 16),
          const Row(
            children: [
              Expanded(
                child: _StatCard(label: 'Active sessions', value: '04', accent: Color(0xFFF6B94A)),
              ),
              SizedBox(width: 12),
              Expanded(
                child: _StatCard(label: 'Present now', value: '126', accent: Color(0xFF37D6C5)),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Row(
            children: [
              Expanded(
                child: _StatCard(label: 'Late', value: '09', accent: Color(0xFF5BA7FF)),
              ),
              SizedBox(width: 12),
              Expanded(
                child: _StatCard(label: 'Missing', value: '03', accent: Color(0xFFEB5757)),
              ),
            ],
          ),
          const SizedBox(height: 18),
          Text('Live sessions', style: theme.textTheme.titleMedium),
          const SizedBox(height: 10),
          const _SessionCard(
            title: 'Mina camp morning roll call',
            meta: 'Group A · 06:30 AM',
            status: 'In progress',
            progress: '42 / 48 checked in',
          ),
          const SizedBox(height: 10),
          const _SessionCard(
            title: 'Clinic volunteer attendance',
            meta: 'Operations · 08:15 AM',
            status: 'Needs review',
            progress: '17 / 21 checked in',
          ),
          const SizedBox(height: 18),
          Text('Action flow', style: theme.textTheme.titleMedium),
          const SizedBox(height: 10),
          const _ActionTile(
            title: 'Open a session',
            body: 'Create an attendance window for an event, checkpoint, or household group.',
          ),
          const SizedBox(height: 10),
          const _ActionTile(
            title: 'Scan or mark participants',
            body: 'Use QR check-in first, then manually resolve late or no-show cases.',
          ),
          const SizedBox(height: 10),
          const _ActionTile(
            title: 'Escalate missing members',
            body: 'Hand off unresolved absences into gather mode or missing-person workflows.',
          ),
        ],
      ),
    );
  }
}

class _HeroCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final List<String> chips;

  const _HeroCard({
    required this.title,
    required this.subtitle,
    required this.chips,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w700)),
          const SizedBox(height: 10),
          Text(subtitle, style: Theme.of(context).textTheme.bodyMedium),
          const SizedBox(height: 16),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: chips
                .map(
                  (chip) => Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(999),
                      color: Colors.white.withValues(alpha: 0.06),
                      border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
                    ),
                    child: Text(chip, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                  ),
                )
                .toList(),
          ),
        ],
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String label;
  final String value;
  final Color accent;

  const _StatCard({
    required this.label,
    required this.value,
    required this.accent,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              height: 10,
              width: 10,
              decoration: BoxDecoration(color: accent, shape: BoxShape.circle),
            ),
            const SizedBox(height: 16),
            Text(value, style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w700)),
            const SizedBox(height: 4),
            Text(label, style: Theme.of(context).textTheme.bodyMedium),
          ],
        ),
      ),
    );
  }
}

class _SessionCard extends StatelessWidget {
  final String title;
  final String meta;
  final String status;
  final String progress;

  const _SessionCard({
    required this.title,
    required this.meta,
    required this.status,
    required this.progress,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(999),
                    color: const Color(0xFF37D6C5).withValues(alpha: 0.14),
                  ),
                  child: Text(status, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(meta, style: Theme.of(context).textTheme.bodySmall),
            const SizedBox(height: 12),
            Text(progress, style: Theme.of(context).textTheme.bodyMedium),
          ],
        ),
      ),
    );
  }
}

class _ActionTile extends StatelessWidget {
  final String title;
  final String body;

  const _ActionTile({required this.title, required this.body});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF101723),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: Colors.white.withValues(alpha: 0.06)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700)),
          const SizedBox(height: 8),
          Text(body, style: Theme.of(context).textTheme.bodyMedium),
        ],
      ),
    );
  }
}
