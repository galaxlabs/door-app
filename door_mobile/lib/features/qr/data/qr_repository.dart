import '../../../core/api/api_client.dart';
import '../../sync/data/sync_local_repository.dart';

class QrRepository {
  final ApiClient _api;
  final SyncLocalRepository _local;

  QrRepository(this._api, this._local);

  Future<Map<String, dynamic>> scan(String qrCodeId, {required String deviceId}) async {
    final res = await _api.dio.post('/qr/scan/', data: {'qr_code_id': qrCodeId, 'device_id': deviceId});
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
