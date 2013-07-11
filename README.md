CloudRoast, CloudCAFE Test Repo
================================
<pre>
 (----) (----)--)
  (--(----)  (----) --)
(----) (--(----) (----)
-----------------------
\                     /
 \                   /
  \_________________/    
     )\ `   `(` `
     ( ) ` )' )  \_
    (   )  _)  \   )
  ) )   (_  )   ,  (
  (  ,  )   (   (
    (  (    )    )
  === CloudRoast ===
= A CloudCAFE Test Repository =
</pre> 

CloudRoast is a rich, full bodied blend of premium roasted automated test cases. CloudRoast tests are based on the expanded unittest driver in the 
[Open CAFE Core](https://github.com/stackforge) and built using the [CloudCAFE Framework](https://github.com/stackforge).
 
CloudRoast tests support smoke, functional, integration, scenario and reliability based test cases for OpenStack. It is meant to be highly flexible 
and leave the logic of the testing in the hands of the test case developer while leaving the interactions with OpenStack, various resources and 
support infrastructure to CloudCAFE.

Installation
------------
CloudRoast can be [installed with pip](https://pypi.python.org/pypi/pip) from the git repository after it is cloned to a local machine. 
 
* First follow the README instructions to install the [CloudCAFE Framework](https://github.com/stackforge)
* Clone this repository to your local machine  
* CD to the root directory in your cloned repository.
* Run "pip install . --upgrade" and pip will auto install all other dependencies.

Configuration
--------------
CloudRoast runs on the [CloudCAFE Framework](https://github.com/stackforge) using the cafe-runner. It relies on the configurations installed to: 
<USER_HOME>/.cloudcafe/configs/<PRODUCT> by CloudCAFE.

At this stage you will have the Open CAFE Core engine, the CloudCAFE Framework implementation and the Open Source automated test cases. You are now 
ready to:
1) Execute the test cases against a deployed Open Stack.
                       or
2) Write entirely new tests in this repository using the CloudCAFE Framework.

Logging
-------
If tests are executed with the built-in cafe-runner, runtime logs will be output to 
<USER_HOME>/.cloudcafe/logs/<PRODUCT>/<CONFIGURATION>/<TIME_STAMP>. 

In addition, tests built from the built-in CAFE unittest driver will generate 
csv statistics files in <USER_HOME>/.cloudcafe/logs/<PRODUCT>/<CONFIGURATION>/statistics for each and ever execution of each and every test case that 
provides metrics of execution over time for elapsed time, pass/fail rates, etc...

Basic CloudRoast Package Anatomy
-------------------------------
Below is a short description of the top level CloudRoast Packages.

##cloudroast
This is the root package for all automated tests. This is namespace is currently **required** by the cafe-runner for any Test Repository plug-in.

##identity
OpenStack Identity Service cafe-runner plug-in test cases. 

##compute
OpenStack Compute Service cafe-runner plug-in test cases. 
