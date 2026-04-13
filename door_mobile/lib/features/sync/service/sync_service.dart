import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

/// Local SQLite-based offline sync engine.
/// Mirrors SyncQueue table from server.
class SyncService {
  static Database? _db;

  static Future<void> init() async {
    _db = await openDatabase(
      join(await getDatabasesPath(), 'door_offline.db'),
      version: 1,
      onCreate: _onCreate,
    );
  }

  static Future<void> _onCreate(Database db, int version) async {
    await db.execute('''
      CREATE TABLE sync_queue (
        id TEXT PRIMARY KEY,
        operation TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        entity_id TEXT,
        client_id TEXT,
        payload TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        sequence INTEGER NOT NULL,
        created_at TEXT NOT NULL
      )
    ''');

    await db.execute('''
      CREATE TABLE cached_entities (
        entity_type TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        data TEXT NOT NULL,
        synced_at TEXT,
        PRIMARY KEY (entity_type, entity_id)
      )
    ''');
  }

  Database get db => _db!;

  /// Queue an operation for later sync
  Future<void> enqueue({
    required String operation,
    required String entityType,
    String? entityId,
    String? clientId,
    required Map<String, dynamic> payload,
    required int sequence,
  }) async {
    final id = DateTime.now().millisecondsSinceEpoch.toString();
    await _db!.insert('sync_queue', {
      'id': id,
      'operation': operation,
      'entity_type': entityType,
      'entity_id': entityId ?? '',
      'client_id': clientId ?? '',
      'payload': payload.toString(),
      'status': 'pending',
      'sequence': sequence,
      'created_at': DateTime.now().toIso8601String(),
    });
  }

  /// Get all pending operations
  Future<List<Map<String, dynamic>>> getPending() async {
    return _db!.query(
      'sync_queue',
      where: 'status = ?',
      whereArgs: ['pending'],
      orderBy: 'sequence ASC',
    );
  }

  /// Mark operation as synced
  Future<void> markSynced(String id) async {
    await _db!.update(
      'sync_queue',
      {'status': 'synced'},
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  /// Cache entity locally
  Future<void> cacheEntity(String entityType, String entityId, String jsonData) async {
    await _db!.insert(
      'cached_entities',
      {
        'entity_type': entityType,
        'entity_id': entityId,
        'data': jsonData,
        'synced_at': DateTime.now().toIso8601String(),
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  /// Retrieve cached entity
  Future<String?> getCached(String entityType, String entityId) async {
    final rows = await _db!.query(
      'cached_entities',
      where: 'entity_type = ? AND entity_id = ?',
      whereArgs: [entityType, entityId],
      limit: 1,
    );
    return rows.isNotEmpty ? rows.first['data'] as String : null;
  }
}
