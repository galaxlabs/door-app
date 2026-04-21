import '../../../core/api/api_client.dart';
import '../../sync/data/sync_local_repository.dart';

class BroadcastRepository {
  final ApiClient _api;
  final SyncLocalRepository _local;

  BroadcastRepository(this._api, this._local);

  Future<void> ackDelivery({
    required String deliveryId,
    required String channelId,
  }) async {
    await _local.enqueue(
      entityType: 'broadcast_deliveries',
      operation: 'ack',
      entityId: deliveryId,
      payload: {
        'delivery_id': deliveryId,
        'channel_id': channelId,
      },
    );

    await _api.dio.post('broadcast/deliveries/$deliveryId/ack/');
  }
}
