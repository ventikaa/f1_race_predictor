
import pandas as pd
import numpy as np
import requests

# query API

races = {'season': [],
        'round': [],
        'circuit_id': [],
        'lat': [],
        'long': [],
        'country': [],
        'date': [],
        'url': []}

for year in list(range(1950,2020)):
    
    url = 'https://ergast.com/api/f1/{}.json'
    r = requests.get(url.format(year))
    json = r.json()

    for item in json['MRData']['RaceTable']['Races']:
        try:
            races['season'].append(int(item['season']))
        except:
            races['season'].append(None)

        try:
            races['round'].append(int(item['round']))
        except:
            races['round'].append(None)

        try:
            races['circuit_id'].append(item['Circuit']['circuitId'])
        except:
            races['circuit_id'].append(None)

        try:
            races['lat'].append(float(item['Circuit']['Location']['lat']))
        except:
            races['lat'].append(None)

        try:
            races['long'].append(float(item['Circuit']['Location']['long']))
        except:
            races['long'].append(None)

        try:
            races['country'].append(item['Circuit']['Location']['country'])
        except:
            races['country'].append(None)

        try:
            races['date'].append(item['date'])
        except:
            races['date'].append(None)

        try:
            races['url'].append(item['url'])
        except:
            races['url'].append(None)
        
races = pd.DataFrame(races)

# append the number of rounds to each season from the races_df

rounds = []
for year in np.array(race.season.unique()):
    rounds.append([year, list(race[race.season == year]['round'])])

# query API
    
results = {'season': [],
          'round':[],
           'circuit_id':[],
          'driver': [],
           'date_of_birth': [],
           'nationality': [],
          'constructor': [],
          'grid': [],
          'time': [],
          'status': [],
          'points': [],
          'podium': []}

for n in list(range(len(rounds))):
    for i in rounds[n][1]:
    
        url = 'http://ergast.com/api/f1/{}/{}/results.json'
        r = requests.get(url.format(rounds[n][0], i))
        json = r.json()

        for item in json['MRData']['RaceTable']['Races'][0]['Results']:
            try:
                results['season'].append(int(json['MRData']['RaceTable']['Races'][0]['season']))
            except:
                results['season'].append(None)

            try:
                results['round'].append(int(json['MRData']['RaceTable']['Races'][0]['round']))
            except:
                results['round'].append(None)

            try:
                results['circuit_id'].append(json['MRData']['RaceTable']['Races'][0]['Circuit']['circuitId'])
            except:
                results['circuit_id'].append(None)

            try:
                results['driver'].append(item['Driver']['driverId'])
            except:
                results['driver'].append(None)
            
            try:
                results['date_of_birth'].append(item['Driver']['dateOfBirth'])
            except:
                results['date_of_birth'].append(None)
                
            try:
                results['nationality'].append(item['Driver']['nationality'])
            except:
                results['nationality'].append(None)

            try:
                results['constructor'].append(item['Constructor']['constructorId'])
            except:
                results['constructor'].append(None)

            try:
                results['grid'].append(int(item['grid']))
            except:
                results['grid'].append(None)

            try:
                results['time'].append(int(item['Time']['millis']))
            except:
                results['time'].append(None)

            try:
                results['status'].append(item['status'])
            except:
                results['status'].append(None)

            try:
                results['points'].append(int(item['points']))
            except:
                results['points'].append(None)

            try:
                results['podium'].append(int(item['position']))
            except:
                results['podium'].append(None)

           
results = pd.DataFrame(results)

driver_standings = {'season': [],
                    'round':[],
                    'driver': [],
                    'driver_points': [],
                    'driver_wins': [],
                   'driver_standings_pos': []}

# query API

