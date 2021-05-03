def format_degrees_to_coordinate_lat(lat_deg: float) -> str:
    ns = 'S' if lat_deg < 0 else 'N'
    degrees = int(abs(lat_deg))
    minutes = (abs(lat_deg) - degrees) * 60
    return ns + ' ' + format_degrees_lat(degrees) + '° ' + format_minutes(minutes) + "'"


def format_degrees_to_coordinate_long(long_deg: float) -> str:
    ew = 'W' if long_deg < 0 else 'E'
    degrees = int(abs(long_deg))
    minutes = (abs(long_deg) - degrees) * 60
    return ew + ' ' + format_degrees_long(degrees) + '° ' + format_minutes(minutes) + "'"


def format_degrees_long(long: float) -> str:
    return str("%03i" % (round(abs(long))))


def format_degrees_lat(lat: float) -> str:
    return str("%02i" % (round(abs(lat))))


def format_minutes(lat: float) -> str:
    return str("%05.2f" % round(lat, 2))
