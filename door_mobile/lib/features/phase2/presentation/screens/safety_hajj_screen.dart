import 'package:flutter/material.dart';

class SafetyHajjScreen extends StatelessWidget {
  const SafetyHajjScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Safety + Hajj')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 28),
        children: [
          const _SafetyHero(),
          const SizedBox(height: 16),
          const _PriorityStrip(),
          const SizedBox(height: 18),
          Text('Emergency readiness', style: theme.textTheme.titleMedium),
          const SizedBox(height: 10),
          const _SafetyCard(
            title: 'Emergency cards',
            body:
                'Keep blood group, medical notes, allergies, primary contacts, and home location ready for fast field access.',
          ),
          const SizedBox(height: 10),
          const _SafetyCard(
            title: 'Hajj tracker profiles',
            body:
                'Store tent, bus, passport tail, health flags, and lead assignments for large pilgrim groups.',
          ),
          const SizedBox(height: 18),
          Text('Recovery workflow', style: theme.textTheme.titleMedium),
          const SizedBox(height: 10),
          const _RecoveryStep(
            step: '1',
            title: 'Open case',
            body: 'Capture last-seen location, time window, clothing notes, and priority.',
          ),
          const SizedBox(height: 10),
          const _RecoveryStep(
            step: '2',
            title: 'Collect sightings',
            body: 'Gather structured reports instead of scattering updates across chat threads.',
          ),
          const SizedBox(height: 10),
          const _RecoveryStep(
            step: '3',
            title: 'Close safely',
            body: 'Resolve the case once the person is found and preserve the full audit trail.',
          ),
        ],
      ),
    );
  }
}

class _SafetyHero extends StatelessWidget {
  const _SafetyHero();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(28),
        gradient: const LinearGradient(
          colors: [Color(0x22EB5757), Color(0x1437D6C5)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        border: Border.all(color: const Color(0x33EB5757)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Safety and Hajj support', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w700)),
          const SizedBox(height: 10),
          Text(
            'Move from basic communication into real group protection with emergency identity, pilgrim context, and missing-person workflows.',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        ],
      ),
    );
  }
}

class _PriorityStrip extends StatelessWidget {
  const _PriorityStrip();

  @override
  Widget build(BuildContext context) {
    return const Row(
      children: [
        Expanded(child: _PriorityPill(label: 'Emergency', color: Color(0xFFEB5757))),
        SizedBox(width: 10),
        Expanded(child: _PriorityPill(label: 'Medical', color: Color(0xFFF6B94A))),
        SizedBox(width: 10),
        Expanded(child: _PriorityPill(label: 'Group lead', color: Color(0xFF37D6C5))),
      ],
    );
  }
}

class _PriorityPill extends StatelessWidget {
  final String label;
  final Color color;

  const _PriorityPill({required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 14),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(18),
        color: color.withValues(alpha: 0.12),
        border: Border.all(color: color.withValues(alpha: 0.28)),
      ),
      child: Center(
        child: Text(
          label,
          style: TextStyle(color: color, fontWeight: FontWeight.w700, fontSize: 12),
        ),
      ),
    );
  }
}

class _SafetyCard extends StatelessWidget {
  final String title;
  final String body;

  const _SafetyCard({required this.title, required this.body});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w700)),
            const SizedBox(height: 8),
            Text(body, style: Theme.of(context).textTheme.bodyMedium),
          ],
        ),
      ),
    );
  }
}

class _RecoveryStep extends StatelessWidget {
  final String step;
  final String title;
  final String body;

  const _RecoveryStep({
    required this.step,
    required this.title,
    required this.body,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF101723),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: Colors.white.withValues(alpha: 0.06)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            height: 34,
            width: 34,
            decoration: const BoxDecoration(
              shape: BoxShape.circle,
              color: Color(0x22F6B94A),
            ),
            child: Center(
              child: Text(step, style: const TextStyle(fontWeight: FontWeight.w700)),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700)),
                const SizedBox(height: 8),
                Text(body, style: Theme.of(context).textTheme.bodyMedium),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
