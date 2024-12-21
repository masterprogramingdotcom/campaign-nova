from django.db import IntegrityError

from home.models import Location


def create_or_get_location(request, latitude, longitude, system_identifier):
    # Prepare a filter for the location query
    filter_kwargs = {
        "latitude": latitude,
        "longitude": longitude,
        "system_identifier": system_identifier,
        "user": request.user if request.user.is_authenticated else None,
    }

    # Try to get an existing location or create a new one
    try:
        location = Location.objects.get(user=request.user)
        location.latitude = latitude
        location.longitude = longitude
        location.system_identifier = system_identifier
        location.save()
    except Exception:
        # If an IntegrityError occurs, retrieve the existing location instead
        location = Location.objects.filter(**filter_kwargs).first()
        if location is None:
            # If no location is found, you can create a new one if needed
            location = Location.objects.create(**filter_kwargs)
        else:
            location.latitude = latitude
            location.longitude = longitude
            location.system_identifier = system_identifier
            location.save()
    except Location.DoesNotExist:
        # If Location does not exist, create a new one
        location = Location.objects.create(**filter_kwargs)

    return location  # Return the retrieved or created location
