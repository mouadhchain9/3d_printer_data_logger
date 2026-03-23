this a makeshift data pooler using MQQT mosquitto,
websockets and some simple scripts for octoprint to 
store telemetry while printing.

--> the goal is to build some datasets that could be 
usefull in some future machineLearning or AI models 
that could help in maintenance or make improvements 
in future designs.


1) first thing you have to do is installing octoprint,

2) next go to the plugin manager and install the MQTT
 plugging, don't forget to restart it.
 note: check if it has the correct config

3) next go into :
	C:\Users\<your_user>\AppData\Roaming\OctoPrint\plugins
- create a folder "motion_mqtt" and move in "__init__.py".

4) download mosquitto : https://mosquitto.org/download/

5) once installed, open: 
	C:\Program Files\mosquitto\mosquitto.conf
- and add at the bottom of the file: 
		listener 1883
		allow_anonymous true

		listener 9001
		protocol websockets
- this would be our publishing and listening configuration

6) start mosquitto with you configuration using this command:
	mosquitto -c "C:\Program Files\mosquitto\mosquitto.conf" -v 

7) start your logger.py script and start printing, in case you
want to monitor data flow irt open the html dashboard, it will read
from the same data flow as your logging script.

-- you can also view your data either by installing sqlite cli tool
for ease of use or run the "db_viewer.py"

-- once finished with a print a csv exporter can be used to prep
your data for submission