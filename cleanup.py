import boto3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def cleanup_aws_resources():
    print("Starting cleanup process...")
    
    # Initialize AWS clients
    ecs = boto3.client('ecs')
    ecr = boto3.client('ecr')
    
    # 1. Update service to 0 tasks
    print("Scaling down ECS service...")
    try:
        ecs.update_service(
            cluster='code-explainer-cluster',
            service='code-explainer-service',
            desiredCount=0
        )
    except Exception as e:
        print(f"Warning: Could not scale down service: {str(e)}")
    
    # 2. Delete the service
    print("Deleting ECS service...")
    try:
        ecs.delete_service(
            cluster='code-explainer-cluster',
            service='code-explainer-service'
        )
    except Exception as e:
        print(f"Warning: Could not delete service: {str(e)}")
    
    # 3. Delete the cluster
    print("Deleting ECS cluster...")
    try:
        ecs.delete_cluster(
            cluster='code-explainer-cluster'
        )
    except Exception as e:
        print(f"Warning: Could not delete cluster: {str(e)}")
    
    # 4. Delete ECR repository
    print("Deleting ECR repository...")
    try:
        ecr.delete_repository(
            repositoryName='code-explainer',
            force=True
        )
    except Exception as e:
        print(f"Warning: Could not delete repository: {str(e)}")
    
    print("Cleanup completed!")

if __name__ == '__main__':
    cleanup_aws_resources() 