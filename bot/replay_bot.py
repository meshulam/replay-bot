import twitter
from datetime import datetime, timedelta
import json

# replay_bot.py: Tweet a timeline of events
#
# (c) 2016 Matt Meshulam


def parseTimestamp(tsString):
    try:
        return datetime.strptime(tsString, "%Y-%m-%dT%H:%M:%S")
    except:
        return None


class ReplayBot(object):
    def __init__(self, twitter_api, template, events,
                 time_offset=None, last_timestamp=None):
        self.api = twitter_api
        self.template = template
        self.events = events
        self.last_timestamp = last_timestamp
        self.time_offset = time_offset or timedelta()

    def pending_events(self, replay_time):
        events = []
        for ev in self.events:
            ts = parseTimestamp(ev['timestamp'])
            if self.last_timestamp and ts <= self.last_timestamp:
                next
            elif ts > replay_time:
                return events
            else:
                events.append(ev)
        return events

    def pending_events_now(self):
        replay_time = datetime.now() - self.time_offset
        return self.pending_events(replay_time)

    def tweet(self, event):
        message = self.template(event)
        #status = self.api.PostUpdate(message)
        #print("{}  Tweeted [{}]".format(datetime.now().isoformat(), status.text))
        # TODO: check that tweet was sent?
        if message:
            return event['timestamp']
        else:
            return None


# Renders an event dict to a tweetable string
def tweet_template(event):
    max_chars = 140 - 2*24  # 2 t.co links

    tweet = "{}: {} {}".format(event['title'][:max_chars],
                               event['url'],
                               event['newurl'])
    return tweet

def save_timestamp(dt, filename):
    with open(filename, 'w') as f:
        if hasattr(dt, 'isoformat'):    # it's a datetime, stringify it
            dt = dt.isoformat()
        f.write(dt)

def main():
    config = {}
    with open("bot_config.json") as cfg_file:
        config = json.load(cfg_file)

    api = twitter.Api(consumer_key=config['tw_consumer_key'],
                      consumer_secret=config['tw_consumer_secret'],
                      access_token_key=config['tw_access_key'],
                      access_token_secret=config['tw_access_secret'])

    events = []
    with open(config['event_file']) as event_file:
        events = json.load(event_file)

    offset_days = config.get('time_offset_days', 0)
    time_offset = timedelta(days=config.get('time_offset_days', 0),
                            seconds=config.get('time_offset_seconds', 0))

    last_time = None
    try:
        with open(config['time_file']) as time_file:
            ts = time_file.readline().strip()
            last_time = parseTimestamp(ts)
    except:
        pass

    bot = ReplayBot(api, tweet_template, events,
                    time_offset, last_time)
    pending = bot.pending_events_now()

    latest_time = None
    for ev in pending:
        print("Pending: {}".format(ev))
        res = bot.tweet(ev)
        if res:
            latest_time = res
        else:
            print("Failed to send tweet. Canceling remaining pending.")
            break

    if latest_time:
        save_timestamp(latest_time, config['time_file'])


if __name__ == "__main__":
    main()

