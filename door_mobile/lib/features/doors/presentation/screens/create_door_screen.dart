import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:go_router/go_router.dart';

import '../../../doors/models/door_models.dart';
import '../../../doors/repositories/door_repository.dart';

class CreateDoorScreen extends StatefulWidget {
  const CreateDoorScreen({super.key});

  @override
  State<CreateDoorScreen> createState() => _CreateDoorScreenState();
}

class _CreateDoorScreenState extends State<CreateDoorScreen> {
  final _repo = DoorRepository();
  final _nameCtrl = TextEditingController();

  bool _loadingTypes = true;
  bool _creating = false;
  String? _error;

  List<DoorType> _doorTypes = [];
  DoorType? _selectedType;
  final Map<String, dynamic> _fieldValues = {};

  @override
  void initState() {
    super.initState();
    _loadTypes();
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadTypes() async {
    try {
      final types = await _repo.getDoorTypes();
      if (!mounted) return;
      setState(() {
        _doorTypes = types;
        if (types.isNotEmpty) _selectedType = types.first;
        _loadingTypes = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _error = 'Could not load door types.';
        _loadingTypes = false;
      });
    }
  }

  Future<void> _create() async {
    if (FirebaseAuth.instance.currentUser == null) {
      setState(() => _error = 'Sign in first.');
      return;
    }
    if (_selectedType == null) {
      setState(() => _error = 'Select a door type.');
      return;
    }
    final name = _nameCtrl.text.trim();
    if (name.isEmpty) {
      setState(() => _error = 'Door name is required.');
      return;
    }
    for (final f in _selectedType!.fields) {
      if (f.isRequired &&
          (_fieldValues[f.fieldKey] == null ||
              _fieldValues[f.fieldKey].toString().isEmpty)) {
        setState(() => _error = '${f.label} is required.');
        return;
      }
    }
    setState(() {
      _creating = true;
      _error = null;
    });
    try {
      final result = await _repo.createDoor(
        name: name,
        typeId: _selectedType!.id,
        fieldValues: Map<String, dynamic>.from(_fieldValues),
      );
      if (!mounted) return;
      context.pushReplacement('/doors/${result.id}');
    } catch (_) {
      if (!mounted) return;
      setState(() => _error = 'Could not create door. Please try again.');
    } finally {
      if (mounted) setState(() => _creating = false);
    }
  }

  Color _accentFor(String slug) {
    switch (slug) {
      case 'hospital': return const Color(0xFFFF6D6D);
      case 'shop':     return const Color(0xFF37D6C5);
      case 'office':   return const Color(0xFF4D9EFF);
      case 'education':return const Color(0xFFA78BFA);
      case 'trip':     return const Color(0xFF4ECB71);
      case 'checkpoint':return const Color(0xFFFF9A3C);
      case 'emergency':return const Color(0xFFFF4444);
      default:         return const Color(0xFFF6B94A);
    }
  }

  IconData _iconFor(String name) {
    switch (name) {
      case 'local_hospital': return Icons.local_hospital_rounded;
      case 'storefront':     return Icons.storefront_rounded;
      case 'business':       return Icons.business_rounded;
      case 'school':         return Icons.school_rounded;
      case 'directions_bus': return Icons.directions_bus_rounded;
      case 'fact_check':     return Icons.fact_check_rounded;
      case 'emergency':      return Icons.emergency_rounded;
      default:               return Icons.home_rounded;
    }
  }

  Widget _buildField(DoorTypeField field) {
    switch (field.fieldType) {
      case 'boolean':
        return SwitchListTile.adaptive(
          contentPadding: EdgeInsets.zero,
          title: Text(field.label,
              style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
          value: (_fieldValues[field.fieldKey] as bool?) ?? false,
          onChanged: (v) => setState(() => _fieldValues[field.fieldKey] = v),
        );
      case 'select':
        return InputDecorator(
          decoration: InputDecoration(labelText: field.label + (field.isRequired ? ' *' : '')),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<String>(
              value: _fieldValues[field.fieldKey]?.toString(),
              hint: const Text('Select…'),
              items: field.options
                  .map((o) => DropdownMenuItem(
                        value: o['value'],
                        child: Text(o['label'] ?? o['value'] ?? ''),
                      ))
                  .toList(),
              onChanged: (v) => setState(() => _fieldValues[field.fieldKey] = v),
            ),
          ),
        );
      case 'number':
        return TextField(
          keyboardType: TextInputType.number,
          decoration: InputDecoration(labelText: field.label + (field.isRequired ? ' *' : '')),
          onChanged: (v) => _fieldValues[field.fieldKey] = int.tryParse(v) ?? v,
        );
      case 'textarea':
        return TextField(
          maxLines: 3,
          decoration: InputDecoration(
            labelText: field.label + (field.isRequired ? ' *' : ''),
            alignLabelWithHint: true,
          ),
          onChanged: (v) => _fieldValues[field.fieldKey] = v,
        );
      default:
        return TextField(
          decoration: InputDecoration(labelText: field.label + (field.isRequired ? ' *' : '')),
          onChanged: (v) => _fieldValues[field.fieldKey] = v,
        );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF111111),
      appBar: AppBar(
        backgroundColor: const Color(0xFF111111),
        title: const Text('New Door', style: TextStyle(fontWeight: FontWeight.w900)),
      ),
      body: _loadingTypes
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
              children: [
                // Type picker
                const Text('DOOR TYPE',
                    style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700,
                        color: Color(0xFF666666), letterSpacing: 1.2)),
                const SizedBox(height: 10),
                SizedBox(
                  height: 100,
                  child: ListView.separated(
                    scrollDirection: Axis.horizontal,
                    itemCount: _doorTypes.length,
                    separatorBuilder: (_, __) => const SizedBox(width: 10),
                    itemBuilder: (_, i) {
                      final t = _doorTypes[i];
                      final accent = _accentFor(t.slug);
                      final selected = _selectedType?.id == t.id;
                      return GestureDetector(
                        onTap: () => setState(() {
                          _selectedType = t;
                          _fieldValues.clear();
                        }),
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 180),
                          width: 88,
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(20),
                            color: selected ? accent.withValues(alpha: 0.15) : const Color(0xFF1D1D1D),
                            border: Border.all(
                              color: selected ? accent.withValues(alpha: 0.7) : const Color(0x22FFFFFF),
                              width: selected ? 1.5 : 1,
                            ),
                          ),
                          padding: const EdgeInsets.all(12),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(_iconFor(t.icon),
                                  color: selected ? accent : const Color(0xFF666666), size: 28),
                              const SizedBox(height: 6),
                              Text(t.name,
                                  style: TextStyle(
                                    fontSize: 11, fontWeight: FontWeight.w700,
                                    color: selected ? accent : const Color(0xFF666666),
                                  ),
                                  textAlign: TextAlign.center,
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),

                // Feature chips
                if (_selectedType != null && _selectedType!.features.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 6, runSpacing: 6,
                    children: _selectedType!.features.map((f) => Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(20),
                        color: _accentFor(_selectedType!.slug).withValues(alpha: 0.12),
                      ),
                      child: Text(f.replaceAll('_', ' '),
                          style: TextStyle(
                            fontSize: 11,
                            color: _accentFor(_selectedType!.slug),
                            fontWeight: FontWeight.w600,
                          )),
                    )).toList(),
                  ),
                ],

                // Door name
                const SizedBox(height: 24),
                const Text('DOOR DETAILS',
                    style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700,
                        color: Color(0xFF666666), letterSpacing: 1.2)),
                const SizedBox(height: 10),
                TextField(
                  controller: _nameCtrl,
                  textInputAction: TextInputAction.next,
                  style: const TextStyle(fontWeight: FontWeight.w700),
                  decoration: InputDecoration(
                    labelText: 'Door name *',
                    hintText: _selectedType != null ? 'e.g. My ${_selectedType!.name} Door' : 'Name',
                    filled: true,
                    fillColor: const Color(0xFF1D1D1D),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(14), borderSide: BorderSide.none),
                  ),
                ),

                // Dynamic fields
                if (_selectedType != null && _selectedType!.fields.isNotEmpty) ...[
                  const SizedBox(height: 20),
                  const Text('SETUP OPTIONS',
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700,
                          color: Color(0xFF666666), letterSpacing: 1.2)),
                  const SizedBox(height: 10),
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(20),
                      color: const Color(0xFF1D1D1D),
                    ),
                    child: Column(
                      children: _selectedType!.fields
                          .map((f) => Padding(
                                padding: const EdgeInsets.only(bottom: 14),
                                child: _buildField(f),
                              ))
                          .toList(),
                    ),
                  ),
                ],

                // Error
                if (_error != null) ...[  
                  const SizedBox(height: 14),
                  Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(14),
                      color: const Color(0xFFFF4444).withValues(alpha: 0.12),
                    ),
                    child: Row(children: [
                      const Icon(Icons.error_outline, color: Color(0xFFFF4444), size: 18),
                      const SizedBox(width: 8),
                      Expanded(child: Text(_error!,
                          style: const TextStyle(color: Color(0xFFFF4444), fontSize: 13))),
                    ]),
                  ),
                ],

                const SizedBox(height: 24),
                SizedBox(
                  height: 54,
                  child: ElevatedButton(
                    onPressed: _creating ? null : _create,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _selectedType != null
                          ? _accentFor(_selectedType!.slug)
                          : const Color(0xFFF6B94A),
                      foregroundColor: Colors.black,
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16)),
                    ),
                    child: _creating
                        ? const SizedBox(width: 22, height: 22,
                            child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black))
                        : const Text('Create Door',
                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900)),
                  ),
                ),
              ],
            ),
    );
  }
}
