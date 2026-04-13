import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:sqflite/sqflite.dart';
import 'package:uuid/uuid.dart';

import '../../../core/db/local_database.dart';

class SyncLocalRepository {
  static const _uuid = Uuid();

  Future<Database> get _db async => LocalDatabase.instance();

  Future<int> nextSequence() async {
    if (kIsWeb) {
      return 1;
    }
    final db = await _db;
    final rows = await db.rawQuery('SELECT COALESCE(MAX(sequence), 0) as max_seq FROM sync_outbox');
    final maxSeq = rows.first['max_seq'] as int;
    return maxSeq + 1;
  }

  Future<void> enqueue({
    required String entityType,
    required String operation,
    String? entityId,
    required Map<String, dynamic> payload,
    int? baseVersion,
    String? createdByDeviceId,
  }) async {
    if (kIsWeb) {
      return;
    }
    final db = await _db;
    final now = DateTime.now().toIso8601String();
    final seq = await nextSequence();

    await db.insert('sync_outbox', {
      'local_op_id': _uuid.v4(),
      'idempotency_key': _uuid.v4(),
      'entity_type': entityType,
      'entity_id': entityId,
      'operation': operation,
      'payload_json': jsonEncode(payload),
      'base_version': baseVersion,
      'sequence': seq,
      'status': 'pending',
      'created_at_client': now,
      'updated_at_client': now,
      'created_by_device_id': createdByDeviceId,
      'retry_count': 0,
    });
  }

  Future<List<Map<String, dynamic>>> pending({int limit = 100}) async {
    if (kIsWeb) {
      return const [];
    }
    final db = await _db;
    return db.query(
      'sync_outbox',
      where: 'status IN (?, ?, ?)',
      whereArgs: const ['pending', 'failed_retryable', 'conflict_retryable'],
      orderBy: 'sequence ASC',
      limit: limit,
    );
  }

  Future<void> markStatus(String localOpId, String status, {String? errorCode, String? errorMessage}) async {
    if (kIsWeb) {
      return;
    }
    final db = await _db;
    await db.update(
      'sync_outbox',
      {
        'status': status,
        'error_code': errorCode,
        'error_message': errorMessage,
      },
      where: 'local_op_id = ?',
      whereArgs: [localOpId],
    );
  }

  Future<void> upsertEntityCache(String entityType, String entityId, Map<String, dynamic> data, int version, String? updatedAtServer) async {
    if (kIsWeb) {
      return;
    }
    final db = await _db;
    await db.insert(
      'entity_cache',
      {
        'entity_type': entityType,
        'entity_id': entityId,
        'version': version,
        'data_json': jsonEncode(data),
        'sync_status': 'synced',
        'updated_at_server': updatedAtServer,
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<void> deleteEntityCache(String entityType, String entityId) async {
    if (kIsWeb) {
      return;
    }
    final db = await _db;
    await db.delete(
      'entity_cache',
      where: 'entity_type = ? AND entity_id = ?',
      whereArgs: [entityType, entityId],
    );
  }

  Future<Map<String, dynamic>?> getCursor(String streamName) async {
    if (kIsWeb) {
      return null;
    }
    final db = await _db;
    final rows = await db.query('sync_cursor', where: 'stream_name = ?', whereArgs: [streamName], limit: 1);
    return rows.isEmpty ? null : rows.first;
  }

  Future<void> upsertCursor({required String streamName, required String cursorToken, required int lastSeenVersion}) async {
    if (kIsWeb) {
      return;
    }
    final db = await _db;
    await db.insert(
      'sync_cursor',
      {
        'stream_name': streamName,
        'cursor_token': cursorToken,
        'last_sync_at': DateTime.now().toIso8601String(),
        'last_seen_version': lastSeenVersion,
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }
}
