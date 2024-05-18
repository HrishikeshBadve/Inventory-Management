from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Record(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	serial_num = models.CharField(max_length = 50)
	name = models.CharField(max_length = 50)
	desc = models.CharField(max_length = 50)
	quant = models.CharField(max_length = 50)
	location = models.CharField(max_length = 50)

	modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='modified_records'
    )
	
	def __str__(self):
		return(f"{self.serial_num} {self.name}")


class AuditLog(models.Model):
	ACTION_CHOICES = [
		('added', 'Added'),
		('updated', 'Updated'),
		('deleted', 'Deleted'),
	]
	action = models.CharField(max_length=10, choices=ACTION_CHOICES)
	details = models.TextField()
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.get_action_display()} by {self.user} on {self.timestamp}"