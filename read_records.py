import os
from pprint import pprint

import requests
from dotenv import load_dotenv


load_dotenv()

APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
APP_TOKEN = os.getenv("FEISHU_APP_TOKEN")
TABLE_ID = os.getenv("FEISHU_TABLE_ID")

required = {
    "FEISHU_APP_ID": APP_ID,
    "FEISHU_APP_SECRET": APP_SECRET,
    "FEISHU_APP_TOKEN": APP_TOKEN,
    "FEISHU_TABLE_ID": TABLE_ID,
}

missing = [name for name, value in required.items() if not value]
if missing:
    raise RuntimeError(f"缺少配置：{', '.join(missing)}")


def get_tenant_access_token():
    response = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={
            "app_id": APP_ID,
            "app_secret": APP_SECRET,
        },
        timeout=15,
    )
    response.raise_for_status()

    result = response.json()
    if result.get("code") != 0:
        raise RuntimeError(f"获取 Token 失败：{result}")

    return result["tenant_access_token"]


def read_records(token):
    response = requests.get(
        (
            "https://open.feishu.cn/open-apis/bitable/v1/apps/"
            f"{APP_TOKEN}/tables/{TABLE_ID}/records"
        ),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        params={"page_size": 20},
        timeout=20,
    )
    response.raise_for_status()

    result = response.json()
    if result.get("code") != 0:
        raise RuntimeError(f"读取表格失败：{result}")

    return result.get("data", {}).get("items", [])


def main():
    token = get_tenant_access_token()
    records = [
    record
    for record in read_records(token)
    if record.get("fields", {}).get("人员编号")
]

    print(f"读取成功，共获取 {len(records)} 条记录。\n")

    for number, record in enumerate(records, start=1):
        print(f"第 {number} 条，record_id={record.get('record_id')}")
        pprint(record.get("fields", {}), sort_dicts=False)
        print("-" * 50)


if __name__ == "__main__":
    main()