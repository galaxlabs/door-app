import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:go_router/go_router.dart';

import '../../data/qr_repository.dart';

class QRScannerScreen extends StatefulWidget {
  const QRScannerScreen({super.key});

  @override
  State<QRScannerScreen> createState() => _QRScannerScreenState();
}

class _QRScannerScreenState extends State<QRScannerScreen> {
  bool _processing = false;

  Future<void> _onDetect(BarcodeCapture capture) async {
    if (_processing) return;
    final barcodes = capture.barcodes;
    if (barcodes.isEmpty) return;
    final raw = barcodes.first.rawValue;
    if (raw == null) return;

    setState(() => _processing = true);
    try {
      final repo = context.read<QrRepository>();
      final data = await repo.scan(raw, deviceId: 'flutter_device');

      final payloadType = data['payload_type'];
      final payloadData = data['payload_data'] as Map<String, dynamic>;

      if (!mounted) return;

      if (payloadType == 'queue_join') {
        context.push('/queue/${payloadData['queue_id']}');
      } else if (payloadType == 'channel_subscribe') {
        context.push('/broadcast/${payloadData['channel_id']}');
      } else {
        _showResult(data);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Scan failed: $e')));
      }
    } finally {
      if (mounted) setState(() => _processing = false);
    }
  }

  void _showResult(Map data) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: Text(data['qr_label'] ?? 'Scanned'),
        content: Text(jsonEncode(data['payload_data'])),
        actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('OK'))],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Scan QR')),
      body: MobileScanner(onDetect: _onDetect),
    );
  }
}
