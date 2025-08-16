from geopy.distance import geodesic
from recognition.models import ZoneAgro


def detect_zone_from_coordinates(latitude, longitude):
    """
    Détermine la zone agro à laquelle appartiennent les coordonnées GPS données,
    en vérifiant si elles se trouvent dans le rayon d'une zone enregistrée.

    Args:
        latitude (float): Latitude du point à vérifier
        longitude (float): Longitude du point à vérifier
    Returns:
        ZoneAgro: L'objet ZoneAgro correspondant si trouvé, None sinon
    """
    if latitude is None or longitude is None:
        return None

    try:
        latitude = float(latitude)
        longitude = float(longitude)

    except (TypeError, ValueError):
        return None

    point = (latitude, longitude)

    for zone in ZoneAgro.objects.all():
        if zone.latitude is None or zone.longitude is None or zone.rayon is None:
            continue

        try:
            zone_center = (float(zone.latitude), float(zone.longitude))
            rayon = float(zone.rayon)
        except (TypeError, ValueError):
            continue

        distance = geodesic(point, zone_center).meters

        if distance <= rayon:
            return zone

    return None
