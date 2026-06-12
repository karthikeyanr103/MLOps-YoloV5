# SNS Notification Configuration

## Create and Subscribe

```bash
TOPIC_ARN=$(aws sns create-topic \
  --name mlops-yolov5-deployments \
  --query TopicArn \
  --output text)

aws sns subscribe \
  --topic-arn "$TOPIC_ARN" \
  --protocol email \
  --notification-endpoint you@example.com
```

Confirm the subscription from the email sent by AWS. A pending subscription
does not receive CodeBuild messages.

## CodeBuild Configuration

Set `SNS_TOPIC_ARN` to the topic ARN and allow the CodeBuild role to call
`sns:Publish` on that specific topic. The buildspec sends:

- Build started
- Deployment succeeded
- Deployment failed

For production, route CodeBuild state-change events through EventBridge so a
notification can still be sent when a build fails before the `post_build`
commands execute.

## Recommended Message Fields

Include build ID, source S3 URI, image URI, task, timestamp, deployment target,
and a link to CloudWatch logs. Do not include credentials or sensitive model
metadata in notifications.
