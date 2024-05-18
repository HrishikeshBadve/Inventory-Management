# signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Record, AuditLog

@receiver(post_save, sender=Record)
def create_audit_log(sender, instance, created, **kwargs):
    action = 'added' if created else 'updated'
    AuditLog.objects.create(
        action=action,
        details=f"Record {instance.name} was {action}.",
        user=instance.modified_by
    )

@receiver(post_delete, sender=Record)
def delete_audit_log(sender, instance, **kwargs):
    # Check if the user is available
    user = getattr(instance, 'modified_by', None)
    if user:
        AuditLog.objects.create(
            action='deleted',
            details=f"Record {instance.name} was deleted.",
            user=user
        )
