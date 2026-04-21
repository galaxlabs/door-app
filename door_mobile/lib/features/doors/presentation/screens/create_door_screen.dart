import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../models/door_models.dart';
import '../../repositories/door_repository.dart';

/// Step 2 of create door: name it and fill any dynamic fields for the chosen type.
class CreateDoorScreen extends StatefulWidget {
  final DoorType? doorType;
  const CreateDoorScreen({super.key, this.doorType});

  @override
  State<CreateDoorScreen> createState() => _CreateDoorScreenState();
}

class _CreateDoorScreenState extends State<CreateDoorScreen> {
  final _repo = DoorRepository();
  final _formKey = GlobalKey<FormState>();
  final _nameCtrl = TextEditingController();
  final Map<String, TextEditingController> _fieldCtrls = {};
  final Map<String, dynamic> _fieldValues = {};

  bool _isPublic = false;
  bool _saving = false;
  String? _error;

  DoorType? get _type => widget.doorType;

  @override
  void initState() {
    super.initState();
    // Pre-build controllers for each dynamic field
    for (final field in _type?.fields ?? []) {
      _fieldCtrls[field.fieldKey] = TextEditingController(
        text: field.defaultValue?.toString() ?? '',
      );
    }
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    for (final c in _fieldCtrls.values) {
      c.dispose();
    }
    super.dispose();
  }

  Future<void> _submit() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;

    // Collect dynamic field values
    for (final field in _type?.fields ?? []) {
      final raw = _fieldCtrls[field.fieldKey]?.text.trim() ?? '';
      _fieldValues[field.fieldKey] = switch (field.fieldType) {
        'number' => num.tryParse(raw) ?? raw,
        'boolean' => raw.toLowerCase() == 'true',
        _ => raw,
      };
    }

    setState(() { _saving = true; _error = null; });

    try {
      final result = await _repo.createDoor(
        name: _nameCtrl.text.trim(),
        typeId: _type!.id,
        isPublic: _isPublic,
        fieldValues: _fieldValues,
      );
      if (!mounted) return;
      context.go('/doors/${result.id}');
    } catch (e) {
      if (!mounted) return;
      setState(() { _saving = false; _error = e.toString(); });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(_type != null ? 'New ${_type!.name} Door' : 'Create Door'),
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Type badge
            if (_type != null) ...[
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                decoration: BoxDecoration(
                  color: const Color(0xFFF6B94A).withOpacity(0.12),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFFF6B94A).withOpacity(0.4)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.door_front_door_rounded, color: Color(0xFFF6B94A), size: 20),
                    const SizedBox(width: 8),
                    Text(
                      _type!.name,
                      style: const TextStyle(
                        color: Color(0xFFF6B94A),
                        fontWeight: FontWeight.w700,
                        fontSize: 14,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      '· ${_type!.features.length} features',
                      style: TextStyle(
                        color: theme.colorScheme.onSurface.withOpacity(0.5),
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
            ],

            // Door name
            TextFormField(
              controller: _nameCtrl,
              decoration: const InputDecoration(
                labelText: 'Door name',
                hintText: 'e.g. My Clinic, Main Entrance…',
                prefixIcon: Icon(Icons.label_outline_rounded),
              ),
              textCapitalization: TextCapitalization.words,
              validator: (v) => (v?.trim().isEmpty ?? true) ? 'Enter a door name' : null,
            ),
            const SizedBox(height: 16),

            // Public toggle
            SwitchListTile(
              value: _isPublic,
              onChanged: (v) => setState(() => _isPublic = v),
              title: const Text('Public door'),
              subtitle: const Text('Anyone with the QR link can see this door'),
              contentPadding: EdgeInsets.zero,
              activeColor: const Color(0xFFF6B94A),
            ),

            // Dynamic fields from door type
            if ((_type?.fields ?? []).isNotEmpty) ...[
              const Divider(height: 32),
              Text('Type fields', style: theme.textTheme.titleSmall?.copyWith(
                color: theme.colorScheme.onSurface.withOpacity(0.6),
                letterSpacing: 0.5,
              )),
              const SizedBox(height: 12),
              ..._type!.fields.map((field) => Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: _buildFieldWidget(field, theme),
              )),
            ],

            // Error
            if (_error != null) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.red.withOpacity(0.4)),
                ),
                child: Text(_error!, style: const TextStyle(color: Colors.red, fontSize: 13)),
              ),
            ],

            const SizedBox(height: 24),
            FilledButton(
              onPressed: _saving ? null : _submit,
              style: FilledButton.styleFrom(
                minimumSize: const Size.fromHeight(52),
                backgroundColor: const Color(0xFFF6B94A),
                foregroundColor: Colors.black,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              ),
              child: _saving
                  ? const SizedBox(
                      height: 20, width: 20,
                      child: CircularProgressIndicator(color: Colors.black, strokeWidth: 2))
                  : const Text('Create Door', style: TextStyle(fontWeight: FontWeight.w700)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFieldWidget(DoorTypeField field, ThemeData theme) {
    switch (field.fieldType) {
      case 'boolean':
        return SwitchListTile(
          value: (_fieldValues[field.fieldKey] as bool?) ?? false,
          onChanged: (v) => setState(() => _fieldValues[field.fieldKey] = v),
          title: Text(field.label),
          contentPadding: EdgeInsets.zero,
          activeColor: const Color(0xFFF6B94A),
        );

      case 'select':
        final opts = field.options;
        return DropdownButtonFormField<String>(
          value: _fieldCtrls[field.fieldKey]?.text.isNotEmpty == true
              ? _fieldCtrls[field.fieldKey]!.text
              : null,
          decoration: InputDecoration(labelText: field.label),
          items: opts
              .map((o) => DropdownMenuItem(value: o['value'], child: Text(o['label'] ?? o['value'] ?? '')))
              .toList(),
          onChanged: (v) => setState(() => _fieldCtrls[field.fieldKey]?.text = v ?? ''),
          validator: field.isRequired
              ? (v) => (v == null || v.isEmpty) ? '${field.label} is required' : null
              : null,
        );

      case 'textarea':
        return TextFormField(
          controller: _fieldCtrls[field.fieldKey],
          decoration: InputDecoration(labelText: field.label),
          maxLines: 3,
          validator: field.isRequired
              ? (v) => (v?.trim().isEmpty ?? true) ? '${field.label} is required' : null
              : null,
        );

      default:
        return TextFormField(
          controller: _fieldCtrls[field.fieldKey],
          decoration: InputDecoration(labelText: field.label),
          keyboardType: field.fieldType == 'number'
              ? TextInputType.number
              : field.fieldType == 'date'
                  ? TextInputType.datetime
                  : TextInputType.text,
          validator: field.isRequired
              ? (v) => (v?.trim().isEmpty ?? true) ? '${field.label} is required' : null
              : null,
        );
    }
  }
}
