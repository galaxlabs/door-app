import 'package:go_router/go_router.dart';

import '../../features/auth/presentation/screens/login_screen.dart';
import '../../features/auth/presentation/screens/register_screen.dart';
import '../../features/home/presentation/screens/home_screen.dart';
import '../../features/qr/presentation/screens/qr_scanner_screen.dart';
import '../../features/queue/presentation/screens/queue_screen.dart';
import '../../features/chat/presentation/screens/chat_room_screen.dart';
import '../../features/broadcast/presentation/screens/broadcast_screen.dart';
import '../../features/phase2/presentation/screens/attendance_screen.dart';
import '../../features/phase2/presentation/screens/family_coordination_screen.dart';
import '../../features/phase2/presentation/screens/safety_hajj_screen.dart';
import '../../features/sync/presentation/screens/sync_center_screen.dart';
import '../../features/profile/presentation/screens/account_screen.dart';
import '../../features/profile/presentation/screens/activity_history_screen.dart';
import '../../features/profile/presentation/screens/language_screen.dart';
import '../../features/profile/presentation/screens/meeting_points_screen.dart';
import '../../features/profile/presentation/screens/privacy_screen.dart';
import '../../features/profile/presentation/screens/quick_guide_screen.dart';
import '../../features/profile/presentation/screens/theme_screen.dart';
import '../../features/doors/presentation/screens/create_door_screen.dart';
import '../../features/doors/presentation/screens/door_details_screen.dart';
import '../../features/doors/presentation/screens/door_type_picker_screen.dart';
import '../../features/doors/presentation/screens/doors_list_screen.dart';
import '../../features/doors/models/door_models.dart';

class AppRouter {
  static final router = GoRouter(
    initialLocation: '/login',
    errorBuilder: (_, __) => const HomeScreen(),
    routes: [
      GoRoute(path: '/', redirect: (_, __) => '/home'),
      GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
      GoRoute(path: '/register', builder: (_, __) => const RegisterScreen()),
      GoRoute(path: '/home', builder: (_, __) => const HomeScreen()),
      GoRoute(path: '/scan', builder: (_, __) => const QRScannerScreen()),
      GoRoute(path: '/account', builder: (_, __) => const AccountScreen()),
      GoRoute(path: '/activity', builder: (_, __) => const ActivityHistoryScreen()),
      GoRoute(path: '/meeting-points', builder: (_, __) => const MeetingPointsScreen()),
      GoRoute(path: '/privacy', builder: (_, __) => const PrivacyScreen()),
      GoRoute(path: '/language', builder: (_, __) => const LanguageScreen()),
      GoRoute(path: '/theme', builder: (_, __) => const ThemeScreen()),
      GoRoute(path: '/quick-guide', builder: (_, __) => const QuickGuideScreen()),
      GoRoute(path: '/doors/pick-type', builder: (_, __) => const DoorTypePickerScreen()),
      GoRoute(
        path: '/doors/create',
        builder: (ctx, state) => CreateDoorScreen(doorType: state.extra as DoorType?),
      ),
      GoRoute(
        path: '/doors/:id',
        builder: (ctx, state) => DoorDetailsScreen(doorId: state.pathParameters['id']!),
      ),
      GoRoute(path: '/doors-list', builder: (_, __) => const DoorsListScreen()),
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
