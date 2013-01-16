import paramiko
import socket
from subprocess import Popen, PIPE
from time import sleep

from PrivateResponse import PrivateResponse

class ServerResponse(PrivateResponse):
    def __init__(self, botname):
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
        subp = Popen(
            """
            arp -n | grep %s | awk '{print $1}'
            """ % mac,
            shell=True, stdout=PIPE
            )
        return subp.stdout.readline().strip()

    def get_ssh_conn(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        return ssh

    def get_ssh_creds(self, base_key):
        ip = self.get_ip_from_mac(self.redis.get(base_key + 'mac'))
        if ip == '':
            return (None, None, None)

        user = self.redis.get(base_key + 'user')
        key_file = self.redis.get(base_key + 'key_file')
        return (ip, user, key_file)


    def check_ssh(self, base_key, initial_wait=0, interval=0, retries=1):
        sleep(initial_wait)
        ssh = self.get_ssh_conn()
        ip, user, key_file = self.get_ssh_creds(base_key)
        if not ip:
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
                print e
                return False
        return False

    def server_check(self, tweet):
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
                                )
                    )
        else:
            self.respond(
                    self.server_replies["server_down"] % (
                                tweet.author.screen_name,
                                server_name
                                )
                    )


    def server_wake(self, tweet):
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
                                )
                    )

    def server_shutdown(self, tweet):
        server_name = tweet.text.lower().split()[3]
        base_key = "%s:server:%s:" % (
                        self.twitter_bot.botname.lower(),
                        server_name
                        )

        ssh = self.get_ssh_conn()
        ip, user, key_file = self.get_ssh_creds(base_key)
        try:
            print "trying"
            ssh.connect(ip, username=user, key_filename=key_file)
        except (
                paramiko.AuthenticationException,
                paramiko.BadHostKeyException,
                paramiko.SSHException,
                socket.error
                ), e:
            self.respond_private(
                    tweet,
                    self.server_replies["fail"] % (
                                tweet.author.screen_name,
                                )
                    )
        print "executing"
        stdin, stdout, sterr = ssh.exec_command("sudo halt")
        self.respond(
                self.server_replies["server_shutdown"] % (
                                tweet.author.screen_name,
                                server_name
                                )
                )


    def react(self, *args):
        tweet, match = args
        if self.is_allowed(tweet.author.screen_name):
            self.replies[match](tweet)
