from apps.qr_engine.models import InteractionTemplate, QRCode


class QRTemplateService:
    @staticmethod
    def validate_template_configuration(*, template: InteractionTemplate) -> InteractionTemplate:
        if not isinstance(template.schema_json, dict):
            raise ValueError("Template schema_json must be a JSON object.")
        return template

    @classmethod
    def create_qr_code(cls, *, label: str, **validated_data) -> QRCode:
        template = validated_data.get("template")
        if template:
            cls.validate_template_configuration(template=template)
            validated_data.setdefault("purpose", template.category)
            validated_data.setdefault("owner_type", validated_data.get("entity_type", "organization"))
            validated_data.setdefault("mode", "custom_action")
            validated_data.setdefault("payload_type", "custom_action")
            validated_data.setdefault(
                "action_payload",
                {
                    "template_id": str(template.id),
                    "template_category": template.category,
                    "template_version": template.version,
                },
            )
        qr_code = QRCode.objects.create(label=label, **validated_data)
        return qr_code
