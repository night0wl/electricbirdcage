from distutils.core import setup

setup(
    name = 'ElectricBirdcage',
    version = '0.1',

    author = 'Matt Revell',
    description = ''.join([
                    'A python module to remotely control home devices and ',
                    'servers using twitter.'
                    ])
    license = '?',

    packages = [
        'ElectricBirdcage',
        'ElectricBirdcage/bots',
        'ElectricBirdcage/listeners',
        'ElectricBirdcage/responders',
        'ElectricBirdcage/monitors'
        ]
)
