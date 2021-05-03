import math


def pos_neg(num):
    if num >= 0:
        return 0 if num == 0 else 1
    else:
        return -1


def convert_yards_to_degrees(lat_yards, long_yards, tact_lat_deg, tact_long_deg):
    if lat_yards == 0 or long_yards == 0:
        return lat_yards, long_yards

    tact_lat_rad = tact_lat_deg * math.pi / 180

    x_heli_meters = lat_yards / 1.09361
    y_heli_meters = long_yards / 1.09361

    x = x_heli_meters
    y = y_heli_meters
    x_y = x / y

    a = 6378137.000
    e = 0.08181919084262

    alpha = math.atan(x_y)
    rho = a * math.sqrt(1 - ((e * e) * math.sin(tact_lat_rad) * math.sin(tact_lat_rad)))
    beta = pos_neg(y) * math.atan(math.sqrt(x * x + y * y) / rho)

    lat_deg = (180 / math.pi) * math.asin((math.sin(tact_lat_rad) * math.cos(beta)) + (math.cos(tact_lat_rad) * math.sin(beta) * math.cos(alpha)))
    lat_rad = lat_deg * math.pi / 180

    long_deg = tact_long_deg + (180 / math.pi) * math.asin(math.sin(alpha) * math.sin(beta) / math.cos(lat_rad))

    return lat_deg, long_deg


