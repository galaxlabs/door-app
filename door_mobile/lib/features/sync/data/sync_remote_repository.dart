import '../../../core/api/api_client.dart';

class SyncRemoteRepository {
  final ApiClient apiClient;

  SyncRemoteRepository(this.apiClient);

  Future<Map<String, dynamic>> push({
    required String deviceId,
    required String streamName,
    required List<Map<String, dynamic>> operations,
  }) async {
    final res = await apiClient.dio.post('sync/upload/', data: {
      'device_id': deviceId,
      'stream_name': streamName,
      'operations': operations,
    });
    return Map<String, dynamic>.from(res.data as Map);
  }

  Future<Map<String, dynamic>> pull({
    required String deviceId,
    required String streamName,
    String since = '',
    required List<String> entityTypes,
  }) async {
    final res = await apiClient.dio.post('sync/pull/', data: {
      'device_id': deviceId,
      'stream_name': streamName,
      'since': since,
      'entity_types': entityTypes,
    });
    return Map<String, dynamic>.from(res.data as Map);
  }

  Future<void> ack({required String deviceId, required String cursor, List<String> ackedOutboxIds = const []}) async {
    await apiClient.dio.post('sync/ack/', data: {
      'device_id': deviceId,
      'cursor': cursor,
      'acked_outbox_ids': ackedOutboxIds,
    });
  }
}
