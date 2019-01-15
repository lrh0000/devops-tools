#!/usr/bin/env python
# This script will set up autoscaling policies for existing, newly created or restored DynamoDB tables. .
# You need to have the tables under a Cloudformation stack and you will need the Arn of a role that has the permission to modify application
# autoscaling. See (https://docs.aws.amazon.com/autoscaling/application/APIReference/API_RegisterScalableTarget.html) for details.
# Edit the sample params.json file, enter the values for RoleARN and the desired autoscaling parameters for the tables. 
# Each table is represented with a JSON object, you can add more for each table and change the table names to match your tables.
# Script will set up autoscaling policies for each table defined in the supplied parameters json file.
# Usage: python autoscale.py <STACK_NAME>

import boto3
import json
import sys
import botocore.session

stack = sys.argv[1]
filename = "params.json"
service = "dynamodb"

def dereg(response):
    response0 = client.deregister_scalable_target(
        ServiceNamespace=service,
        ResourceId=response['ScalableTargets'][x]['ResourceId'],
        ScalableDimension=response['ScalableTargets'][x]['ScalableDimension']
    )

def reg(res):
    response2 = client.register_scalable_target(
        ServiceNamespace=service,
        ResourceId=res,
        ScalableDimension="dynamodb:table:" + type[x] + "CapacityUnits",
        MinCapacity=params["tables"][key]["Min" + type[x]],
        MaxCapacity=params["tables"][key]["Max" + type[x]]
    )
    return (response2)

def policy():
    response3 = client.put_scaling_policy(
        PolicyName=stackres['StackResourceSummaries'][i]['PhysicalResourceId'] + type[x],
        PolicyType='TargetTrackingScaling',
        ResourceId=res,
        ScalableDimension="dynamodb:table:" + type[x] + "CapacityUnits",
        ServiceNamespace=service,
        TargetTrackingScalingPolicyConfiguration={
            'TargetValue': params["tables"][key]["Target"],
            'PredefinedMetricSpecification': {
                'PredefinedMetricType': "DynamoDB" + type[x] + "CapacityUtilization"
            }
        }
    )
    return(response3)

#Read JSON data into the params variable
if filename:
    with open(filename, 'r') as f:
        params = json.load(f)

role = params["RoleARN"]
region = params["Region"]
type = ["Read", "Write"]
session = botocore.session.get_session()
client = boto3.client('application-autoscaling')
clientcf = boto3.client('cloudformation')
# Pull the Resource ID's from the cf stack
stackres = clientcf.list_stack_resources(
    StackName=stack)

# Deregister any existing autoscaling targets first as a workaround to AWS Cloudformation API bug
for key,i in zip(params["tables"].keys(), range(len(params["tables"]))):
    res = str("table/" + stackres['StackResourceSummaries'][i]['PhysicalResourceId'])
    response = client.describe_scalable_targets(
        ServiceNamespace=service,
        ResourceIds=[res],
    )
    if (len(response['ScalableTargets']) != 0):
        for x in range(len(response)):
            dereg(response)
            print("deregistering {} {}".format(response['ScalableTargets'][x]['ResourceId'], response['ScalableTargets'][x]['ScalableDimension']))
            res = str("table/" + stackres['StackResourceSummaries'][i]['PhysicalResourceId'])
            print("registering {} {}".format(res,type[x]))
            reg(res)
            policy()
    else:
        # register scalable targets with the updated values pulled from the supplied json file
        for x in range(len(type)):
            res = str("table/" + stackres['StackResourceSummaries'][i]['PhysicalResourceId'])
            print("registering {} {}".format(res,type[x]))
            reg(res)
            policy()

