#!/usr/bin/env python3

# system imports
import ipaddress
import json

# local imports

# Move all JSON related formatting and parsing here!
class JsonParser:


    def get_value(self, json_data, desired_key, logger):

        for key in json_data:
            if isinstance(json_data[key], list):
                for sub_key in json_data[key][0]:
                    if sub_key == desired_key:  # found key
                        return json_data[desired_key]
            elif isinstance(json_data[key], dict):
                for sub_key in json_data[key]:
                    if isinstance(json_data[key], list):
                        for sub_key in json_data[key][0]:
                            if sub_key == desired_key:  # found key
                                return json_data[desired_key]
                    elif isinstance(json_data[key], dict):
                        for sub_key in json_data[key]:
                            if isinstance(json_data[key], list):
                                for sub_key in json_data[key][0]:
                                    if sub_key == desired_key:  # found key
                                        return json_data[desired_key]
                            elif isinstance(json_data[key], dict):
                                for sub_key in json_data[key]:
                                    if sub_key == desired_key:  # found key
                                        return json_data[desired_key]
            elif key == desired_key: # found key
                return json_data[desired_key]


    def format_reload_payload(self):

        pass