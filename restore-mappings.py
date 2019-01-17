#!/usr/bin/env python
# Usage: python restore-mappings.py mappings.json
# This script removes the broken Lambda triggers for the tables and functions specified in mappings.json 
# and then enables Dynamodb streams with the specified type and creates the desired Lambda triggers.
import boto3
import botocore.session
import sys
import json
import time

filename = sys.argv[1]
#Read JSON data into the params variable
if filename:
    with open(filename, 'r') as f:
        params = json.load(f)

region = params["region"]
clientlm = boto3.client('lambda')
clientdb = boto3.client('dynamodb')
clientstream = boto3.client('dynamodbstreams')
session = botocore.session.get_session()
flist = clientlm.list_functions()
mappings = clientlm.list_event_source_mappings()
m = len(mappings['EventSourceMappings'])


def checkstream(a):
    strchk = clientstream.describe_stream(
        StreamArn=a )
    status = strchk['StreamDescription']['StreamStatus']
    return status

def checkmapping(b,c):
    mapchk = clientlm.list_event_source_mappings(
        EventSourceArn=b,
        FunctionName=c )
    status = len(mapchk['EventSourceMappings'])
    return status

# Delete all the broken event source mappings belonging to the tables listed in the json file
if (m != 0):
    print("Cleaning up the broken Event Source mappings:")
    print(" ")
    for i in range(m):
        uuid = mappings['EventSourceMappings'][i]['UUID']
        state =  mappings['EventSourceMappings'][i]['State']
        farn = mappings['EventSourceMappings'][i]['FunctionArn']
        esarn = mappings['EventSourceMappings'][i]['EventSourceArn']
        for key in params["tables"].keys():
            if key in esarn:
                if (state == "Disabled"):
                    print("Deleting broken event source mapping uuid: {} state: {} ".format(uuid,state))
                    print("Function Arn = {}".format(farn))
                    print("------------------------------")
                    clientlm.delete_event_source_mapping( UUID=uuid )
                    
# Enable the streams and ctreate event source mappings (Lambda triggers)
for key,value in params["tables"].items():
    ff = params["tables"][key]['Functions']
    print("=============================")
    print("Table: {}".format(key))
    print("=============================")
    type = params["tables"][key]['Type']
# Enable stream on table only if stream is disabled
    stream = clientstream.list_streams(
        TableName=key,
    )
    tarn = stream['Streams'][0]['StreamArn']
    stat = checkstream(tarn)
    if (stat == 'DISABLED') or (stat == 'DISABLING'):
        resp = clientdb.update_table(
            TableName=key,
            StreamSpecification={
                'StreamEnabled': True,
                'StreamViewType': type
            }
        )
        tarn = str(resp['TableDescription']['LatestStreamArn'])
        print("Enabled stream for {}, type: {} Arn {}".format(key, type, tarn))
    print(" ")
    time.sleep(5)

# Create the Lambda triggers for the DynamoDB streams
    for x in range(len(ff)):
        z = ff[x]
        mapstat = checkmapping(tarn,z)
        if (mapstat == 0 ):
            resp1 = clientlm.create_event_source_mapping(
                EventSourceArn=tarn,
                FunctionName=z,
                Enabled=True,
                BatchSize=100,
                StartingPosition='LATEST'
            )
            uuid = resp1['UUID']
            print("Created Lambda trigger UUID {} for function {}".format(uuid, ff[x]))

