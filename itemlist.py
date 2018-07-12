from datetime import datetime


class List:

    def __init__(self, name):
        self.name = name
        self.items = []

    def add(self, author, value):
        self.items.append(Item(author, value))
        return f'Added item to list {self.name}.'

    def remove(self, indexes):
        for index in sorted(indexes, reverse=True):
            self.items.pop(index - 1)
        return f'Removed given item{"s" * (len(indexes) > 1)} from list {self.name}.'

    def __str__(self):
        text = f'List {self.name}:\n'
        text += '\n'.join(f'{i + 1}- {item}' for i, item in enumerate(self.items))
        return text

    def __getitem__(self, i):
        return self.items[i - 1]


class Item:

    def __init__(self, author, value):
        self.author = author
        self.value = value
        self.time = datetime.today()

    def __str__(self):
        return f'{self.value} ({self.author})'
