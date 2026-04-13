from apps.organizations.models import Group, GroupMember


class GroupService:
    @staticmethod
    def add_member(*, group: Group, user, role: str = "general_user", added_by=None) -> GroupMember:
        member, _ = GroupMember.objects.get_or_create(
            group=group,
            user=user,
            defaults={"role": role, "added_by": added_by},
        )
        return member
