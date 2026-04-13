import '../../../core/api/api_client.dart';

class NotificationsRepository {
  final ApiClient _api;

  NotificationsRepository(this._api);

  Future<List<Map<String, dynamic>>> list() async {
    final res = await _api.dio.get('/notifications/');
    final rows = List<dynamic>.from(res.data['results'] as List? ?? const []);
    return rows.map((e) => Map<String, dynamic>.from(e as Map)).toList();
  }

  Future<void> markRead(String id) async {
    await _api.dio.post('/notifications/$id/read/');
  }
}
