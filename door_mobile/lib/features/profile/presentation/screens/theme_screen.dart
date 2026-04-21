import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ThemeScreen extends StatefulWidget {
  const ThemeScreen({super.key});

  @override
  State<ThemeScreen> createState() => _ThemeScreenState();
}

class _ThemeScreenState extends State<ThemeScreen> {
  String _current = 'midnight';

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() => _current = prefs.getString('app_theme_mode') ?? 'midnight');
  }

  Future<void> _setTheme(String value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('app_theme_mode', value);
    setState(() => _current = value);
  }

  @override
  Widget build(BuildContext context) {
    const options = [
      ('midnight', 'Midnight amber', 'Default dark theme'),
      ('system', 'System', 'Follow device theme'),
      ('dark', 'Dark', 'Pure dark'),
    ];

    return Scaffold(
      appBar: AppBar(title: const Text('Theme')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Column(
              children: [
                for (final opt in options) ...[
                  ListTile(
                    title: Text(opt.$2, style: const TextStyle(fontWeight: FontWeight.w800)),
                    subtitle: Text(opt.$3),
                    trailing: _current == opt.$1 ? const Icon(Icons.check_circle_rounded, color: Color(0xFF37D6C5)) : null,
                    onTap: () => _setTheme(opt.$1),
                  ),
                  if (opt.$1 != options.last.$1) const Divider(height: 1),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}
