# Circle CI AWS Secrets Manager connector

## About

This image is made to load AWS Secrets Manager secret value to a file which can be sourced by Circle CI.

It is Python 3 based and uses the Boto library.

## Usage in Docker

```
export KEY_ID=<your aws key id>
export ACCESS_KEY=<your aws access key>
docker run pathmotion/aws-secrets-circleci \
    --region=eu-west-1 \
    --secret my-secrets-for-circle-ci \
    --output /root/secrets.env
```

This will write a file like this to `/root/secrets.env` (as defined in the command parameters)

```
export FOO="bar"
export HELLO_CI="I am an AWS Secret"
```

This file can be directly sourced on a bash environment.

## Usage in CircleCI

Define the executor and your credentials as environment variables

```yaml
executors:
    docker:
      - image: pathmotion/aws-secrets-circleci:latest
```

Define those commands to load the secrets from AWS and inject it into the env vars of a job

```yaml
commands:
  aws-secrets-load:
    description: Load secrets from an AWS Secrets Manager secret entry
    parameters:
      secret_name:
        type: string
        default: my-secret-from-aws
      aws_region:
        type: string
        default: eu-west-1
      filename:
        type: string
    steps:
      - attach_workspace:
          at: /secrets
      - run:
          command: |
            echo 'export KEY_ID="$AWSSM_KEY_ID"' >> $BASH_ENV
            echo 'export ACCESS_KEY="$AWSSM_ACCESS_KEY"' >> $BASH_ENV
      - run: load-aws-secrets --region << parameters.aws_region >> --secret << parameters.secret_name >> --output /secrets/<< paramters.filename >>
      - persist_to_workspace:
          root: /secrets
          paths:
            - << paramters.filename >>
  
  aws-secrets-source:
    description: Read the AWS secrets manager secrets
    parameters:
      filename:
        type: string
    steps:
      - attach_workspace:
          at: .
      - run: cat ./<< paramters.filename >> >> $BASH_ENV
```

And in your jobs (here for a composer loading for example)

```yaml
 jobs:
  load-secrets:
    executor: aws-secrets
    steps:
      - aws-secrets-load:
          filename: common-secrets.env

  deps-composer:
    executor: composer
    steps:
      - aws-secrets-source:
          filename: common-secrets.env
      - composer-install

```