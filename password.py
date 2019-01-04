#!/usr/local/bin/python3
"""A simple password manager for kitty, the terminal emulator"""

__name__ = 'password-kitten'
__author__ = 'Michael Cordover'
__version__ = '0.1.0'

import sys
import os
import appdirs
import getpass
import json
import keyring

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

def main(args):
    config = Config()

    if len(args) != 2:
        print_help_and_wait()
        return None

    if args[1] == 'create':
        print('Creating new password (use blank password to abort)')
        while True:
            password_name = input('Name for the password: ')
            if config.password_is_in_list(password_name):
                print('That password already exists! Please choose a different name.')
            elif not password_name:
                print('Aborting due to blank name.')
                wait_key_with_message()
                return None
            else:
                break
        config.add_password_to_list(password_name)
        password_value = getpass.getpass()
        keyring.set_password(__name__, password_name, password_value)
        print('Created a new password: ' + password_name)
        wait_key_with_message()
        return None
    elif args[1] == 'print':
        print('Printing password (use blank password to abort)')
        password_name = get_password_name(config)
        if not password_name:
            print('Aborting due to blank name.')
            wait_key_with_message()
            return None
        elif not config.password_is_in_list(password_name):
            print('That password does not exist!')
            wait_key_with_message()
            return None
        pw_value = keyring.get_password(__name__, password_name)
        return pw_value
    elif args[1] == 'delete':
        print('Deleting password (use blank password to abort)')
        password_name = get_password_name(config)
        if not password_name:
            print('Aborting due to blank name.')
            wait_key_with_message()
            return None
        elif not config.password_is_in_list(password_name):
            print('That password does not exist!')
            wait_key_with_message()
            return None
        keyring.delete_password(__name__, password_name)
        config.remove_password_from_list(password_name)
        print('Password {} deleted.'.format(password_name))
        wait_key_with_message()
        return None
    else:
        print_help_and_wait()
        return None

def get_password_name(config):
    return prompt('Password name: ', completer=WordCompleter(config.get_password_list(), ignore_case=True, sentence=True))


def handle_result(args, result, target_window_id, boss):
    if result is None:
        return
    w = boss.window_id_map.get(target_window_id)
    if w is not None:
        w.paste(result)

def print_help_and_wait():
    print('Usage: {} create | print | delete'.format(__name__))
    wait_key_with_message()

def wait_key_with_message():
    print('Press any key to continue...')
    wait_key()

def wait_key():
    ''' Wait for a key press on the console and return it. '''
    result = None
    import termios
    fd = sys.stdin.fileno()

    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)

    try:
        result = sys.stdin.read(1)
    except IOError:
        pass
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)

    return result

class Config:
    __config_map = None
    __default_config_map = {
        'passwords': {}, # This is really a set, but I'm too lazy to write an appropriate json serializer (and I don't want to pickle)
    }

    def __init__(self):
        try:
            self.__config_map = json.load(open(self.config_path, 'r'))
        except:
            self.__config_map = self.__default_config_map

    @property
    def config_path(self):
        data_dir = appdirs.user_data_dir(__name__, __author__)
        try:
            os.makedirs(data_dir)
        except OSError:
            pass
        return data_dir + os.sep + 'config.json'

    def get_password_list(self):
        return list(self.__config_map['passwords'].keys())

    def remove_password_from_list(self, password_name):
        del self.__config_map['passwords'][password_name]
        self.__save()

    def add_password_to_list(self, password_name):
        self.__config_map['passwords'][password_name] = True
        self.__save()

    def password_is_in_list(self, password_name):
        return password_name in self.__config_map['passwords']

    def __save(self):
        json.dump(self.__config_map, open(self.config_path, 'w'))
        os.chmod(self.config_path, 0o600)

