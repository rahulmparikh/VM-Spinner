import ast
import boto3
import logging
import os

from common import common_functions

LOG_FILE_NAME = 'output.log'

class EC2ResourceHandler:
    """EC2 Resource handler."""

    def __init__(self):
        self.client = boto3.client('ec2')

        logging.basicConfig(filename=LOG_FILE_NAME,
                            level=logging.DEBUG, filemode='w',
                            format='%(asctime)s %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p')
        self.logger = logging.getLogger("EC2ResourceHandler")


    # 1. Update the code to search for Amazon Linux AMI ID
    def _get_ami_id(self):
        self.logger.info("Retrieving AMI id")
        images_response = self.client.describe_images(
            Filters=[{'Name': 'architecture',
                      'Values': ['x86_64']},
                     {'Name': 'hypervisor',
                      'Values': ['xen']},
                     {'Name': 'virtualization-type',
                      'Values': ['hvm']},
                     {'Name': 'image-type',
                      'Values': ['machine']},
                     {'Name': 'root-device-type',
                      'Values': ['ebs']}
                     ],
        )
        ami_id = ''
        images = images_response['Images']
        for image in images:
            if 'Name' in image:
                image_name = image['Name']
                # Modify following line to search for Amazon Linux AMI for us-east-1
                if image_name.find("amzn-ami-hvm-2017.09.1.20180115-x86_64-gp2") >= 0:
                    ami_id = image['ImageId']
                    break
        return ami_id
    
    def _get_userdata(self):
        user_data = """
            #!/bin/bash
            yum update -y
            yum install -y httpd24 php56 mysql55-server php56-mysqlnd
            service httpd start
            chkconfig httpd on
            groupadd www
            usermod -a -G www ec2-user
            chown -R root:www /var/www
            chmod 2775 /var/www
            find /var/www -type d -exec chmod 2775 {} +
            find /var/www -type f -exec chmod 0664 {} +
            echo "<?php phpinfo(); ?>" > /var/www/html/phpinfo.php
        """
        return user_data
    
    def _get_security_groups(self):
        security_groups = []
        
        # 2. Get security group id of the 'default' security group
        response = self.client.describe_security_groups(GroupNames=['default'])
        default_security_group_id = response['SecurityGroups'][0]['GroupId']
        vpc_id = response['SecurityGroups'][0]['VpcId']

        # 3. Create a new security group
        new_security_group = self.client.create_security_group(
            GroupName='HTTP Group',
            Description='HTTP',
            VpcId=vpc_id)

        # 4. Authorize ingress traffic for the group from anywhere to Port 80 for HTTP traffic
        http_security_group_id = new_security_group['GroupId']
        response = self.client.authorize_security_group_ingress(
        GroupId= http_security_group_id,
        IpPermissions=[
            {
             'FromPort': 80,
             'ToPort': 80,  
             'IpProtocol': 'tcp',
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ])

        security_groups.append(default_security_group_id)
        security_groups.append(http_security_group_id)
        return security_groups

    def create(self):
        ami_id = self._get_ami_id()

        if not ami_id:
            print("AMI ID missing..Exiting")
            exit()

        user_data = self._get_userdata()

        security_groups = self._get_security_groups()

        response = self.client.run_instances(
            ImageId=ami_id,
            InstanceType='t2.micro',
            MaxCount=1,
            MinCount=1,
            Monitoring={'Enabled': False},
            UserData=user_data,
            SecurityGroupIds=security_groups
        )
        
        # 5. Parse instance_id from the response
        instance_id =  response['Instances'][0]['InstanceId']

        return instance_id


    # 6. Add logic to get information about the created instance
    def get(self, instance_id):
        self.logger.info("Entered get")
        # Use describe_instances call
        response = self.client.describe_instances(
            InstanceIds=[instance_id]
        )
        public_dns_name = response['Reservations'][0]['Instances'][0]['PublicDnsName']
        public_ip_address = response['Reservations'][0]['Instances'][0]['PublicIpAddress']                                
        
        print("Public Dns Name: ", public_dns_name)
        print("Public Ip Address: ", public_ip_address)

        return

    # 7. Add logic to terminate the created instance
    def delete(self, instance_id):
        self.logger.info("Entered delete")

        # Use terminate_instances call
        response = self.client.terminate_instances(
            InstanceIds=[instance_id]
        )
        
        print("Terminated!!!")
        return


def main():

    available_cloud_setup = common_functions.get_cloud_setup()
    if 'aws' not in available_cloud_setup:
        print("Cloud setup not found for aws.")
        print("Doing the setup now..")
        os.system("pip install awscli")
        os.system("aws configure")

    ec2_handler = EC2ResourceHandler()

    print("Spinning up EC2 instance")

    instance_id = ec2_handler.create()
    print("EC2 instance provisioning started")

    raw_input("Hit Enter to continue>")
    ec2_handler.get(instance_id)

    raw_input("Hit Enter to continue>")
    ec2_handler.delete(instance_id)


if __name__ == '__main__':
    main()