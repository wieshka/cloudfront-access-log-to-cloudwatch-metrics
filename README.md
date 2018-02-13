Cloudfront access logs to CloudWatch custom metrics
====

CloudFront has some nice statistics burried within console, unfortunetly no programmatical access to those data or exposure to CloudWatch is offered.
But I wanted to complement our Grafana based monitoring with some metrics from data available only via console. 

As CloudFront offers to push it's accesss logs to S3 bucket of your choise, a little utility handling this data can fill the metrics gap.

Contents
----
- app.py - little & easy to extend Lambda function taking access logs as input and pushing per line entries to CloudWatch
- sam.yml - Serverless Application Model template, head to their doc to get started with deployment.

Features
----
- Adds to CloudWatch metrics for Hit / RefreshHit / Miss / LimitExceeded / CapacityExceeded / Error / Redirect count, can be later seen as SampleCount in graphs;
- Tracks CloudFront time-taken latency

Note
----
- This SAM template will deploy CloudFormation stack which will consist of Lambda Function and S3 Bucket + suplimentary stuff like execution roles, etc.
- It is expected, that once this stack is deployed, CloudFront access logs should be configured to be pushed to created S3 Bucket.  