Introduction:- 

This is web scraping project created in python/django/D-R-F and project directory structure created by following Two scoops of django 1.8. 

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


Deployment Setup:-

Core Requirements:-

    - Ubuntu 14.04, Python 2.7.6, git 1.9.1, MongoDB 3.0.15, Jenkins 1.0, apache2 2.4, pip and virtual env 

    - Other requirement can be found in requirements/base.txt file

    - Testing requirement can be found in requirements/test.txt file


#MongoDB setup

#Create user on Admin database 

    - use admin

    - db.createUser({user: "rootiec", pwd: "iecroot", roles: ["root"]}) 


#Login with admin user 

    - mongo --port 27017 -u rootiec -p iecroot --authenticationDatabase admin

#Create Production database and user for the same

    - use prod_iec

    - db.createUser({user: "prod_iec_admin", pwd:"prod_iecpass", roles:["readWrite"]})


#Similarly create a test database and user for the same

    - use test_iec

    - db.createUser({user: "iectestadmin", pwd:"iectestpass", roles:["readWrite"]})


#Project Setup

#Create an organizational directory

    - mkdir dgft-site-scraper


#Clone GitHub repository

    - git clone https://github.com/divinedeveloper/iec-web-service.git


#Create virtual env for first time only

    - cd iec-web-service

    - virtualenv env


#Activate virtual env from second time

    - source env/bin/activate


#Install requirements for production environment

    - pip install -r requirements/production.txt



#Jenkins CI setup after logging in as admin

#make Jenkins user owner of project directory to execute job

    - cd dgft-site-scraper/

    - sudo chown -R jenkins . 

    - From Jenkins dashboard click on New Item and enter name of project

    - Select Discard old builds

    - Click on Advance -> Select Use custom workspace -> paste in directory -> /home/devuser/dgft-site-scraper/iec-web-service/

    - In soure code Mgmt select -> git -> repo Url -> https://github.com/divinedeveloper/iec-web-service.git -> Add -> enter credentials

    - In Build Triggers -> Select Poll SCM -> Schedule #EVERY 15 Minutes H/15 * * * *

    - In Build -> Add Build step -> Paste following script

        #!/bin/bash
    
        #activate virtual env
        
        source env/bin/activate
        
        #install requirements
        
        pip install -r requirements/test.txt
        
        #project directory
        
        cd iec/
        
        #run all tests with pytest
        
        pytest -v --ds=iec.settings.test
        
        py.test --cov-report term --cov iec_lookup

    - Save the Project configuration

    - Click Build Now to manually trigger job and see Console output to view passing tests and test coverage


#Apache2 webserver configuration setup

#Configure following WSGIPython path in /etc/apache2/apache2.conf

    - WSGIPythonPath /home/devuser/dgft-site-scraper/iec-web-service/iec:/home/devuser/dgft-site-scraper/iec-web-service/env/lib/python2.7/site-packages


#Configure following in /etc/apache2/sites-available/000-default.conf

    - ServerName my-server-ip-or-domain
    
    - ServerAlias my-server-ip-or-domain
    
    - WSGIScriptAlias / /home/devuser/dgft-site-scraper/iec-web-service/iec/iec/production.wsgi

        <Directory /home/devuser/dgft-site-scraper/iec-web-service/iec>
    
            <Files production.wsgi>
        
                Require all granted
            
            </Files>
        
        </Directory>
    
    
    

#Restart apache2

    - sudo service apache2 restart


#Access REST API's through Postman

    - https://www.getpostman.com/collections/7466a35cef3d58830742

#Further Enhancements(Subjective):-

- From Functionality Perspective:- 

    1. If we could get Excel/CSV file with only IEC numbers and Names, we could enhance this service to automatically read each iec no. and name, poll and fetch data from dgft, parse and save in db.

    2. We could use scrapy to crawl and parse sites like tradegeniusindia to create an IEC datastore

    3. A cron job can run to fetch iec details if dgft site was down.

    4. As lot of html data needs to be parsed, we can implement a RabbitMQ to queue parsing tasks and can also be used in conjuction with cronjob

- From Performance Perspective:- 

    1. Redis cache can be used to cache data which will hardly change

    2. If iec data increases, we can implement ElasticSearch along with current mongoDB indexes. 

- From Architecture Perspective:-

    1. On heavy load , we can span another instance of this microservice as explained in architecture diagram.



