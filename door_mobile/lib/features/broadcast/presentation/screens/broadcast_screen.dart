import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../../core/config/app_env.dart';
import '../../data/broadcast_repository.dart';

class BroadcastScreen extends StatefulWidget {
  final String channelId;
  const BroadcastScreen({super.key, required this.channelId});

  @override
  State<BroadcastScreen> createState() => _BroadcastScreenState();
}

class _BroadcastScreenState extends State<BroadcastScreen> {
  WebSocketChannel? _channel;
  final _messages = <Map<String, dynamic>>[];

  @override
  void initState() {
    super.initState();
    _connect();
  }

  Future<void> _connect() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('access_token');
    const wsBase = AppEnv.wsBaseUrl;
    _channel = WebSocketChannel.connect(
      Uri.parse('$wsBase/ws/broadcast/${widget.channelId}/?token=$token'),
    );
    _channel!.stream.listen((raw) {
      final data = jsonDecode(raw as String) as Map<String, dynamic>;
      final event = (data['event'] ?? data['type'])?.toString();
      if (event == 'broadcast.message') {
        final payload = Map<String, dynamic>.from((data['data'] as Map?) ?? const {});
        setState(() => _messages.insert(0, payload));

        final deliveryId = payload['delivery_id']?.toString();
        if (!mounted) return;
        if (deliveryId != null && deliveryId.isNotEmpty) {
          context.read<BroadcastRepository>().ackDelivery(
                deliveryId: deliveryId,
                channelId: widget.channelId,
              );
        }
      }
    });
  }

  @override
  void dispose() {
    _channel?.sink.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Broadcasts')),
      body: ListView.builder(
        itemCount: _messages.length,
        itemBuilder: (ctx, i) {
          final msg = _messages[i];
          return ListTile(
            leading: const Icon(Icons.campaign),
            title: Text(msg['title'] ?? ''),
            subtitle: Text(msg['body'] ?? ''),
          );
        },
      ),
    );
  }
}
