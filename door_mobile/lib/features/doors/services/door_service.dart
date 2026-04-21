import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:cloud_functions/cloud_functions.dart';
import '../models/door_models.dart';

/// Wraps Firebase Cloud Functions callable endpoints for the doors feature.
class DoorFunctionsService {
  final FirebaseFunctions _functions;

  DoorFunctionsService({FirebaseFunctions? functions})
      : _functions = functions ?? FirebaseFunctions.instance;

  // ── Door Types ─────────────────────────────────────────────────────────────

  Future<List<DoorType>> getDoorTypes() async {
    final result =
        await _functions.httpsCallable('getDoorTypes').call<Map<String, dynamic>>();
    final list = (result.data['door_types'] as List<dynamic>?) ?? [];
    return list.map((e) {
      final map = Map<String, dynamic>.from(e as Map);
      final fields = (map['fields'] as List<dynamic>?)
              ?.map((f) => DoorTypeField.fromMap(
                    (f as Map)['id']?.toString() ?? '',
                    Map<String, dynamic>.from(f),
                  ))
              .toList() ??
          [];
      return DoorType.fromMap(map['id']?.toString() ?? '', map)
          .copyWith(fields: fields);
    }).toList();
  }

  // ── Doors ──────────────────────────────────────────────────────────────────

  Future<({String id, String qrToken})> createDoor({
    required String name,
    required String typeId,
    bool isPublic = false,
    Map<String, dynamic> settings = const {},
    Map<String, dynamic> fieldValues = const {},
  }) async {
    final result =
        await _functions.httpsCallable('createDoor').call<Map<String, dynamic>>({
      'name': name,
      'type_id': typeId,
      'is_public': isPublic,
      'settings': settings,
      'field_values': fieldValues,
    });
    return (
      id: result.data['id'] as String,
      qrToken: result.data['qr_token'] as String,
    );
  }

  Future<List<Door>> listMyDoors({DoorStatus? status}) async {
    final payload = <String, dynamic>{};
    if (status != null) payload['status'] = status.name;

    final result =
        await _functions.httpsCallable('listMyDoors').call<Map<String, dynamic>>(payload);
    final list = (result.data['doors'] as List<dynamic>?) ?? [];
    return list
        .map((e) => Door.fromMap(
              (e as Map)['id']?.toString() ?? '',
              Map<String, dynamic>.from(e),
            ))
        .toList();
  }

  Future<Door> getDoor(String doorId) async {
    final result = await _functions
        .httpsCallable('getDoor')
        .call<Map<String, dynamic>>({'door_id': doorId});
    return Door.fromMap(
        result.data['id']?.toString() ?? doorId,
        Map<String, dynamic>.from(result.data));
  }

  Future<void> updateDoor({
    required String doorId,
    String? name,
    DoorStatus? status,
    bool? isPublic,
    Map<String, dynamic>? settings,
    Map<String, dynamic>? fieldValues,
  }) async {
    final updates = <String, dynamic>{
      if (name != null) 'name': name,
      if (status != null) 'status': status.name,
      if (isPublic != null) 'is_public': isPublic,
      if (settings != null) 'settings': settings,
      if (fieldValues != null) 'field_values': fieldValues,
    };
    await _functions.httpsCallable('updateDoor').call({
      'door_id': doorId,
      'updates': updates,
    });
  }

  Future<void> deleteDoor(String doorId) async {
    await _functions
        .httpsCallable('deleteDoor')
        .call({'door_id': doorId});
  }

  Future<({String interactionId, String doorName})> scanDoor({
    required String qrToken,
    String? visitorName,
    String? visitorPhone,
    String? visitorMessage,
    Map<String, dynamic> fieldData = const {},
  }) async {
    final result =
        await _functions.httpsCallable('scanDoor').call<Map<String, dynamic>>({
      'qr_token': qrToken,
      if (visitorName != null) 'visitor_name': visitorName,
      if (visitorPhone != null) 'visitor_phone': visitorPhone,
      if (visitorMessage != null) 'visitor_message': visitorMessage,
      'field_data': fieldData,
    });
    return (
      interactionId: result.data['interaction_id'] as String,
      doorName: result.data['door_name'] as String,
    );
  }
}

/// Direct Firestore streams — for real-time door list on the home screen.
class DoorFirestoreService {
  final FirebaseFirestore _db;

  DoorFirestoreService({FirebaseFirestore? db})
      : _db = db ?? FirebaseFirestore.instance;

  /// Real-time stream of the current user's active doors.
  Stream<List<Door>> watchMyDoors(String uid) {
    return _db
        .collection('doors')
        .where('owner_id', isEqualTo: uid)
        .where('status', isEqualTo: 'active')
        .orderBy('created_at', descending: true)
        .snapshots()
        .map((snap) => snap.docs
            .map((d) => Door.fromMap(d.id, d.data()))
            .toList());
  }

  /// Real-time stream of interactions on a specific door.
  Stream<List<DoorInteraction>> watchDoorInteractions(String doorId) {
    return _db
        .collection('door_interactions')
        .where('door_id', isEqualTo: doorId)
        .orderBy('created_at', descending: true)
        .limit(50)
        .snapshots()
        .map((snap) => snap.docs
            .map((d) => DoorInteraction.fromMap(d.id, d.data()))
            .toList());
  }
}
