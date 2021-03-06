# ElectricBirdcage #
#### A twitter bot framework for home automation ####

----------

## Features ##

Currently implemented modules allows ElectricBirdcage to:

- Send simple responses to tweets using regex
- Report current temperature and change
- Switch an electrical device on / off (implemented in heating)
- Report a server's status
- Wake up and shutdown a *nix server

## Requirements ##
At very least you will need:

- Python >=2.7 (should work with >=2.5 but untested)
- Redis >=2.2
- A twitter account with an app that has full API access (see [Twitter's docs](https://dev.twitter.com/docs))

To run the full example implementation (home_agent.py) you will need:

- An X10 CM15 module (or equivelant USB based X10 controller)
- At least one X10 actuator device
- A USB TEMPer1 device
- A *nix server on the local network with wake-on-lan configured and a user that can execute 'sudo halt' without a password

## Installation ##

It is highly recommended that you run ElectricBirdcage within a virtual environment. The following instructions assume an environment has been created already.

Start your environment and clone the latest version of ElectricBirdcage from github

```
cd /path/to/env/  
. bin/activate  
git clone git@github.com:night0wl/electricbirdcage.git
```

Then install requirements and run setup

```
cd electricbirdcage  
pip install -r requirements.txt  
python setup.py install  
```

**NOTE: I have experienced problems with pyUSB v1.x, but v0.4.3 is known to work. If you experience problems uninstall v1.x and download v0.4.3 from the [sourceforge page](http://sourceforge.net/projects/pyusb/files/PyUSB%200.x/0.4.3/)**

#### Adittional Requirements ####

If you have a TEMPer1 device and / or an X10 controller, you will need to install the relevant modules:

```
cd /path/to/env  
git clone git@github.com:night0wl/python-x10.git  
python python-x10/setup.py install  
git clone git@github.com:night0wl/temper-python.git   
python temper-python/setup.py install
```

You must also ensure the user running ElectricBirdcage has permissions to read and write to the devices. You can do so by:

- Running your bot as root (not recommended) or,
- Adding the bots user to root group (not recommended) or,
- Using the udev rules supplied, setting the group to the bots user group (recommended)

## Setup ##
#### ElectricBirdcage Server ####

In order to setup ElectricBirdcage, you will need to add data to Redis keys (this will be incorporated into a setup script at some point but for now must be created manually). Here is a list of currently used keys which must be created and populated using the Redis CLI.

*twitterbot*:consumer\_key  
*twitterbot*:consumer\_secret  
*twitterbot*:access\_token  
*twitterbot*:access\_token\_secret

These are required to communicate with the Twitter API, ElectricBirdcage cannot run at all without them (see [Twitter's docs](https://dev.twitter.com/docs) for details on setting up an application). The *twitterbot* is the screen name of the twitter account and is not case sensitive.

*twitterbot*:server:*servername*:mac  
*twitterbot*:server:*servername*:user  

These are only required if you wish to control a server. The mac address must be in the form of *xx:xx:xx:xx:xx*, case insensitive. The user is case sensitive, but the *servername* is not case sensitive.

ElectricBirdcage also uses the logging module, so the account you use must be able to write to /var/log/electricbirdcage.log. If you use root, it will create it automatically, otherwise:

```
sudo touch /var/log/electricbirdcage.log  
sudo chown username:username /var/log/electricbirdcage.log 
```

A sample init script is also provided, you need to modify the paths, and bot name and copy it to /etc/init.d/*botname* (assuming your *nix flavour supports this method)

#### Twitter bot account ####

ElectricBirdcage's philosohpy is to use Twitter's features wherever possible. The UI and authentication, for example, is handled entirely by Twitter. Access control is also handled by Twitter, using following lists (you don't want anyone to be able to activate your bot!) so in order to work, your bot account must follow any accounts you use to tweet at it.

## Usage ##
It is recommended that you run your agent from the command line at first, this will allow you to spot and work out any issues and errors much more easily:

```
cd /path/to/env  
. bin/activate  
python electricbirdcage/home_agent.py <TwitterBot>
```

You should then be able to send tweets in the following forms:

`@twitterbot achoo` 
`@twitterbot heating status`  
`@twitterbot heating on`  
`@twitterbot heating off`  
`@twitterbot server status <server>`  
`@twitterbot server wakeup <server>`  
`@twitterbot server shutdown <server>`  
