import re

class VarParser:

    def __init__(self):
        pass

    def desc_id_split(self, desc):
        # Split the description string if it is comma seperated
        desc_list = desc.split(",")
        modified_desc_list = ""
        # Iterate through descriptions to remove characters that cause issues
        for desc_iterator in desc_list:
            # currently does not support brackets
            stripped_desc = re.sub(r'(\(|\))', r"", desc_iterator)
            modified_desc_list = modified_desc_list + "&ethernetInterface.description=contains(" + stripped_desc + ")"
        return modified_desc_list

