Cloudfront access logs to CloudWatch custom metrics
====

CloudFront has some nice statistics burried within console, unfortunetly no programmatical access to those data or exposure to CloudWatch is offered.
But I wanted to complement our Grafana based monitoring with some metrics from data available only via console. 

As CloudFront offers to push it's accesss logs to S3 bucket of your choise, a little utility handling this data can fill the metrics gap.

This plain simple yet effective peace of Python should be easy to extend as anyone who might use this would have interest to modify this. 

Contents
----
- app.py - little & easy to extend Lambda function taking access logs as input and pushing per line entries to CloudWatch
- sam.yml - Serverless Application Model template, head to their doc to get started with deployment.

Features
----
- Adds to CloudWatch metrics for Hit / RefreshHit / Miss / LimitExceeded / CapacityExceeded / Error / Redirect count, can be later seen as SampleCount in graphs;
- Tracks CloudFront time-taken latency


Install
----
- Create bucket for code (CodeUri): `aws s3 mb s3://<bucket-name-where-code-should-be-stored>`
- Upload code, generate CloudFormation: `sam package --template-file template.yml --s3-bucket <bucket-name-where-code-should-be-stored> --output-template-file cloudformation.yml`
- Deploy CloudFormation stack: `aws cloudformation deploy --template-file path/to/cloudformation.yml --stack-name <cf-stack-name> --capabilities CAPABILITY_IAM`
- Configure yout CloudFront distriubtion to write logs to just deployed S3 bucket by enabling Logging under it's generic settings


Note
----
- This SAM template will deploy CloudFormation stack which will consist of Lambda Function and S3 Bucket + suplimentary stuff like execution roles, etc.
- It is expected, that once this stack is deployed, CloudFront access logs should be configured to be pushed to created S3 Bucket. 
- If CLoudFront bucket is quite bussy/in use, Lambda max exec time will be hit easy with this low performant/dirty trick. More proper approach is needed for heavy traffic distriubtions. For example: Lambda splits access log in chunks, PutMetrics sends items to CLoudWatch in group of 20, loop optimisations ( very ineffective loop). 