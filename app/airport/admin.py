from django.conf import settings
from django.contrib import admin
from django.contrib.admin import sites
from django.views.decorators.cache import never_cache

from airport.models import Aircraft, StateChangeLog

from weather.models import WeatherData
from weather.tasks import load_weather_data


class AirportAdminSite(sites.AdminSite):

    @never_cache
    def index(self, request, extra_context=None):
        parked_large_count = Aircraft.objects.filter(
            type='AIRLINER',
            state='PARKED'
        ).count()
        parked_small_count = Aircraft.objects.filter(
            type='PRIVATE',
            state='PARKED'
        ).count()

        taken_small_percent = round((parked_small_count / settings.AIRPORT_SMALL_PARKING_SPOTS) * 100)
        taken_large_percent = round((parked_large_count / settings.AIRPORT_LARGE_PARKING_SPOTS) * 100)

        weather_data = WeatherData.objects.first()
        if not weather_data:
            load_weather_data.delay()

        extra_context = {
            'LARGE_PARKING_SPOTS': settings.AIRPORT_LARGE_PARKING_SPOTS,
            'SMALL_PARKING_SPOTS': settings.AIRPORT_SMALL_PARKING_SPOTS,
            'parked_large_count': parked_large_count,
            'parked_small_count': parked_small_count,
            'taken_small_percent': taken_small_percent,
            'taken_large_percent': taken_large_percent,
            'weather_data': weather_data
        }
        return super(AirportAdminSite, self).index(request, extra_context)


class ReadOnlyModelAdmin(admin.ModelAdmin):
    actions = None

    def has_add_permission(self, request):
        return False

    # Allow viewing objects but not actually changing them.
    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class StateChangeLogAdmin(ReadOnlyModelAdmin):
    list_display = ('aircraft', 'from_state', 'to_state', 'outcome', 'description', 'time')


class AircraftAdmin(ReadOnlyModelAdmin):
    list_display = ('call_sign', 'type', 'state', 'longitude', 'latitude', 'altitude', 'heading')


admin_site = AirportAdminSite()
admin_site.site_header = "Airport Administration"
admin_site.index_title = "Dashboard"

admin_site.register(Aircraft, AircraftAdmin)
admin_site.register(StateChangeLog, StateChangeLogAdmin)

admin.site = admin_site
sites.site = admin_site
