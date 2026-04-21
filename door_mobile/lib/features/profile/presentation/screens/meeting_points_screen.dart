import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';

class MeetingPointsScreen extends StatefulWidget {
  const MeetingPointsScreen({super.key});

  @override
  State<MeetingPointsScreen> createState() => _MeetingPointsScreenState();
}

class _MeetingPointsScreenState extends State<MeetingPointsScreen> {
  final _titleCtrl = TextEditingController();
  final _noteCtrl = TextEditingController();
  final _locationCtrl = TextEditingController();
  int _durationHours = 1;

  List<Map<String, dynamic>> _savedLocations = [];
  List<Map<String, dynamic>> _savedPoints = [];

  @override
  void initState() {
    super.initState();
    _loadState();
  }

  @override
  void dispose() {
    _titleCtrl.dispose();
    _noteCtrl.dispose();
    _locationCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadState() async {
    final prefs = await SharedPreferences.getInstance();
    final defaultDuration = prefs.getInt('meeting_default_duration') ?? 1;
    final raw = prefs.getString('meeting_saved_locations') ?? '[]';
    final pointsRaw = prefs.getString('meeting_saved_points') ?? '[]';
    try {
      final decoded = jsonDecode(raw) as List;
      final pointsDecoded = jsonDecode(pointsRaw) as List;
      setState(() {
        _durationHours = defaultDuration;
        _savedLocations = decoded.map((e) => Map<String, dynamic>.from(e as Map)).toList();
        _savedPoints = pointsDecoded.map((e) => Map<String, dynamic>.from(e as Map)).toList();
      });
    } catch (_) {
      setState(() {
        _durationHours = defaultDuration;
        _savedLocations = [];
        _savedPoints = [];
      });
    }
  }

  Future<void> _saveLocationLabel() async {
    final label = _locationCtrl.text.trim();
    if (label.isEmpty) return;
    final prefs = await SharedPreferences.getInstance();

    final next = [
      {'id': 'loc_${DateTime.now().millisecondsSinceEpoch}', 'label': label},
      ..._savedLocations.where((l) => (l['label'] ?? '').toString().toLowerCase() != label.toLowerCase()),
    ];
    await prefs.setString('meeting_saved_locations', jsonEncode(next));
    setState(() => _savedLocations = next);
  }

  Future<void> _deleteLocation(String id) async {
    final prefs = await SharedPreferences.getInstance();
    final next = _savedLocations.where((l) => (l['id'] ?? '') != id).toList();
    await prefs.setString('meeting_saved_locations', jsonEncode(next));
    setState(() => _savedLocations = next);
  }

  Future<void> _saveMeetingPoint() async {
    final title = _titleCtrl.text.trim();
    final location = _locationCtrl.text.trim();
    final note = _noteCtrl.text.trim();
    if (title.isEmpty && location.isEmpty && note.isEmpty) return;

    final prefs = await SharedPreferences.getInstance();
    final entry = {
      'id': 'meet_${DateTime.now().millisecondsSinceEpoch}',
      'title': title,
      'location': location,
      'note': note,
      'duration': _durationHours,
      'created_at': DateTime.now().millisecondsSinceEpoch,
    };
    final next = [entry, ..._savedPoints].take(30).toList();
    await prefs.setString('meeting_saved_points', jsonEncode(next));
    setState(() => _savedPoints = next);
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Meeting point saved.'), behavior: SnackBarBehavior.floating),
    );
  }

  Future<void> _deleteMeetingPoint(String id) async {
    final prefs = await SharedPreferences.getInstance();
    final next = _savedPoints.where((p) => (p['id'] ?? '') != id).toList();
    await prefs.setString('meeting_saved_points', jsonEncode(next));
    setState(() => _savedPoints = next);
  }

  Future<void> _setDefaultDuration(int value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt('meeting_default_duration', value);
    setState(() => _durationHours = value);
  }