for n in list(range(len(rounds))):     
    for i in rounds[n][1]:    # iterate through rounds of each year
    
        url = 'https://ergast.com/api/f1/{}/{}/driverStandings.json'
        r = requests.get(url.format(rounds[n][0], i))
        json = r.json()

        for item in json['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']:
            try:
                driver_standings['season'].append(int(json['MRData']['StandingsTable']['StandingsLists'][0]['season']))
            except:
                driver_standings['season'].append(None)

            try:
                driver_standings['round'].append(int(json['MRData']['StandingsTable']['StandingsLists'][0]['round']))
            except:
                driver_standings['round'].append(None)
                                         
            try:
                driver_standings['driver'].append(item['Driver']['driverId'])
            except:
                driver_standings['driver'].append(None)
            
            try:
                driver_standings['driver_points'].append(int(item['points']))
            except:
                driver_standings['driver_points'].append(None)
            
            try:
                driver_standings['driver_wins'].append(int(item['wins']))
            except:
                driver_standings['driver_wins'].append(None)
                
            try:
                driver_standings['driver_standings_pos'].append(int(item['position']))
            except:
                driver_standings['driver_standings_pos'].append(None)
            
driver_standings = pd.DataFrame(driver_standings)

# define lookup function to shift points and number of wins from previous rounds

def lookup (df, team, points):
    df['lookup1'] = df.season.astype(str) + df[team] + df['round'].astype(str)
    df['lookup2'] = df.season.astype(str) + df[team] + (df['round']-1).astype(str)
    new_df = df.merge(df[['lookup1', points]], how = 'left', left_on='lookup2',right_on='lookup1')
    new_df.drop(['lookup1_x', 'lookup2', 'lookup1_y'], axis = 1, inplace = True)
    new_df.rename(columns = {points+'_x': points+'_after_race', points+'_y': points}, inplace = True)
    new_df[points].fillna(0, inplace = True)
    return new_df
  
driver_standings = lookup(driver_standings, 'driver', 'driver_points')
driver_standings = lookup(driver_standings, 'driver', 'driver_wins')
driver_standings = lookup(driver_standings, 'driver', 'driver_standings_pos')

driver_standings.drop(['driver_points_after_race', 'driver_wins_after_race', 'driver_standings_pos_after_race'], 
                      axis = 1, inplace = True)

# start from year 1958

constructor_rounds = rounds[8:]

constructor_standings = {'season': [],
                    'round':[],
                    'constructor': [],
                    'constructor_points': [],
                    'constructor_wins': [],
                   'constructor_standings_pos': []}
# query API

for n in list(range(len(constructor_rounds))):
    for i in constructor_rounds[n][1]:
    
        url = 'https://ergast.com/api/f1/{}/{}/constructorStandings.json'
        r = requests.get(url.format(constructor_rounds[n][0], i))
        json = r.json()

        for item in json['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']:
            try:
                constructor_standings['season'].append(int(json['MRData']['StandingsTable']['StandingsLists'][0]['season']))
            except:
                constructor_standings['season'].append(None)

            try:
                constructor_standings['round'].append(int(json['MRData']['StandingsTable']['StandingsLists'][0]['round']))
            except:
                constructor_standings['round'].append(None)
                                         
            try:
                constructor_standings['constructor'].append(item['Constructor']['constructorId'])
            except:
                constructor_standings['constructor'].append(None)
            
            try:
                constructor_standings['constructor_points'].append(int(item['points']))
            except:
                constructor_standings['constructor_points'].append(None)
            
            try:
                constructor_standings['constructor_wins'].append(int(item['wins']))
            except:
                constructor_standings['constructor_wins'].append(None)
                
            try:
                constructor_standings['constructor_standings_pos'].append(int(item['position']))
            except:
                constructor_standings['constructor_standings_pos'].append(None)
            
constructor_standings = pd.DataFrame(constructor_standings)

constructor_standings = lookup(constructor_standings, 'constructor', 'constructor_points')
constructor_standings = lookup(constructor_standings, 'constructor', 'constructor_wins')
constructor_standings = lookup(constructor_standings, 'constructor', 'constructor_standings_pos')

constructor_standings.drop(['constructor_points_after_race', 'constructor_wins_after_race','constructor_standings_pos_after_race' ],
                           axis = 1, inplace = True)

