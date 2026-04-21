import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:go_router/go_router.dart';
import 'package:qr_flutter/qr_flutter.dart';

import '../../../doors/models/door_models.dart';
import '../../../doors/repositories/door_repository.dart';

class DoorDetailsScreen extends StatefulWidget {
  final String doorId;
  const DoorDetailsScreen({super.key, required this.doorId});

  @override
  State<DoorDetailsScreen> createState() => _DoorDetailsScreenState();
}

class _DoorDetailsScreenState extends State<DoorDetailsScreen> {
  final _repo = DoorRepository();

  bool _loading = true;
  bool _saving = false;
  String? _error;

  Door? _door;
  final _nameCtrl = TextEditingController();
  bool _isPublic = false;



  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final door = await _repo.getDoor(widget.doorId);
      if (!mounted) return;
      setState(() {
        _door = door;
        _nameCtrl.text = door.name;
        _isPublic = door.isPublic;
        _loading = false;
      });

    } catch (_) {
      if (!mounted) return;
      setState(() { _error = 'Could not load this door.'; _loading = false; });
    }
  }



  Future<void> _save() async {
    final name = _nameCtrl.text.trim();
    if (name.isEmpty) {
      setState(() => _error = 'Door name is required.');
      return;
    }
    setState(() { _saving = true; _error = null; });
    try {
      await _repo.updateDoor(
        doorId: widget.doorId,
        name: name,
        isPublic: _isPublic,
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Saved.'), behavior: SnackBarBehavior.floating),
      );
    } catch (_) {
      if (!mounted) return;
      setState(() => _error = 'Could not save door.');
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  Future<void> _copyToken() async {
    final token = _door?.qrToken ?? '';
    if (token.isEmpty) return;
    await Clipboard.setData(ClipboardData(text: token));
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Token copied.'), behavior: SnackBarBehavior.floating),
    );
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

  Color get _accent => _door != null ? _accentFor(_door!.typeSlug) : const Color(0xFFF6B94A);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF111111),
      appBar: AppBar(
        backgroundColor: const Color(0xFF111111),
        title: Text(_door?.name ?? 'Door', style: const TextStyle(fontWeight: FontWeight.w900)),
        actions: [
          if (_door != null)
            IconButton(
              icon: const Icon(Icons.delete_outline_rounded),
              color: const Color(0xFFFF6D6D),
              onPressed: () async {
                final confirmed = await showDialog<bool>(
                  context: context,
                  builder: (_) => AlertDialog(
                    title: const Text('Archive door?'),
                    content: const Text('This door will be archived and removed from your list.'),
                    actions: [
                      TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
                      TextButton(
                        onPressed: () => Navigator.pop(context, true),
                        child: const Text('Archive', style: TextStyle(color: Color(0xFFFF6D6D))),
                      ),
                    ],
                  ),
                );
                if (confirmed == true) {
                  await _repo.deleteDoor(widget.doorId);
                  if (mounted) context.pop();
                }
              },
            ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null && _door == null
              ? Center(child: Text(_error!, style: const TextStyle(color: Color(0xFFFF6D6D))))
              : ListView(
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
                  children: [
                    // Status chip
                    if (_door != null)
                      Row(children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(20),
                            color: _door!.status == DoorStatus.active
                                ? _accent.withValues(alpha: 0.15)
                                : const Color(0x22FFFFFF),
                          ),
                          child: Row(mainAxisSize: MainAxisSize.min, children: [
                            Container(
                              width: 7, height: 7,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: _door!.status == DoorStatus.active
                                    ? _accent : const Color(0xFF666666),
                              ),
                            ),
                            const SizedBox(width: 6),
                            Text(
                              _door!.status.name[0].toUpperCase() + _door!.status.name.substring(1),
                              style: TextStyle(
                                fontSize: 12, fontWeight: FontWeight.w700,
                                color: _door!.status == DoorStatus.active
                                    ? _accent : const Color(0xFF666666),
                              ),
                            ),
                          ]),
                        ),
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(20),
                            color: _accent.withValues(alpha: 0.10),
                          ),
                          child: Text(
                            _door!.typeSlug.replaceAll('_', ' '),
                            style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: _accent),
                          ),
                        ),
                      ]),

                    // Edit section
                    const SizedBox(height: 20),
                    const Text('DOOR SETTINGS',
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700,
                            color: Color(0xFF666666), letterSpacing: 1.2)),
                    const SizedBox(height: 10),
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(20),
                        color: const Color(0xFF1D1D1D),
                      ),
                      child: Column(children: [
                        TextField(
                          controller: _nameCtrl,
                          style: const TextStyle(fontWeight: FontWeight.w700),
                          decoration: const InputDecoration(labelText: 'Door name'),
                        ),
                        const SizedBox(height: 8),
                        SwitchListTile.adaptive(
                          contentPadding: EdgeInsets.zero,
                          title: const Text('Public door',
                              style: TextStyle(fontWeight: FontWeight.w700)),
                          subtitle: const Text('Visitors can scan without being a member'),
                          value: _isPublic,
                          onChanged: (v) => setState(() => _isPublic = v),
                          activeThumbColor: _accent,
          activeTrackColor: _accent.withValues(alpha: 0.4),
                        ),
                        if (_error != null) ...[  
                          const SizedBox(height: 8),
                          Text(_error!, style: const TextStyle(color: Color(0xFFFF4444), fontSize: 13)),
                        ],
                        const SizedBox(height: 12),
                        SizedBox(
                          width: double.infinity,
                          height: 48,
                          child: ElevatedButton(
                            onPressed: _saving ? null : _save,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: _accent,
                              foregroundColor: Colors.black,
                              shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(14)),
                            ),
                            child: _saving
                                ? const SizedBox(width: 20, height: 20,
                                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black))
                                : const Text('Save', style: TextStyle(fontWeight: FontWeight.w900)),
                          ),
                        ),
                      ]),
                    ),

                    // QR section
                    if (_door != null && _door!.qrToken.isNotEmpty) ...[  
                      const SizedBox(height: 24),
                      const Text('QR CODE',
                          style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700,
                              color: Color(0xFF666666), letterSpacing: 1.2)),
                      const SizedBox(height: 10),
                      Container(
                        padding: const EdgeInsets.all(20),
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(20),
                          color: const Color(0xFF1D1D1D),
                        ),
                        child: Column(children: [
                          Container(
                            padding: const EdgeInsets.all(14),
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(16),
                              color: Colors.white,
                            ),
                            child: QrImageView(data: _door!.qrToken, size: 180),
                          ),
                          const SizedBox(height: 14),
                          GestureDetector(
                            onTap: _copyToken,
                            child: Row(children: [
                              Expanded(
                                child: Text(_door!.qrToken,
                                    style: const TextStyle(
                                        fontFamily: 'monospace',
                                        fontSize: 13,
                                        color: Color(0xFF888888))),
                              ),
                              const Icon(Icons.copy_rounded, size: 16, color: Color(0xFF888888)),
                            ]),
                          ),
                        ]),
                      ),
                    ],

                    // Interactions
                    const SizedBox(height: 24),
                    Row(children: [
                      const Expanded(
                        child: Text('RECENT VISITORS',
                            style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700,
                                color: Color(0xFF666666), letterSpacing: 1.2)),
                      ),
                      StreamBuilder<List<DoorInteraction>>(
                        stream: _repo.watchDoorInteractions(widget.doorId),
                        builder: (context, snap) {
                          final count = snap.data?.length ?? 0;
                          if (count == 0) return const SizedBox.shrink();
                          return Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(10),
                              color: _accent.withValues(alpha: 0.15),
                            ),
                            child: Text('$count',
                                style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: _accent)),
                          );
                        },
                      ),
                    ]),
                    const SizedBox(height: 10),
                    StreamBuilder<List<DoorInteraction>>(
                      stream: _repo.watchDoorInteractions(widget.doorId),
                      builder: (context, snap) {
                        if (snap.connectionState == ConnectionState.waiting) {
                          return const Center(child: CircularProgressIndicator());
                        }
                        final items = snap.data ?? [];
                        if (items.isEmpty) {
                          return Container(
                            padding: const EdgeInsets.all(20),
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(20),
                              color: const Color(0xFF1D1D1D),
                            ),
                            child: const Center(
                              child: Text('No visitors yet.',
                                  style: TextStyle(color: Color(0xFF666666))),
                            ),
                          );
                        }
                        return Column(
                          children: items.map((interaction) {
                            final name = interaction.visitorName ?? 'Anonymous';
                            final time = interaction.createdAt != null
                                ? _formatTime(interaction.createdAt!)
                                : '';
                            return Container(
                              margin: const EdgeInsets.only(bottom: 8),
                              padding: const EdgeInsets.all(14),
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(16),
                                color: const Color(0xFF1D1D1D),
                              ),
                              child: Row(children: [
                                Container(
                                  width: 36, height: 36,
                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    color: _accent.withValues(alpha: 0.15),
                                  ),
                                  child: Icon(Icons.person_rounded, color: _accent, size: 18),
                                ),
                                const SizedBox(width: 12),
                                Expanded(child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(name, style: const TextStyle(
                                        fontWeight: FontWeight.w700, fontSize: 14)),
                                    if (interaction.visitorMessage != null)
                                      Text(interaction.visitorMessage!,
                                          style: const TextStyle(
                                              color: Color(0xFF888888), fontSize: 12)),
                                  ],
                                )),
                                Column(crossAxisAlignment: CrossAxisAlignment.end, children: [
                                  _StatusChip(status: interaction.status, accent: _accent),
                                  if (time.isNotEmpty)
                                    Text(time,
                                        style: const TextStyle(
                                            color: Color(0xFF666666), fontSize: 11)),
                                ]),
                              ]),
                            );
                          }).toList(),
                        );
                      },
                    ),
                  ],
                ),
    );
  }

  String _formatTime(Timestamp ts) {
    final dt = ts.toDate();
    final now = DateTime.now();
    final diff = now.difference(dt);
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    return '${diff.inDays}d ago';
  }
}

class _StatusChip extends StatelessWidget {
  final InteractionStatus status;
  final Color accent;
  const _StatusChip({required this.status, required this.accent});

  @override
  Widget build(BuildContext context) {
    Color color;
    switch (status) {
      case InteractionStatus.admitted: color = const Color(0xFF4ECB71); break;
      case InteractionStatus.declined: color = const Color(0xFFFF6D6D); break;
      case InteractionStatus.completed: color = const Color(0xFF888888); break;
      case InteractionStatus.seen: color = accent; break;
      default: color = const Color(0xFFF6B94A);
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(10),
        color: color.withValues(alpha: 0.15),
      ),
      child: Text(
        status.name[0].toUpperCase() + status.name.substring(1),
        style: TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: color),
      ),
    );
  }
}
