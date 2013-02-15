# A response object for handling servers
#
# Author: Matt Revell

import logging
import paramiko
import socket
from subprocess import Popen, PIPE
from time import sleep

from PrivateResponse import PrivateResponse

class ServerResponse(PrivateResponse):
    """
    A response object for handling servers
    """
    def __init__(self, botname):
        """
        Initialise parameters
        """
        replies = {
            "@%s SERVER STATUS.*$" % botname: self.server_check,
            "@%s SERVER WAKEUP.*$" % botname: self.server_wake,
            "@%s SERVER SHUTDOWN.*$" % botname: self.server_shutdown
            }

        PrivateResponse.__init__(self, botname, replies)

        self.server_replies = {
            "server_down": "@%s %s is down",
            "server_up": "@%s %s is up",
            "server_down_now": "@%s %s has shut down",
            "server_up_now":  "@%s %s is now up",
            "server_uptime": "@%s %s has been up for %s",
            "server_shutdown": "@%s Acknowledged. %s is shutting down",
            "wakeup_sent": "@%s Acknowledged. Wakeup packet sent to %s",
            "fail": "DM @%s Oh Noes! That failed"
            }

    def get_ip_from_mac(self, mac):
        """
        Uses shell commands to determine the ip address from the mac address

        Returns an ip as a string 'x.x.x.x'
        """
        subp = Popen(
            """
            arp -n | grep %s | awk '{print $1}'
            """ % mac,
            shell=True, stdout=PIPE
            )
        return subp.stdout.readline().strip()

    def get_ssh_conn(self):
        """
        Establishes an SSH connection.

        Returns an SSH connection handle
        """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        return ssh

    def get_ssh_creds(self, base_key):
        """
        Retrieves the username and keyfile from redis.

        Returns credentials or a tuple of (None, None, None) if no IP is found.
        """
        ip = self.get_ip_from_mac(self.redis.get(base_key + 'mac'))
        if ip == '':
            return (None, None, None)

        user = self.redis.get(base_key + 'user')
        key_file = self.redis.get(base_key + 'key_file')
        return (ip, user, key_file)


    def check_ssh(self, base_key, initial_wait=0, interval=0, retries=1):
        """
        Attempts to establish an SSH connection.

        Returns True if successful, False otherwise
        """
        sleep(initial_wait)
        ssh = self.get_ssh_conn()
        ip, user, key_file = self.get_ssh_creds(base_key)
        if not ip:
            logging.debug("Failed to obtain an IP address")
            return False

        for x in range(retries):
            print "Attempt %s" % x
            try:
                ssh.connect(ip, username=user, key_filename=key_file)
                return True
            except (paramiko.SSHException, socket.error):
                sleep(interval)
            except (
                    paramiko.AuthenticationException,
                    paramiko.BadHostKeyException,
                    ), e:
                logging.error("Paramiko Exception caught: %s" % e)
                return False
        logging.debug(
                "Failed to connect to server, args:\n%s\t%s\t%s\t%s" % (
                    base_key,
                    initial_wait,
                    interval,
                    retries
                    )
                )
        return False

    def server_check(self, tweet):
        """
        Checks whether or not a server is up (SSH) and triggers the appropriate
        response.
        """
        server_name = tweet.text.lower().split()[3]
        base_key = "%s:server:%s:" % (
                        self.twitter_bot.botname.lower(),
                        server_name
                        )
        if self.check_ssh(base_key):
            self.respond(
                    self.server_replies["server_up"] % (
                                tweet.author.screen_name,
                                server_name
                                ),
                    tweet.id
                    )
        else:
            self.respond(
                    self.server_replies["server_down"] % (
                                tweet.author.screen_name,
                                server_name
                                ),
                    tweet.id
                    )


    def server_wake(self, tweet):
        """
        Attempts to wake up a server and triggers the appropriate response when
        it succeeds of fails.
        """
        server_name = tweet.text.lower().split()[3]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 2)
        base_key = "%s:server:%s:" % (
                        self.twitter_bot.botname.lower(),
                        server_name
                        )
        mac = self.redis.get(base_key + 'mac')
        s.sendto(
            '\xff' * 6 + mac.replace(':','').decode('hex') * 16,
            ('255.255.255.255', 9)
            )

        self.respond(
                self.server_replies["wakeup_sent"] % (
                                    tweet.author.screen_name,
                                    server_name
                                    ),
                tweet.id
                )

        if self.check_ssh(base_key, initial_wait=80, interval=10, retries=4):
            self.respond(
                    self.server_replies["server_up_now"] % (
                                    tweet.author.screen_name,
                                    server_name
                                    ),
                    tweet.id
                    )
        else:
            self.respond_private(
                    tweet,
                    self.server_replies["fail"] % (
                                tweet.author.screen_name,
                                ),
                    tweet.id
                    )

    def server_shutdown(self, tweet):
        """
        Attempts to shutdown a server and triggers the appropriate response
        when it succeeds or fails.
        """
        server_name = tweet.text.lower().split()[3]
        base_key = "%s:server:%s:" % (
                        self.twitter_bot.botname.lower(),
                        server_name
                        )

        ssh = self.get_ssh_conn()
        ip, user, key_file = self.get_ssh_creds(base_key)
        try:
            logging.info("Attempting to shutdown '%s'" % server_name)
            ssh.connect(ip, username=user, key_filename=key_file)
        except (
                paramiko.AuthenticationException,
                paramiko.BadHostKeyException,
                paramiko.SSHException,
                socket.error
                ), e:
            loggoing.error("failed to shutdown '%s'" % server_name)

            self.respond_private(
                    tweet,
                    self.server_replies["fail"] % (
                                tweet.author.screen_name,
                                ),
                    tweet.id
                    )
        logging.info("Executing 'sudo halt' on '%s'" % server_name)
        stdin, stdout, sterr = ssh.exec_command("sudo halt")
        self.respond(
                self.server_replies["server_shutdown"] % (
                                tweet.author.screen_name,
                                server_name
                                ),
                tweet.id
                )


    def react(self, *args):
        """
        Invokes the method corresponding to the match.
        """
        tweet, match = args
        if self.is_allowed(tweet.author.screen_name):
            self.replies[match](tweet)
