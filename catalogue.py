import os, re
import ephem
import ephem.stars

CATALOGUES_DIR = 'catalogues'
SOLAR_SYSTEM = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter',
                'Saturn', 'Uranus', 'Neptune', 'Pluto']
COMMON_STARS = [star.split(',')[0] for star in ephem.stars.db.split('\n')]

def list_catalogues():
    catalogues_list = os.listdir(CATALOGUES_DIR)
    print("Available catalogues: ")
    for name in catalogues_list:
        print(name[:-4], end=' ')
    print()

def get_target(target_name):
    if target_name in SOLAR_SYSTEM:
        return eval(f'ephem.{target_name}()')

    if target_name in COMMON_STARS:
        return ephem.star(target_name)

    pattern = re.compile('(^|\|)' + re.escape(target_name) + '(,|\|)')

    for filename in os.listdir(CATALOGUES_DIR):
        path = CATALOGUES_DIR + '/' + filename 
        with open(path, 'r', encoding='ISO-8859-1') as catalogue:
            for line in catalogue:
                if pattern.search(line):
                    return ephem.readdb(line)
    return None

