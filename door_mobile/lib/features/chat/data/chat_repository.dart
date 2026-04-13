import '../../../core/api/api_client.dart';
import '../../sync/data/sync_local_repository.dart';

class ChatRepository {
  final ApiClient _api;
  final SyncLocalRepository _local;

  ChatRepository(this._api, this._local);

  Future<void> sendMessage({
    required String roomId,
    required String content,
    required String clientId,
  }) async {
    await _local.enqueue(
      entityType: 'chat_messages',
      operation: 'send',
      entityId: roomId,
      payload: {
        'room_id': roomId,
        'content': content,
        'client_id': clientId,
      },
    );

    await _api.dio.post('/chat/rooms/$roomId/messages/', data: {
      'content': content,
      'message_type': 'text',
      'client_id': clientId,
    });
  }
}
