import sys

from features.enums import MessageType, MessageLevel
from features.message import MessageSender

if __name__ == '__main__':
    app_id = sys.argv[1]
    business_type = sys.argv[2]
    message_text = sys.argv[3]
    MessageSender(MessageType.DINGTALK, business_type, MessageLevel.ERROR).send_message(app_id, message_text)
