import '../models/door_models.dart';
import '../services/door_service.dart';

/// Single entry point for the doors feature.
/// Composes Cloud Functions calls + Firestore real-time streams.
class DoorRepository {
  final DoorFunctionsService _fn;
  final DoorFirestoreService _fs;

  DoorRepository({
    DoorFunctionsService? functions,
    DoorFirestoreService? firestore,
  })  : _fn = functions ?? DoorFunctionsService(),
        _fs = firestore ?? DoorFirestoreService();

  // ── Door Types ─────────────────────────────────────────────────────────────

  Future<List<DoorType>> getDoorTypes() => _fn.getDoorTypes();

  // ── Doors ──────────────────────────────────────────────────────────────────

  Future<({String id, String qrToken})> createDoor({
    required String name,
    required String typeId,
    bool isPublic = false,
    Map<String, dynamic> settings = const {},
    Map<String, dynamic> fieldValues = const {},
  }) =>
      _fn.createDoor(
        name: name,
        typeId: typeId,
        isPublic: isPublic,
        settings: settings,
        fieldValues: fieldValues,
      );

  Future<List<Door>> listMyDoors({DoorStatus? status}) =>
      _fn.listMyDoors(status: status);

  Future<Door> getDoor(String doorId) => _fn.getDoor(doorId);

  Future<void> updateDoor({
    required String doorId,
    String? name,
    DoorStatus? status,
    bool? isPublic,
    Map<String, dynamic>? settings,
    Map<String, dynamic>? fieldValues,
  }) =>
      _fn.updateDoor(
        doorId: doorId,
        name: name,
        status: status,
        isPublic: isPublic,
        settings: settings,
        fieldValues: fieldValues,
      );

  Future<void> deleteDoor(String doorId) => _fn.deleteDoor(doorId);

  Future<({String interactionId, String doorName})> scanDoor({
    required String qrToken,
    String? visitorName,
    String? visitorPhone,
    String? visitorMessage,
    Map<String, dynamic> fieldData = const {},
  }) =>
      _fn.scanDoor(
        qrToken: qrToken,
        visitorName: visitorName,
        visitorPhone: visitorPhone,
        visitorMessage: visitorMessage,
        fieldData: fieldData,
      );

  // ── Real-time streams ──────────────────────────────────────────────────────

  Stream<List<Door>> watchMyDoors(String uid) => _fs.watchMyDoors(uid);

  Stream<List<DoorInteraction>> watchDoorInteractions(String doorId) =>
      _fs.watchDoorInteractions(doorId);
}
