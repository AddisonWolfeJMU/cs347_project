from django.contrib import admin
from django import forms
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import format_html

from .models import Rating, Review, BNB, Plan, Trip, BucketList, MyTrips

class TripAdminForm(forms.ModelForm):
    LIST_CHOICES = [
        ('', '--- Select List ---'),
        ('bucketlist', 'Bucket List'),
        ('mytrips', 'My Trips'),
    ]
    assign_to = forms.ChoiceField(choices=LIST_CHOICES, required=False, label="Add Trip To")

    class Meta:
        model = Trip
        exclude = ['id']  # exclude ID but keep everything else

    def save(self, commit=True):
        # 1. Save trip first (so we have a valid instance)
        trip = super().save(commit=True)
        user = trip.user
        choice = self.cleaned_data.get('assign_to')

        # 2. Explicitly clear both lists first to prevent duplicates
        if user:
            bucketlist = BucketList.objects.filter(user=user).first()
            mytrips = MyTrips.objects.filter(user=user).first()

            if bucketlist:
                bucketlist.trips.remove(trip)
            if mytrips:
                mytrips.trips.remove(trip)

            # 3. Add to the selected one
            if choice == 'bucketlist' and bucketlist:
                bucketlist.trips.add(trip)
                print("Added to bucketlist only")
            elif choice == 'mytrips' and mytrips:
                mytrips.trips.add(trip)
                print("Added to mytrips only")
            else:
                print("No list chosen — trip removed from both")

        return trip


class PlanInline(admin.StackedInline):
    model = Plan
    extra = 1

class BNBInline(admin.StackedInline):
    model = BNB
    extra = 1


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    form = TripAdminForm
    list_display = ('name', 'location', 'user', 'image_preview')
    inlines = [PlanInline, BNBInline]
    fields = ('user', 'name', 'location', 'date', 'image', 'image_preview', 'assign_to')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        """Display image preview in admin"""
        if obj.image:
            return format_html('<img src="{}" style="max-width: 200px; max-height: 200px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Image Preview'

    def save_model(self, request, obj, form, change):
        # make sure the trip is tied to the logged-in user if not already set
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        """
        Override this to stop Django Admin from automatically re-saving
        ManyToMany relations that we already handled manually in the form.
        """
        # Only run the non-M2M saves (no form.save_m2m)
        for formset in formsets:
            self.save_formset(request, form, formset, change=change)


class TripsInline(admin.TabularInline):
    extra = 0
    readonly_fields = ('trip',)
    fields = ('trip',)
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class BucketListInline(admin.TabularInline):
    model = BucketList.trips.through
    extra = 0
    readonly_fields = ('trip',)
    fields = ('trip',)
    can_delete = False
    verbose_name_plural = "Trips in this Bucket List"

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # ✅ Filter so only trips belonging to the currently displayed bucketlist show
        if hasattr(self, 'parent_object') and self.parent_object:
            return qs.filter(bucketlist=self.parent_object)
        return qs

    # Django doesn’t automatically provide obj to get_queryset, so we grab it from parent change_view
    def get_formset(self, request, obj=None, **kwargs):
        self.parent_object = obj
        return super().get_formset(request, obj, **kwargs)

class MyTripsInline(admin.TabularInline):
    model = MyTrips.trips.through
    extra = 0
    readonly_fields = ('trip',)
    fields = ('trip',)
    can_delete = False
    verbose_name_plural = "Trips in this MyTrips list"

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(self, 'parent_object') and self.parent_object:
            return qs.filter(mytrips=self.parent_object)
        return qs

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_object = obj
        return super().get_formset(request, obj, **kwargs)


@admin.register(BucketList)
class BucketListAdmin(admin.ModelAdmin):
    list_display = ('user',)
    inlines = [BucketListInline]
    readonly_fields = ('user',)
    def has_add_permission(self, request, obj=None):
        return False  # no manual adds allowed

    def has_change_permission(self, request, obj=None):
        return False  # fully read-only inline


@admin.register(MyTrips)
class MyTripsAdmin(admin.ModelAdmin):
    list_display = ('user',)
    inlines = [MyTripsInline]
    readonly_fields = ('user',)
    def has_add_permission(self, request, obj=None):
        return False  # no manual adds allowed

    def has_change_permission(self, request, obj=None):
        return False  # fully read-only inline