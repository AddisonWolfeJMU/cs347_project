from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator



class Rating(models.Model):
    value = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    def __str__(self):
        return str(self.value)


class Review(models.Model):
    statement = models.CharField(max_length=4000)
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE, related_name='reviews')
    def __str__(self):
        return self.statement[:50]  # show first 50 chars

class BNB(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=400)
    availability =  models.BooleanField(default=True)
    reviews = models.ManyToManyField(Review,blank=True)
    rating = models.ManyToManyField(Rating, blank=True)
    def __str__(self):
        return self.name


class Plan(models.Model):
    activity = models.CharField(max_length=400)
    def __str__(self):
        return self.activity

class Trip(models.Model):
    location = models.CharField(max_length=250)
    availability = models.BooleanField(default=True)
    reviews = models.ManyToManyField(Review, blank=True)
    rating = models.ManyToManyField(Rating, blank=True)
    plans = models.ManyToManyField(Plan, blank=True)
    def __str__(self):
        return self.location


class BucketList(models.Model):
    trips = models.ManyToManyField(Trip, blank=True)
    def __str__(self):
        return f"BucketList ({self.trips.count()} trips)"


class MyTrips(models.Model):
    trips = models.ManyToManyField(Trip, blank=True)
    def __str__(self):
        return f"MyTrips ({self.trips.count()} trips)"

