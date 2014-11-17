saltinventory
=============

This application retrieves some information from all running and reachable salt minnions and creates some html pages.

At current state these salt calls are made:

* grains.items
* network.interfaces

and these pages are created:

* List of all hosts
* List of all networks
* Detail page for each host
* Detail page for each network

# Requirements

* Salt
This application must run on a salt master
* python-netaddr

# Instructions

* Clone repository
* Run saltinventory.py
* Open www/hostlist.html in your browser
