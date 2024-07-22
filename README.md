# LangChain API Template for AWS Lambda

This project template provides a simple way to deploy a language model API using FastAPI, LangChain, and AWS services on AWS Lambda.

## Requirements

- Docker
- AWS Account (for deploying to AWS Lambda)

## Setup

1. Clone the repository:

    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Build the Docker image:

    ```sh
    docker build -t langchain-api .
    ```

## Deployment to AWS Lambda

1. Install the AWS CLI and configure it with your credentials:

    ```sh
    aws configure
    ```

2. Build the Docker image for AWS Lambda:

    ```sh
    docker build -t langchain-api-lambda .
    ```

3. Create an ECR repository (if you don't have one):

    ```sh
    aws ecr create-repository --repository-name langchain-api
    ```

4. Tag the Docker image for your ECR repository:

    ```sh
    docker tag langchain-api-lambda:latest <aws_account_id>.dkr.ecr.<region>.amazonaws.com/langchain-api:latest
    ```

5. Push the Docker image to ECR:

    ```sh
    aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.<region>.amazonaws.com
    docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/langchain-api:latest
    ```

6. Create a Lambda function using the pushed Docker image:

    ```sh
    aws lambda create-function --function-name langchain-api \
        --package-type Image \
        --code ImageUri=<aws_account_id>.dkr.ecr.<region>.amazonaws.com/langchain-api:latest \
        --role <your_lambda_execution_role_arn>
    ```

## Usage

Once deployed, you can invoke the Lambda function via API Gateway or directly. Here is an example of a POST request to the `/chat` endpoint:

### Example Request

```json
{
    "name": "Yua"
}