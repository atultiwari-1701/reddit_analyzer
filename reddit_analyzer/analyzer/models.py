from django.db import models

class AnalysisResult(models.Model):
    title = models.CharField(max_length=500)
    url = models.URLField()
    upvotes = models.IntegerField()
    comments_count = models.IntegerField()
    positive_sentiments = models.IntegerField()
    negative_sentiments = models.IntegerField()
    neutral_sentiments = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
