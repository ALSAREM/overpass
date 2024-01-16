# Find the right address
from geo_functions import geo_one_loc, geo_multi_loc

addr = "61 chemin de crépieux, caluire et cuire"
loc = geo_one_loc(addr)

structured_query = {
    'street': loc.raw['address']['road'],
    'city': loc.raw['address']['town'],
    'country': '',
    'postalcode': ''
}

locs = geo_multi_loc(structured_query)
for loc in locs:
    print(loc.raw)