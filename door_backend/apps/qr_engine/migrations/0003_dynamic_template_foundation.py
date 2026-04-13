import secrets
import uuid

from django.db import migrations, models
import django.db.models.deletion


def backfill_qr_template_foundation(apps, schema_editor):
    QRCode = apps.get_model("qr_engine", "QRCode")

    for qr in QRCode.objects.all().iterator():
        changed = []

        if not qr.qr_token:
            qr.qr_token = f"qr-{secrets.token_hex(8)}"
            changed.append("qr_token")

        if not qr.metadata_json:
            qr.metadata_json = qr.metadata or {}
            changed.append("metadata_json")

        if not qr.owner_type:
            if qr.organization_id:
                qr.owner_type = "organization"
                qr.owner_id = str(qr.organization_id)
            elif qr.event_id:
                qr.owner_type = "event"
                qr.owner_id = str(qr.event_id)
            elif qr.group_id:
                qr.owner_type = "group"
                qr.owner_id = str(qr.group_id)
            elif qr.queue_id:
                qr.owner_type = "queue"
                qr.owner_id = str(qr.queue_id)
            else:
                qr.owner_type = qr.entity_type or "organization"
                qr.owner_id = ""
            changed.extend(["owner_type", "owner_id"])

        if not qr.purpose:
            qr.purpose = qr.mode or qr.payload_type or "custom_action"
            changed.append("purpose")

        if changed:
            qr.save(update_fields=changed)


