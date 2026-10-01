import requests

from create_record import (
    APP_TOKEN,
    TABLE_ID,
    get_tenant_access_token,
)


def find_test_record(token):
    url = (
        "https://open.feishu.cn/open-apis/bitable/v1/apps/"
        f"{APP_TOKEN}/tables/{TABLE_ID}/records"
    )

    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        params={"page_size": 100},
        timeout=20,
    )
    response.raise_for_status()

    result = response.json()
    if result.get("code") != 0:
        raise RuntimeError(f"查询测试记录失败：{result}")

    records = result.get("data", {}).get("items", [])

    matching_records = [
        record
        for record in records
        if record.get("fields", {}).get("人员编号") == "U999"
    ]

    if not matching_records:
        raise RuntimeError("没有找到人员编号为 U999 的测试记录")

    return matching_records[-1]["record_id"]


def update_record(token, record_id):
    url = (
        "https://open.feishu.cn/open-apis/bitable/v1/apps/"
        f"{APP_TOKEN}/tables/{TABLE_ID}/records/{record_id}"
    )

    fields = {
        "日志内容": "这条记录已经通过 Python 更新",
        "成果出处": "Python 更新接口测试",
        "提交状态": "已交",
    }

    response = requests.put(
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
        raise RuntimeError(f"修改记录失败：{result}")

    return result["data"]["record"]


def main():
    token = get_tenant_access_token()
    record_id = find_test_record(token)
    record = update_record(token, record_id)

    print("修改记录成功！")
    print("record_id =", record.get("record_id"))
    print("日志内容 =", record.get("fields", {}).get("日志内容"))
    print("成果出处 =", record.get("fields", {}).get("成果出处"))


if __name__ == "__main__":
    main()