import 'dart:convert';

import 'package:connectivity_plus/connectivity_plus.dart';

import '../../../core/config/app_env.dart';
import '../../sync/data/sync_local_repository.dart';
import '../../sync/data/sync_remote_repository.dart';

class SyncManager {
  final SyncLocalRepository local;
  final SyncRemoteRepository remote;

  bool _isRunning = false;

  SyncManager({required this.local, required this.remote});

  Future<void> syncNow({
    required String deviceId,
    String streamName = 'core',
    List<String> entityTypes = const [
      'organizations',
      'events',
      'groups',
      'qr_scans',
      'queue_tickets',
      'chat_messages',
      'broadcast_deliveries',
      'notifications',
    ],
  }) async {
    if (_isRunning) return;
    _isRunning = true;
    try {
      final connectivity = await Connectivity().checkConnectivity();
      if (connectivity.contains(ConnectivityResult.none)) return;

      await _push(deviceId: deviceId, streamName: streamName);
      await _pull(deviceId: deviceId, streamName: streamName, entityTypes: entityTypes);
    } finally {
      _isRunning = false;
    }
  }

  Future<void> _push({required String deviceId, required String streamName}) async {
    final pending = await local.pending(limit: AppEnv.syncBatchSize);
    if (pending.isEmpty) return;

    final operations = pending.map((row) {
      return {
        'idempotency_key': row['idempotency_key'],
        'client_id': row['local_op_id'],
        'operation': row['operation'],
        'entity_type': row['entity_type'],
        'entity_id': row['entity_id'],
        'payload': jsonDecode(row['payload_json'] as String),
        'sequence': row['sequence'],
        'created_at_client': row['created_at_client'],
        'updated_at_client': row['updated_at_client'],
        'base_version': row['base_version'],
      };
    }).toList();

    final result = await remote.push(
      deviceId: deviceId,
      streamName: streamName,
      operations: operations,
    );

    final opResults = List<Map<String, dynamic>>.from((result['results'] as List?) ?? []);
    for (final row in pending) {
      final localOpId = row['local_op_id'] as String;
      final match = opResults.where((r) => r['client_id'] == localOpId).cast<Map<String, dynamic>>().toList();
      if (match.isEmpty) continue;
      final status = (match.first['status'] as String?) ?? 'failed';

      switch (status) {
        case 'applied':
        case 'ignored_duplicate':
          await local.markStatus(localOpId, 'synced');
          break;
        case 'conflict':
          await local.markStatus(localOpId, 'conflict', errorCode: 'conflict', errorMessage: 'Version conflict');
          break;
        default:
          await local.markStatus(
            localOpId,
            'failed_retryable',
            errorCode: match.first['error_code']?.toString(),
            errorMessage: match.first['error_message']?.toString(),
          );
      }
    }
  }

  Future<void> _pull({
    required String deviceId,
    required String streamName,
    required List<String> entityTypes,
  }) async {
    final cursor = await local.getCursor(streamName);
    final since = (cursor?['cursor_token'] as String?) ?? '';

    final result = await remote.pull(
      deviceId: deviceId,
      streamName: streamName,
      since: since,
      entityTypes: entityTypes,
    );

    final delta = Map<String, dynamic>.from((result['delta'] as Map?) ?? {});
    for (final entry in delta.entries) {
      final entityType = entry.key;
      final rows = List<Map<String, dynamic>>.from(entry.value as List);
      for (final row in rows) {
        final entityId = (row['id'] ?? '').toString();
        final version = (row['version'] as num?)?.toInt() ?? 1;
        final updatedAt = row['updated_at_server']?.toString();
        await local.upsertEntityCache(entityType, entityId, row, version, updatedAt);
      }
    }

    final tombstones = Map<String, dynamic>.from((result['tombstones'] as Map?) ?? {});
    for (final entry in tombstones.entries) {
      final entityType = entry.key;
      final ids = List<dynamic>.from(entry.value as List);
      for (final id in ids) {
        await local.deleteEntityCache(entityType, id.toString());
      }
    }

    final nextCursor = (result['cursor'] ?? '').toString();
    final lastSeenVersion = (result['last_seen_version'] as num?)?.toInt() ?? 0;
    await local.upsertCursor(
      streamName: streamName,
      cursorToken: nextCursor,
      lastSeenVersion: lastSeenVersion,
    );

    if (nextCursor.isNotEmpty) {
      await remote.ack(deviceId: deviceId, cursor: nextCursor);
    }
  }
}
