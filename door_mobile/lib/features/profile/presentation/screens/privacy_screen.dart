import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class PrivacyScreen extends StatefulWidget {
  const PrivacyScreen({super.key});

  @override
  State<PrivacyScreen> createState() => _PrivacyScreenState();
}

class _PrivacyScreenState extends State<PrivacyScreen> {
  bool _savePhoto = true;
  bool _shareAnalytics = false;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _savePhoto = prefs.getBool('privacy_save_photo') ?? true;
      _shareAnalytics = prefs.getBool('privacy_share_analytics') ?? false;
      _loading = false;
    });
  }

  Future<void> _setSavePhoto(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('privacy_save_photo', value);
    setState(() => _savePhoto = value);
  }

  Future<void> _setShareAnalytics(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('privacy_share_analytics', value);
    setState(() => _shareAnalytics = value);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Privacy')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Column(
              children: [
                if (_loading)
                  const Padding(
                    padding: EdgeInsets.all(18),
                    child: Center(child: CircularProgressIndicator()),
                  )
                else ...[
                  SwitchListTile.adaptive(
                    value: _savePhoto,
                    onChanged: _setSavePhoto,
                    title: const Text('Save photo'),
                    subtitle: const Text('Allow storing visitor card photo on this device'),
                  ),
                  const Divider(height: 1),
                  SwitchListTile.adaptive(
                    value: _shareAnalytics,
                    onChanged: _setShareAnalytics,
                    title: const Text('Share analytics'),
                    subtitle: const Text('Share anonymous usage analytics'),
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(height: 12),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Privacy policy', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800)),
                  const SizedBox(height: 10),
                  Text(
                    'We will write the full privacy policy in the next iteration.',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  const SizedBox(height: 12),
                  TextButton(
                    onPressed: () => ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Policy text will be added next.'), behavior: SnackBarBehavior.floating),
                    ),
                    child: const Text('View full Privacy Policy'),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

