# devops-tools
Various AWS automation tools for DevOps use

# autoscale.py

This script will set up autoscaling policies for existing, newly created or restored DynamoDB tables. 
Requirements:
* You need to have the tables under a Cloudformation stack 
* and you will need the Arn of a role that has the permission to modify application  autoscaling. See the AWS documentation for the details: https://docs.aws.amazon.com/autoscaling/application/APIReference/API_RegisterScalableTarget.html

## Usage 

python autoscale.py <STACK_NAME>

* STACK_NAME is the Cloudformation stack your dynamodb tables are under.
* Edit the sample **params.json** file, enter the values for RoleARN and the desired autoscaling parameters for the tables. 
* Each table is represented with a JSON object, you can add more for each table and change the table names to match your tables.
* The script will set up autoscaling policies for each table defined in the supplied json file.
* Number of tables does not matter, you can place as many as you want. You can create different parameter files for different stacks and environments and run iterations through a bash script or integrate it into your CI/CD pipeline for restoring the autoscaling settings each time a new deployment is run on the DynamoDb stack.
