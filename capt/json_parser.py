

class JsonParser:

    def __init__(self):

        pass

    def value(self, json_data, key_list, logger):

        try:
            key = key_list.pop(0)
        except IndexError:
            return ""
        if key_list:
            try:
                return self.value(json_data[key], key_list, logger)
            except KeyError: # fails on first lookup
                return ""
        else:
            try:
                return json_data[key] # found result
            except KeyError: # fails on last lookup
                return ""
