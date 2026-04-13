class AppEnv {
  static const String apiBaseUrl = String.fromEnvironment(
    'API_URL',
    defaultValue: 'http://localhost:8010/api/v1',
  );

  static const String wsBaseUrl = String.fromEnvironment(
    'WS_URL',
    defaultValue: 'ws://localhost:8010',
  );

  static const int syncBatchSize = int.fromEnvironment('SYNC_BATCH_SIZE', defaultValue: 100);
}
