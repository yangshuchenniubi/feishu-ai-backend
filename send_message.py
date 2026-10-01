import json
import os

import requests
from dotenv import load_dotenv

from create_record import get_tenant_access_token


load_dotenv()

RECEIVER_OPEN_ID = (
    os.getenv("FEISHU_RECEIVER_OPEN_ID") or ""
).strip()


def send_text_message(token, receiver_open_id, text):
    if not receiver_open_id:
        raise RuntimeError(
            "请先在 .env 中填写 "
            "FEISHU_RECEIVER_OPEN_ID"
        )

    url = (
        "https://open.feishu.cn/open-apis/"
        "im/v1/messages"
    )

    request_body = {
        "receive_id": receiver_open_id,
        "msg_type": "text",
        # 飞书要求 content 是 JSON 字符串
        "content": json.dumps(
            {"text": text},
            ensure_ascii=False,
        ),
    }

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        params={
            "receive_id_type": "open_id",
        },
        json=request_body,
        timeout=20,
    )

    try:
        result = response.json()
    except ValueError:
        raise RuntimeError(
            f"飞书返回了非 JSON 错误：HTTP {response.status_code}"
        )

    if response.status_code != 200 or result.get("code") != 0:
        raise RuntimeError(
            f"HTTP {response.status_code}，"
            f"飞书错误码：{result.get('code')}，"
            f"错误信息：{result.get('msg')}"
        )

    return result.get("data", {})


def main():
    token = get_tenant_access_token()

    message_text = (
        "【测试通知】\n"
        "飞书智能管理系统的消息接口已经连接成功。\n"
        "这是一条由 Python 程序发送的测试消息。"
    )

    result = send_text_message(
        token,
        RECEIVER_OPEN_ID,
        message_text,
    )

    print("飞书消息发送成功！")
    print("message_id =", result.get("message_id"))


if __name__ == "__main__":
    main()