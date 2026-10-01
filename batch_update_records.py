import requests

from create_record import (
    APP_TOKEN,
    TABLE_ID,
    get_tenant_access_token,
)
from read_all_records import read_all_records


def find_batch_test_records(token):
    records = read_all_records(token)
    target_person_ids = {"B901", "B902"}

    matched_records = []

    for record in records:
        fields = record.get("fields", {})

        if fields.get("人员编号") in target_person_ids:
            matched_records.append(
                {
                    "record_id": record["record_id"],
                    "person_id": fields["人员编号"],
                }
            )

    return matched_records


def batch_update_records(token, matched_records):
    url = (
        "https://open.feishu.cn/open-apis/bitable/v1/apps/"
        f"{APP_TOKEN}/tables/{TABLE_ID}/records/batch_update"
    )

    records_to_update = []

    for record in matched_records:
        person_id = record["person_id"]

        records_to_update.append(
            {
                "record_id": record["record_id"],
                "fields": {
                    "日志内容": f"{person_id} 已通过 Python 批量修改",
                    "成果出处": "Python 批量修改接口",
                    "提交状态": "已交",
                },
            }
        )

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        json={"records": records_to_update},
        timeout=20,
    )
    response.raise_for_status()

    result = response.json()
    if result.get("code") != 0:
        raise RuntimeError(f"批量修改失败：{result}")

    return result.get("data", {}).get("records", [])


def main():
    token = get_tenant_access_token()
    matched_records = find_batch_test_records(token)

    found_person_ids = {
        record["person_id"]
        for record in matched_records
    }

    missing_person_ids = {"B901", "B902"} - found_person_ids

    if missing_person_ids:
        missing_text = "、".join(sorted(missing_person_ids))
        raise RuntimeError(
            f"没有找到 {missing_text}，请先运行 batch_create_records.py"
        )

    updated_records = batch_update_records(token, matched_records)

    print()
    print(f"批量修改成功，共修改 {len(updated_records)} 条：")

    for record in updated_records:
        fields = record.get("fields", {})

        print(
            record.get("record_id"),
            fields.get("人员编号"),
            fields.get("日志内容"),
        )


if __name__ == "__main__":
    main()