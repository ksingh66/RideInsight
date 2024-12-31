from django.db import models
from django.contrib.auth.models import User
import os
# Create your models here.


class UploadedCSV(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    raw_csv = models.FileField(upload_to='csv_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_csv = models.FileField(upload_to='summaries/', null=True)
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s CSV - {self.uploaded_at}"
    def delete(self, *args, **kwargs):
        # Delete the files from storage
        if self.raw_csv:
            if os.path.isfile(self.raw_csv.path):
                os.remove(self.raw_csv.path)
        if self.processed_csv:
            if os.path.isfile(self.processed_csv.path):
                os.remove(self.processed_csv.path)
        super().delete(*args, **kwargs)
