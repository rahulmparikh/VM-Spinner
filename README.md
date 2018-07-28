Project Goal
-------------

This is a Python program that spins up a EC2 instance and configures it with user data

Steps to get started
--------------------

1) Create virtual environment

   $ virtualenv venv

   $ source venv/bin/activate

2) Install requirements in the virtual environment

   $ pip install -r requirements.txt

3) Setup PYTHONPATH

   $ export PYTHONPATH=.:$PYTHONPATH

4) Do AWS setup as outlined below

5) $ python VM/ec2_handler.py


AWS setup
-----------

1) if you dont have aws account Sign up for AWS

2) Add AWS IAM user:
   Login to AWS Dashboard -> My Security Credentials -> Continue to Security Credentials -> Users -> Add User

3) Add permission to the user created:
   Select user -> Add permissions -> Attach existing policies directly -> Search for "AmazonEC2FullAccess"

4) Do AWS setup in your local account to allow SDK access to AWS.
   The sample examples will guide you through the setup process. You will be asked to enter
   aws_access_key_id, aws_secret_access_key, region, and output format.
   You can find names of AWS regions at the following link:

   https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html
