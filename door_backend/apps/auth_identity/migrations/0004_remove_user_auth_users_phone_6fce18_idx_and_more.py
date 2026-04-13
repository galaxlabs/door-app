from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auth_identity", "0003_phase1_identity_cleanup"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="user",
            name="auth_users_phone_6fce18_idx",
        ),
        migrations.RenameIndex(
            model_name="user",
            old_name="auth_users_email_617476_idx",
            new_name="auth_users_email_9c7e62_idx",
        ),
        migrations.RenameIndex(
            model_name="user",
            old_name="auth_users_status_7a9ef4_idx",
            new_name="auth_users_status_b9e3aa_idx",
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["phone_number"], name="auth_users_phone_6fce18_idx"),
        ),
    ]
