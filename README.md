A simple list-keeping bot for Matrix, written in Python.  
It serves as a proof-of-concept for end-to-end encryption support in matrix-python-sdk.

# Installation

First, make sure you are using Python 3.6. Then, install the requirements.  
Copy `example_config.py` to `config.py`.
Create an account for the bot, and write the associated credentials in `config.py`.  

# Usage
Run the bot with `./main.py`.  
Then invite the bot to some rooms.

# Limitations

The bot lacks proper command parsing, proper config handling and proper data persistence (data is saved only when the bot is terminated properly).
