from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_save

class Rating(models.Model):
    bnb = models.ForeignKey("BNB", on_delete=models.CASCADE, related_name="ratings", null=True, blank=True)
    value = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self):
        return f"{self.value}/5 for {self.trip.location if self.trip else 'No Trip'}"


class Review(models.Model):
    bnb = models.ForeignKey("BNB", on_delete=models.CASCADE, related_name="reviews", null=True, blank=True)
    statement = models.CharField(max_length=4000)
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE, related_name="review_ratings", null=True, blank=True)
    def __str__(self):
        return f"Review for {self.trip.location if self.trip else 'No Trip'}: {self.statement[:50]}"


class BNB(models.Model):
    trip = models.OneToOneField("Trip", on_delete=models.CASCADE, related_name="bnbs", null=True, blank=True)
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=400)
    availability = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.name} ({self.trip.location if self.trip else 'No Trip'})"


class Plan(models.Model):
    name = models.CharField(max_length=400)
    trip = models.ForeignKey("Trip", on_delete=models.CASCADE, related_name="plans", null=True, blank=True)
    activity = models.TextField(blank=True,null=True)
    def __str__(self):
        return f"{self.activity} ({self.trip.location if self.trip else 'No Trip'})"

class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="trip",null=True,blank=True)
    name = models.CharField(max_length=400)
    location = models.CharField(max_length=250)
    date = models.DateField(auto_now_add=False)
    def __str__(self):
        return self.location

class MyTrips(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="my_trips", null=True, blank=True)
    trips = models.ManyToManyField(Trip, related_name='in_mytrips', blank=True)
    class Meta:
        verbose_name_plural = "My trips"

    def __str__(self):
        return f"{self.user.username}'s Trips"


class BucketList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="bucket_list",null=True, blank=True)
    trips = models.ManyToManyField(Trip, related_name='bucketlists', blank=True)
    def __str__(self):
        return f"{self.user.username}'s Bucket List"

# ✅ Auto-create both lists for every user
@receiver(post_save, sender=User)
def create_user_lists(sender, instance, created, **kwargs):
    if created:
        BucketList.objects.get_or_create(user=instance)
        MyTrips.objects.get_or_create(user=instance)