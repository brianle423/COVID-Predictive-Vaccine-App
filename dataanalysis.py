# importing the goods
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from sklearn.linear_model import LinearRegression
# import scipy
# from scipy import stats
# from shapely.geometry import LineString, Pointß

import warnings
import datetime
from datetime import date

# Plotly
import plotly.express as px
# import ptly.io as pio
# import json

warnings.filterwarnings('ignore')

vaccine_df = pd.read_csv('/Users/Dev/Desktop/My_Apps/School_Stuff/AP_CSP/country_vaccinations.csv')

# %%
# Missing Data
vaccine_df = vaccine_df.drop(['source_website', 'source_name'], axis=1)

# total_vaccinations and people_vaccinated
vaccine_df = vaccine_df.drop(vaccine_df[vaccine_df['total_vaccinations'].isna()].index)
check_vaccine = vaccine_df.drop(vaccine_df[vaccine_df['people_vaccinated'].isna()].index)

# people_vaccinated and people_vaccinated_per_hundred
# plt.subplots(figsize=(8,8))
# sns.heatmap(check_vaccine.corr(), annot=True, square=True)
# print(scipy.stats.mannwhitneyu(check_vaccine['total_vaccinations'], check_vaccine['people_vaccinated'], alternative='two-sided'))
# print(scipy.stats.mannwhitneyu(check_vaccine['total_vaccinations_per_hundred'], check_vaccine['people_vaccinated_per_hundred'], alternative='two-sided'))

mean = check_vaccine['total_vaccinations'].mean() - check_vaccine['people_vaccinated'].mean()
mean_per_hundred = check_vaccine['total_vaccinations_per_hundred'].mean() - check_vaccine[
    'people_vaccinated_per_hundred'].mean()
vaccine_df['people_vaccinated'] = vaccine_df['people_vaccinated'].fillna(vaccine_df['total_vaccinations'] - mean)
vaccine_df['people_vaccinated_per_hundred'] = vaccine_df['people_vaccinated_per_hundred'].fillna(
    vaccine_df['total_vaccinations_per_hundred'] - mean_per_hundred)
# print(vaccine_df.isna().sum())

# daily_vaccinations and daily_vaccinations_per_million

vaccine_df['daily_vaccinations'] = vaccine_df['daily_vaccinations'].fillna(0)
vaccine_df['daily_vaccinations_per_million'] = vaccine_df['daily_vaccinations_per_million'].fillna(0)

# print(vaccine_df.isna().sum())

# people_fully_vaccinated and people_fully_vaccinated_per_hundred
vaccine_df['people_fully_vaccinated'] = vaccine_df['people_fully_vaccinated'].fillna(0)
vaccine_df['people_fully_vaccinated_per_hundred'] = vaccine_df['people_fully_vaccinated_per_hundred'].fillna(0)

# daily_vaccinations_raw
vaccine_df['daily_vaccinations_raw'] = vaccine_df['daily_vaccinations_raw'].fillna(0)
# print(vaccine_df.isna().sum())

# negative vaccine numbers
vaccine_df = vaccine_df.drop(vaccine_df[vaccine_df['people_vaccinated'] < 0].index)

# %%
# EDA

# selecting lastest vaccine numbers
# latest_num = vaccine_df.groupby(['country', 'iso_code']).people_vaccinated.max().reset_index()
#
# latest_sorted = latest_num.sort_values('people_vaccinated')
# top_countries = latest_sorted[-20:]
#
# fig, ax = plt.subplots()
# ax.barh(top_countries['country'], top_countries['people_vaccinated'])
# plt.xticks(rotation=30)
# plt.ylabel('Countries')
# plt.xlabel('Number of Vaccinated Citizens (Hundred Millions)')
# plt.title('Top 20 Vaccinated Countries')

# World Map

# latest_num['people_vaccinated_scale'] = np.log10(latest_num['people_vaccinated'])

# pio.renderers.default = 'chrome'
# fig = px.choropleth(latest_num,
#                     locations='iso_code',
#                     color='people_vaccinated_scale',
#                     hover_name='country',
#                     hover_data=['people_vaccinated'],
#                     title='People Vaccinated Per Country',
#                     labels={'people_vaccinated_scale': 'People Vaccinated Scaled ',
#                             'people_vaccinated': 'Number of People Vaccinated ',
#                             'iso_code': 'Code '},
#                     color_continuous_scale='Oranges'
#                     )
# fig.show()

