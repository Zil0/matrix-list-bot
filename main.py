#!/usr/bin/python

from bot import Bot
from config import domain, username, password

bot = Bot(domain, username, password)
bot.run()
