import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../models/door_models.dart';
import '../../repositories/door_repository.dart';

/// Step 1 of create door: pick a type from the live Firestore list.
class DoorTypePickerScreen extends StatefulWidget {
  const DoorTypePickerScreen({super.key});

  @override
  State<DoorTypePickerScreen> createState() => _DoorTypePickerScreenState();
}

class _DoorTypePickerScreenState extends State<DoorTypePickerScreen> {
  final _repo = DoorRepository();
  List<DoorType>? _types;
  String? _error;
  DoorType? _selected;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final types = await _repo.getDoorTypes();
      if (!mounted) return;
      setState(() => _types = types);
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString());
    }
  }

  static const _iconMap = {
    'home': Icons.home_rounded,
    'local_hospital': Icons.local_hospital_rounded,
    'storefront': Icons.storefront_rounded,
    'business': Icons.business_rounded,
    'school': Icons.school_rounded,
    'directions_bus': Icons.directions_bus_rounded,
    'fact_check': Icons.fact_check_rounded,
    'emergency': Icons.emergency_rounded,
  };

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Choose Door Type')),
      body: Builder(builder: (_) {
        if (_error != null) {
          return Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.error_outline, size: 48, color: Color(0xFFFF6D6D)),
                const SizedBox(height: 12),
                Text('Failed to load door types', style: theme.textTheme.titleMedium),
                const SizedBox(height: 6),
                Text(_error!, style: theme.textTheme.bodySmall, textAlign: TextAlign.center),
                const SizedBox(height: 16),
                FilledButton.icon(
                  onPressed: () { setState(() { _error = null; _types = null; }); _load(); },
                  icon: const Icon(Icons.refresh),
                  label: const Text('Retry'),
                ),
              ],
            ),
          );
        }

        if (_types == null) {
          return const Center(child: CircularProgressIndicator());
        }

        return Column(
          children: [
            Expanded(
              child: GridView.builder(
                padding: const EdgeInsets.all(16),
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  mainAxisSpacing: 12,
                  crossAxisSpacing: 12,
                  childAspectRatio: 1.1,
                ),
                itemCount: _types!.length,
                itemBuilder: (_, i) {
                  final t = _types![i];
                  final isSelected = _selected?.id == t.id;
                  return GestureDetector(
                    onTap: () => setState(() => _selected = t),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 180),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(20),
                        color: isSelected
                            ? const Color(0xFFF6B94A).withOpacity(0.15)
                            : theme.colorScheme.surface,
                        border: Border.all(
                          color: isSelected
                              ? const Color(0xFFF6B94A)
                              : theme.colorScheme.outline.withOpacity(0.3),
                          width: isSelected ? 2 : 1,
                        ),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              _iconMap[t.icon] ?? Icons.door_front_door_rounded,
                              size: 36,
                              color: isSelected
                                  ? const Color(0xFFF6B94A)
                                  : theme.colorScheme.onSurface.withOpacity(0.7),
                            ),
                            const SizedBox(height: 10),
                            Text(
                              t.name,
                              textAlign: TextAlign.center,
                              style: theme.textTheme.titleSmall?.copyWith(
                                color: isSelected ? const Color(0xFFF6B94A) : null,
                                fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              '${t.features.length} features',
                              style: theme.textTheme.bodySmall?.copyWith(
                                color: theme.colorScheme.onSurface.withOpacity(0.5),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
            SafeArea(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                child: FilledButton(
                  onPressed: _selected == null
                      ? null
                      : () => context.push('/doors/create', extra: _selected),
                  style: FilledButton.styleFrom(
                    minimumSize: const Size.fromHeight(52),
                    backgroundColor: const Color(0xFFF6B94A),
                    foregroundColor: Colors.black,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  ),
                  child: const Text('Continue', style: TextStyle(fontWeight: FontWeight.w700)),
                ),
              ),
            ),
          ],
        );
      }),
    );
  }
}
