# House Hunt project - Progress 
- [ ] Git rebase ?
- Done for now. It doesn't look great but that's not really what you want to do in life.

Next step: Scrape scrape scrape !

## Backlog

### Make crawling recurrent
- Get the data then use it.
- No need to create new spiders for lots and condos for the moment, just get the data for plexes.

### Add one or more geo-fence that make sense to you.
- Right now tests are boring because it's all in the suburbs.
- Being able to pick several zone could be nice too....
    - Should be just about changing the type of dash filter.

### Include datatable in App
- iFrame or other way.

### Crawl on a regular time interval
- Cron Job first then automagically if on Heroku.
- Also you might want some data for a side project at some point.
    - The first seen last seen is kinda cool.

### Add login
- To be able to show to specific people
- Being able to add geo-fence per user would be cool and is not really hard to do...

### Add Lots
- Create lots spiders from plex template.
- Add it as a selection on the home menu
    - The filters currently there are now in the `dash table`
        - destructive innovation.

### Put it online
- To gather user feedback
- Also getting use to push, pull ssh etc.

# NOTES
Your UDEMY password is 34Pigeon$$ with email address eric.j.fontaine@gmail.com\

> `jdm` pops up your journal, c'est une BLAgue avec le JOURNAL DE MONTREAL


# Sidebrain

## Launching Splash
terminal > ssplash
`docker run -p 8050:8050 scrapinghub/splash`


# Testing xpath on JS pages
> this works in `scrapy shell`

from scrapy_splash import SplashRequest

link = "https://www.centris.ca/en/houses~for-sale~mont-royal/16827175?view=Summary"
script_detail = '''
        function main(splash, args)
        splash.images_enabled = false
        splash:on_request(function(request)
            if request.url:find('ResponsiveWebService.asmx') or request.url:find('recaptcha') or request.url:find('css') or request.url:find('linkedin') or request.url:find('cdn') then
                request:abort()
            end
            end)
        assert(splash:go(args.url))
        assert(splash:wait(0.5))
        return splash:html()
        end
    '''

r = SplashRequest(url=link, endpoint='execute', args={'lua_source': script_detail})


tables = response.xpath('//div[@class="teaser"]/following-sibling::table')

features = {}

for table in tables:
    col1 = table.xpath('.//tr/td/text()').getall()
    col2 = table.xpath('.//tr/td/span/text()').getall()

    features.update(dict(list(zip(col1,col2))))

print(features)

