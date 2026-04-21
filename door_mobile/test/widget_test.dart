import 'package:flutter_test/flutter_test.dart';

import 'package:door_mobile/main.dart';

void main() {
  testWidgets('renders the login surface', (WidgetTester tester) async {
    await tester.pumpWidget(const DoorApp());
    await tester.pumpAndSettle();

    expect(find.text('Door App'), findsWidgets);
    expect(find.text('Sign in'), findsWidgets);
    expect(find.text('Create account'), findsOneWidget);
    expect(find.text('Skip for now'), findsOneWidget);
  });
}
