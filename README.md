# devops-tools
Various AWS automation tools for DevOps use

# autoscale.py

This script will set up autoscaling policies for existing, newly created or restored DynamoDB tables. 
Requirements:
* You need to have the tables under a Cloudformation stack 
* and you will need the Arn of a role that has the permission to modify application  autoscaling. See the AWS documentation for the details: https://docs.aws.amazon.com/autoscaling/application/APIReference/API_RegisterScalableTarget.html

## Usage 

python autoscale.py FILENAME

* FILENAME is the json file where you list your tables and autoscaling parameters.
* Use the sample **params.json** file for reference, enter the values for RoleARN and the desired autoscaling parameters for the tables. 
* Each table is represented with a JSON object.
* Number of tables does not matter, you can place as many as you want. You can create different parameter files for different environments (such as dev, staging, qa) and integrate it into your CI/CD pipeline for restoring the autoscaling settings each time a new deployment is run on the Dynamodb stack or the autoscaling policies are modified.


# restore-mappings.py

This script recreates Dynamodb streams and Lambda function triggers for the Dynamodb tables after database restores. Particularly useful for automating disaster recovery and restore tests, it can be also useful for CI/CD if any major upgrades break Dynamodb streams and/or Lambda triggers, or adding new Lambda triggers and streams. It also cleans up any broken Lambda triggers left over from disaster recovery and major database upgrades.

Script will check for existing and enabled streams and Lambda triggers and create them only if they are broken or non-existing.


## Usage 

python restore-mappings.py mappings.json

* Edit mappings.json and list your tables, stream types and Lambda functions to create the triggers for the Dynamodb streams.

## Use Cases

* Restore broken Lambda triggers and streams for Dynamodb tables after disaster recovery and major upgrades
* Automate adding new Lambda triggers for Dynamodb tables without involving Cloudformation templates, saving time
* Add monitoring such as Datadog for the Dynamodb tables.
* Clean up broken Dynamodb triggers 
