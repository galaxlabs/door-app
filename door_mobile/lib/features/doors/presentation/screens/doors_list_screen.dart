import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:go_router/go_router.dart';

import '../../models/door_models.dart';
import '../../repositories/door_repository.dart';

/// Doors tab — real-time list of the user's doors via Firestore stream.
class DoorsListScreen extends StatelessWidget {
  final void Function(String)? showNote;

  const DoorsListScreen({super.key, this.showNote});

  @override
  Widget build(BuildContext context) {
    final user = FirebaseAuth.instance.currentUser;
    final theme = Theme.of(context);

    if (user == null) {
      return _SignInPrompt(
        onSignIn: () => context.go('/login'),
      );
    }

    final repo = DoorRepository();

    return StreamBuilder<List<Door>>(
      stream: repo.watchMyDoors(user.uid),
      builder: (context, snapshot) {
        if (snapshot.hasError) {
          return Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.error_outline, size: 48, color: Color(0xFFFF6D6D)),
                const SizedBox(height: 12),
                Text('Could not load doors', style: theme.textTheme.titleMedium),
                const SizedBox(height: 6),
                Text(snapshot.error.toString(),
                    style: theme.textTheme.bodySmall, textAlign: TextAlign.center),
              ],
            ),
          );
        }

        final doors = snapshot.data;

        return CustomScrollView(
          slivers: [
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
                child: Row(
                  children: [
                    Expanded(
                      child: Text(
                        doors == null
                            ? 'Loading…'
                            : doors.isEmpty
                                ? 'No doors yet'
                                : '${doors.length} door${doors.length == 1 ? '' : 's'}',
                        style: theme.textTheme.titleMedium,
                      ),
                    ),
                    FilledButton.icon(
                      onPressed: () => context.push('/doors/pick-type'),
                      icon: const Icon(Icons.add_rounded, size: 18),
                      label: const Text('Add Door'),
                      style: FilledButton.styleFrom(
                        backgroundColor: const Color(0xFFF6B94A),
                        foregroundColor: Colors.black,
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        textStyle: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            if (doors == null)
              const SliverFillRemaining(
                child: Center(child: CircularProgressIndicator()),
              )
            else if (doors.isEmpty)
              SliverFillRemaining(
                child: _EmptyDoors(onAdd: () => context.push('/doors/pick-type')),
              )
            else
              SliverPadding(
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                sliver: SliverList(
                  delegate: SliverChildBuilderDelegate(
                    (ctx, i) => Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: _DoorCard(door: doors[i]),
                    ),
                    childCount: doors.length,
                  ),
                ),
              ),
          ],
        );
      },
    );
  }
}

// ── Door card ─────────────────────────────────────────────────────────────────

class _DoorCard extends StatelessWidget {
  final Door door;
  const _DoorCard({required this.door});

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

  Color get _accentColor {
    return switch (door.typeSlug) {
      'hospital' => const Color(0xFFFF6D6D),
      'shop' => const Color(0xFF37D6C5),
      'office' => const Color(0xFF4ECB71),
      'education' => const Color(0xFF6C9EFF),
      'trip' => const Color(0xFFFFB347),
      'checkpoint' => const Color(0xFFB47AFF),
      'emergency' => const Color(0xFFFF4444),
      _ => const Color(0xFFF6B94A),
    };
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final icon = _typeIcons[door.typeSlug] ?? Icons.door_front_door_rounded;

    return GestureDetector(
      onTap: () => context.push('/doors/${door.id}'),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: theme.colorScheme.surface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: theme.colorScheme.outline.withOpacity(0.2)),
        ),
        child: Row(
          children: [
            Container(
              width: 48, height: 48,
              decoration: BoxDecoration(
                color: _accentColor.withOpacity(0.15),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(icon, color: _accentColor, size: 24),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(door.name,
                      style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
                  const SizedBox(height: 2),
                  Text(
                    door.typeSlug.replaceAll('_', ' ').replaceFirstMapped(
                        RegExp(r'^.'), (m) => m.group(0)!.toUpperCase()),
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurface.withOpacity(0.5),
                    ),
                  ),
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                _StatusChip(status: door.status),
                const SizedBox(height: 4),
                if (door.isPublic)
                  const Icon(Icons.public_rounded, size: 14, color: Color(0xFF37D6C5)),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

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
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(label,
          style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.w600)),
    );
  }
}

// ── Empty state ───────────────────────────────────────────────────────────────

class _EmptyDoors extends StatelessWidget {
  final VoidCallback onAdd;
  const _EmptyDoors({required this.onAdd});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 80, height: 80,
              decoration: BoxDecoration(
                color: const Color(0xFFF6B94A).withOpacity(0.12),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.door_front_door_outlined,
                  size: 40, color: Color(0xFFF6B94A)),
            ),
            const SizedBox(height: 20),
            Text('No doors yet',
                style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w700)),
            const SizedBox(height: 8),
            Text(
              'Create your first door and get a QR code that visitors can scan.',
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurface.withOpacity(0.6),
              ),
            ),
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: onAdd,
              icon: const Icon(Icons.add_rounded),
              label: const Text('Create First Door'),
              style: FilledButton.styleFrom(
                backgroundColor: const Color(0xFFF6B94A),
                foregroundColor: Colors.black,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
                textStyle: const TextStyle(fontWeight: FontWeight.w700),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ── Sign-in prompt ────────────────────────────────────────────────────────────

class _SignInPrompt extends StatelessWidget {
  final VoidCallback onSignIn;
  const _SignInPrompt({required this.onSignIn});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.lock_outline_rounded, size: 48, color: Color(0xFFF6B94A)),
            const SizedBox(height: 16),
            Text('Sign in to manage doors',
                style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w700)),
            const SizedBox(height: 8),
            Text(
              'Your doors and QR codes are stored securely in your account.',
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurface.withOpacity(0.6),
              ),
            ),
            const SizedBox(height: 24),
            FilledButton(
              onPressed: onSignIn,
              style: FilledButton.styleFrom(
                backgroundColor: const Color(0xFFF6B94A),
                foregroundColor: Colors.black,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                minimumSize: const Size(200, 50),
                textStyle: const TextStyle(fontWeight: FontWeight.w700),
              ),
              child: const Text('Sign In'),
            ),
          ],
        ),
      ),
    );
  }
}
