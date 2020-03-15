# PyWallStreet
[![Github All Releases](https://img.shields.io/github/downloads/atom/atom/total.svg?style=flat)]()  
[![PyPi Version](https://img.shields.io/pypi/v/yt2mp3.svg)](https://pypi.python.org/pypi/yt2mp3/)
[![GitHub watchers](https://img.shields.io/github/watchers/badges/shields.svg?style=social&label=Watch&style=plastic)]()
## About
T+his project is a Python 3 bot for automate online trading.

## Install
To install the project launch the command 
```
pip3 install -r requirements.txt
```
Before you run the project you need to create a file called alpaca_api_key.json with your API key of AlpacaTrading. 
The file need the public and the secret key formatted like the example below:
```
{
    "key" : "yourPublicKey",
    "secret_key" : "yourSecretKey"
}
```
If you don't have the keys you can create a new account on https://alpaca.markets/

## Run 
To run the project you need to launch by CLI passing the name of the stocks you want your bot to buy / sell. Example:
```
python3 main.py GOOGL AAPL AMZN
```

## Release History
 * 1.0.0 
    * First release

## Author
Developed by me and only me.