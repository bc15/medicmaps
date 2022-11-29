mesimport pandas as pd
import geopandas as gpd # Pandas addon for geolocation data
import matplotlib.pyplot as plt
from shapely.geometry import Point
import numpy as np

# MAP 1: map the location of one, or several, CHW’s home(s) and the locations of all households 
#associated with those CHW(s) in a given village/municipality

households_df = pd.read_csv("household_locations.csv")
households_df = households_df.sort_values("geo_accuracy", ascending = (False)) #sorting the values in order and removing all duplicates
households_df = households_df.drop_duplicates(subset=['household_id', 'geo_accuracy'], keep='last') 

households_df["chw_id"] = households_df["reported_by"] # rename column
households_df = households_df[["household_id", "chw_id", "longitude", "latitude"]]
fillnan = lambda a: households_df[a].fillna(households_df[a].mean()) # Fill nans, can alternatively drop them
households_df["longitude"] = fillnan("longitude")
households_df["latitude"] = fillnan("latitude")


chw_households_df = pd.read_csv("MedicCHWHouseholdData.csv")
chw_households_df = chw_households_df.sort_values("geo_accuracy", ascending = (False))
chw_households_df = chw_households_df.drop_duplicates(subset=['household_id', 'geo_accuracy'], keep='last') # keeps households with highest geo accuracy

chw_households_df["chw_id"] = chw_households_df["reported_by"] # rename column
chw_households_df = chw_households_df[["chw_id", "chw_area_id", "longitude", "latitude"]]
fillnan = lambda a: chw_households_df[a].fillna(chw_households_df[a].mean()) # Fill nans, can alternatively drop them
chw_households_df["longitude"] = fillnan("longitude")
chw_households_df["latitude"] = fillnan("latitude")

hospitals_df = pd.read_csv("neno_facilities.csv")
hospitals_df["Disability"] = hospitals_df["Disability"].apply(lambda a: "Yes" if a else "No")

tasks_df_monthly_followup_by_chw_area = pd.read_csv("task_locations_monthly_followup_by_chw_id.csv")

tasks_df_monthly_followup = pd.read_csv("task_locations_monthly_followup.csv")
tasks_df_postnatal = pd.read_csv("task_locations_postnatal_followup.csv")
tasks_df_referral = pd.read_csv("task_locations_referral_followup.csv")
tasks_df_sputum = pd.read_csv("task_locations_sputum_collection.csv")
tasks_df_delivery = pd.read_csv("task_locations_delivery.csv")

world_map = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres')) # downloading the data set from 
malawi_map = world_map.query('iso_a3 == "MWI"') # selecting the Milawe area on the world data

#converting dataframe latlon to Point() object
households_geometry = [Point(xy) for xy in zip(households_df.longitude, households_df.latitude)]
chw_households_geometry = [Point(xy) for xy in zip(chw_households_df.longitude, chw_households_df.latitude)]
hospitals_geometry = [Point(xy) for xy in zip(hospitals_df.longitude, hospitals_df.latitude)]
tasks_geometry_monthly_followup_by_chw_area = [Point(xy) for xy in zip(tasks_df_monthly_followup_by_chw_area.longitude, tasks_df_monthly_followup_by_chw_area.latitude)]
tasks_geometry_monthly_followup = [Point(xy) for xy in zip(tasks_df_monthly_followup.lon, tasks_df_monthly_followup.lat)]
tasks_geometry_postnatal = [Point(xy) for xy in zip(tasks_df_postnatal.longitude, tasks_df_postnatal.latitude)]
tasks_geometry_referral = [Point(xy) for xy in zip(tasks_df_referral.longitude, tasks_df_referral.latitude)]
tasks_geometry_sputum = [Point(xy) for xy in zip(tasks_df_sputum.longitude, tasks_df_sputum.latitude)]
tasks_geometry_delivery = [Point(xy) for xy in zip(tasks_df_delivery.longitude, tasks_df_delivery.latitude)]

# geodataframes are basically just dataframes with coordinate systems for mapping
households_gdf = gpd.GeoDataFrame(
    households_df.drop(['longitude', 'latitude'], axis=1), 
    crs="EPSG:4326", geometry=households_geometry
).to_crs(malawi_map.crs)
households_gdf["type"] = 'Patient Household'

