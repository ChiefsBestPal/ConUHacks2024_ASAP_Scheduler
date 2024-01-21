from datetime import datetime
from vehicule_enum import VehiculeCategory

def csv_date_to_epoch(date_string: str) -> int:
    datetime_object = datetime.strptime(date_string, r"%Y-%m-%d %H:%M")

    return int(datetime_object.timestamp())

def csv_vehicule_to_enumvehicule(vehicule_string : str) -> VehiculeCategory:
    for category in VehiculeCategory:
        if category.csv_name.casefold() == vehicule_string.casefold():
            return category
    raise TypeError()

