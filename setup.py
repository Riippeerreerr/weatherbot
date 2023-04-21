from setuptools import setup, find_packages

VERSION = '1.0.17'

# Runtime dependencies. See requirements.txt for development dependencies.
DEPENDENCIES = [
    "websockets==11.0.1",
    "requests==2.28.2",
    "aiogram==2.25.1"
]

setup(
    name='weatherbot',
    version=VERSION,
    description='Weather forecast used on a Telegram Bot',
    author='Vlad Catanoiu',
    author_email='vcatanoiu2000@yahoo.com',
    url='https://github.com/dantimofte/bfxtelegram',
    license='MIT',
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    keywords=[ 'telegram', 'weather'],
    classifiers=[],
    zip_safe=True,
    entry_points={
        "console_scripts": [
            "ws_server = weatherbot.server_websocket:main",
            "wbot = weatherbot.echo_bot:main",
        ],
    },
)

