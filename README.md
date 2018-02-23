Cloudfront access logs to CloudWatch custom metrics
====

CloudFront has some nice statistics burried within console, unfortunetly neither programmatical access to those data or exposure to CloudWatch is offered out of the box. 
Let's say you want to compliment your existing monitoring data for CloudFront distribution with some nice data which are available only within web console. This SAM Lambda will allow you to do that. 

CloudFront offers to push it's accesss logs to S3 bucket of your choise, this Lamba will pick them up and convert to CloudWatch metrics.

Contents
----
- app.py - simple & easy to extend [Lambda](https://aws.amazon.com/lambda/), which gets triggered by S3 PUT event when access logs are being parked at S3.
- template.yml - [Serverless Application Model](https://github.com/awslabs/serverless-application-model) template file, works just fine with [AWS SAM Local](https://github.com/awslabs/aws-sam-local/).

Features
----
- Currently extracts from log files count per *x-edge-response-result-type* - _Hit / RefreshHit / Miss / LimitExceeded / CapacityExceeded / Error / Redirect count_. This allows to visualize event count per second as SampleCount;
- That should give fairly good idea how to extract other desired data from access log;

Install
----
- Create S3 bucket for code or specify existing one in next step (CodeUri): `aws s3 mb s3://<bucket-name-where-code-should-be-stored>`. That's something you need to work normally with [sam](https://github.com/awslabs/aws-sam-local/);
- Upload code, generate CloudFormation: `sam package --template-file template.yml --s3-bucket <bucket-name-where-code-should-be-stored> --output-template-file cloudformation.yml`
- Deploy CloudFormation stack: `aws cloudformation deploy --template-file path/to/cloudformation.yml --stack-name <cf-stack-name> --capabilities CAPABILITY_IAM`
- Configure yout CloudFront distriubtion to write logs to just deployed S3 bucket by enabling Logging under it's generic settings
- If all is good, you should see something like this in CloudWatch logs (for Lambda): `Access log XXXXXXXXXXXXXX.2018-02-23-19.bd7ae1f4.gz originating from targetbucket-xxxxxxx with 22347 lines was parsed and pushed to CloudWatch`
- If for some reason (extending?) you need to install any additional Python packages, the absolutely easiest approach will be adding them to _requirements.txt_ and executing: `pip install -r requirments.txt -t .` within repo root directory.

Note
----
- This SAM template will deploy CloudFormation stack which will consist of Lambda Function and S3 Bucket + suplimentary stuff like execution roles, etc. You can find under CloudFormation Resources what exactly was deployed.
- It is expected, that once this stack is deployed, CloudFront access logs should be configured to be pushed to created S3 Bucket. 
- Consider need to improve performance of this Lambda otherwise for very busy CloudFront distributions, you might reach timeout. Current performance is about 0.83 lines of CSV per ms aka 25 000 lines takes ~30 seconds of Lambda exec time.
- Mind quite allowing policies given to Lambda, in more strict environment that should be modified.
- _CSV_FIELDS_ lists all CSV fields with it's order number and description - for your convinience to extend or if you desire to switch to csv.DictRead
 
Seeing is believing
----
![Screenshot from Grafana](screenshot.png)
![Screenshot from CloudWatch metrics](screenshot2.png)
- normally I observe 5-15 min floating delay for data with this approach


Testing locally
----
- you will need [AWS SAM Local](https://github.com/awslabs/aws-sam-local/)
- `sam local generate-event s3 > event.json`
- modify your event.json to match existing S3 bucket with actual access log file key
- `sam local invoke -e event.json`