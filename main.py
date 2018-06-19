#!/usr/bin/python

from bot import Bot
from config import domain, username, password


device_id = 'fixed_device_id'
bot = Bot(domain, username, password, device_id)
bot.run()
