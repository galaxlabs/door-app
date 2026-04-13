from apps.organizations.models import OrganizationMember, GroupMember


class MembershipSelector:
    @staticmethod
    def user_organization_roles(user):
        return OrganizationMember.objects.filter(user=user, membership_status="active").values_list(
            "organization_id", "role"
        )

    @staticmethod
    def user_groups(user):
        return GroupMember.objects.filter(user=user, membership_status="active").select_related("group")
