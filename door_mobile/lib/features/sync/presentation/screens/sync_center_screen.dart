import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../../features/sync/service/sync_manager.dart';

class SyncCenterScreen extends StatefulWidget {
  const SyncCenterScreen({super.key});

  @override
  State<SyncCenterScreen> createState() => _SyncCenterScreenState();
}

class _SyncCenterScreenState extends State<SyncCenterScreen> {
  bool _running = false;
  String _status = 'Idle';

  Future<void> _runSync() async {
    setState(() {
      _running = true;
      _status = 'Sync in progress...';
    });

    try {
      await context.read<SyncManager>().syncNow(deviceId: 'flutter_device');
      if (!mounted) return;
      setState(() => _status = 'Sync complete');
    } catch (e) {
      if (!mounted) return;
      setState(() => _status = 'Sync failed: $e');
    } finally {
      if (mounted) {
        setState(() => _running = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Sync Center')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(_status, style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _running ? null : _runSync,
              icon: const Icon(Icons.sync),
              label: Text(_running ? 'Syncing...' : 'Sync Now'),
            ),
          ],
        ),
      ),
    );
  }
}
