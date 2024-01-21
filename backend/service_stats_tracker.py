import operator as op
from collections import Counter

from vehicule_enum import VehiculeCategory

SERVICED_VEHICULE_CATEGORIES_COUNTER = Counter(**dict.fromkeys(list(VehiculeCategory.__members__),0))
