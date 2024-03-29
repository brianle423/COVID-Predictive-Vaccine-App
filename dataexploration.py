#######################################################################################################################
#
#   dataanalysis.py
#
#
#   Description:
#   This code cleans and analyzes global vaccination data to produce a model that predicts a selected country's
#   vaccine progress and outputs when a country will be 100 percent vaccinated. Developed collaboratively with a partner,
#   I worked on cleaning the data and created the vaccineDate model to generate a graph that predicts a country's
#   vaccination progress, while my partner coded the app.
#
#   Inputs: Country and Doses
#   Outputs: {country}-{doses}.png (Image of graph produced from model)
#
#
#######################################################################################################################
# %% Importing Modules

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.linear_model import LinearRegression
import warnings
import datetime
from datetime import date

# Plotly
import plotly.express as px
import plotly.io as pio

warnings.filterwarnings('ignore')

# Importing Dataset
vaccine_df = pd.read_csv('/Users/Brian/PycharmProjects/CreateTask/vaccinedata/country_vaccinations.csv')
# %% Missing Data
vaccine_df = vaccine_df.drop(['source_website', 'source_name'], axis=1)

# total_vaccinations and people_vaccinated
vaccine_df = vaccine_df.drop(vaccine_df[vaccine_df['total_vaccinations'].isna()].index)
check_vaccine = vaccine_df.drop(vaccine_df[vaccine_df['people_vaccinated'].isna()].index)

mean = check_vaccine['total_vaccinations'].mean() - check_vaccine['people_vaccinated'].mean()
mean_per_hundred = check_vaccine['total_vaccinations_per_hundred'].mean() - check_vaccine[
    'people_vaccinated_per_hundred'].mean()
vaccine_df['people_vaccinated'] = vaccine_df['people_vaccinated'].fillna(vaccine_df['total_vaccinations'] - mean)
vaccine_df['people_vaccinated_per_hundred'] = vaccine_df['people_vaccinated_per_hundred'].fillna(
    vaccine_df['total_vaccinations_per_hundred'] - mean_per_hundred)

# daily_vaccinations and daily_vaccinations_per_million

vaccine_df['daily_vaccinations'] = vaccine_df['daily_vaccinations'].fillna(0)
vaccine_df['daily_vaccinations_per_million'] = vaccine_df['daily_vaccinations_per_million'].fillna(0)

# people_fully_vaccinated and people_fully_vaccinated_per_hundred
vaccine_df['people_fully_vaccinated'] = vaccine_df['people_fully_vaccinated'].fillna(0)
vaccine_df['people_fully_vaccinated_per_hundred'] = vaccine_df['people_fully_vaccinated_per_hundred'].fillna(0)

# daily_vaccinations_raw
vaccine_df['daily_vaccinations_raw'] = vaccine_df['daily_vaccinations_raw'].fillna(0)
# print(vaccine_df.isna().sum())

# negative vaccine numbers
vaccine_df = vaccine_df.drop(vaccine_df[vaccine_df['people_vaccinated'] < 0].index)

# %%
# Cleaning Population Dataset
pop_df = pd.read_csv('/Users/Brian/PycharmProjects/CreateTask/population_by_country_2020.csv')
pop_df.rename(columns={
    'Country (or dependency)': 'country',
    'Population (2020)': 'population',
    'World Share': 'world_share'},
    inplace=True)
pop_df = pop_df[['country', 'population', 'world_share']]

# Finding Percentage of Population Vaccinated
world_vaccinated = vaccine_df[['country', 'iso_code', 'date', 'people_vaccinated', 'people_fully_vaccinated']]
vaccine_pop = pd.merge(pop_df, world_vaccinated)
# Vaccine Rate Variables
vaccine_pop['vaccine_rate'] = (vaccine_pop['people_vaccinated'] / vaccine_pop['population']) * 100
vaccine_pop['full_vaccine_rate'] = (vaccine_pop['people_fully_vaccinated'] / vaccine_pop['population']) * 100

# %% More EDA
'''
latest_rate = vaccine_pop.groupby(['country', 'iso_code']).vaccine_rate.max().reset_index()
rate_sorted = latest_rate.sort_values('vaccine_rate')
top_country_rate = rate_sorted[-20:]

# Bar Chart By Vaccine Percentage
fig, ax = plt.subplots()
ax.barh(top_country_rate['country'], top_country_rate['vaccine_rate'], color='orange')
plt.ylabel('Countries')
plt.xlabel('Percentage of Vaccinated Citizens')
plt.title('Top 20 Vaccinated Countries By Percentage')

# World Map By Vaccine Percentage
pio.renderers.default = 'chrome'
fig = px.choropleth(latest_rate,
                    locations='iso_code',
                    color='vaccine_rate',
                    hover_name='country',
                    hover_data=['vaccine_rate'],
                    title='Percentage of People Vaccinated Per Country',
                    labels={'vaccine_rate_scale': 'Percentage of People Vaccinated Scaled ',
                            'vaccine_rate': 'Percentage of People Vaccinated ',
                            'iso_code': 'Code ', },
                    color_continuous_scale='Reds'
                    )
fig.show()'''

# %% Tracking And Predicting Vaccination Progress

