from django.db import models

class Record(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	serial_num = models.CharField(max_length = 50)
	name = models.CharField(max_length = 50)
	desc = models.CharField(max_length = 50)
	quant = models.CharField(max_length = 50)
	location = models.CharField(max_length = 50)

	def __str__(self):
		return(f"{self.serial_num} {self.name}")
	