# %%
# Cleaning Population Dataset
pop_df = pd.read_csv('/Users/Dev/Desktop/My_Apps/School_Stuff/AP_CSP/population_by_country_2020.csv')
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

# %%
# More EDA

# latest_rate = vaccine_pop.groupby(['country', 'iso_code']).vaccine_rate.max().reset_index()
# rate_sorted = latest_rate.sort_values('vaccine_rate')
# top_country_rate = rate_sorted[-20:]
#
# # Bar Chart By Vaccine Percentage
# fig, ax = plt.subplots()
# ax.barh(top_country_rate['country'], top_country_rate['vaccine_rate'], color='orange')
# plt.ylabel('Countries')
# plt.xlabel('Percentage of Vaccinated Citizens')
# plt.title('Top 20 Vaccinated Countries By Percentage')

# World Map By Vaccine Percentage
# pio.renderers.default = 'chrome'
# fig = px.choropleth(latest_rate,
#                     locations='iso_code',
#                     color='vaccine_rate',
#                     hover_name='country',
#                     hover_data=['vaccine_rate'],
#                     title='Percentage of People Vaccinated Per Country',
#                     labels={'vaccine_rate_scale': 'Percentage of People Vaccinated Scaled ',
#                             'vaccine_rate': 'Percentage of People Vaccinated ',
#                             'iso_code': 'Code ', },
#                     color_continuous_scale='Reds'
#                     )
# fig.show()

# %%
# Tracking And Predicting Vaccination Progress

# Organizing Date
vaccine_pop['date'] = pd.to_datetime(vaccine_pop['date'], format='%Y-%m-%d')
vaccine_pop['date_ordinal'] = pd.to_datetime(vaccine_pop['date']).apply(lambda date: date.toordinal())

most_dates = vaccine_pop.groupby(['country']).date.count().sort_values(ascending=False).reset_index()
most_data = vaccine_pop.groupby(['country']).people_fully_vaccinated.count().sort_values(ascending=False).reset_index()


# Linear Regression

def vaccineDate(country, full):
    country_rows = vaccine_pop[vaccine_pop['country'] == country]

    x_values = country_rows[['date_ordinal']]

    if full == 2:
        y_values = country_rows[['full_vaccine_rate']]
    else:
        y_values = country_rows[['vaccine_rate']]

    fig, ax = plt.subplots()
    ax.scatter(x_values, y_values, label='Real Vaccine Data')

    line_fitter = LinearRegression()
    line_fitter.fit(x_values, y_values)
    predicted_vaccine_rate = line_fitter.predict(x_values)
    r2_score = line_fitter.score(x_values, y_values)
    ax.plot(x_values, predicted_vaccine_rate, 'orange', label='Current Vaccine Progress')

    ax.grid('both')
    ax.set_xlabel('Date')
    ax.set_ylabel('Percentage of Population Vaccinated')
    ax.set_title('Prediction for ' + country + '\'s Vaccine Progress')
    ax.set_ylim([0, 100])

    # Predicting When Country Will Be 100% Vaccinated

    first_date = country_rows.loc[country_rows.index[0], 'date_ordinal']
    latest_date = country_rows.loc[country_rows.index[-1], 'date_ordinal']
    xrange = int(100 / line_fitter.coef_)
    predicted_date = latest_date + xrange

    future_x = np.arange(latest_date, predicted_date).reshape(-1, 1)
    future_y = line_fitter.predict(future_x)

    ax.plot(future_x, future_y, '--', color='#f24e35', label='Future Vaccine Progress')
    ax.set_xlim([first_date, predicted_date])
    new_labels = [date.fromordinal(int(item)) for item in ax.get_xticks()]
    ax.set_xticklabels(new_labels, rotation=30)
    ax.legend(loc='lower right')

    x = np.arange(latest_date, predicted_date)
    df_future_y = (pd.DataFrame(future_y, columns=['y']))
    y_upper = [i * ((1 - r2_score) + 1) for i in df_future_y['y']]
    y_lower = [i * r2_score for i in df_future_y['y']]
    ax.fill_between(x, y_lower, y_upper, alpha=0.2)

    over_hundred = future_x[future_y > 100]
    first_hundred = datetime.datetime.fromordinal(over_hundred[0])
    current_date = datetime.datetime.now()
    time_til_hundred = first_hundred - current_date

    print('Model Accuracy: {:.2%}'.format(r2_score))
    print('Time until ' + country + ' is fully vaccinated: ', time_til_hundred)
    print('Estimated Date: ' + str(first_hundred))
    plt.savefig('country.png', dpi=1500)

