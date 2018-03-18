from django.db import models

# Create your models here.
import json
from django.utils import timezone

class ScrapyUnit(models.Model):
    unique_id = models.CharField(max_length=100, null=True)
    data = models.TextField() # this stands for our crawled data
    date = models.DateTimeField(default=timezone.now)

    # Converting to JSON to send it to frontend
    @property
    def to_dict(self):
        data = {
            'data': json.loads(self.data),
            'date': self.date
        }
        return data
    
    def __str__(self):
        return self.unique_id