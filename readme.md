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