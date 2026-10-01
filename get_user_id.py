import os

import requests
from dotenv import load_dotenv

from create_record import get_tenant_access_token


load_dotenv()

USER_EMAIL = (os.getenv("FEISHU_USER_EMAIL") or "").strip()
USER_MOBILE = (os.getenv("FEISHU_USER_MOBILE") or "").strip()


def get_user_open_id(token):
    if not USER_EMAIL and not USER_MOBILE:
        raise RuntimeError(
            "请在 .env 中填写 "
            "FEISHU_USER_EMAIL 或 FEISHU_USER_MOBILE"
        )

    if USER_EMAIL and USER_MOBILE:
        raise RuntimeError(
            "邮箱和手机号只保留一种，请删除另一项"
        )

    request_body = {}

    if USER_EMAIL:
        request_body["emails"] = [USER_EMAIL]

    if USER_MOBILE:
        request_body["mobiles"] = [USER_MOBILE]

    response = requests.post(
        (
            "https://open.feishu.cn/open-apis/"
            "contact/v3/users/batch_get_id"
        ),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        params={
            "user_id_type": "open_id",
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

    user_list = result.get("data", {}).get("user_list", [])

    if not user_list:
        raise RuntimeError(
            "没有找到对应的飞书用户，请检查邮箱或手机号"
        )

    open_id = user_list[0].get("user_id")

    if not open_id:
        raise RuntimeError(
            "飞书返回了用户，但没有返回 open_id"
        )

    return open_id


def main():
    token = get_tenant_access_token()
    open_id = get_user_open_id(token)

    print("用户 ID 查询成功！")
    print("open_id =", open_id)
    print()
    print("请把下面一行添加到 .env：")
    print(f"FEISHU_RECEIVER_OPEN_ID={open_id}")


if __name__ == "__main__":
    main()