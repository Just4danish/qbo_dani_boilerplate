from django.db import models

# Create your models here.

class QBODetails(models.Model):
    auth_code = models.CharField(max_length = 250, null=True)
    realm_id = models.CharField(max_length = 250, null=True)
    access_token = models.CharField(max_length = 250, null=True)
    refresh_token = models.CharField(max_length = 250, null=True)
    id_token = models.CharField(max_length = 250, null=True)