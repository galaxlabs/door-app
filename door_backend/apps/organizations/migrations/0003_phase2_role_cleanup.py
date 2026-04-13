from django.db import migrations, models


def normalize_member_roles(apps, schema_editor):
    OrganizationMember = apps.get_model("organizations", "OrganizationMember")
    GroupMember = apps.get_model("organizations", "GroupMember")

    OrganizationMember.objects.filter(role="general_user").update(role="member")
    GroupMember.objects.filter(role="general_user").update(role="member")


class Migration(migrations.Migration):

    dependencies = [
        ("organizations", "0002_checkpoint_household_missingpersoncase_trip_and_more"),
    ]

    operations = [
        migrations.RunPython(normalize_member_roles, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="organizationmember",
            name="role",
            field=models.CharField(
                choices=[
                    ("owner", "Owner"),
                    ("organization_admin", "Organization Admin"),
                    ("manager", "Manager"),
                    ("group_leader", "Group Leader"),
                    ("staff", "Staff"),
                    ("member", "Member"),
                ],
                db_index=True,
                default="member",
                max_length=24,
            ),
        ),
        migrations.AlterField(
            model_name="group",
            name="group_type",
            field=models.CharField(
                choices=[
                    ("family", "Family"),
                    ("hajj_group", "Hajj Group"),
                    ("expo_team", "Expo Team"),
                    ("clinic_team", "Clinic Team"),
                    ("office_team", "Office Team"),
                    ("team", "Team"),
                    ("staff", "Staff"),
                    ("attendee", "Attendee"),
                    ("vip", "VIP"),
                    ("custom", "Custom"),
                ],
                default="custom",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="groupmember",
            name="role",
            field=models.CharField(
                choices=[
                    ("owner", "Owner"),
                    ("organization_admin", "Organization Admin"),
                    ("manager", "Manager"),
                    ("group_leader", "Group Leader"),
                    ("staff", "Staff"),
                    ("member", "Member"),
                ],
                db_index=True,
                default="member",
                max_length=24,
            ),
        ),
    ]
