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
    final res = await _api.dio.post('/queues/$queueId/join/', data: {'device_id': deviceId});
    final data = Map<String, dynamic>.from(res.data as Map);

    await _local.enqueue(
      entityType: 'queue_tickets',
      operation: 'join',
      entityId: data['ticket_id']?.toString(),
      payload: {'queue_id': queueId, 'device_id': deviceId},
    );

    return data;
  }
}
