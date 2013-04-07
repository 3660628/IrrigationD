=============
IrrigationD
=============

An Irrigation Controller daemon written in python.

I needed to integrate our Irrigation System with our custom Home Automation project, so I threw together this daemon...
Since it's a plugin for our Home Automation AI, many of the Scheduling tasks, rain logic and such are handled outside
of this daemon. But it'll be easy to add it here or write a simple wrapper. IrrigationD offers a webservice, by which
you can submit Irrigation Cycles via JSON and it'll ensure they're completed per your request.

This project meets all of my requirements, but since it's 90% there for most others, I'll be adding the other 10% as
I have time.


Features
-----------

*Multi-Zone (I'm currently running 8)
*WebService
*Currently integrates with USB relay boards via pyIOBoard (would be easy to add support for other relay boards)



What it Doesn't Do (yet - see note above)
--------------------

*Scheduling... (you can use a curl command in cron)
*Rain Logic  (we don't get much)



License
---------
Version 0.5.x is being released under LGPLv3.