import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../../core/config/app_env.dart';
import '../../data/queue_repository.dart';

class QueueScreen extends StatefulWidget {
  final String queueId;
  const QueueScreen({super.key, required this.queueId});

  @override
  State<QueueScreen> createState() => _QueueScreenState();
}

class _QueueScreenState extends State<QueueScreen> {
  WebSocketChannel? _channel;
  Map<String, dynamic>? _queueState;
  int? _myTicketNumber;
  String? _queueStatus;

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
      Uri.parse('$wsBase/ws/queues/${widget.queueId}/?token=$token'),
    );
    _channel!.stream.listen((msg) {
      final data = jsonDecode(msg as String) as Map<String, dynamic>;
      final event = (data['event'] ?? data['type'])?.toString();
      final payload = Map<String, dynamic>.from((data['data'] as Map?) ?? const {});
      if (event == 'queue.state') {
        final queue = Map<String, dynamic>.from((payload['queue'] as Map?) ?? const {});
        setState(() {
          _queueState = {
            ...queue,
            'waiting_count': payload['waiting_count'],
            'current_serving': payload['current_serving'],
          };
          _queueStatus = queue['status']?.toString();
        });
      } else if (event == 'ticket.called') {
        final ticketData = payload;
        if (ticketData['number'] == _myTicketNumber) {
          _showCalled(ticketData);
        }
      } else if (event == 'ticket.issued') {
        setState(() => _myTicketNumber = (payload['number'] as num?)?.toInt());
      } else if (event == 'queue.status') {
        setState(() => _queueStatus = payload['status']?.toString());
      }
    });
  }

  Future<void> _joinQueue() async {
    try {
      final data = await context.read<QueueRepository>().joinQueue(
            queueId: widget.queueId,
            deviceId: 'flutter_device',
          );
      final ticketNumber = (data['ticket_number'] as num?)?.toInt();
      if (ticketNumber != null && mounted) {
        setState(() => _myTicketNumber = ticketNumber);
      }
    } catch (_) {
      _channel?.sink.add(jsonEncode({'type': 'queue.join', 'device_id': 'flutter_device'}));
    }
  }

  void _showCalled(Map data) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Your Turn!'),
        content: Text('Ticket #${data['number']} — Desk ${data['desk_number'] ?? '-'}'),
        actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('OK'))],
      ),
    );
  }

  @override
  void dispose() {
    _channel?.sink.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = _queueState;
    final statusText = (_queueStatus ?? state?['status'] ?? 'connecting').toString().toUpperCase();
    return Scaffold(
      appBar: AppBar(title: Text(state?['name'] ?? 'Queue')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(22),
                child: Column(
                  children: [
                    Text(
                      state != null ? 'Now Serving: #${state['current_serving']}' : 'Queue connection in progress',
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 30, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 10),
                    Text(
                      state != null
                          ? 'Waiting: ${state['waiting_count']}'
                          : 'No live queue snapshot yet. You can still try joining or wait for the first websocket update.',
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 12),
                    Chip(label: Text(statusText)),
                  ],
                ),
              ),
            ),
            if (state == null) ...[
              const SizedBox(height: 16),
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('What this screen should show', style: TextStyle(fontWeight: FontWeight.w700)),
                      SizedBox(height: 8),
                      Text('Current serving token, waiting count, join action, and live queue status updates.'),
                    ],
                  ),
                ),
              ),
            ],
            const Spacer(),
            if (_myTicketNumber != null)
              Text('Your ticket: #$_myTicketNumber',
                  style: const TextStyle(fontSize: 22, color: Color(0xFFF6B94A))),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _myTicketNumber == null ? _joinQueue : null,
                icon: const Icon(Icons.confirmation_number),
                label: Text(_myTicketNumber == null ? 'Join Queue' : 'In Queue'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
