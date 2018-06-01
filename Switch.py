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
        global software_version
        global stack_member        # a list of dictionaries
        global vlan
        global cdp_neighbour       # a list of dictionaries