# Organizing Date
vaccine_pop['date'] = pd.to_datetime(vaccine_pop['date'], format='%Y-%m-%d')
vaccine_pop['date_ordinal'] = pd.to_datetime(vaccine_pop['date']).apply(lambda date: date.toordinal())

# Sorting Countries by Population for Dropdown Menu
most_population = vaccine_pop.groupby(['country']).population.max().sort_values(ascending=False).reset_index()


# Vaccine Function

def vaccineDate(country, doses):
    # Selecting X and Y values based on parameters
    country_rows = vaccine_pop[vaccine_pop['country'] == country]

    x_values = country_rows[['date_ordinal']]

    if doses == '2':
        y_values = country_rows[['full_vaccine_rate']]
    else:
        y_values = country_rows[['vaccine_rate']]

    fig, ax = plt.subplots()
    ax.scatter(x_values, y_values, label='Real Vaccine Data')

    # Linear Regression Model

    line_fitter = LinearRegression()
    line_fitter.fit(x_values, y_values)
    predicted_vaccine_rate = line_fitter.predict(x_values)
    r2_score = line_fitter.score(x_values, y_values)

    # Graphing Original Vaccine Data and Model

    ax.plot(x_values, predicted_vaccine_rate, 'orange', label='Current Vaccine Progress')
    ax.grid('both')
    ax.set_xlabel('Date')
    ax.set_ylabel('Percentage of Population Vaccinated')
    ax.set_title('Prediction for ' + country + '\'s Vaccine Progress')
    ax.set_ylim([0, 100])
    sns.despine(left=True, bottom=True)

    # Predicting When Country Will Be 100% Vaccinated

    first_date = country_rows.loc[country_rows.index[0], 'date_ordinal']
    latest_date = country_rows.loc[country_rows.index[-1], 'date_ordinal']
    xrange = int(100 / line_fitter.coef_)
    predicted_date = latest_date + xrange

    # Predicting Future Values
    future_x = np.arange(latest_date, predicted_date).reshape(-1, 1)
    future_y = line_fitter.predict(future_x)

    # Fixing graph to update boundaries
    future_progress = ax.plot(future_x, future_y, '--', color='#f24e35')
    ax.set_xlim([first_date, predicted_date])
    new_labels = [date.fromordinal(int(item)) for item in ax.get_xticks()]
    ax.set_xticklabels(new_labels, rotation=15)
    ax.legend(loc='lower right', frameon=False)

    x = np.arange(latest_date, predicted_date)
    df_future_y = (pd.DataFrame(future_y, columns=['y']))
    y_upper = [i * ((1 - r2_score) + 1) for i in df_future_y['y']]
    y_lower = [i * r2_score for i in df_future_y['y']]
    ax.fill_between(x, y_lower, y_upper, alpha=0.2)

    # Finding when model reaches 100% vaccinated
    over_hundred = future_x[future_y > 100]
    first_hundred = datetime.datetime.fromordinal(over_hundred[0])
    first_hundred_str = str(first_hundred)
    first_hundred_split = first_hundred_str.split()
    first_hundred_date = first_hundred_split[0]

    current_date = datetime.datetime.now()
    time_til_hundred = str((first_hundred - current_date))
    num, day, tail = time_til_hundred.partition('days')
    day_til_hundred = num + day

    from matplotlib.legend import Legend
    results = Legend(ax, future_progress, [
        'Model Accuracy: {:.2%} \nTime until fully vaccinated with {doses} dose(s): {} \nEstimated Date: {first_hundred_date}'.format(
            r2_score, day_til_hundred, doses=doses, first_hundred_date=first_hundred_date)], loc='upper left',
                     frameon=False)
    ax.add_artist(results)

    print('Model Accuracy: {:.2%}'.format(r2_score))
    print(f'Time until {country} is fully vaccinated: {time_til_hundred}')
    print('Estimated Date: ' + str(first_hundred))

    # Save figure for display
    plt.savefig(f'{country}-{doses}.png', dpi=500)


vaccineDate('United States', 1)

# %% EDA
'''
#selecting lastest vaccine numbers
latest_num = vaccine_df.groupby(['country','iso_code']).people_vaccinated.max().reset_index()

latest_sorted = latest_num.sort_values('people_vaccinated')
top_countries = latest_sorted[-20:]

fig, ax = plt.subplots()
ax.barh(top_countries['country'], top_countries['people_vaccinated'])
plt.xticks(rotation=30)
plt.ylabel('Countries')
plt.xlabel('Number of Vaccinated Citizens (Hundred Millions)')
plt.title('Top 20 Vaccinated Countries')

#World Map

latest_num['people_vaccinated_scale'] = np.log10(latest_num['people_vaccinated'])

pio.renderers.default = 'chrome'
fig = px.choropleth(latest_num, 
              locations='iso_code',  
              color = 'people_vaccinated_scale',
              hover_name = 'country',
              hover_data = ['people_vaccinated'],
              title = 'People Vaccinated Per Country',
              labels = {'people_vaccinated_scale': 'People Vaccinated Scaled ',
                        'people_vaccinated': 'Number of People Vaccinated ',
                        'iso_code': 'Code '},
              color_continuous_scale = 'Oranges'
              )
fig.show()'''
