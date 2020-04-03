#!/bin/sh
lambda_name=$1
bucket_name=$2
env=$3
role_name=$4
# project=$5

template_name="lambda"
sed -e s/{{lambda_name}}/$lambda_name/ ./template-$template_name.yaml > ./template-$template_name-sed.yaml
packaged_name="./packaged.yaml"
stack_name="$template_name-`echo $lambda_name | sed s/_/-/`-$env"
param="Env=$env RoleName=$role_name"
aws cloudformation package --template-file ./template-$template_name-sed.yaml --s3-bucket $bucket_name --output-template-file $packaged_name
aws cloudformation deploy --template-file $packaged_name --stack-name $stack_name --parameter-overrides $param --capabilities CAPABILITY_IAM