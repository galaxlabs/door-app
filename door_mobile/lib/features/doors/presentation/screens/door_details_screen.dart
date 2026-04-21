import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:go_router/go_router.dart';

import '../../models/door_models.dart';
import '../../repositories/door_repository.dart';

class DoorDetailsScreen extends StatefulWidget {
  final String doorId;
  const DoorDetailsScreen({super.key, required this.doorId});

  @override
  State<DoorDetailsScreen> createState() => _DoorDetailsScreenState();
}

class _DoorDetailsScreenState extends State<DoorDetailsScreen> {
  final _repo = DoorRepository();
  bool _archiving = false;

  static const _typeIcons = {
    'home': Icons.home_rounded,
    'hospital': Icons.local_hospital_rounded,
    'shop': Icons.storefront_rounded,
    'office': Icons.business_rounded,
    'education': Icons.school_rounded,
    'trip': Icons.directions_bus_rounded,
    'checkpoint': Icons.fact_check_rounded,
    'emergency': Icons.emergency_rounded,
  };

  Color _accent(String slug) => switch (slug) {
    'hospital' => const Color(0xFFFF6D6D),
    'shop' => const Color(0xFF37D6C5),
    'office' => const Color(0xFF4ECB71),
    'education' => const Color(0xFF6C9EFF),
    'trip' => const Color(0xFFFFB347),
    'checkpoint' => const Color(0xFFB47AFF),
    'emergency' => const Color(0xFFFF4444),
    _ => const Color(0xFFF6B94A),
  };

  Future<void> _archiveDoor(Door door) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Archive door?'),
        content: const Text('The door will be deactivated. You can restore it later.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Archive', style: TextStyle(color: Color(0xFFFF6D6D))),
          ),
        ],
      ),
    );
    if (confirm != true) return;
    setState(() => _archiving = true);
    await _repo.deleteDoor(door.id);
    if (!mounted) return;
    context.pop();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return StreamBuilder<List<Door>>(
      // Listen to all user doors and find this one
      stream: FirebaseFirestore.instance
          .collection('doors')
          .doc(widget.doorId)
          .snapshots()
          .map((s) => s.exists ? [Door.fromMap(s.id, s.data()!)] : <Door>[]),
      builder: (context, snap) {
        if (!snap.hasData) {
          return const Scaffold(body: Center(child: CircularProgressIndicator()));
        }
        if (snap.data!.isEmpty) {
          return Scaffold(
            appBar: AppBar(),
            body: const Center(child: Text('Door not found')),
          );
        }

        final door = snap.data!.first;
        final accent = _accent(door.typeSlug);
        final icon = _typeIcons[door.typeSlug] ?? Icons.door_front_door_rounded;

        return Scaffold(
          appBar: AppBar(
            title: Text(door.name),
            actions: [
              if (!_archiving)
                IconButton(
                  icon: const Icon(Icons.archive_outlined),
                  tooltip: 'Archive door',
                  onPressed: () => _archiveDoor(door),
                ),
            ],
          ),
          body: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // Header card
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: accent.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: accent.withOpacity(0.25)),
                ),
                child: Row(
                  children: [
                    Container(
                      width: 64, height: 64,
                      decoration: BoxDecoration(
                        color: accent.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(18),
                      ),
                      child: Icon(icon, color: accent, size: 32),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(door.name,
                              style: theme.textTheme.titleLarge?.copyWith(
                                fontWeight: FontWeight.w800,
                              )),
                          const SizedBox(height: 4),
                          Text(
                            door.typeSlug.replaceAll('_', ' ').replaceFirstMapped(
                                RegExp(r'^.'), (m) => m.group(0)!.toUpperCase()),
                            style: theme.textTheme.bodyMedium?.copyWith(
                              color: accent,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ),
                    _StatusChip(status: door.status),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // QR Token row
              _InfoTile(
                icon: Icons.qr_code_rounded,
                label: 'QR Token',
                value: door.qrToken,
                accent: accent,
                trailing: IconButton(
                  icon: const Icon(Icons.copy_rounded, size: 18),
                  tooltip: 'Copy',
                  onPressed: () {
                    Clipboard.setData(ClipboardData(text: door.qrToken));
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('QR token copied'),
                        behavior: SnackBarBehavior.floating,
                        duration: Duration(seconds: 2),
                      ),
                    );
                  },
                ),
              ),
              const SizedBox(height: 8),

              // Public / private
              _InfoTile(
                icon: door.isPublic ? Icons.public_rounded : Icons.lock_outline_rounded,
                label: 'Visibility',
                value: door.isPublic ? 'Public' : 'Private',
                accent: door.isPublic ? const Color(0xFF37D6C5) : const Color(0xFFB8B0A0),
              ),
              const SizedBox(height: 16),

              // Live interactions
              Text('Recent interactions',
                  style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
              const SizedBox(height: 10),
              _InteractionsList(doorId: door.id),

              const SizedBox(height: 24),

              // Toggle active/inactive
              if (door.status != DoorStatus.archived)
                OutlinedButton.icon(
                  onPressed: () => _repo.updateDoor(
                    doorId: door.id,
                    status: door.status == DoorStatus.active
                        ? DoorStatus.inactive
                        : DoorStatus.active,
                  ),
                  icon: Icon(
                    door.status == DoorStatus.active
                        ? Icons.pause_circle_outline_rounded
                        : Icons.play_circle_outline_rounded,
                  ),
                  label: Text(door.status == DoorStatus.active ? 'Deactivate' : 'Activate'),
                  style: OutlinedButton.styleFrom(
                    minimumSize: const Size.fromHeight(50),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  ),
                ),
            ],
          ),
        );
      },
    );
  }
}

