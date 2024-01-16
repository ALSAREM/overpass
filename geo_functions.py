from geopy.geocoders import Nominatim
import overpy
import pandas as pd

geolocator = Nominatim(user_agent="my_user_agent")


### Full Data
# {
# 'place_id': 108617706,
# 'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright',
# 'osm_type': 'way',
# 'osm_id': 106641202,
# 'lat': '45.8017244',
# 'lon': '4.859929909961929',
# 'class': 'building',
# 'type': 'residential',
# 'place_rank': 30,
# 'importance': 9.99999999995449e-06,
# 'addresstype': 'building',
# 'name': 'La Clé des Champs',
# 'display_name': 'La Clé des Champs, 61, Chemin de Crépieux, Vassieux, Caluire-et-Cuire, Lyon,
# Métropole de Lyon, Rhône, Auvergne-Rhône-Alpes, France métropolitaine, 69300, France',
# 'address': {
#   'building': 'La Clé des Champs',
#   'house_number': '61',
#   'road': 'Chemin de Crépieux',
#   'suburb': 'Vassieux',
#   'town': 'Caluire-et-Cuire',
#   'municipality': 'Lyon',
#   'county': 'Métropole de Lyon',
#   'ISO3166-2-lvl6': 'FR-69M',
#   'state_district': 'Rhône',
#   'state': 'Auvergne-Rhône-Alpes',
#   'ISO3166-2-lvl4': 'FR-ARA', 'region':
#   'France métropolitaine',
#   'postcode': '69300',
#   'country': 'France',
#   'country_code': 'fr'
#  },
#  'extratags': None,
#  'boundingbox': ['45.8014978', '45.8020221', '4.8597485', '4.8600255']}
def geo_one_loc(addr):
    loc = geolocator.geocode(query=addr, addressdetails=True, extratags=True)
    return loc


def geo_multi_loc(structured_query):
    return geolocator.geocode(query=structured_query, addressdetails=True, extratags=True, exactly_one=False)


def reverse(node):
    return geolocator.reverse(query="" + str(node.lat) + "," + str(node.lon))


def find_poi_in_street(street):
    api = overpy.Overpass()
    result = api.query("way['name'='" + street + "'];out;")
    way = result.ways[0]
    return [reverse(node) for node in way.get_nodes(resolve_missing=True)]


def nodes_to_df(nodes):
    try:
        df = pd.DataFrame([{**node.raw, **(node.raw['address'])} for node in nodes])
        accepted_type = 'place'
        return df.query("""osm_type == 'node'""")
    except:
        return None


def find_near_pois(node, poi_type, distance):
    node_boundaries = node.raw['boundingbox']
    params = {
        'perimeter': distance,
        'nb': 10,
        'boundary_1': node_boundaries[0],  # 45.8014978,
        'boundary_2': node_boundaries[2],  # 4.8597485,
        'boundary_3': node_boundaries[1],  # 45.8020221,
        'boundary_4': node_boundaries[3],  # 4.8600255,
        'poi_type': poi_type
    }

    if poi_type == 'all':
        query = """
            node({boundary_1}, {boundary_2}, {boundary_3}, {boundary_4})->.centerPoint;
            (
              node(around.centerPoint:{perimeter}.00)["tourism"];
              node(around.centerPoint:{perimeter}.00)["amenity"];
              node(around.centerPoint:{perimeter}.00)["building"];
            );
            out {nb};
        """.format(**params)
    else:
        query = """
                    node({boundary_1}, {boundary_2}, {boundary_3}, {boundary_4})->.centerPoint;
                    (
                      node(around.centerPoint:{perimeter}.00)["{poi_type}"];                    
                    );
                    out {nb};
                """.format(**params)

    print(query)
    api = overpy.Overpass()
    result = api.query(query)
    return result.nodes


def enrich_pois(nodes):
    return [reverse(node) for node in nodes]

def show_map(pois):
    names = [get_poi_name(pois, idx) for idx in range(len(pois))]
    lats = [float(l) for l in pois['lat'].tolist()]
    lons = [float(l) for l in pois['lon'].tolist()]
    df = pd.DataFrame(
        {'Point': names,
         'Latitude': lats,
         'Longitude': lons})
    map_1 = KeplerGl(height=400)
    map_1.add_data(
        data=df, name="POIs"
    )
    # keplergl_static(map_1, center_map=True)