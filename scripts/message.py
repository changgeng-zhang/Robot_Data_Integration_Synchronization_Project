# message.py
import base64
import hashlib
import hmac
import json
import smtplib
import urllib.parse
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests

from scripts import utils
from scripts.config import ConfigManager
from scripts.enums import MessageType, BusinessType

config_manager = ConfigManager(None)


def send_dingtalk_message(content, phone_list=None):
    """
    构建钉钉消息内容
    :param content: 消息内容
    :param phone_list: @人群
    :return:
    """
    message_url, message_secret = config_manager.get_dingtalk_message()
    timestamp = utils.get_timestamp()
    secret_enc = message_secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, message_secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    url = f"{message_url}&timestamp={timestamp}&sign={sign}"
    post_json = {
        "msgtype": "text",
        "text": {
            "content": content
        },
        "at": {
            "atMobiles": phone_list,
            "isAtAll": False
        }
    }
    data = json.dumps(post_json).encode("utf-8")
    res = requests.post(url=url, data=data, headers=utils.get_headers())
    # 钉钉消息是否发送成功暂不处理
    return res.text


def send_email(sender_email, email_password, receiver_email, subject, body):
    """
    构建邮件内容
    :param sender_email: 发件人邮箱
    :param email_password: 发件人邮箱密码（注意：这里使用的是授权码而不是登录密码）
    :param receiver_email: 收件人邮箱
    :param subject: 邮件主题
    :param body: 邮件内容
    :return:
    """
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # 使用SMTP_SSL连接，端口号为465
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            # 登录邮箱
            server.login(sender_email, email_password)
            # 发送邮件
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("邮件发送成功！")
    except Exception as e:
        print(f"邮件发送失败，错误信息：{e}")


class MessageSender:
    """
    消息处理类
    """

    def __init__(self, message_type, business_type, message_level):
        self.message_type = message_type
        self.business_type = business_type
        self.message_level = message_level

    def send_message(self, message_text):
        """
        发送消息的方法。
        :param message_text: 消息文本，即要发送的消息内容。
        """
        # 获取当前时间
        current_time = datetime.now()
        # 指定日期时间格式
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")
        org_name = config_manager.get_org_name()
        device_identifier = config_manager.get_device_identifier()
        business = BusinessType.find_name_by_member(self.business_type)
        if org_name is None:
            return
        formatted_message_text = f"{formatted_time} {self.message_level.name.upper()} {org_name} {device_identifier} [{business}] \n {message_text}"
        print(formatted_message_text)
        if self.message_type == MessageType.EMAIL:
            print("EMAIL消息类型暂未实现。")
        elif self.message_type == MessageType.DINGTALK:
            send_dingtalk_message(formatted_message_text, None)
        else:
            print("消息类型暂未开放。")
