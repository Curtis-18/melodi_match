from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count, Sum


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6D6D00')  # Hex color for UI
    spotify_id = models.CharField(max_length=100, blank=True)  # For future integration
    
    def __str__(self):
        return self.name
    
    @property
    def prediction_count(self):
        return self.prediction_set.count()
    
    @classmethod
    def get_most_predicted(cls, days=30):
        """Returns the most predicted genre in last X days"""
        return cls.objects.annotate(
            num_predictions=Count('prediction', 
                                filter=models.Q(prediction__created_at__gte=timezone.now()-timezone.timedelta(days=days)))
        ).order_by('-num_predictions').first()

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    audio_file = models.FileField(upload_to='predictions/%Y/%m/%d/')
    predicted_genre = models.ForeignKey(Genre, on_delete=models.PROTECT)
    confidence = models.FloatField()
    features = models.JSONField()  # Stores extracted audio features
    created_at = models.DateTimeField(auto_now_add=True)
    feedback = models.BooleanField(null=True, blank=True)  # User accuracy feedback
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.predicted_genre} ({self.confidence:.0f}%)"

class UserActivity(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_prediction = models.DateTimeField(null=True, blank=True)
    total_predictions = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username}'s activity"

class TrendingGenre(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    score = models.FloatField()  # Calculated trend score
    date = models.DateField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', '-score']
        get_latest_by = 'date'
    
    @classmethod
    def update_trends(cls):
        """Calculate and update trending genres"""
        # Get predictions from last 7 days
        recent = Prediction.objects.filter(
            created_at__gte=timezone.now()-timezone.timedelta(days=7))
        
        # Calculate growth rate compared to previous period
        genre_stats = recent.values('predicted_genre').annotate(
            current_count=Count('id'),
            previous_count=Count('prediction', 
                               filter=models.Q(created_at__gte=timezone.now()-timezone.timedelta(days=14),
                                            created_at__lt=timezone.now()-timezone.timedelta(days=7)))
        ).order_by('-current_count')
        
        # Update trending genres
        for stat in genre_stats:
            genre = Genre.objects.get(pk=stat['predicted_genre'])
            growth_rate = (stat['current_count'] - stat['previous_count']) / max(1, stat['previous_count'])
            score = stat['current_count'] * (1 + growth_rate)
            
            cls.objects.create(
                genre=genre,
                score=score
            )
    
    def __str__(self):
        return f"Trending: {self.genre.name} ({self.score:.1f})"
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    predicted_genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)  # Made optional
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        genre_name = self.predicted_genre.name if self.predicted_genre else "No genre"
        return f"{self.user.username} - {genre_name}"
