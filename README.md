## ReplayBot

#### To scrape:

```
scrapy runspider scraper/archive_scraper.py -o events.json
```

#### To tweet:

1. Copy `bot_config_example.json` to `bot_config.json` and edit values as
   necessary. Make sure to add your Twitter API credentials.
2. `cd` to the bot/ directory and run `python3 bot.py`


