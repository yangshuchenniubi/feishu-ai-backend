import os
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
APP_TOKEN = os.getenv("FEISHU_APP_TOKEN")
TABLE_ID = os.getenv("FEISHU_TABLE_ID")


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


def create_record(token):
    now = datetime.now()
    record_number = f"TEST-{now:%Y%m%d-%H%M%S}"
    work_date = int(
        now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000
    )

    fields = {
        "记录编号": record_number,
        "人员编号": "U999",
        "姓名": "接口测试",
        "部门编号": "D999",
        "部门名称": "测试部",
        "角色": "基层学生",
        "是否为骨干": "否",
        "工作日期": work_date,
        "日志内容": "这条记录由 Python 调用飞书 API 创建",
        "成果出处": "Python 接口测试",
        "提交状态": "已交",
        "来源记录编号": "无",
    }

    url = (
        "https://open.feishu.cn/open-apis/bitable/v1/apps/"
        f"{APP_TOKEN}/tables/{TABLE_ID}/records"
    )

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        json={"fields": fields},
        timeout=20,
    )
    response.raise_for_status()

    result = response.json()
    if result.get("code") != 0:
        raise RuntimeError(f"新增记录失败：{result}")

    return result["data"]["record"]


def main():
    token = get_tenant_access_token()
    record = create_record(token)

    print("新增记录成功！")
    print("record_id =", record.get("record_id"))
    print("记录编号 =", record.get("fields", {}).get("记录编号"))


if __name__ == "__main__":
    main()