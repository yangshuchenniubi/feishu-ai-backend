import requests

from create_record import (
    APP_TOKEN,
    TABLE_ID,
    get_tenant_access_token,
)


def read_all_records(token):
    url = (
        "https://open.feishu.cn/open-apis/bitable/v1/apps/"
        f"{APP_TOKEN}/tables/{TABLE_ID}/records"
    )

    all_records = []
    page_token = None
    page_number = 1

    while True:
        params = {
            # 故意每页只取2条，用来测试分页
            "page_size": 2,
        }

        if page_token:
            params["page_token"] = page_token

        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            params=params,
            timeout=20,
        )
        response.raise_for_status()

        result = response.json()
        if result.get("code") != 0:
            raise RuntimeError(f"读取第 {page_number} 页失败：{result}")

        data = result.get("data", {})
        records = data.get("items", [])
        all_records.extend(records)

        print(f"第 {page_number} 页：读取 {len(records)} 条")

        if not data.get("has_more"):
            break

        page_token = data.get("page_token")
        if not page_token:
            raise RuntimeError("接口显示还有下一页，但没有返回 page_token")

        page_number += 1

    return all_records


def main():
    token = get_tenant_access_token()
    records = read_all_records(token)

    valid_records = [
        record
        for record in records
        if record.get("fields", {}).get("人员编号")
    ]

    print()
    print(f"接口总共返回：{len(records)} 条")
    print(f"排除空记录后：{len(valid_records)} 条")
    print()

    for record in valid_records:
        fields = record.get("fields", {})
        print(
            record.get("record_id"),
            fields.get("人员编号"),
            fields.get("姓名"),
        )


if __name__ == "__main__":
    main()