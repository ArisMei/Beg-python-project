import pandas as pd # For data manipulation
import geopandas # For map visualization
import folium # For map visualization
import pycountry # For inconsistent country names

# Create a dictionary of inconsistent country names and their standardized names
country_dict = {}
for country in pycountry.countries:
    country_dict[country.name] = country.name
    country_dict[country.alpha_2] = country.name
    country_dict[country.alpha_3] = country.name


# Clean Global land temperature dataset
df = pd.read_csv('data\land-data\GlobalLandTemperaturesByCountry.csv')
df.dt = pd.to_datetime(df.dt)
df.dt = df.dt.dt.year
df.rename(columns={"dt": "Year"}, inplace=True)
df_year_temp =df.groupby(['Country', 'Year']).mean()
df_year_temp.drop(columns=['AverageTemperatureUncertainty'], inplace=True)
df_year_temp.reset_index(inplace=True)


# Clean and merge GDP dataset
df_gdp = pd.read_csv('data\gdp-data\GDP_Country.csv', skiprows=4)

## Drop unnecessary columns
df_gdp.drop(columns=['Country Code', 'Indicator Name', 'Indicator Code','Unnamed: 66'], inplace=True)
df_gdp.rename(columns={"Country Name": "Country"}, inplace=True)

df_gdp = df_gdp.melt(id_vars=['Country'], var_name='Year', value_name='GDP')

## Order by country name
df_gdp.sort_values(by=['Country'], inplace=True)


# Merge datasets by country and year
df_year_temp['Year'] = df_year_temp['Year'].astype(int)
df_gdp['Year'] = df_gdp['Year'].astype(int)
df_merged = df_year_temp.merge(df_gdp, on=['Country', 'Year'], how='inner')

# Clean and merge population dataset
df_pop = pd.read_csv('data\population-data\population_data.csv', skiprows=4)

## Drop unnecessary columns
df_pop.drop(columns=['Country Code', 'Indicator Name', 'Indicator Code','Unnamed: 66'], inplace=True)

## Rename columns
df_pop.rename(columns={"Country Name": "Country"}, inplace=True)

df_pop = df_pop.melt(id_vars=['Country'], var_name='Year', value_name='Population')

## Order by country name
df_pop.sort_values(by=['Country'], inplace=True)

# Merge datasets by country and year
df_pop['Year'] = df_pop['Year'].astype(int)

df_merged = df_merged.merge(df_pop, on=['Country', 'Year'], how='inner')

# Save merge dataset in clean-data folder
df_merged.to_csv('data\clean-data\merged_data.csv', index=False)

# Plot 2010 Average temperature values in a map
df_2000 = pd.DataFrame(df_merged[df_merged.Year == 2000])
df_2000.drop(columns = ["Population", "AverageTemperature"], inplace=True)

## import geopandas dataset for map
world = geopandas.read_file(geopandas.datasets.get_path("naturalearth_lowres"))
print(world.head())

data_map = world.merge(df_2000, how = "left", left_on=["name"], right_on=["Country"])

my_map = folium.Map()

folium.Choropleth(
    geo_data=data_map,
    name='choropleth',
    data=data_map,
    columns=['Country', 'GDP'],
    key_on='feature.properties.name',
    fill_color='OrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Población del mundo a tope'

).add_to(my_map)

my_map.save('gdp.html')

## Los valores del mapa seguramente estén mal, hay que mirar que salen bien los datos y si existe una 
## librería que pueda juntar bien los nombres de los países