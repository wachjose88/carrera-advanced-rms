# Advanced Race Management for Carrera Digital

This is an advanced race management for Carrera Digital implemented in python. 

## Install and Run

To install the RMS at first the requirements have to be installed:

    pip install -r requirements.txt

Now you can run the RMS by the following commands: 

    cd rms
    python main.py -cu CUADDRESS

CUADDRESS should be replaced by the adress of your Carrera Control Unit. This could be a bluetooth address or a serial port.

## Screenshots

![Homescreen](/screenshots/home.png)

![Racemode](/screenshots/race.png)

## Web Statistic

It is possible to upload the data to a web app in order to view different types of
statistics online. 

Source code of the web app: https://github.com/wachjose88/carrera-advanced-rms-statistic
