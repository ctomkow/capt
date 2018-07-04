#!/usr/bin/env python3

# system imports

# local imports

# Move all JSON related formatting and parsing here!
class JsonParser:


    def get_value(self, json_data, key_list, logger):

        try:
            key = key_list.pop(0)
        except IndexError:
            return ""

        if key_list:
            return self.get_value(self, json_data[key], key_list, logger)
        else:
            try:
                return json_data[key] # found result
            except KeyError:
                return ""
