import tweepy

# A simple implementation of a tweepy StreamListener class
#
# Author: Matt Revell

class StreamListener(tweepy.StreamListener):
    """
    A simple implementation of a tweepy StreamListener class

    Implements the on_status method only
    """
    def __init__(self, stream_bot):
        """
        Set the bot object and init the super class
        """
        self.stream_bot = stream_bot
        tweepy.StreamListener.__init__(self)

    def on_status(self, status):
        """
        Triggers when a filtered tweet is recieved. Passes the status to the
        bot to be processed.
        """
        self.stream_bot.process(status)
