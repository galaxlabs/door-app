from django.db import transaction

from apps.organizations.models import Organization, OrganizationMember


class OrganizationService:
    @staticmethod
    @transaction.atomic
    def create_organization(*, owner, **data) -> Organization:
        org = Organization.objects.create(owner=owner, created_by=owner, **data)
        OrganizationMember.objects.get_or_create(
            organization=org,
            user=owner,
            defaults={"role": "owner", "membership_status": "active"},
        )
        return org
