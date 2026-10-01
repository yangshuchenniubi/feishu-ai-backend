import argparse

from create_record import get_tenant_access_token
from read_all_records import read_all_records


def query_records(records, department=None, status=None, role=None):
    results = []

    for record in records:
        fields = record.get("fields", {})

        # 排除空记录
        if not fields.get("人员编号"):
            continue

        if department and fields.get("部门名称") != department:
            continue

        if status and fields.get("提交状态") != status:
            continue

        if role and fields.get("角色") != role:
            continue

        results.append(record)

    return results


def main():
    parser = argparse.ArgumentParser(description="查询飞书多维表格记录")

    parser.add_argument(
        "--department",
        help="部门名称，例如：技术部",
    )
    parser.add_argument(
        "--status",
        help="提交状态，例如：已交",
    )
    parser.add_argument(
        "--role",
        help="人员角色，例如：基层学生",
    )

    args = parser.parse_args()

    token = get_tenant_access_token()
    all_records = read_all_records(token)

    results = query_records(
        all_records,
        department=args.department,
        status=args.status,
        role=args.role,
    )

    print()
    print(f"符合条件的记录共 {len(results)} 条：")
    print()

    for record in results:
        fields = record.get("fields", {})

        print(
            f"{fields.get('人员编号')} | "
            f"{fields.get('姓名')} | "
            f"{fields.get('部门名称')} | "
            f"{fields.get('角色')} | "
            f"{fields.get('提交状态')}"
        )

    if not results:
        print("没有找到符合条件的记录。")


if __name__ == "__main__":
    main()