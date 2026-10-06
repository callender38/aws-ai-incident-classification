# AI-Enhanced Automated Incident Classification

This repository contains the implementation artifacts for the Unit 6 Choose-Your-Own AI Enhancement Project. The prototype classifies cloud incidents into compute, network, database, security, or storage and predicts P1-P4 severity. A conservative guardrail forces critical outage language to P1 and human review.

## Architecture
CloudWatch Alarm -> EventBridge -> Step Functions -> Lambda classifier -> SNS routing or human review.

## Run locally
1. Create a Python 3.12 virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Train and evaluate: `python src/train_model.py`
4. Run tests: `pytest tests/test_model.py`

## Deploy to AWS
1. Build the container image: `docker build -t ai-incident-classifier .`
2. Push the image to Amazon ECR.
3. Create an AWS Lambda function from the ECR image.
4. Create the SNS topics referenced by the Step Functions definition.
5. Create the Step Functions state machine using `config/step_functions.json` and substitute the topic ARNs.
6. Create an EventBridge rule using `config/eventbridge_rule.json` and set the state machine as the target.
7. Apply least-privilege IAM permissions. The included policy is a starting point and should be scoped to exact ARNs before production use.

## Evaluation summary
- Category accuracy: 92%
- Category macro F1: 0.918
- Hybrid severity accuracy: 84%
- Automatic route rate: 62%
- Automatic-route category accuracy: 100%

## Important limitation
The included dataset is synthetic and intended to validate the design and workflow. Production deployment requires retraining and validation on organization-specific incident data, calibrated confidence thresholds, privacy review, and ongoing drift monitoring.

## Repository
https://github.com/callender38/aws-ai-incident-classification
