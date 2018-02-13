Cloudfront access logs to CloudWatch custom metrics
====

CloudFront has some nice statistics burried within console, unfortunetly no programmatical access to those data or exposure to CloudWatch is offered.
But I wanted to complement our Grafana based monitoring with some metrics from data available only via console. 

As CloudFront offers to push it's accesss logs to S3 bucket of you choise, a little utility handling this data can fill the metrics gap.

Contents
----
- app.py - little & easy to extend Lambda function taking access logs as input and pushing per line entries to CloudWatch
- sam.yml - Serverless Application Model template, head to their doc to get started with deployment.