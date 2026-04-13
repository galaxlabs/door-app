import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../../core/config/app_env.dart';
import '../../data/chat_repository.dart';

class ChatRoomScreen extends StatefulWidget {
  final String roomId;
  const ChatRoomScreen({super.key, required this.roomId});

  @override
  State<ChatRoomScreen> createState() => _ChatRoomScreenState();
}

class _ChatRoomScreenState extends State<ChatRoomScreen> {
  WebSocketChannel? _channel;
  final _messages = <Map<String, dynamic>>[];
  final _ctrl = TextEditingController();
  int _seq = 0;

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
      Uri.parse('$wsBase/ws/chat/${widget.roomId}/?token=$token'),
    );
    _channel!.stream.listen((raw) {
      final data = jsonDecode(raw as String) as Map<String, dynamic>;
      final event = (data['event'] ?? data['type'])?.toString();
      if (event == 'message.new' || event == 'chat.message') {
        final payload = Map<String, dynamic>.from((data['data'] as Map?) ?? const {});
        setState(() => _messages.add(payload));
      }
    });
  }

  Future<void> _sendMessage() async {
    final text = _ctrl.text.trim();
    if (text.isEmpty) return;
    _seq++;
    final clientId = '${DateTime.now().millisecondsSinceEpoch}_$_seq';
    _channel?.sink.add(jsonEncode({
      'type': 'message.send',
      'msg_type': 'text',
      'content': text,
      'client_id': clientId,
    }));
    await context.read<ChatRepository>().sendMessage(
          roomId: widget.roomId,
          content: text,
          clientId: clientId,
        );
    _ctrl.clear();
  }

  @override
  void dispose() {
    _channel?.sink.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Chat')),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(12),
              itemCount: _messages.length,
              itemBuilder: (ctx, i) {
                final msg = _messages[i];
                return Align(
                  alignment: Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 4),
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: Colors.indigo[50],
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(msg['sender_name'] ?? '', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                        Text(msg['content'] ?? ''),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
          Padding(
            padding: EdgeInsets.only(
              bottom: MediaQuery.of(context).viewInsets.bottom + 8,
              left: 12, right: 12, top: 4,
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _ctrl,
                    decoration: const InputDecoration(
                      hintText: 'Type a message…',
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filled(onPressed: _sendMessage, icon: const Icon(Icons.send)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
