import argparse
from datetime import datetime

from create_record import get_tenant_access_token
from send_message import (
    RECEIVER_OPEN_ID,
    send_text_message,
)


NOTIFICATION_TYPES = {
    "completed": {
        "label": "任务完成",
        "icon": "✅",
    },
    "pending": {
        "label": "待确认",
        "icon": "⏳",
    },
    "error": {
        "label": "运行异常",
        "icon": "⚠️",
    },
    "workflow": {
        "label": "工作流提醒",
        "icon": "📌",
    },
}


def build_notification(notification_type, title, detail):
    config = NOTIFICATION_TYPES[notification_type]
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return (
        f"{config['icon']}【{config['label']}】\n"
        f"事项：{title}\n"
        f"说明：{detail}\n"
        f"时间：{current_time}\n"
        f"状态：{config['label']}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="发送飞书系统通知"
    )

    parser.add_argument(
        "--type",
        required=True,
        choices=NOTIFICATION_TYPES.keys(),
        help="通知类型",
    )
    parser.add_argument(
        "--title",
        required=True,
        help="通知标题",
    )
    parser.add_argument(
        "--detail",
        required=True,
        help="通知详情",
    )

    args = parser.parse_args()

    message = build_notification(
        args.type,
        args.title,
        args.detail,
    )

    token = get_tenant_access_token()

    result = send_text_message(
        token,
        RECEIVER_OPEN_ID,
        message,
    )

    print("系统通知发送成功！")
    print("通知类型：", NOTIFICATION_TYPES[args.type]["label"])
    print("message_id =", result.get("message_id"))


if __name__ == "__main__":
    main()