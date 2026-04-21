import '../../../core/api/api_client.dart';

class OrganizationsRepository {
  final ApiClient _api;

  OrganizationsRepository(this._api);

  List<Map<String, dynamic>> _extractCollection(dynamic data) {
    if (data is List) {
      return data.map((item) => Map<String, dynamic>.from(item as Map)).toList();
    }
    if (data is Map<String, dynamic>) {
      final candidate = data['results'] ?? data['items'] ?? data['data'];
      if (candidate is List) {
        return candidate.map((item) => Map<String, dynamic>.from(item as Map)).toList();
      }
    }
    return const [];
  }

  Future<List<Map<String, dynamic>>> listOrganizations() async {
    final res = await _api.dio.get('organizations/');
    return _extractCollection(res.data);
  }
}

