# AWS IoT Greengrass V2 Example - List S3 Buckets

This archive is meant as a working example of creating a simple component for AWS IoT Greengrass V2.

This project assumes you have already followed the steps necessary to provision one or more Laird Connectivity Sentrius IG60s with AWS IoT Greengrass Version 2.

This project is based on this example:
https://docs.aws.amazon.com/greengrass/v2/developerguide/interact-with-aws-services.html

## Getting Started
1. Update the AWS GDK config file (`ListS3Buckets-python/gdk-config.json`):
```json
{
  "component": {
    "com.example.ListS3Buckets": {    # << Component name will be set to this value
      "author": "YOUR NAME",          # << Your name
      "version": "1.0.0",
      "build": {
        "build_system": "zip"
      },
      "publish": {
        "bucket": "YOUR BUCKET NAME", # << A new S3 bucket will be created starting with this name
        "region": "YOUR AWS REGION"   # << The region your Greengrass core is registered
      }
    }
  },
  "gdk_version": "1.0.0"
}
```
2. Update the recipe file (`ListS3Buckets-python/recipe.yaml`):
```yaml
---
RecipeFormatVersion: '2020-01-25'
ComponentName: com.example.ListS3Buckets  # << Component name, must match GDK config
ComponentVersion: '1.0.0'                 # << Component version, must match GDK config
ComponentDescription: A component that uses the token exchange service to list S3 buckets.
ComponentPublisher: Amazon
ComponentDependencies:
  aws.greengrass.TokenExchangeService:
    VersionRequirement: '^2.0.0'
    DependencyType: HARD
Manifests:
  - Platform:
      os: linux
    Artifacts:
      - URI: "s3://YOUR BUCKET NAME - YOUR AWS REGION - YOUR AWS ID/com.example.ListS3Buckets/1.0.0/ListS3Buckets-python.zip" # << Replace with the path to your AWS account info
        Unarchive: ZIP
    Lifecycle:
      Run: |-
        python3 -u {artifacts:decompressedPath}/ListS3Buckets-python/list_s3_buckets.py
```

**NOTE:** not included in this archive is a required directory "boto3local". This directory is meant to be created using `pip3` from the "ListS3Buckets-python" directory in this fashion:

```bash
pip3 install --target boto3local boto3
```

(Feel free to rename to local installation - just be sure to update the import)

3. When properly configured, this component can be built using:

```bash
gdk component build
```

This should not produce any errors.

4. The component then needs to be published to the S3 bucket specified in the `recipe.yaml` and `gdk-config.json` files

```bash
gdk component publish
```

This step may take 30 seconds due to the size of the `boto3` module being published to the S3 bucket. Again, this operation should not result in any erorrs.

An error such as this:
```
Failed to publish new version of component with the given configuration.
Creating private version '1.0.1' of the component 'com.example.ListS3Buckets' failed.
An error occurred (ConflictException) when calling the CreateComponentVersion operation: Component [com.example.ListS3Buckets : 1.0.1] for account [xxxxxxxxxxxx] already exists with state: [DEPLOYABLE]
```
is indicative that the version you are attempting to publish "1.0.1" already exists on the S3 bucket. The tools do not support overwriting previously published component versions, so a newer version will need to be specified and the two commands redone.

In this case, both `gdk-config.json` and `recipe.yaml` will need to have their specified versions modified from "1.0.1" to something else, like "1.0.2".

Change locations in `gdk-config.json`:
```json
{
  "component": {
    "com.example.ListS3Buckets": {
      "author": "your name here",
      "version": "1.0.1",
                 ^^^^^^^^
      "build": {
        "build_system": "zip"
      },
      "publish": {
        "bucket": "your bucket name",
        "region": "your aws region"
      }
    }
  },
  "gdk_version": "1.0.1"
                 ^^^^^^^
}
```
change location in `recipe.yaml`:
```yaml
---
RecipeFormatVersion: '2020-01-25'
ComponentName: com.example.ListS3Buckets
ComponentVersion: '1.0.1'
                  ^^^^^^^
ComponentDescription: A component that uses the token exchange service to list S3 buckets.
ComponentPublisher: Amazon
ComponentDependencies:
  aws.greengrass.TokenExchangeService:
    VersionRequirement: '^2.0.0'
    DependencyType: HARD
Manifests:
  - Platform:
      os: linux
    Artifacts:
      - URI: "s3://your bucket name - your aws region -your aws id/com.example.ListS3Buckets/1.0.1/ListS3Buckets-python.zip"
                                                                                             ^^^^^ 
        Unarchive: ZIP
    Lifecycle:
      Run: |-
        python3 -u {artifacts:decompressedPath}/ListS3Buckets-python/list_s3_buckets.py


```
5. The appropriate policy needs to be applied to give your GGv2 installation permission to access the S3 shares.

This policy will allow the same access to all S3 buckets as your AWS account:
(`S3component_policy.json`)
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:GetBucketLocation",
                "s3:ListAllMyBuckets",
                "s3:ListBucket"

            ],
            "Resource": "*"
        }
    ]
}
```
**NOTE:** This policy is meant for testing purposes only, for production components,
the policy should be more restrictive where "Resource" is concerned.

Attach this policy to your token exchange role by following these instructions:

https://docs.aws.amazon.com/greengrass/v2/developerguide/device-service-role.html#device-service-role-access-s3-bucket

6. Update the deployment configuration for your Greengrass core device to add the newly published component.

### Pycharm and PEP 8 warning
When viewing `list_s3_buckets.py` in Pycharm, it will give the following warning
due to the location of 

```python
import boto3
```

**PEP 8: E402 module level import not at top of file**

The IG60 firmware package does not include boto3, nor does it include `pip` which means
we are unable to properly install `boto3` at runtime.

Boto3 (or any module) needs to be side loaded with the component and the path env var needed to be updated to allow the main program to find it - prior to the import.

## Successful Deployment
If the deployment of the component was successful, the target device status will be "Healthy".

Output from the S3 bucket list query will be found in `/tmp/S3buckets.txt`. This file can be viewed in either via the console (if available) or by creating and sending a simple software update from EdgeIQ that contains the shell command

```bash
cat /tmp/S3buckets.txt
```

The output from this will then appear in the edge log which you can retrieve via the EdgeIQ console and viewed.

### Example Output
```
2022-01-10 18:54:03 Creating boto3 S3 client...
2022-01-10 18:54:10 Successfully created boto3 S3 client
2022-01-10 18:54:10 Listing S3 buckets...
2022-01-10 18:54:11 Creation Date: 2021-Sep-01, Bucket Name: xxxxxxxxx
...
2022-01-10 18:54:11 Successfully listed S3 buckets
```