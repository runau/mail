# ↓ここ書き換える 
in_source=$1
out_source=$2
bucket_name=$3
env=$4
# ↑ここ書き換える 
template_name="sns-to-lambda"
packaged_name="./packaged.yaml"
stack_name="$template_name-$in_source-$out_source-$env"
param="Env=$env OutSource=$out_source InSource=$in_source"
aws cloudformation package --template-file ./template-$template_name.yaml --s3-bucket $bucket_name --output-template-file $packaged_name
aws cloudformation deploy --template-file $packaged_name --stack-name $stack_name --parameter-overrides $param
