# Craig Tomkow
# June 1, 2018
#
# Device class to store state information (a Globals class pattern). No instantiation should be done.
# I like to liken this to a C struct (functionally speaking)
# Also remember, resist the getters and setters!
#
# ... Hmmm, if I want to multi-thread this, I need to convert this to a instantiable class so I can have device objects
# .. Ok, so I succumb and turned it into a instantiable class with global variables, now I can multi-thread


class Switch:


    def __init__(self):

        global ipv4_address
        global id
        global reachability

        global pre_software_version
        global pre_stack_member        # a list of dictionaries
        global pre_stack_member_key    # a list of sorted entPhysicalIndex values
        global pre_vlan
        global pre_cdp_neighbour       # a list of dictionaries
        global pre_cdp_neighbour_key   # a list of sorted interfaceIndex values
        global pre_sync_state

        global post_software_version
        global post_stack_member        # a list of dictionaries
        global post_stack_member_key    # a list of sorted entPhysicalIndex values
        global post_vlan
        global post_cdp_neighbour       # a list of dictionaries
        global post_cdp_neighbour_key   # a list of sorted interfaceIndex values
        global post_sync_state
