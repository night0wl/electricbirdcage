import tweepy

class StreamListener(tweepy.StreamListener):
    def __init__(self, stream_bot):
        self.stream_bot = stream_bot
        tweepy.StreamListener.__init__(self)

    def on_status(self, status):
        self.stream_bot.process(status)
