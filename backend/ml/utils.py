
def temp_comfort_score(temp_max):
    """Score temperature based on golden zone of 65-78F."""
    golden_zone = [65,78]

    if golden_zone[0] <= temp_max <= golden_zone[1]:
        return 1.0
    
    min_diff, max_diff = abs(temp_max - golden_zone[0]), abs(temp_max - golden_zone[1])
    score = 1-(min(min_diff, max_diff)/25)
    return max(0, score)

def rain_comfort_score(precip_mm):
    """Score rainfall based on mm of rainfall."""
    if precip_mm == 0:
        return 1.0
    elif precip_mm < 2:
        return 0.6
    elif precip_mm < 10:
        return 0.3
    else:
        return 0.0

def humidity_comfort_score(h):
    """Score humidity based on ideal band of 30-60%."""
    if 30 <= h <= 60:
        return 1.0
    
    # Too dry
    if h < 30:
        return max(0, 1 - (30 - h) / 30)  
    
    # Too humid
    if h > 60:
        return max(0, 1 - (h - 60) / 40)  


def wind_comfort_score(wind_kmh):
    """Score wind speed based on ideal being <=24 km/h."""
    if wind_kmh <= 24:
        return 1.0
    
    # Linear decay from 24 to 48 km/h
    if wind_kmh <= 48:
        return max(0, 1 - (wind_kmh - 24) / 24)
    
    # Too windy
    return 0.0

def cloud_comfort_score(cloud_pct):
    """Score cloud cover based on ideal being 50%."""
    center = abs(cloud_pct - 50)
    return max(0, 1 - center / 50)


def compute_comfort_index(row):
    """Compute overall comfort index from weather parameters."""

    temp = row.temp_max 
    temp_score = temp_comfort_score(temp)
    rain_score = rain_comfort_score(row.precipitation)
    humidity_score = humidity_comfort_score(row.humidity_max)
    wind_score = wind_comfort_score(row.wind_max)
    cloud_score = cloud_comfort_score(row.cloudcover)

    comfort = (
        0.40 * temp_score +
        0.30 * rain_score +
        0.10 * humidity_score +
        0.10 * wind_score +
        0.10 * cloud_score
    )

    # Scale to 0–100
    return comfort * 100