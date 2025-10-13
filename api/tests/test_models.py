from django.test import TestCase
from django.contrib.auth.models import User
from api.models import Trip, BucketList, MyTrips


class UserListSignalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='1234')

    def test_bucketlist_and_mytrips_created(self):
        """Each user automatically gets a BucketList and MyTrips."""
        self.assertTrue(BucketList.objects.filter(user=self.user).exists())
        self.assertTrue(MyTrips.objects.filter(user=self.user).exists())

    def test_user_deletion_cascades_lists(self):
        """Deleting a user deletes both their lists."""
        self.user.delete()
        self.assertFalse(BucketList.objects.exists())
        self.assertFalse(MyTrips.objects.exists())


class TripAssignmentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='1234')
        self.trip = Trip.objects.create(
            user=self.user,
            name='Paris',
            location='France',
            date='2025-10-13'
        )

    def test_trip_adds_to_bucketlist(self):
        """Trip can be added to the user's bucket list."""
        bucketlist = self.user.bucket_list
        bucketlist.trips.add(self.trip)
        self.assertIn(self.trip, bucketlist.trips.all())
        # ✅ use correct related name here
        self.assertNotIn(self.trip, self.user.my_trips.trips.all())

    def test_trip_moves_between_lists(self):
        """Trip should only belong to one list at a time."""
        bucketlist = self.user.bucket_list
        mytrips = self.user.my_trips  # ✅ correct related name

        bucketlist.trips.add(self.trip)
        self.assertIn(self.trip, bucketlist.trips.all())

        # move trip to MyTrips
        bucketlist.trips.remove(self.trip)
        mytrips.trips.add(self.trip)

        self.assertNotIn(self.trip, bucketlist.trips.all())
        self.assertIn(self.trip, mytrips.trips.all())
