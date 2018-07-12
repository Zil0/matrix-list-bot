import logging
import shelve
import signal
import sys

from matrix_client.client import MatrixClient

from itemlist import List
from config import command_prefix, data_file

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


class Bot:

    def __init__(self, hs_url, username, password):
        self.cli = MatrixClient(hs_url)
        self.cli.login_with_password(username=username, password=password)
        self.shelf = shelve.open(data_file, writeback=True)
        signal.signal(signal.SIGTERM, self.close_shelf)
        signal.signal(signal.SIGINT, self.close_shelf)
        self.cli.add_invite_listener(self.on_invite)
        self.joined_rooms = self.cli.get_rooms()
        logger.info(f'Joined to {[r.display_name for r in self.joined_rooms.values()]}')
        self.add_room_listeners()

    def run(self):
        self.cli.listen_forever()
        logger.info('Bot started.')

    def add_room_listeners(self):
        for room_id, room in self.joined_rooms.items():
            self.add_local_bot(room)

    def on_invite(self, room_id, state):
        room = self.cli.join_room(room_id)
        # Force a sync in order not to process previous room messages
        self.cli._sync()
        self.add_local_bot(room)
        self.joined_rooms[room_id] = room
        room.send_notice(f'Hi! I\'m a list keeping bot. Send {LocalBot.prefix}help'
                       ' to learn how to use me.')
        logger.info(f'Received an invite for room {room.display_name}, and joined.')

    def add_local_bot(self, room):
        lbot = LocalBot(room, self.cli.api, self.shelf)
        room.add_listener(lbot.on_message, event_type='m.room.message')

    def close_shelf(self, *args):
        logger.info('Closing shelf...')
        self.shelf.close()
        logger.info('Shelf is closed.')
        sys.exit()


class LocalBot:

    prefix = command_prefix
    commands = {
        'new': 'name: Create an new empty list.',
        'add': 'name item: Add a new item to a list.',
        'remove': ('name [index [index...]]: Remove list items by index, or the whole '
                   'list if no indexes are given.'),
        'show': '[name]: Print a list, or all available lists if no name is given.',
        'info': ('name index: Print additional information about an item, such as date '
                 'added.'),
        'goaway': ': Leave the room.',
        'help': ': Print this help.'
    }

    def __init__(self, room, api, shelf):
        self.room = room
        self.api = api
        self.lists = shelf.setdefault(room.room_id, {})

    def on_message(self, room, event):
        if event['content']['msgtype'] != 'm.text':
            return
        if not event['content']['body'].startswith(self.prefix):
            return

        args = event['content']['body'].split()
        command = args.pop(0)[1:]
        if command not in self.commands:
            return

        sender = self.api.get_display_name(event['sender'])
        try:
            text = self.handle_command(command, args, sender)
            if text:
                self.room.send_notice(text)
        except (IndexError, ValueError) as e:
            self.room.send_notice('Wrong usage. Use !help to learn more.')
        except KeyError:
            self.room.send_notice('List does not exist.')

    def handle_command(self, command, args, sender):
        if command == 'help':
            text = 'List bot usage:\n'
            text += '\n'.join(f'{self.prefix}{k} {v}'
                              for k, v in self.commands.items())
            return text
        elif command == 'goaway':
            self.room.send_notice('bye!')
            self.room.leave()
            logger.info(f'Left room {self.room.display_name}')
            return
        elif command == 'show':
            if args:
                return str(self.lists[args[0]])
            else:
                return f'Available lists: {list(self.lists)}'
        else:
            name = args.pop(0)
            if command == 'new':
                if name in self.lists:
                    return f'List {name} already exists.'
                self.lists[name] = List(name)
                return f'Created new list {name}.'
            elif command == 'add':
                return self.lists[name].add(sender, ' '.join(args))
            elif command == 'remove':
                if args:
                    indexes = [int(i) for i in args if int(i) >= 0]
                    if not indexes:
                        raise ValueError
                    return self.lists[name].remove(indexes)
                else:
                    del self.lists[name]
                    return f'List {name} has been deleted.'
            elif command == 'info':
                index = int(args[0])
                if index < 0:
                    raise ValueError
                item = self.lists[name][index]
                return (f'Item number {args[0]} "{item.value}" was added by {item.author}'
                        f'on {item.time}.')