chw_households_gdf = gpd.GeoDataFrame(
    chw_households_df.drop(['longitude', 'latitude'], axis=1), 
    crs="EPSG:4326", geometry=chw_households_geometry
).to_crs(malawi_map.crs)
chw_households_gdf["type"] = 'CHW Household'

hospitals_gdf = gpd.GeoDataFrame(
    hospitals_df.drop(['longitude', 'latitude'], axis=1), 
    crs="EPSG:4326", geometry=hospitals_geometry
).to_crs(malawi_map.crs)

tasks_gdf_monthly_followup = gpd.GeoDataFrame(
    tasks_df_monthly_followup.drop(['lon', 'lat'], axis=1), 
    crs="EPSG:4326", geometry=tasks_geometry_monthly_followup
).to_crs(malawi_map.crs)
tasks_gdf_monthly_followup['geometry'] = tasks_gdf_monthly_followup.buffer(tasks_gdf_monthly_followup['count'].apply(lambda a: 0.0005 * (1 + a ** 0.5))) # scales each circular region by the count of monthly followups
tasks_gdf_monthly_followup['type'] = 'Monthly Follow-up Tasks'

tasks_gdf_monthly_followup_by_chw_area = gpd.GeoDataFrame(
    tasks_df_monthly_followup_by_chw_area.drop(['longitude', 'latitude'], axis=1), 
    crs="EPSG:4326", geometry=tasks_geometry_monthly_followup_by_chw_area
).to_crs(malawi_map.crs)
tasks_gdf_monthly_followup_by_chw_area['geometry'] = tasks_gdf_monthly_followup_by_chw_area.buffer(tasks_gdf_monthly_followup_by_chw_area['count'].apply(lambda a: 0.0005 * (1 + a ** 0.5)))
tasks_gdf_monthly_followup_by_chw_area['type'] = 'Chw Monthly Follow-up Tasks'

tasks_gdf_postnatal = gpd.GeoDataFrame(
    tasks_df_postnatal.drop(['longitude', 'latitude'], axis=1), 
    crs="EPSG:4326", geometry=tasks_geometry_postnatal
).to_crs(malawi_map.crs)
tasks_gdf_postnatal['geometry'] = tasks_gdf_postnatal.buffer(tasks_gdf_postnatal['count'].apply(lambda a: 0.0005 * (1 + a ** 0.5)))
tasks_gdf_postnatal['type'] = 'Postnatal Tasks'

tasks_gdf_referral = gpd.GeoDataFrame(
    tasks_df_referral.drop(['longitude', 'latitude'], axis=1), 
    crs="EPSG:4326", geometry=tasks_geometry_referral
).to_crs(malawi_map.crs)
tasks_gdf_referral['geometry'] = tasks_gdf_referral.buffer(tasks_gdf_referral['count'].apply(lambda a: 0.0005 * (1 + a ** 0.5)))
tasks_gdf_referral['type'] = 'Referral Tasks'

tasks_gdf_sputum = gpd.GeoDataFrame(
    tasks_df_sputum.drop(['longitude', 'latitude'], axis=1), 
    crs="EPSG:4326", geometry=tasks_geometry_sputum
).to_crs(malawi_map.crs)
tasks_gdf_sputum['geometry'] = tasks_gdf_sputum.buffer(tasks_gdf_sputum['count'].apply(lambda a: 0.0005 * (1 + a ** 0.5)))
tasks_gdf_sputum['type'] = 'Sputum Collection Tasks'

tasks_gdf_delivery = gpd.GeoDataFrame(
    tasks_df_delivery.drop(['longitude', 'latitude'], axis=1), 
    crs="EPSG:4326", geometry=tasks_geometry_delivery
).to_crs(malawi_map.crs)
tasks_gdf_delivery['geometry'] = tasks_gdf_delivery.buffer(tasks_gdf_delivery['count'].apply(lambda a: 0.0005 * (1 + a ** 0.5)))
tasks_gdf_delivery['type'] = 'Delivery Tasks'

