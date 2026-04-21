import '../../../core/api/api_client.dart';
import '../../sync/data/sync_local_repository.dart';

class QrRepository {
  final ApiClient _api;
  final SyncLocalRepository _local;

  QrRepository(this._api, this._local);

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

  Future<List<Map<String, dynamic>>> listCodes() async {
    final res = await _api.dio.get('qr/codes/');
    return _extractCollection(res.data);
  }

  Future<Map<String, dynamic>> getCode(String codeId) async {
    final res = await _api.dio.get('qr/codes/$codeId/');
    return Map<String, dynamic>.from(res.data as Map);
  }

  Future<Map<String, dynamic>> updateCode(
    String codeId, {
    String? name,
    String? purpose,
    String? mode,
    bool? isActive,
  }) async {
    final payload = <String, dynamic>{};
    if (name != null) payload['name'] = name;
    if (purpose != null) payload['purpose'] = purpose;
    if (mode != null) payload['mode'] = mode;
    if (isActive != null) {
      payload['is_active'] = isActive;
      payload['status'] = isActive ? 'active' : 'inactive';
    }
    final res = await _api.dio.patch('qr/codes/$codeId/', data: payload);
    return Map<String, dynamic>.from(res.data as Map);
  }

  Future<Map<String, dynamic>> createDoor({
    required String name,
    required String entityType,
    required String mode,
    String purpose = '',
    String? organizationId,
    String? queueId,
    bool isActive = true,
  }) async {
    final payload = {
      'name': name,
      'purpose': purpose,
      'entity_type': entityType,
      'mode': mode,
      'organization': organizationId,
      'queue': queueId,
      'payload_type': mode,
      'payload_data': {
        'entity_type': entityType,
        'mode': mode,
        'organization_id': organizationId,
        'queue_id': queueId,
      },
      'action_payload': {
        'entity_type': entityType,
        'mode': mode,
        'organization_id': organizationId,
        'queue_id': queueId,
      },
      'is_active': isActive,
      'status': isActive ? 'active' : 'inactive',
    };
    final res = await _api.dio.post('qr/codes/', data: payload);
    return Map<String, dynamic>.from(res.data as Map);
  }

  Future<List<Map<String, dynamic>>> listTemplatePacks() async {
    final res = await _api.dio.get('qr/template-packs/');
    final data = res.data;
    if (data is Map<String, dynamic>) {
      final packs = data['packs'];
      if (packs is List) {
        return packs.map((e) => Map<String, dynamic>.from(e as Map)).toList();
      }
    }
    return const [];
  }

  Future<Map<String, dynamic>> createDoorFromTemplatePack({
    required String packKey,
    required String name,
    String? organizationId,
    String? queueId,
  }) async {
    final payload = <String, dynamic>{
      'pack_key': packKey,
      'name': name,
    };
    if (organizationId != null && organizationId.trim().isNotEmpty) {
      payload['organization'] = organizationId.trim();
    }
    if (queueId != null && queueId.trim().isNotEmpty) {
      payload['queue'] = queueId.trim();
    }

    final res = await _api.dio.post('qr/template-packs/admin-setup/', data: payload);
    if (res.data is Map<String, dynamic>) {
      final root = Map<String, dynamic>.from(res.data as Map);
      final qr = root['qr_code'];
      if (qr is Map) {
        return Map<String, dynamic>.from(qr);
      }
      return root;
    }
    return const {};
  }

  Future<Map<String, dynamic>> scan(String qrCodeId, {required String deviceId}) async {
    final res = await _api.dio.post('qr/scan/', data: {'qr_code_id': qrCodeId, 'device_id': deviceId});
    final data = Map<String, dynamic>.from(res.data as Map);

    await _local.enqueue(
      entityType: 'qr_scans',
      operation: 'scan',
      entityId: data['scan_id']?.toString(),
      payload: {
        'qr_code_id': qrCodeId,
        'device_id': deviceId,
      },
    );

    return data;
  }
}
