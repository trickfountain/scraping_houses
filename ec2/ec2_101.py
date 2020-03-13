#!/usr/bin/env python

'''
    Short library of basic functions to programatically interact
        with EC2 instance.
        
    To run test and mess around use ec2_sandbox.py
''' 

# Imports and assignments
import boto3
import os
from botocore.exceptions import ClientError
ec2 = boto3.client('ec2')
instance_id = os.getenv('ec2_id')

# DESCRIBE_INSTANCES
def describe_instances():
    response = ec2.describe_instances()
    for instance in response.get('Reservations')[0].get('Instances'):
        print(
            f'id: {instance.get("InstanceId")}\n',
            f'status: {instance.get("State").get("Name")}\n',
            f'Zone: {instance.get("Placement").get("AvailabilityZone")}\n',
            f'PublicDnsName: {instance.get("PublicDnsName")}\n',
    )

# CREATE new instance
    # ImageId for CentOS-7 is :  ami-0f2b4fc905b0bd1f1. Subscription is required
    
def create_instance(ImageId='ami-0f2b4fc905b0bd1f1', InstanceType='t2.micro'):

    print(f'Creating new instance from image id {ImageId}')

    instance = ec2.create_instances(
        ImageId=ImageId,
        MinCount=1,
        MaxCount=1,
        InstanceType=InstanceType
    )
    print(f'Creation successful, instance id is {instance[0].id}')


# START
def ec2_start(instance_id=None):
    ''' Starts ec2 instance.
    Default is instace_id = os.getenv(ec2_id)
    '''
    if not instance_id:
        instance_id = os.getenv('ec2_id')
    
    if instance_id == None:
        print('Could not find instance id, aborting')
        return None
    
    print(f'Trying to start instance {instance_id}')
    
    try: 
        response = ec2.start_instances(InstanceIds=[instance_id])
        print(response)
    except ClientError as e:
        print(e)

# STOP

def ec2_stop(instance_id=None):
    
    print(f'Stoping instance {instance_id}')
    try: 
        response = ec2.stop_instances(InstanceIds=[instance_id])
        print(response)
    except ClientError as e:
        print(e)

# # Terminate aka DELETE
# print(f"Turning off instance {instance_id}")
# instance = ec2.Instance(instance_id)
# response = instance.terminate()
# print(response)


## Troubleshooting

# # Print full response
# response = ec2.describe_instances()
# import pprint
# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(response)
