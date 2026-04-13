import 'package:flutter/material.dart';

class FamilyCoordinationScreen extends StatelessWidget {
  const FamilyCoordinationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Family Coordination')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 28),
        children: [
          const _FamilyHero(),
          const SizedBox(height: 16),
          const Row(
            children: [
              Expanded(child: _MiniStat(label: 'Households', value: '56')),
              SizedBox(width: 12),
              Expanded(child: _MiniStat(label: 'Children linked', value: '104')),
              SizedBox(width: 12),
              Expanded(child: _MiniStat(label: 'Pending regroup', value: '05')),
            ],
          ),
          const SizedBox(height: 18),
          Text('Family groups', style: theme.textTheme.titleMedium),
          const SizedBox(height: 10),
          const _HouseholdCard(
            name: 'Rahman household',
            contextLine: 'Sector C · Tent 14',
            members: '7 members · 2 guardians · 1 elder support',
            status: 'All accounted for',
          ),
          const SizedBox(height: 10),
          const _HouseholdCard(
            name: 'Al Noor travel group',
            contextLine: 'Bus 5 · Mina route',
            members: '12 members · 3 families merged',
            status: '2 awaiting regroup',
          ),
          const SizedBox(height: 18),
          Text('Gather mode', style: theme.textTheme.titleMedium),
          const SizedBox(height: 10),
          const _GatherCard(
            title: 'After prayer regroup',
            note: 'Use this mode when family members split across movement points and need a fast status roll-up.',
          ),
          const SizedBox(height: 10),
          const _GatherCard(
            title: 'Guardian-led follow-up',
            note: 'Track who is safe, delayed, or missing before escalating to the safety workflow.',
          ),
        ],
      ),
    );
  }
}

class _FamilyHero extends StatelessWidget {
  const _FamilyHero();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(28),
        color: const Color(0xFF111925),
        border: Border.all(color: const Color(0x2237D6C5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Households and hierarchy',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 10),
          Text(
            'Manage family units, guardian relationships, and quick regroup sessions without losing the premium mobile flow.',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: 16),
          const Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _Chip(label: 'Guardian links'),
              _Chip(label: 'Family groups'),
              _Chip(label: 'Gather status'),
            ],
          ),
        ],
      ),
    );
  }
}

class _Chip extends StatelessWidget {
  final String label;

  const _Chip({required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(999),
        color: Colors.white.withValues(alpha: 0.05),
      ),
      child: Text(label, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
    );
  }
}

class _MiniStat extends StatelessWidget {
  final String label;
  final String value;

  const _MiniStat({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(value, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w700)),
            const SizedBox(height: 6),
            Text(label, style: Theme.of(context).textTheme.bodySmall),
          ],
        ),
      ),
    );
  }
}

class _HouseholdCard extends StatelessWidget {
  final String name;
  final String contextLine;
  final String members;
  final String status;

  const _HouseholdCard({
    required this.name,
    required this.contextLine,
    required this.members,
    required this.status,
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
                  child: Text(name, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(999),
                    color: const Color(0xFFF6B94A).withValues(alpha: 0.12),
                  ),
                  child: Text(status, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(contextLine, style: Theme.of(context).textTheme.bodySmall),
            const SizedBox(height: 12),
            Text(members, style: Theme.of(context).textTheme.bodyMedium),
          ],
        ),
      ),
    );
  }
}

class _GatherCard extends StatelessWidget {
  final String title;
  final String note;

  const _GatherCard({required this.title, required this.note});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
        gradient: const LinearGradient(
          colors: [Color(0x1A37D6C5), Color(0x14111925)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        border: Border.all(color: const Color(0x2237D6C5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700)),
          const SizedBox(height: 8),
          Text(note, style: Theme.of(context).textTheme.bodyMedium),
        ],
      ),
    );
  }
}
