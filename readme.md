# Budgeting App with Kivy

This is a small desktop application written in Python 3 and KivyMD
that tracks your spending.

This application was tested using github.com/kivymd/KivyMD commit f995f8e

## Install Guide

`pip install pandas matplotlib`
`pip install https://github.com/kivymd/KivyMD/archive/f995f8e.zip`
`pip install kivy-garden`
`garden install matplotlib`

## Running the App

Run the app with the following command:
`python app.py`

This app works best with mobile screen sizes.
As an example, using the screen of a Samsung Galaxy S6:

`python app.py -m screen:phone_samsung_galaxy_s6,portrait,scale=0.25`

## Provide the Data

Go to the online banking portal of your bank, download the CSV file of your transactions, and place it within the "data" folder.

## To-Do

### General
- Set homescreen metrics to display data only for current month✅
- Find and choose metrics to display
- Design best method of presenting the metrics
- Functionality to import csv files manually
- Add input csv files into a principal SQL database
- Solve conflicts between new and existing data for overlaping timestamps
- Fix global theme

## Overview Tab
- Copy top app bar with date selector here
- Present metrics for this month using grid of cards, scrollview, and donut/line plots

### Data Tab
- Selecting date displays list of transactions and money spent✅
- Add elevation to region where total money spent is shown