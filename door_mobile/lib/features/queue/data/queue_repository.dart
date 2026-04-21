import '../../../core/api/api_client.dart';
import '../../sync/data/sync_local_repository.dart';

class QueueRepository {
  final ApiClient _api;
  final SyncLocalRepository _local;

  QueueRepository(this._api, this._local);

  Future<Map<String, dynamic>> joinQueue({
    required String queueId,
    required String deviceId,
  }) async {
    final res = await _api.dio.post('queues/$queueId/join/', data: {'device_id': deviceId});
    final data = Map<String, dynamic>.from(res.data as Map);

    await _local.enqueue(
      entityType: 'queue_tickets',
      operation: 'join',
      entityId: data['ticket_id']?.toString(),
      payload: {'queue_id': queueId, 'device_id': deviceId},
    );

    return data;
  }

  Future<List<Map<String, dynamic>>> listQueues() async {
    final res = await _api.dio.get('queues/');
    if (res.data is List) {
      return (res.data as List).map((e) => Map<String, dynamic>.from(e as Map)).toList();
    }
    if (res.data is Map<String, dynamic>) {
      final root = Map<String, dynamic>.from(res.data as Map);
      final candidate = root['results'] ?? root['items'] ?? root['data'];
      if (candidate is List) {
        return candidate.map((e) => Map<String, dynamic>.from(e as Map)).toList();
      }
    }
    return const [];
  }
}
