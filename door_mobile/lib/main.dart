import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart';

import 'firebase_options.dart';
import 'core/router/app_router.dart';
import 'core/theme/app_theme.dart';
import 'core/api/api_client.dart';
import 'core/db/local_database.dart';
import 'features/auth/data/auth_repository.dart';
import 'features/broadcast/data/broadcast_repository.dart';
import 'features/chat/data/chat_repository.dart';
import 'features/notifications/data/notifications_repository.dart';
import 'features/organizations/data/organizations_repository.dart';
import 'features/qr/data/qr_repository.dart';
import 'features/queue/data/queue_repository.dart';
import 'features/sync/data/sync_local_repository.dart';
import 'features/sync/data/sync_remote_repository.dart';
import 'features/sync/service/sync_manager.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  // On web: handle Google redirect sign-in result after page reload
  if (kIsWeb) {
    try {
      await FirebaseAuth.instance.getRedirectResult();
    } catch (_) {}
  }
  if (!kIsWeb) {
    await LocalDatabase.instance();
  }
  runApp(const DoorApp());
}

class DoorApp extends StatelessWidget {
  const DoorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiRepositoryProvider(
      providers: [
        RepositoryProvider(create: (_) => ApiClient()),
        RepositoryProvider(create: (_) => AuthRepository()),
        RepositoryProvider(create: (_) => SyncLocalRepository()),
        RepositoryProvider(create: (ctx) => SyncRemoteRepository(ctx.read<ApiClient>())),
        RepositoryProvider(
          create: (ctx) => SyncManager(
            local: ctx.read<SyncLocalRepository>(),
            remote: ctx.read<SyncRemoteRepository>(),
          ),
        ),
        RepositoryProvider(create: (ctx) => QrRepository(ctx.read<ApiClient>(), ctx.read<SyncLocalRepository>())),
        RepositoryProvider(create: (ctx) => QueueRepository(ctx.read<ApiClient>(), ctx.read<SyncLocalRepository>())),
        RepositoryProvider(create: (ctx) => ChatRepository(ctx.read<ApiClient>(), ctx.read<SyncLocalRepository>())),
        RepositoryProvider(create: (ctx) => BroadcastRepository(ctx.read<ApiClient>(), ctx.read<SyncLocalRepository>())),
        RepositoryProvider(create: (ctx) => NotificationsRepository(ctx.read<ApiClient>())),
        RepositoryProvider(create: (ctx) => OrganizationsRepository(ctx.read<ApiClient>())),
      ],
      child: MaterialApp.router(
        title: 'Door App',
        theme: AppTheme.light,
        darkTheme: AppTheme.dark,
        routerConfig: AppRouter.router,
        localizationsDelegates: const [
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: const [
          Locale('en'),
          Locale('ar'),
          Locale('ur'),
        ],
      ),
    );
  }
}
