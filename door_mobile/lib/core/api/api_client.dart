import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../config/app_env.dart';

class ApiClient {
  late final Dio _dio;
  static const String _baseUrl = AppEnv.apiBaseUrl;

  ApiClient() {
    _dio = Dio(BaseOptions(baseUrl: _baseUrl, connectTimeout: const Duration(seconds: 10)));
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: _onRequest,
      onError: _onError,
    ));
  }

  Dio get dio => _dio;

  Future<void> _onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('access_token');
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  Future<void> _onError(DioException error, ErrorInterceptorHandler handler) async {
    if (error.response?.statusCode == 401) {
      final prefs = await SharedPreferences.getInstance();
      final refresh = prefs.getString('refresh_token');
      if (refresh != null) {
        try {
          final res = await Dio().post('$_baseUrl/auth/token/refresh/', data: {'refresh': refresh});
          final newAccess = res.data['access'] as String;
          await prefs.setString('access_token', newAccess);
          error.requestOptions.headers['Authorization'] = 'Bearer $newAccess';
          final clone = await _dio.fetch(error.requestOptions);
          return handler.resolve(clone);
        } catch (_) {
          await prefs.clear();
        }
      }
    }
    handler.next(error);
  }
}
