import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';

class LocalDatabase {
  static const _dbName = 'door_phase1.db';
  static const _dbVersion = 2;

  static Database? _instance;

  static Future<Database> instance() async {
    if (_instance != null) return _instance!;
    _instance = await _open();
    return _instance!;
  }

  static Future<Database> _open() async {
    final path = join(await getDatabasesPath(), _dbName);
    return openDatabase(
      path,
      version: _dbVersion,
      onCreate: _onCreate,
      onUpgrade: _onUpgrade,
    );
  }

  static Future<void> _onCreate(Database db, int version) async {
    await db.execute('''
      CREATE TABLE sync_outbox (
        local_op_id TEXT PRIMARY KEY,
        idempotency_key TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        entity_id TEXT,
        operation TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        base_version INTEGER,
        sequence INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        error_code TEXT,
        error_message TEXT,
        created_at_client TEXT NOT NULL,
        updated_at_client TEXT,
        created_by_device_id TEXT,
        retry_count INTEGER NOT NULL DEFAULT 0,
        next_retry_at TEXT
      )
    ''');

    await db.execute('CREATE UNIQUE INDEX idx_sync_outbox_device_idem ON sync_outbox(idempotency_key)');
    await db.execute('CREATE INDEX idx_sync_outbox_status_seq ON sync_outbox(status, sequence)');

    await db.execute('''
      CREATE TABLE sync_cursor (
        stream_name TEXT PRIMARY KEY,
        cursor_token TEXT,
        last_sync_at TEXT,
        last_seen_version INTEGER NOT NULL DEFAULT 0
      )
    ''');

    await db.execute('''
      CREATE TABLE entity_cache (
        entity_type TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        version INTEGER NOT NULL DEFAULT 1,
        data_json TEXT NOT NULL,
        sync_status TEXT NOT NULL DEFAULT 'synced',
        updated_at_server TEXT,
        PRIMARY KEY (entity_type, entity_id)
      )
    ''');
    await db.execute('CREATE INDEX idx_entity_cache_type_ver ON entity_cache(entity_type, version)');

    await db.execute('''
      CREATE TABLE pending_ack (
        ack_id TEXT PRIMARY KEY,
        delivery_id TEXT,
        ws_channel TEXT,
        payload_json TEXT NOT NULL,
        created_at_client TEXT NOT NULL,
        sent INTEGER NOT NULL DEFAULT 0
      )
    ''');
    await db.execute('CREATE INDEX idx_pending_ack_sent ON pending_ack(sent, created_at_client)');
  }

  static Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    if (oldVersion < 2) {
      await db.execute('''
        CREATE TABLE IF NOT EXISTS pending_ack (
          ack_id TEXT PRIMARY KEY,
          delivery_id TEXT,
          ws_channel TEXT,
          payload_json TEXT NOT NULL,
          created_at_client TEXT NOT NULL,
          sent INTEGER NOT NULL DEFAULT 0
        )
      ''');
      await db.execute('CREATE INDEX IF NOT EXISTS idx_pending_ack_sent ON pending_ack(sent, created_at_client)');
    }
  }
}
