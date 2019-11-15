# House hunter
This is a personal project to scrape real estate listings and present them through a simple flask App.
The project has two central parts:
- 'Scraper' which is the web scrapping aspect that uses Scrappy.
- 'flaskApp' the flask app in charge of delivering the scraped results.


# Installation
`requirements.txt` contains the packages needed to run both parts of the projects.
Make sure your environment is activated and simply type `pip install -r requirements.txt`

## Setting up Scrappy
- The directory structure of `Scrapper` is based on `scrapy startproject Scraper`
    - If you have to use the command, make sure that `scrapy.cfg` refers to the same paths/names.
- 
