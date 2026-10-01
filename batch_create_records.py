from datetime import datetime

import requests

from create_record import (
    APP_TOKEN,
    TABLE_ID,
    get_tenant_access_token,
)
from read_all_records import read_all_records


def build_test_records():
    now = datetime.now()
    work_date = int(
        now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000
    )
    time_text = now.strftime("%Y%m%d-%H%M%S")

    return [
        {
            "fields": {
                "记录编号": f"BATCH-{time_text}-01",
                "人员编号": "B901",
                "姓名": "批量测试一",
                "部门编号": "D901",
                "部门名称": "批量测试部",
                "角色": "基层学生",
                "是否为骨干": "否",
                "工作日期": work_date,
                "日志内容": "批量新增测试记录一",
                "成果出处": "Python 批量新增接口",
                "提交状态": "已交",
                "来源记录编号": "无",
            }
        },
        {
            "fields": {
                "记录编号": f"BATCH-{time_text}-02",
                "人员编号": "B902",
                "姓名": "批量测试二",
                "部门编号": "D901",
                "部门名称": "批量测试部",
                "角色": "基层学生",
                "是否为骨干": "否",
                "工作日期": work_date,
                "日志内容": "批量新增测试记录二",
                "成果出处": "Python 批量新增接口",
                "提交状态": "已交",
                "来源记录编号": "无",
            }
        },
    ]


def batch_create_records(token, records):
    url = (
        "https://open.feishu.cn/open-apis/bitable/v1/apps/"
        f"{APP_TOKEN}/tables/{TABLE_ID}/records/batch_create"
    )

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        json={"records": records},
        timeout=20,
    )
    response.raise_for_status()

    result = response.json()
    if result.get("code") != 0:
        raise RuntimeError(f"批量新增失败：{result}")

    return result.get("data", {}).get("records", [])


def main():
    token = get_tenant_access_token()

    existing_records = read_all_records(token)
    existing_person_ids = {
        record.get("fields", {}).get("人员编号")
        for record in existing_records
    }

    test_records = build_test_records()

    records_to_create = [
        record
        for record in test_records
        if record["fields"]["人员编号"] not in existing_person_ids
    ]

    if not records_to_create:
        print("B901 和 B902 已经存在，无需重复创建。")
        return

    created_records = batch_create_records(token, records_to_create)

    print()
    print(f"批量新增成功，共新增 {len(created_records)} 条：")

    for record in created_records:
        fields = record.get("fields", {})
        print(
            record.get("record_id"),
            fields.get("人员编号"),
            fields.get("姓名"),
        )


if __name__ == "__main__":
    main()