import bs4
from bs4 import BeautifulSoup

qualifying_results = pd.DataFrame()

# Qualifying times are only available from 1983

for year in list(range(1983,2020)):
    url = 'https://www.formula1.com/en/results.html/{}/races.html'
    r = requests.get(url.format(year))
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # find links to all circuits for a certain year
    
    year_links = []
    for page in soup.find_all('a', attrs = {'class':"resultsarchive-filter-item-link FilterTrigger"}):
        link = page.get('href')
        if f'/en/results.html/{year}/races/' in link: 
            year_links.append(link)
    
    # for each circuit, switch to the starting grid page and read table

    year_df = pd.DataFrame()
    new_url = 'https://www.formula1.com{}'
    for n, link in list(enumerate(year_links)):
        link = link.replace('race-result.html', 'starting-grid.html')
        df = pd.read_html(new_url.format(link))
        df = df[0]
        df['season'] = year
        df['round'] = n+1
        for col in df:
            if 'Unnamed' in col:
                df.drop(col, axis = 1, inplace = True)

        year_df = pd.concat([year_df, df])

    # concatenate all tables from all years  
        
    qualifying_results = pd.concat([qualifying_results, year_df])

# rename columns
    
qualifying_results.rename(columns = {'Pos': 'grid', 'Driver': 'driver_name', 'Car': 'car',
                                     'Time': 'qualifying_time'}, inplace = True)
# drop driver number column

qualifying_results.drop('No', axis = 1, inplace = True)
    

from selenium import webdriver

weather = races.iloc[:,[0,1,2]]

info = []

# read wikipedia tables

for link in races.url:
    try:
        df = pd.read_html(link)[0]
        if 'Weather' in list(df.iloc[:,0]):
            n = list(df.iloc[:,0]).index('Weather')
            info.append(df.iloc[n,1])
        else:
            df = pd.read_html(link)[1]
            if 'Weather' in list(df.iloc[:,0]):
                n = list(df.iloc[:,0]).index('Weather')
                info.append(df.iloc[n,1])
            else:
                df = pd.read_html(link)[2]
                if 'Weather' in list(df.iloc[:,0]):
                    n = list(df.iloc[:,0]).index('Weather')
                    info.append(df.iloc[n,1])
                else:
                    df = pd.read_html(link)[3]
                    if 'Weather' in list(df.iloc[:,0]):
                        n = list(df.iloc[:,0]).index('Weather')
                        info.append(df.iloc[n,1])
                    else:
                        driver = webdriver.Chrome()
                        driver.get(link)

                        # click language button
                        button = driver.find_element_by_link_text('Italiano')
                        button.click()
                        
                        # find weather in italian with selenium
                        
                        clima = driver.find_element_by_xpath('//*[@id="mw-content-text"]/div/table[1]/tbody/tr[9]/td').text
                        info.append(clima) 
                                
    except:
        info.append('not found')

# append column with weather information to dataframe  
  
weather['weather'] = info

# set up a dictionary to convert weather information into keywords

weather_dict = {'weather_warm': ['soleggiato', 'clear', 'warm', 'hot', 'sunny', 'fine', 'mild', 'sereno'],
               'weather_cold': ['cold', 'fresh', 'chilly', 'cool'],
               'weather_dry': ['dry', 'asciutto'],
               'weather_wet': ['showers', 'wet', 'rain', 'pioggia', 'damp', 'thunderstorms', 'rainy'],
               'weather_cloudy': ['overcast', 'nuvoloso', 'clouds', 'cloudy', 'grey', 'coperto']}

# map new df according to weather dictionary

weather_df = pd.DataFrame(columns = weather_dict.keys())
for col in weather_df:
    weather_df[col] = weather['weather'].map(lambda x: 1 if any(i in weather_dict[col] for i in x.lower().split()) else 0)
   
weather_info = pd.concat([weather, weather_df], axis = 1)