// ── Info tile ─────────────────────────────────────────────────────────────────

class _InfoTile extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color accent;
  final Widget? trailing;

  const _InfoTile({
    required this.icon,
    required this.label,
    required this.value,
    required this.accent,
    this.trailing,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: theme.colorScheme.outline.withOpacity(0.2)),
      ),
      child: Row(
        children: [
          Icon(icon, color: accent, size: 20),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurface.withOpacity(0.5),
                  )),
              Text(value,
                  style: theme.textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w600)),
            ],
          ),
          const Spacer(),
          if (trailing != null) trailing!,
        ],
      ),
    );
  }
}

// ── Status chip ───────────────────────────────────────────────────────────────

class _StatusChip extends StatelessWidget {
  final DoorStatus status;
  const _StatusChip({required this.status});

  @override
  Widget build(BuildContext context) {
    final (label, color) = switch (status) {
      DoorStatus.active => ('Active', const Color(0xFF4ECB71)),
      DoorStatus.inactive => ('Inactive', const Color(0xFFB8B0A0)),
      DoorStatus.archived => ('Archived', const Color(0xFFFF6D6D)),
    };
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(label,
          style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.w700)),
    );
  }
}

// ── Live interactions list ────────────────────────────────────────────────────

class _InteractionsList extends StatelessWidget {
  final String doorId;
  const _InteractionsList({required this.doorId});

  @override
  Widget build(BuildContext context) {
    final repo = DoorRepository();
    final theme = Theme.of(context);

    return StreamBuilder<List<DoorInteraction>>(
      stream: repo.watchDoorInteractions(doorId),
      builder: (context, snap) {
        if (!snap.hasData) {
          return const Padding(
            padding: EdgeInsets.symmetric(vertical: 20),
            child: Center(child: CircularProgressIndicator()),
          );
        }

        final interactions = snap.data!;
        if (interactions.isEmpty) {
          return Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: theme.colorScheme.surface,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: theme.colorScheme.outline.withOpacity(0.2)),
            ),
            child: Center(
              child: Text('No visitor interactions yet',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurface.withOpacity(0.5),
                  )),
            ),
          );
        }

        return Column(
          children: interactions.map((i) => _InteractionTile(interaction: i)).toList(),
        );
      },
    );
  }
}

class _InteractionTile extends StatelessWidget {
  final DoorInteraction interaction;
  const _InteractionTile({required this.interaction});

  Color get _statusColor => switch (interaction.status) {
    InteractionStatus.pending => const Color(0xFFF6B94A),
    InteractionStatus.seen => const Color(0xFF6C9EFF),
    InteractionStatus.admitted => const Color(0xFF4ECB71),
    InteractionStatus.declined => const Color(0xFFFF6D6D),
    InteractionStatus.completed => const Color(0xFFB8B0A0),
  };

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: theme.colorScheme.outline.withOpacity(0.2)),
      ),
      child: Row(
        children: [
          Container(
            width: 36, height: 36,
            decoration: BoxDecoration(
              color: _statusColor.withOpacity(0.15),
              shape: BoxShape.circle,
            ),
            child: Icon(Icons.person_outline_rounded, color: _statusColor, size: 18),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  interaction.visitorName ?? 'Anonymous visitor',
                  style: theme.textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w600),
                ),
                if (interaction.visitorMessage != null)
                  Text(interaction.visitorMessage!,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurface.withOpacity(0.6),
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
            decoration: BoxDecoration(
              color: _statusColor.withOpacity(0.15),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              interaction.status.name.replaceFirstMapped(
                  RegExp(r'^.'), (m) => m.group(0)!.toUpperCase()),
              style: TextStyle(
                  color: _statusColor, fontSize: 11, fontWeight: FontWeight.w600),
            ),
          ),
        ],
      ),
    );
  }
}
