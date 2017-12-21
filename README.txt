====================================================
                  Contents
====================================================
I.   Running the application
II.  Assumptions
III. Technology and implementation
IV.  Hacks

====================================================
        I. Running the application
====================================================
  1. Launching the applicaiton
    a. Using the Run.sh script
        ./Run.sh //This will run the application container a deamon 
    Alternatively
    b. Mannual execution
        1. docker pull vrajeshjp/nextbus-reverseproxy
        2. sudo docker run -d -p 80:80 vrajeshjp/nextbus-reverseproxy

  2. Use the IP of instance/machine in browser to test if application in reachable. 
  3. To rest various commands, execute the Tests.sh file. This inturn is executing a client side python script to test the appliaction for various test cases.
	
====================================================
            II. Assumptions
====================================================
  1. pip should be installed and available for container as it uses pip to download dependancies 

  2. The response time reported is the total time to request the the given command from nextBus API, form a response and send a responsebackto client. "retrive_response_time" can be used if the intention is to measure response time fo quering to nextBus API only

  3. The application has been tested for bassic nextBus API commands like:
     '?command=agencyList',
     '?command=routeList&a=umd',
     '?command=routeList&a=sf-muni',
     '?command=routeConfig&a=umd&r=118'
      Based on the application design, it can be assumed that that application can handle any query being made to the original nextBus API.

  4. The default threshold value dor delay is set to 1s. Thus queries that require more the 1 second to process in the application are only logged.
	
  5. Currently the application dumps the queries with response time longer than the threshold in a file and prints out the content of the file if the getAPIStats endpoint is invoked.

  6.  For testing purposes, it was easier to create a client side python script and test. Thus the test.sh script only execute the ip.py script(the client side script) I had also test the appliaction using a script using curl and it worked perfectly fine.

  7. The application establishes a connection to monogodb to store the query statistic on a public monogodb database. 

====================================================
      III. Technology and Implementation
====================================================
  1. The application uses simple "BaseHTTPServer" python module instead of Flask or any other module to make it as light as possible.

  2. The base docker image used is "python:2.7-alpine" as it has a very small footprint size( of just around 75Mbytes). The the appliaction size after packaging is within 80 Mbytes


====================================================
               IV. Hacks
====================================================
  1. The application requires the instance/docker IP over whicht the application is running. In an production environment this can be configured using some deployment/configuration tool like Jenkins/Ansible. However to ensure this application runs on any machine for testing purposes, the IP of application is set to 0.0.0.0.
  
  2. In order to use a central database, I created a mongodb container and tried to link all the application containers to the common mongodb data base. However, the connection between the two required troubleshooting. So for proof of concept, I have used a public mongodb db.