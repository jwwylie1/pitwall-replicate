from urllib.request import urlopen
import num_name_map
import json
import re

F1_TERMS = "This is a Formula 1 broadcast. Max Verstappen. Liam Lawson. Yuki Tsunoda. Isack Hadjar.\
            Sergio Perez. Charles Leclerc. Carlos Sainz. Fernando Alonso. Lewis Hamilton.\
            George Russell. Oscar Piastri. Lando Norris. Pierre Gasly. Esteban Ocon.\
            Alex Albon. Nyck de Vries. Logan Sargeant. Valtteri Bottas. Guanyu Zhou.\
            Lance Stroll. Felipe Drugovich. Nico Hulkenberg. Kevin Magnussen.\
            Gabriel Bortoleto. Jack Doohan. Oliver Bearman. Arthur Leclerc. Lance Stroll.\
            Mercedes. Red Bull. Racing Bulls. Aston Martin. Ferrari. McLaren. Alpine.\
            Haas. Cadillac. Renault. Alfa Romeo. Williams. Toro Rosso. AlphaTauri"

REPLACEMENTS = {
    "deck": "deg",
    "Joe": "Zhou",
    "breaking at home": "bring it home",
    "Gaz leave": "Gasly",
    "Ghastly": "Gasly",
    "orlando": "Lando",
    "sonoda": "Tsunoda",
    "understay": "understeer",
    "tire": "tyre",
    "tyred": "tired",
    "strut": "strat",
    "Paris": "Perez",
    "fuck": "front",
    "the RS": "DRS",
    "insecta": "in sector",
    "house": "Haas",
    "Stephanie Wetz": "definitely wets",
    "Javi": "Gabi",
    "Berndt": "Bernd",
    "the clerk": "Leclerc",
    "Leica": "lighter",
    "Portoleto": "Bortoleto",
    "Lennon": "Lando",
    
}

def get_lap(session_key, audio):
    """ Gets the lap a radio message was given in 
    
        Returns the lap (int) of the message, and the start time (UTC) of the lap
        (used in other functions)
    """
    current_lap = 0
    start_time_of_lap = 0
    
    response = urlopen('https://api.openf1.org/v1/laps?session_key={}&driver_number={}'
                       .format(session_key, audio.driver_number))
    laps = json.loads(response.read().decode('utf-8'))
    
    audio_time = audio.date
    
    for lap in laps:
        try:
            if audio_time < lap['date_start']:
                prev_lap_index = laps.index(lap) - 1
                start_time_of_lap = laps[prev_lap_index]['date_start']
                break
            else: current_lap += 1
        except: current_lap += 1
        
    return current_lap, start_time_of_lap
    

def get_gap_ahead(session_key, audio, start_time_of_lap):
    
    response = urlopen('https://api.openf1.org/v1/intervals?session_key={}&driver_number={}&date>{}'
                       .format(session_key, audio.driver_number, start_time_of_lap))
    intervals = json.loads(response.read().decode('utf-8'))
    
    for interval in intervals:
        if audio.date < interval['date']:
            # found the closest interval check
            gap = str(interval['interval']) + 's'
            if gap == "Nones": gap = "N/A"
            return gap, interval['date']
        
    # occurs after the race finishes
    return "N/A", None
            

def get_compound(session_key, audio, lap_num):
    response = urlopen('https://api.openf1.org/v1/stints?session_key={}&driver_number={}&lap_start<={}&lap_end>={}'
                       .format(session_key, audio.driver_number, lap_num, lap_num))
    
    try:
        stint = json.loads(response.read().decode('utf-8'))[0]
        return stint['compound']
    except:
        return "N/A"
    
def get_weather(session_key, audio, start_time_of_lap):
    response = urlopen('https://api.openf1.org/v1/weather?session_key={}&date>{}'
                       .format(session_key, start_time_of_lap))
    try:
        weather = json.loads(response.read().decode('utf-8'))[0]
    except:
        return "N/A"
    # choose weather at start of lap

    try:
        if (weather['rainfall']): return 'Rain'
        else: return 'Dry'
    except:
        return "N/A"
    
def get_position(session_key, audio, date_to_check, is_P1):
    """ Gets the position of a driver at a specific date """
    if is_P1: return "P1"
        
    position = "N/A"
    
    try:
        response = urlopen('https://api.openf1.org/v1/position?session_key={}&driver_number={}&date>={}'
                       .format(session_key, audio.driver_number, date_to_check))
        position = json.loads(response.read().decode('utf-8'))[0]['position']
        position = "P" + str(position)
        
    except:
        try:
            response = urlopen('https://api.openf1.org/v1/position?session_key={}&driver_number={}&date<{}'
                       .format(session_key, audio.driver_number, date_to_check))
            position = json.loads(response.read().decode('utf-8'))[-1]['position']
            position = "P" + str(position)
        except:
            position = "N/A"
        
    return position
    
    
    
def get_extra_info(session_key, audio):
        
    NUMBER_NAME_MAP = num_name_map.number_name_map(session_key)
    
    driver_name = NUMBER_NAME_MAP[audio.driver_number]
    lap_num, start_time_of_lap = get_lap(session_key, audio)
    gap_ahead, date_to_check = get_gap_ahead(session_key, audio, start_time_of_lap)
    position = get_position(session_key, audio, date_to_check, gap_ahead=="0.0s")
    compound = get_compound(session_key, audio, lap_num)
    weather = get_weather(session_key, audio, start_time_of_lap)
    
    if lap_num == 1 and position == "N/A":
        lap_num = "Pre-Race"
    
    return [driver_name, lap_num, compound, gap_ahead, weather, position]  


def fix_terms(text):
    for key in REPLACEMENTS:
        pattern = re.compile(re.escape(key), re.IGNORECASE)
        text = pattern.sub(REPLACEMENTS[key], text)
    return text