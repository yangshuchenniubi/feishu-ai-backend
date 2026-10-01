import json
import os

import requests
from dotenv import load_dotenv

from create_record import get_tenant_access_token


load_dotenv()

OPEN_ID = (
    os.getenv("FEISHU_RECEIVER_OPEN_ID") or ""
).strip()


def get_user_info(token):
    if not OPEN_ID:
        raise RuntimeError(
            "请先在 .env 中填写 "
            "FEISHU_RECEIVER_OPEN_ID"
        )

    url = (
        "https://open.feishu.cn/open-apis/"
        f"contact/v3/users/{OPEN_ID}"
    )

    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {token}",
        },
        params={
            "user_id_type": "open_id",
            "department_id_type": "open_department_id",
        },
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

    user = result.get("data", {}).get("user")

    if not user:
        raise RuntimeError("飞书没有返回用户信息")

    return user


def build_safe_user_info(user):
    """
    只保存项目需要的基本字段，
    不保存手机号、邮箱等敏感信息。
    """
    return {
        "name": user.get("name"),
        "open_id": user.get("open_id"),
        "user_id": user.get("user_id"),
        "union_id": user.get("union_id"),
        "employee_no": user.get("employee_no"),
        "job_title": user.get("job_title"),
        "department_ids": user.get("department_ids", []),
        "status": user.get("status"),
    }


def main():
    token = get_tenant_access_token()
    user = get_user_info(token)
    safe_user = build_safe_user_info(user)

    with open(
        "current_user.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            safe_user,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print("人员信息查询成功！")
    print("姓名：", safe_user.get("name"))
    print("职位：", safe_user.get("job_title"))
    print("部门 ID：", safe_user.get("department_ids"))
    print("结果文件：current_user.json")
    print("手机号和邮箱没有写入结果文件。")


if __name__ == "__main__":
    main()