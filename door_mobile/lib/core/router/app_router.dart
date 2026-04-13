import 'package:go_router/go_router.dart';

import '../../features/auth/presentation/screens/login_screen.dart';
import '../../features/auth/presentation/screens/otp_screen.dart';
import '../../features/home/presentation/screens/home_screen.dart';
import '../../features/qr/presentation/screens/qr_scanner_screen.dart';
import '../../features/queue/presentation/screens/queue_screen.dart';
import '../../features/chat/presentation/screens/chat_room_screen.dart';
import '../../features/broadcast/presentation/screens/broadcast_screen.dart';
import '../../features/phase2/presentation/screens/attendance_screen.dart';
import '../../features/phase2/presentation/screens/family_coordination_screen.dart';
import '../../features/phase2/presentation/screens/safety_hajj_screen.dart';
import '../../features/sync/presentation/screens/sync_center_screen.dart';

class AppRouter {
  static final router = GoRouter(
    initialLocation: '/login',
    routes: [
      GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
      GoRoute(path: '/otp', builder: (ctx, state) => OtpScreen(phone: state.extra as String)),
      GoRoute(path: '/home', builder: (_, __) => const HomeScreen()),
      GoRoute(path: '/scan', builder: (_, __) => const QRScannerScreen()),
      GoRoute(
        path: '/queue/:id',
        builder: (ctx, state) => QueueScreen(queueId: state.pathParameters['id']!),
      ),
      GoRoute(
        path: '/chat/:roomId',
        builder: (ctx, state) => ChatRoomScreen(roomId: state.pathParameters['roomId']!),
      ),
      GoRoute(
        path: '/broadcast/:channelId',
        builder: (ctx, state) => BroadcastScreen(channelId: state.pathParameters['channelId']!),
      ),
      GoRoute(path: '/attendance', builder: (_, __) => const AttendanceScreen()),
      GoRoute(path: '/family', builder: (_, __) => const FamilyCoordinationScreen()),
      GoRoute(path: '/safety-hajj', builder: (_, __) => const SafetyHajjScreen()),
      GoRoute(path: '/sync-center', builder: (_, __) => const SyncCenterScreen()),
    ],
  );
}
