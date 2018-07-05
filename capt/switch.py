
# Instantiable (so it can be threaded) class to store state information (a Globals class pattern).
# I liken this to a C struct (functionally speaking)


class Switch:

    def __init__(self):

        global ipv4_address
        global id
        global reachability
        global sync_state
        global phones          # a list of phone names
        global access_points   # a list of access points
        global test_ap         # a list of one access point to test (save on API calls until core code is fixed)

        global pre_software_version
        global pre_stack_member            # a list of sorted dictionaries based on 'name'
        global pre_stack_member_desc       # a list of sorted description values
        global pre_stack_member_name       # a list of sorted name values
        global pre_vlan
        global pre_cdp_neighbour           # a list of sorted dictionaries
        global pre_cdp_neighbour_nearend   # a list of sorted interfaceIndex values

        global post_software_version
        global post_stack_member            # a list of sorted dictionaries based on 'name'
        global post_stack_member_desc       # a list of sorted description values
        global post_stack_member_name       # a list of sorted name values
        global post_vlan
        global post_cdp_neighbour           # a list of sorted dictionaries
        global post_cdp_neighbour_nearend   # a list of sorted interfaceIndex values

