import json
import email
import boto3
import os
import re

def put_s3(bucket_name,file_name,body):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    obj = bucket.Object(file_name)
    if type(body) is not str:
        body = json.dumps(followerList, ensure_ascii=False,
                                indent=4).encode('utf-8')
    return obj.put(
        Body=body,
        ContentEncoding='utf-8',
        ContentType='text/html'
    )

def send_sns_topic(topic_arn,message,subject):
    client = boto3.client('sns')
    response = client.publish(
        TopicArn = topic_arn,
        Message = message,
        Subject = subject
    )

def send_sqs_message(queue_name, msg):
    queue = boto3.resource("sqs").get_queue_by_name(QueueName=queue_name)
    response = queue.send_message(MessageBody=msg)
    return response


def lambda_handler(event, context):
    # TODO implement
    print(json.dumps(event))
    message = json.loads(event["Records"][0]["body"])
    message_id = event['Records'][0]['messageId']
    # print(message_id)

    email_body = message["content"]
    email_object = email.message_from_string(email_body)
    email_header = dict(map(lambda x:(x["name"],x["value"]),message["mail"]["headers"]))

    body_text = ""
    body_html = ""
    for part in email_object.walk():
        # ContentTypeがmultipartの場合は実際のコンテンツはさらに
        # 中のpartにあるので読み飛ばす
        if part.get_content_maintype() == 'multipart':
            continue

        # ファイル名の取得
        attach_fname = part.get_filename()
        # ファイル名がない場合は本文のはず
        if not attach_fname:
            charset = str(part.get_content_charset())
            if charset:
                body = part.get_payload(decode=True).decode(charset, errors="replace")
            else:
                body = part.get_payload(decode=True)

            if part.get_content_type() == "text/html":
                body_html += body
            elif part.get_content_type() == "text/plain":
                body_text += body
        else:
            # ファイル名があるならそれは添付ファイルなので
            # データを取得する
            attach_file_list.append({
                "name": attach_fname,
                "data": part.get_payload(decode=True)
            })
    # print(body)
    
    #もしhtmlメッセージが用意されてなかったら、textを出力
    if body_html == "":
        put_s3("linebot-pub",f"mail/{message_id}.html",body_text)
    else:
        put_s3("linebot-pub",f"mail/{message_id}.html",body_html)
    body = f"https://linebot-pub.s3-ap-northeast-1.amazonaws.com/mail/{message_id}.html"
    
    #メール解析
    # callLambdaRequestResponse("analysisMail",{"header":email_header,"body":body})

    # dynamo取得
    dynamoDB = boto3.resource("dynamodb")
    table = dynamoDB.Table("mailTransfer")
    item = table.get_item(Key={"receiveMail":email_header["To"]})
    if "Item" in item:
        defines = item["Item"]["data"]
    else:
        item = table.get_item(Key={"receiveMail":"default"})
        if "Item" in item:
            defines = item["Item"]["data"]
        else:
            defines = []
    
    print(f"defines:{defines}")

    mess = f'To：{email_header["To"]}\nFrom：{email_header["From"]}\nDate：{email_header["Date"]}\n本文：{body}'

    for define in defines:
        # メール
        if "topicName" in define and define['topicName'] == 'sendMaid':
            topic_arn = f"arn:aws:sns:ap-northeast-1:{os.environ['ACCOUNT_ID']}:{define['topicName']}"
            subject = f'メール受信:{email_header["Subject"]}'
            send_sns_topic(topic_arn,mess,subject)

        # slack
        else:
        # if "queueName" in define:
            print("slack")
            
            # format
            if "format" in define:
                if "url" in define["format"]:
                    tmp = re.findall(r'Point.+(https.+)\r\n', body)
                    if len(tmp) > 0:
                        mess = tmp[0]
                    else:
                        tmp = re.findall(r'(https.+)\r\n', body)
                        if len(tmp) > 0:
                            mess = tmp[0]
        
            value = define
            value["message"] = mess
            topic_arn = f"arn:aws:sns:ap-northeast-1:{os.environ['ACCOUNT_ID']}:{define['topicName']}"
            subject = f'メール受信:{email_header["Subject"]}'
            send_sns_topic(topic_arn,json.dumps(value),subject)

    return {
        'statusCode': 200
    }