#plots the dataframe onto the maps
m = tasks_gdf_monthly_followup.explore(
     column='family_id', #the column of the dataframe that we're plotting
     tooltip='type',
     popup=True,
     legend=False,
     style_kwds={'color':'red','fillColor':'red','fillOpacity':0.1} #the style of the datapoints
)
m = tasks_gdf_monthly_followup_by_chw_area.explore(
     m=m,
     column='chw_id',
     tooltip='type',
     popup=True,
     legend=False,
     style_kwds={'color':'blue','fillColor':'blue','fillOpacity':0.1}
)
m = tasks_gdf_postnatal.explore(
     m=m,
     column='reported_by',
     tooltip='type',
     popup=True,
     legend=False,
     style_kwds={'color':'green','fillColor':'green','fillOpacity':0.1}
)
m = tasks_gdf_referral.explore(
     m=m,
     column='reported_by',
     tooltip='type',
     popup=True,
     legend=False,
     style_kwds={'color':'purple','fillColor':'purple','fillOpacity':0.1}
)
m = tasks_gdf_sputum.explore(
     m=m,
     column='reported_by',
     tooltip='type',
     popup=True,
     legend=False,
     style_kwds={'color':'yellow','fillColor':'yellow','fillOpacity':0.1}
)
m = tasks_gdf_delivery.explore(
     m=m,
     column='reported_by',
     tooltip='type',
     popup=True,
     legend=False,
     style_kwds={'color':'orange','fillColor':'orange','fillOpacity':0.1}
)
m = chw_households_gdf.explore(
     m=m,
     column="chw_id", # make choropleth based on "BoroName" column
     tooltip=['type',"chw_id"], # show "BoroName" value in tooltip (on hover)
     popup=True, # show all values in popup (on click)
     #tiles="CartoDB positron", # use "CartoDB positron" tiles
     #cmap="Set1", # use "Set1" matplotlib colormap
     legend=False,
     style_kwds={'color':'gray','fillColor':'gray','fillOpacity':0.5}
)

m = households_gdf.explore(
     m=m,
     column="household_id", # make choropleth based on "BoroName" column
     tooltip=['type',"household_id"], # show "BoroName" value in tooltip (on hover)
     popup=True, # show all values in popup (on click)
     #tiles="CartoDB positron", # use "CartoDB positron" tiles
     #cmap="Set1", # use "Set1" matplotlib colormap
     legend=False,
     marker_type="circle",
     style_kwds={'color':'black','fillColor':'black','fillOpacity':0.5}
)
m = hospitals_gdf.explore(
     m=m,
     column='NAME',
     tooltip=['NAME','TYPE'],
     popup=True,
     cmap="Set1",
     legend=False,
     marker_type='marker'
)
combined = households_gdf.append(chw_households_gdf)
combined['geometry'] = combined.buffer(combined['type'].apply(lambda a: 0.0004 if a == 'CHW Household' else 0.0001))
combined = combined.sort_values('chw_id')

n = combined[:1500].explore( #only extracted a subset of the data
     column="chw_id", # make choropleth based on column
     tooltip=['type',"chw_id"], # show value in tooltip (on hover)
     popup=True, # show all values in popup (on click)
     #tiles="CartoDB positron", # use "CartoDB positron" tiles
     highlight=False,
     cmap="Set1", # use "Set1" matplotlib colormap
     style_kwds={'fillOpacity':1},
     legend=False
)
m3 = households_gdf.explore(
     column="household_id", # make choropleth based on "BoroName" column
     tooltip=['type',"household_id"], # show "BoroName" value in tooltip (on hover)
     popup=True, # show all values in popup (on click)
     #tiles="CartoDB positron", # use "CartoDB positron" tiles
     #cmap="Set1", # use "Set1" matplotlib colormap
     legend=False,
     marker_type="circle",
     style_kwds={'color':'black','fillColor':'black','fillOpacity':0.5}
)
m3 = chw_households_gdf.explore(
     m=m3,
     column="chw_id", # make choropleth based on "BoroName" column
     tooltip=['type',"chw_id"], # show "BoroName" value in tooltip (on hover)
     popup=True, # show all values in popup (on click)
     #tiles="CartoDB positron", # use "CartoDB positron" tiles
     #cmap="Set1", # use "Set1" matplotlib colormap
     legend=False,
     style_kwds={'color':'red','fillColor':'red','fillOpacity':0.5}
)
m3 = hospitals_gdf.explore(
     m=m3,
     column='NAME',
     tooltip=['NAME','TYPE'],
     popup=True,
     cmap="Set1",
     legend=False,
     marker_type='marker'
)
