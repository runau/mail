bash build-lambda.sh receive-mail backet-for-cloudformation-dev dev slackBotRole
bash build-lambda.sh send-slack backet-for-cloudformation-dev dev slackBotRole
bash build-sns-to-lambda.sh receive-mail send-slack backet-for-cloudformation-dev dev
