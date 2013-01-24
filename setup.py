from distutils.core import setup

setup(
    name = 'Botwit',
    version = '0.1',

    author = 'Matt Revell',
    description = ''.join([
                    'A python module to remotely control home devices and ',
                    'servers using twitter.'
                    ])
    license = '?',

    packages = [
        'botwit',
        'botwit/bots',
        'botwit/listeners',
        'botwit/responders',
        'botwit/monitors'
        ]
)
