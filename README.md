Introduction:- 

This project is for Drip Capital. 

An IEC Web Service would provide data about any Indian exporter with the following technical
functionalities:

1. Maintains IEC datastore
2. Provides IEC lookup and validation
3. Regularly updates data in datastore

The Web Service interface will be REST API defined by following endpoints:

1. GET /iec/:code - Retrieves data in datastore
2. POST /iec/:code/:name - Validates IEC with company name on Gov website [1].


References:
[1] http://dgft.delhi.nic.in:8100/dgft/IecPrint
Sample IEC 3499000172 for Dhara Foods Pvt Ltd