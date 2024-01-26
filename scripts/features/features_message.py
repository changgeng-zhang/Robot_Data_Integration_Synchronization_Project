import sys

from scripts.enums import MessageType, MessageLevel
from scripts.message import MessageSender

if __name__ == '__main__':
    app_id = sys.argv[1]
    business_type = sys.argv[2]
    message_text = sys.argv[3]
    MessageSender(MessageType.DINGTALK, business_type, MessageLevel.ERROR).send_message(message_text)