  String _shareText() {
    final title = _titleCtrl.text.trim();
    final location = _locationCtrl.text.trim();
    final note = _noteCtrl.text.trim();

    final lines = <String>[
      if (title.isNotEmpty) 'Meet: $title',
      if (location.isNotEmpty) 'Location: $location',
      if (note.isNotEmpty) 'Note: $note',
      'Duration: $_durationHours hour${_durationHours > 1 ? "s" : ""}',
    ];
    return lines.join('\n');
  }

  Future<void> _copyShareText() async {
    await Clipboard.setData(ClipboardData(text: _shareText()));
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Meeting details copied.'), behavior: SnackBarBehavior.floating),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Meeting points')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Create meeting point', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800)),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _titleCtrl,
                    decoration: const InputDecoration(labelText: 'Meet location / title'),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _noteCtrl,
                    maxLines: 4,
                    decoration: const InputDecoration(labelText: 'Note'),
                  ),
                  const SizedBox(height: 12),
                  InputDecorator(
                    decoration: const InputDecoration(labelText: 'Meet duration'),
                    child: DropdownButtonHideUnderline(
                      child: DropdownButton<int>(
                        value: _durationHours,
                        items: [1, 2, 3, 4, 5, 6]
                            .map((v) => DropdownMenuItem<int>(value: v, child: Text('$v hour${v > 1 ? "s" : ""}')))
                            .toList(),
                        onChanged: (v) => _setDefaultDuration(v ?? 1),
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _locationCtrl,
                    decoration: const InputDecoration(labelText: 'Location label'),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: _saveLocationLabel,
                          icon: const Icon(Icons.bookmark_add_outlined),
                          label: const Text('Save location'),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: _copyShareText,
                          icon: const Icon(Icons.copy_rounded),
                          label: const Text('Copy'),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton.icon(
                      onPressed: _saveMeetingPoint,
                      icon: const Icon(Icons.save_outlined),
                      label: const Text('Save meeting point'),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: const Color(0x1FFFFFFF)),
                      color: const Color(0x141D1D1D),
                    ),
                    child: const Text('Tip: Use a saved location label so sharing is consistent.'),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Saved meeting points', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800)),
                  const SizedBox(height: 10),
                  if (_savedPoints.isEmpty)
                    Text('No saved meeting points yet.', style: Theme.of(context).textTheme.bodyMedium)
                  else
                    ..._savedPoints.take(12).map((p) {
                      final id = (p['id'] ?? '').toString();
                      final title = (p['title'] ?? '').toString().trim();
                      final location = (p['location'] ?? '').toString().trim();
                      final duration = (p['duration'] ?? 1).toString();
                      final label = title.isNotEmpty ? title : (location.isNotEmpty ? location : 'Meeting point');
                      return ListTile(
                        contentPadding: EdgeInsets.zero,
                        title: Text(label, style: const TextStyle(fontWeight: FontWeight.w700)),
                        subtitle: Text('${location.isNotEmpty ? location : 'No location'} • ${duration}h'),
                        trailing: IconButton(
                          icon: const Icon(Icons.delete_outline_rounded, color: Color(0xFFFF6D6D)),
                          onPressed: () => _deleteMeetingPoint(id),
                        ),
                        onTap: () {
                          setState(() {
                            _titleCtrl.text = title;
                            _locationCtrl.text = location;
                            _noteCtrl.text = (p['note'] ?? '').toString();
                            _durationHours = int.tryParse(duration) ?? _durationHours;
                          });
                        },
                      );
                    }),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Saved locations', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800)),
                  const SizedBox(height: 10),
                  if (_savedLocations.isEmpty)
                    Text('No saved locations yet.', style: Theme.of(context).textTheme.bodyMedium)
                  else
                    ..._savedLocations.take(12).map((l) {
                      final id = (l['id'] ?? '').toString();
                      final label = (l['label'] ?? '').toString();
                      return ListTile(
                        contentPadding: EdgeInsets.zero,
                        title: Text(label, style: const TextStyle(fontWeight: FontWeight.w700)),
                        trailing: IconButton(
                          icon: const Icon(Icons.delete_outline_rounded, color: Color(0xFFFF6D6D)),
                          onPressed: () => _deleteLocation(id),
                        ),
                        onTap: () => setState(() => _locationCtrl.text = label),
                      );
                    }),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
