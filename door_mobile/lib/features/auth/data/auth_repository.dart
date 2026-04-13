import '../../../core/api/api_client.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AuthRepository {
  final ApiClient _client;

  AuthRepository(this._client);

  Future<void> requestOtp(String phone) async {
    await _client.dio.post('/auth/otp/request/', data: {'phone': phone});
  }

  Future<Map<String, dynamic>> verifyOtp(String phone, String code) async {
    final res = await _client.dio.post(
      '/auth/otp/verify/',
      data: {'phone': phone, 'code': code},
    );
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', res.data['access']);
    await prefs.setString('refresh_token', res.data['refresh']);
    return res.data as Map<String, dynamic>;
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }
}
