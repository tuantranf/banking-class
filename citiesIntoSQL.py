"""
wrangle US Census data into a useable lookup table for US cities
downloaded from http://www.census.gov/geo/maps-data/data/gazetteer2015.html

this is done only once
"""

from sqlalchemy import create_engine, event, MetaData
from sqlalchemy.schema import DDL
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import numpy as np

datafile = '/home/eli/Data/Narmi/2015_Gaz_place_national.txt'
filename = '/home/eli/Data/Narmi/cities_by_state.pickle'

dbname = 'narmi_db'
username = 'eli'
password = 'eli'

engine = create_engine('postgresql://%s:%s@localhost:5432/%s'%(username,password,dbname))

## create a database (if it doesn't exist)
if not database_exists(engine.url):
    create_database(engine.url)
print(database_exists(engine.url))

# read the data
all_places = pd.read_table(datafile, encoding='latin-1')
places = all_places[['USPS','NAME']] # TODO do this in one step

# remove the place description
regex = ' CDP| city| town| village| borough| zona urbana| comunidad'
places['NAME'] = places['NAME'].str.replace(regex,'') # TODO why does this give a warning?
places.columns = ['state','city']

# find all the states
states = places.state.unique()

# actually want a list of every city in each state
cities_by_state = pd.DataFrame(states, columns=['state'])
cities_by_state['cities'] = np.empty((len(cities_by_state), 0)).tolist()
for index, row in cities_by_state.iterrows(): # TODO vectorize this
    st = row['state']
    cities_in_st = places.loc[places['state']==st]
    cities_by_state['cities'][index] = cities_in_st['city'].tolist()

# put it in the database
# this is annoying, bc sql messes up the list
#cities_by_state.to_sql('us_cities', engine, if_exists='replace')

# save the dataframe
cities_by_state.to_pickle(filename)




