# Required IAM Permissions

Replace all account, region, bucket, project, repository, and topic placeholders
before use. Start narrow and expand only when CloudTrail or service logs show a
legitimate missing action.

## Lambda Role

Lambda needs CloudWatch logging through the managed basic execution policy and
permission to start only the deployment project:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "codebuild:StartBuild",
      "Resource": "arn:aws:codebuild:REGION:ACCOUNT_ID:project/mlops-yolov5-deploy"
    }
  ]
}
```

## CodeBuild Role

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadUploadedModels",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:GetObjectVersion"],
      "Resource": "arn:aws:s3:::mlops-yolov5-models/models/*"
    },
    {
      "Sid": "AuthenticateEcr",
      "Effect": "Allow",
      "Action": "ecr:GetAuthorizationToken",
      "Resource": "*"
    },
    {
      "Sid": "PushDeploymentImages",
      "Effect": "Allow",
      "Action": [
        "ecr:BatchCheckLayerAvailability",
        "ecr:CompleteLayerUpload",
        "ecr:InitiateLayerUpload",
        "ecr:PutImage",
        "ecr:UploadLayerPart"
      ],
      "Resource": "arn:aws:ecr:us-east-1:107072320163:repository/mlops-yolov5"
    },
    {
      "Sid": "PublishDeploymentStatus",
      "Effect": "Allow",
      "Action": "sns:Publish",
      "Resource": "arn:aws:sns:us-east-1:107072320163:mlops-yolov5-deployments"
    },
    {
      "Sid": "WriteBuildLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:us-east-1:107072320163:log-group:/aws/codebuild/mlops-yolov5-deploy:*"
    }
  ]
}
```

If CodeBuild source is stored in S3, add `s3:GetObject` for that exact source
location. Add `secretsmanager:GetSecretValue` for the Hugging Face token secret
and configure `HF_TOKEN` with type `SECRETS_MANAGER`.

## Trust Policies

The Lambda role trusts `lambda.amazonaws.com`; the CodeBuild role trusts
`codebuild.amazonaws.com`. Do not reuse developer administrator credentials as
service roles.
