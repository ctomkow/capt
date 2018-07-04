#!/usr/bin/env python3

# system imports
import ipaddress
import json

# local imports

# Move all JSON related formatting and parsing here!
class JsonParser:


    def get_value(self, json_data, key_list, logger):

        try:
            key = key_list.pop(0)
        except IndexError:
            return ""

        if key_list:
            try:
                return self.get_value(self, json_data[key], key_list, logger)
            except UnboundLocalError: # hit a key/value that doesn't exist
                return ""
        else:
            try:
                value = json_data[key] # found result
            except KeyError:
                return ""
            finally:
                return value

    def format_reload_payload(self):

        pass