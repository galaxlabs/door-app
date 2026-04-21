import 'package:cloud_firestore/cloud_firestore.dart';

// ── DoorTypeField ─────────────────────────────────────────────────────────────
class DoorTypeField {
  final String id;
  final String fieldKey;
  final String label;
  final String fieldType; // text, number, boolean, select, date, link, textarea
  final bool isRequired;
  final dynamic defaultValue;
  final List<Map<String, String>> options;
  final Map<String, dynamic> validation;
  final int order;

  const DoorTypeField({
    required this.id,
    required this.fieldKey,
    required this.label,
    required this.fieldType,
    required this.isRequired,
    this.defaultValue,
    this.options = const [],
    this.validation = const {},
    required this.order,
  });

  factory DoorTypeField.fromMap(String id, Map<String, dynamic> map) {
    return DoorTypeField(
      id: id,
      fieldKey: map['field_key'] as String? ?? '',
      label: map['label'] as String? ?? '',
      fieldType: map['field_type'] as String? ?? 'text',
      isRequired: map['is_required'] as bool? ?? false,
      defaultValue: map['default_value'],
      options: (map['options'] as List<dynamic>?)
              ?.map((e) => Map<String, String>.from(e as Map))
              .toList() ??
          [],
      validation: (map['validation'] as Map<String, dynamic>?) ?? {},
      order: (map['order'] as num?)?.toInt() ?? 0,
    );
  }
}

// ── DoorType ──────────────────────────────────────────────────────────────────
class DoorType {
  final String id;
  final String slug;
  final String name;
  final String icon;
  final String description;
  final List<String> features;
  final bool isActive;
  final int order;
  final List<DoorTypeField> fields;

  const DoorType({
    required this.id,
    required this.slug,
    required this.name,
    required this.icon,
    required this.description,
    required this.features,
    required this.isActive,
    required this.order,
    this.fields = const [],
  });

  factory DoorType.fromMap(String id, Map<String, dynamic> map) {
    return DoorType(
      id: id,
      slug: map['slug'] as String? ?? '',
      name: map['name'] as String? ?? '',
      icon: map['icon'] as String? ?? 'door_front',
      description: map['description'] as String? ?? '',
      features: List<String>.from(map['features'] as List<dynamic>? ?? []),
      isActive: map['is_active'] as bool? ?? true,
      order: (map['order'] as num?)?.toInt() ?? 0,
    );
  }

  DoorType copyWith({List<DoorTypeField>? fields}) {
    return DoorType(
      id: id,
      slug: slug,
      name: name,
      icon: icon,
      description: description,
      features: features,
      isActive: isActive,
      order: order,
      fields: fields ?? this.fields,
    );
  }
}

// ── Door ──────────────────────────────────────────────────────────────────────
enum DoorStatus { active, inactive, archived }

class Door {
  final String id;
  final String ownerId;
  final String name;
  final String typeId;
  final String typeSlug;
  final DoorStatus status;
  final bool isPublic;
  final String qrToken;
  final Map<String, dynamic> settings;
  final Map<String, dynamic> fieldValues;
  final String? linkedQrId;
  final Timestamp? createdAt;
  final Timestamp? updatedAt;

  const Door({
    required this.id,
    required this.ownerId,
    required this.name,
    required this.typeId,
    required this.typeSlug,
    required this.status,
    required this.isPublic,
    required this.qrToken,
    this.settings = const {},
    this.fieldValues = const {},
    this.linkedQrId,
    this.createdAt,
    this.updatedAt,
  });

  factory Door.fromMap(String id, Map<String, dynamic> map) {
    return Door(
      id: id,
      ownerId: map['owner_id'] as String? ?? '',
      name: map['name'] as String? ?? '',
      typeId: map['type_id'] as String? ?? '',
      typeSlug: map['type_slug'] as String? ?? '',
      status: _parseStatus(map['status'] as String? ?? 'active'),
      isPublic: map['is_public'] as bool? ?? false,
      qrToken: map['qr_token'] as String? ?? '',
      settings: (map['settings'] as Map<String, dynamic>?) ?? {},
      fieldValues: (map['field_values'] as Map<String, dynamic>?) ?? {},
      linkedQrId: map['linked_qr_id'] as String?,
      createdAt: map['created_at'] as Timestamp?,
      updatedAt: map['updated_at'] as Timestamp?,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'owner_id': ownerId,
      'name': name,
      'type_id': typeId,
      'type_slug': typeSlug,
      'status': status.name,
      'is_public': isPublic,
      'qr_token': qrToken,
      'settings': settings,
      'field_values': fieldValues,
      if (linkedQrId != null) 'linked_qr_id': linkedQrId,
    };
  }

  static DoorStatus _parseStatus(String value) {
    return DoorStatus.values.firstWhere(
      (e) => e.name == value,
      orElse: () => DoorStatus.active,
    );
  }
}

// ── DoorInteraction ───────────────────────────────────────────────────────────
enum InteractionStatus { pending, seen, admitted, declined, completed }

class DoorInteraction {
  final String id;
  final String doorId;
  final String doorOwnerId;
  final String? visitorName;
  final String? visitorPhone;
  final String? visitorMessage;
  final Map<String, dynamic> fieldData;
  final InteractionStatus status;
  final Timestamp? createdAt;

  const DoorInteraction({
    required this.id,
    required this.doorId,
    required this.doorOwnerId,
    this.visitorName,
    this.visitorPhone,
    this.visitorMessage,
    this.fieldData = const {},
    required this.status,
    this.createdAt,
  });

  factory DoorInteraction.fromMap(String id, Map<String, dynamic> map) {
    return DoorInteraction(
      id: id,
      doorId: map['door_id'] as String? ?? '',
      doorOwnerId: map['door_owner_id'] as String? ?? '',
      visitorName: map['visitor_name'] as String?,
      visitorPhone: map['visitor_phone'] as String?,
      visitorMessage: map['visitor_message'] as String?,
      fieldData: (map['field_data'] as Map<String, dynamic>?) ?? {},
      status: InteractionStatus.values.firstWhere(
        (e) => e.name == (map['status'] as String? ?? 'pending'),
        orElse: () => InteractionStatus.pending,
      ),
      createdAt: map['created_at'] as Timestamp?,
    );
  }
}
