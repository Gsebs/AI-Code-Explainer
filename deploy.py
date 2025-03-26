import boto3
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

def create_ecr_repository():
    ecr = boto3.client('ecr')
    try:
        response = ecr.create_repository(
            repositoryName='code-explainer'
        )
        return response['repository']['repositoryUri']
    except ecr.exceptions.RepositoryAlreadyExistsException:
        response = ecr.describe_repositories(
            repositoryNames=['code-explainer']
        )
        return response['repositories'][0]['repositoryUri']

def build_and_push_image(repository_uri):
    # Get AWS account ID
    sts = boto3.client('sts')
    account_id = sts.get_caller_identity()['Account']
    region = os.getenv('AWS_REGION', 'us-east-1')
    
    # Login to ECR
    os.system(f'aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin {account_id}.dkr.ecr.{region}.amazonaws.com')
    
    # Build and push Docker image
    os.system(f'docker build -t code-explainer .')
    os.system(f'docker tag code-explainer:latest {repository_uri}:latest')
    os.system(f'docker push {repository_uri}:latest')
    
    return f'{repository_uri}:latest'

def create_task_definition(image_uri):
    ecs = boto3.client('ecs')
    
    response = ecs.register_task_definition(
        family='code-explainer',
        networkMode='awsvpc',
        requiresCompatibilities=['FARGATE'],
        cpu='256',
        memory='512',
        containerDefinitions=[
            {
                'name': 'code-explainer',
                'image': image_uri,
                'portMappings': [
                    {
                        'containerPort': 8000,
                        'protocol': 'tcp'
                    }
                ],
                'environment': [
                    {
                        'name': 'OPENAI_API_KEY',
                        'value': os.getenv('OPENAI_API_KEY')
                    },
                    {
                        'name': 'ANTHROPIC_API_KEY',
                        'value': os.getenv('ANTHROPIC_API_KEY')
                    }
                ]
            }
        ]
    )
    
    return response['taskDefinition']['taskDefinitionArn']

def create_or_update_service(task_definition_arn):
    ecs = boto3.client('ecs')
    
    # Create cluster if it doesn't exist
    try:
        ecs.create_cluster(clusterName='code-explainer-cluster')
    except:
        pass
    
    # Create or update service
    try:
        response = ecs.create_service(
            cluster='code-explainer-cluster',
            serviceName='code-explainer-service',
            taskDefinition=task_definition_arn,
            desiredCount=1,
            launchType='FARGATE',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': ['YOUR_SUBNET_ID'],  # Replace with your subnet ID
                    'securityGroups': ['YOUR_SECURITY_GROUP_ID'],  # Replace with your security group ID
                    'assignPublicIp': 'ENABLED'
                }
            }
        )
    except ecs.exceptions.ServiceNotFoundException:
        response = ecs.update_service(
            cluster='code-explainer-cluster',
            service='code-explainer-service',
            taskDefinition=task_definition_arn,
            desiredCount=1
        )
    
    return response['service']['serviceArn']

def main():
    print("Starting deployment process...")
    
    # Create ECR repository and get URI
    print("Creating ECR repository...")
    repository_uri = create_ecr_repository()
    
    # Build and push Docker image
    print("Building and pushing Docker image...")
    image_uri = build_and_push_image(repository_uri)
    
    # Create task definition
    print("Creating task definition...")
    task_definition_arn = create_task_definition(image_uri)
    
    # Create or update service
    print("Creating/updating ECS service...")
    service_arn = create_or_update_service(task_definition_arn)
    
    print("Deployment completed!")
    print(f"Service ARN: {service_arn}")

if __name__ == '__main__':
    main() 