class Migration(migrations.Migration):

    dependencies = [
        ("qr_engine", "0002_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="InteractionTemplate",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at_client", models.DateTimeField(blank=True, null=True)),
                ("updated_at_client", models.DateTimeField(blank=True, null=True)),
                ("created_at_server", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at_server", models.DateTimeField(auto_now=True, db_index=True)),
                ("sync_status", models.CharField(choices=[("pending_local", "Pending Local"), ("queued_sync", "Queued Sync"), ("synced", "Synced"), ("conflict", "Conflict"), ("failed", "Failed"), ("deleted", "Deleted")], db_index=True, default="synced", max_length=24)),
                ("created_by_device_id", models.CharField(blank=True, max_length=128)),
                ("last_modified_by_device_id", models.CharField(blank=True, max_length=128)),
                ("idempotency_key", models.UUIDField(blank=True, db_index=True, null=True)),
                ("is_deleted", models.BooleanField(db_index=True, default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("name", models.CharField(max_length=255)),
                ("category", models.CharField(db_index=True, max_length=64)),
                ("description", models.TextField(blank=True)),
                ("icon", models.CharField(blank=True, max_length=64)),
                ("default_language", models.CharField(default="en", max_length=12)),
                ("is_public", models.BooleanField(db_index=True, default=False)),
                ("supports_offline", models.BooleanField(default=False)),
                ("version", models.PositiveIntegerField(default=1)),
                ("schema_json", models.JSONField(blank=True, default=dict)),
            ],
            options={"db_table": "qr_interaction_templates"},
        ),
        migrations.CreateModel(
            name="TemplateField",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at_client", models.DateTimeField(blank=True, null=True)),
                ("updated_at_client", models.DateTimeField(blank=True, null=True)),
                ("created_at_server", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at_server", models.DateTimeField(auto_now=True, db_index=True)),
                ("sync_status", models.CharField(choices=[("pending_local", "Pending Local"), ("queued_sync", "Queued Sync"), ("synced", "Synced"), ("conflict", "Conflict"), ("failed", "Failed"), ("deleted", "Deleted")], db_index=True, default="synced", max_length=24)),
                ("version", models.BigIntegerField(default=1)),
                ("created_by_device_id", models.CharField(blank=True, max_length=128)),
                ("last_modified_by_device_id", models.CharField(blank=True, max_length=128)),
                ("idempotency_key", models.UUIDField(blank=True, db_index=True, null=True)),
                ("is_deleted", models.BooleanField(db_index=True, default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("field_key", models.CharField(max_length=100)),
                ("label", models.CharField(max_length=255)),
                ("field_type", models.CharField(max_length=50)),
                ("is_required", models.BooleanField(default=False)),
                ("default_value", models.JSONField(blank=True, default=dict)),
                ("options_json", models.JSONField(blank=True, default=dict)),
                ("validation_json", models.JSONField(blank=True, default=dict)),
                ("visibility_rule_json", models.JSONField(blank=True, default=dict)),
                ("template", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="fields", to="qr_engine.interactiontemplate")),
            ],
            options={"db_table": "qr_template_fields"},
        ),
        migrations.CreateModel(
            name="TemplateWorkflowState",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at_client", models.DateTimeField(blank=True, null=True)),
                ("updated_at_client", models.DateTimeField(blank=True, null=True)),
                ("created_at_server", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at_server", models.DateTimeField(auto_now=True, db_index=True)),
                ("sync_status", models.CharField(choices=[("pending_local", "Pending Local"), ("queued_sync", "Queued Sync"), ("synced", "Synced"), ("conflict", "Conflict"), ("failed", "Failed"), ("deleted", "Deleted")], db_index=True, default="synced", max_length=24)),
                ("version", models.BigIntegerField(default=1)),
                ("created_by_device_id", models.CharField(blank=True, max_length=128)),
                ("last_modified_by_device_id", models.CharField(blank=True, max_length=128)),
                ("idempotency_key", models.UUIDField(blank=True, db_index=True, null=True)),
                ("is_deleted", models.BooleanField(db_index=True, default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("state_name", models.CharField(max_length=100)),
                ("state_type", models.CharField(db_index=True, max_length=50)),
                ("order", models.PositiveIntegerField(default=1)),
                ("color", models.CharField(blank=True, max_length=32)),
                ("is_initial", models.BooleanField(default=False)),
                ("is_final", models.BooleanField(default=False)),
                ("template", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="workflow_states", to="qr_engine.interactiontemplate")),
            ],
            options={"db_table": "qr_template_workflow_states", "ordering": ["order", "created_at_server"]},
        ),
        migrations.CreateModel(
            name="TemplateAction",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at_client", models.DateTimeField(blank=True, null=True)),
                ("updated_at_client", models.DateTimeField(blank=True, null=True)),
                ("created_at_server", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at_server", models.DateTimeField(auto_now=True, db_index=True)),
                ("sync_status", models.CharField(choices=[("pending_local", "Pending Local"), ("queued_sync", "Queued Sync"), ("synced", "Synced"), ("conflict", "Conflict"), ("failed", "Failed"), ("deleted", "Deleted")], db_index=True, default="synced", max_length=24)),
                ("version", models.BigIntegerField(default=1)),
                ("created_by_device_id", models.CharField(blank=True, max_length=128)),
                ("last_modified_by_device_id", models.CharField(blank=True, max_length=128)),
                ("idempotency_key", models.UUIDField(blank=True, db_index=True, null=True)),
                ("is_deleted", models.BooleanField(db_index=True, default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("action_name", models.CharField(max_length=100)),
                ("action_key", models.CharField(max_length=100)),
                ("role_required", models.CharField(blank=True, max_length=50)),
                ("button_style", models.CharField(blank=True, max_length=50)),
                ("action_config_json", models.JSONField(blank=True, default=dict)),
                ("source_state", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="outgoing_actions", to="qr_engine.templateworkflowstate")),
                ("target_state", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="incoming_actions", to="qr_engine.templateworkflowstate")),
                ("template", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="actions", to="qr_engine.interactiontemplate")),
            ],
            options={"db_table": "qr_template_actions"},
        ),
        migrations.CreateModel(
            name="NotificationRule",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at_client", models.DateTimeField(blank=True, null=True)),
                ("updated_at_client", models.DateTimeField(blank=True, null=True)),
                ("created_at_server", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at_server", models.DateTimeField(auto_now=True, db_index=True)),
                ("sync_status", models.CharField(choices=[("pending_local", "Pending Local"), ("queued_sync", "Queued Sync"), ("synced", "Synced"), ("conflict", "Conflict"), ("failed", "Failed"), ("deleted", "Deleted")], db_index=True, default="synced", max_length=24)),
                ("version", models.BigIntegerField(default=1)),
                ("created_by_device_id", models.CharField(blank=True, max_length=128)),
                ("last_modified_by_device_id", models.CharField(blank=True, max_length=128)),
                ("idempotency_key", models.UUIDField(blank=True, db_index=True, null=True)),
                ("is_deleted", models.BooleanField(db_index=True, default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("trigger_event", models.CharField(db_index=True, max_length=100)),
                ("audience_type", models.CharField(db_index=True, max_length=50)),
                ("audience_config", models.JSONField(blank=True, default=dict)),
                ("channel", models.CharField(max_length=30)),
                ("priority", models.CharField(default="normal", max_length=30)),
                ("fallback_rule_json", models.JSONField(blank=True, default=dict)),
                ("template", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notification_rules", to="qr_engine.interactiontemplate")),
            ],
            options={"db_table": "qr_notification_rules"},
        ),
        migrations.AddField(
            model_name="qrcode",
            name="metadata_json",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="qrcode",
            name="owner_id",
            field=models.CharField(blank=True, db_index=True, max_length=100),
        ),
        migrations.AddField(
            model_name="qrcode",
            name="owner_type",
            field=models.CharField(blank=True, db_index=True, max_length=50),
        ),
        migrations.AddField(
            model_name="qrcode",
            name="purpose",
            field=models.CharField(blank=True, db_index=True, max_length=100),
        ),
        migrations.AddField(
            model_name="qrcode",
            name="qr_token",
            field=models.SlugField(blank=True, db_index=False, max_length=120, null=True),
        ),
        migrations.AddField(
            model_name="qrcode",
            name="template",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="qr_codes", to="qr_engine.interactiontemplate"),
        ),
        migrations.AddField(
            model_name="qrscan",
            name="template_snapshot",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.RunPython(backfill_qr_template_foundation, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="qrcode",
            name="qr_token",
            field=models.SlugField(db_index=False, default="placeholder-token", max_length=120, unique=True),
            preserve_default=False,
        ),
        migrations.AddIndex(
            model_name="interactiontemplate",
            index=models.Index(fields=["category", "is_public"], name="qr_interact_categor_b20c4e_idx"),
        ),
        migrations.AddIndex(
            model_name="interactiontemplate",
            index=models.Index(fields=["updated_at_server"], name="qr_interact_updated_6c354d_idx"),
        ),
        migrations.AddIndex(
            model_name="templatefield",
            index=models.Index(fields=["template", "field_key"], name="qr_template_templat_359f41_idx"),
        ),
        migrations.AddIndex(
            model_name="templatefield",
            index=models.Index(fields=["updated_at_server"], name="qr_template_updated_f7fd45_idx"),
        ),
        migrations.AlterUniqueTogether(name="templatefield", unique_together={("template", "field_key")}),
        migrations.AddIndex(
            model_name="templateworkflowstate",
            index=models.Index(fields=["template", "order"], name="qr_template_templat_fe37f8_idx"),
        ),
        migrations.AddIndex(
            model_name="templateworkflowstate",
            index=models.Index(fields=["template", "state_type"], name="qr_template_templat_1bb018_idx"),
        ),
        migrations.AddIndex(
            model_name="templateworkflowstate",
            index=models.Index(fields=["updated_at_server"], name="qr_template_updated_82e690_idx"),
        ),
        migrations.AddIndex(
            model_name="templateaction",
            index=models.Index(fields=["template", "action_key"], name="qr_template_templat_61bf9d_idx"),
        ),
        migrations.AddIndex(
            model_name="templateaction",
            index=models.Index(fields=["updated_at_server"], name="qr_template_updated_fa33cd_idx"),
        ),
        migrations.AlterUniqueTogether(name="templateaction", unique_together={("template", "action_key")}),
        migrations.AddIndex(
            model_name="notificationrule",
            index=models.Index(fields=["template", "trigger_event"], name="qr_notifica_templat_aeeda6_idx"),
        ),
        migrations.AddIndex(
            model_name="notificationrule",
            index=models.Index(fields=["audience_type", "channel"], name="qr_notifica_audienc_98ef55_idx"),
        ),
        migrations.AddIndex(
            model_name="notificationrule",
            index=models.Index(fields=["updated_at_server"], name="qr_notifica_updated_3f79cc_idx"),
        ),
        migrations.AddIndex(
            model_name="qrcode",
            index=models.Index(fields=["owner_type", "owner_id"], name="qr_codes_owner_t_47e537_idx"),
        ),
        migrations.AddIndex(
            model_name="qrcode",
            index=models.Index(fields=["template", "purpose"], name="qr_codes_templat_08ba38_idx"),
        ),
    ]
