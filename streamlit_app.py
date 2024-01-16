import pandas as pd
import streamlit as st
from geo_functions import geo_one_loc, find_poi_in_street, nodes_to_df, find_near_pois, enrich_pois
from streamlit_keplergl import keplergl_static
from keplergl import KeplerGl

st.set_page_config(layout="wide")


def click_button():
    st.session_state.clicked = True


def get_poi_name(pois, idx):
    try:
        if len(pois.loc[idx, 'name']) != 0:
            return pois.loc[idx, 'name']
        else:
            return pois.loc[idx, 'display_name']
    except:
        print('error in get_poi_name')
        return 'no_name'


def show_POIs(pois):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("POIs")
        for idx in range(len(pois)):
            show_POI(pois, idx)
    with col2:
        st.subheader("Map")
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
        keplergl_static(map_1, center_map=True)


def show_POI(pois, idx):
    try:
        name = get_poi_name(pois, idx)
        with st.expander(name):
            container = st.container(border=True)
            container.subheader(pois.loc[idx, 'type'])
            container.text('Address: ' + pois.loc[idx, 'display_name'])
            st.markdown("""---""")
            container.text('Street: ' + pois.loc[idx, 'road'])
            container.text('Suburb: ' + pois.loc[idx, 'suburb'])
            container.text('City: ' + pois.loc[idx, 'town'])
            container.text('Municipality: ' + pois.loc[idx, 'municipality'])
            container.text('Region: ' + pois.loc[idx, 'state_district'] + ' | ' + pois.loc[idx, 'state'])
            container.text('Country: ' + pois.loc[idx, 'country'])
    except:
        print('error')


st.title("Gaided First POC (POIs)")
st.subheader("Find all POIs near to an address")
main_container = st.container(border=True)
addr = main_container.text_input("Your Address", "37 Quai Jacques Chirac, 75007 Paris")
poi_type = main_container.selectbox(
    'You are interested in what?',
    ('tourism', 'amenity', 'building', 'all'))
distance = main_container.slider('Distance (m)', 100, 1000)
main_container.button("Search for POIs", on_click=click_button)

if "clicked" not in st.session_state:
    st.session_state.clicked = False

if st.session_state.clicked:
    bar = st.progress(0)
    # Find the right address
    loc = geo_one_loc(addr)
    if loc is not None:
        st.text('Full name: ' + loc.raw['display_name'])
        st.text('Street name: ' + loc.raw['address']['road'])
        # find POIs on the same street
        bar.progress(10)
        nodes = find_near_pois(loc, poi_type, distance)
        bar.progress(50)
        pois = enrich_pois(nodes)
        bar.progress(80)
        POIs = nodes_to_df(pois)
        bar.progress(90)
        show_POIs(POIs)
        bar.progress(100)
        st.balloons()
        with st.expander("Data"):
            st.dataframe(POIs)
    else:
        st.warning('no results')
