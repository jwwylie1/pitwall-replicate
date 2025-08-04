from urllib.request import urlopen
import json

def number_name_map(SESSION_KEY):
    """
    Returns a dictionary mapping driver numbers to their names.
    This is used to convert driver numbers in the API responses to names.
    """
    nm_map = {}
    
    print('https://api.openf1.org/v1/drivers?session_key={}'.format(SESSION_KEY), flush=True)
    
    response = urlopen('https://api.openf1.org/v1/drivers?session_key={}'.format(SESSION_KEY))
    
    print("Found drivers!", flush=True)
    drivers = json.loads(response.read().decode('utf-8'))
    
    for driver in drivers:
        nm_map[driver['driver_number']] = driver['full_name']
        
    return nm_map
    