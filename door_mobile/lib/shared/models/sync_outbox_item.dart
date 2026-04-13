class SyncOutboxItem {
  final String localOpId;
  final String idempotencyKey;
  final String entityType;
  final String? entityId;
  final String operation;
  final String payloadJson;
  final int? baseVersion;
  final int sequence;
  final String status;
  final String createdAtClient;
  final String? updatedAtClient;

  const SyncOutboxItem({
    required this.localOpId,
    required this.idempotencyKey,
    required this.entityType,
    required this.entityId,
    required this.operation,
    required this.payloadJson,
    required this.baseVersion,
    required this.sequence,
    required this.status,
    required this.createdAtClient,
    required this.updatedAtClient,
  });

  factory SyncOutboxItem.fromMap(Map<String, dynamic> row) {
    return SyncOutboxItem(
      localOpId: row['local_op_id'] as String,
      idempotencyKey: row['idempotency_key'] as String,
      entityType: row['entity_type'] as String,
      entityId: row['entity_id'] as String?,
      operation: row['operation'] as String,
      payloadJson: row['payload_json'] as String,
      baseVersion: row['base_version'] as int?,
      sequence: row['sequence'] as int,
      status: row['status'] as String,
      createdAtClient: row['created_at_client'] as String,
      updatedAtClient: row['updated_at_client'] as String?,
    );
  }
}
