import json
from collections import defaultdict
from datetime import datetime

from create_record import get_tenant_access_token
from read_all_records import read_all_records


def format_date(timestamp_ms):
    if not timestamp_ms:
        return None

    return datetime.fromtimestamp(
        timestamp_ms / 1000
    ).strftime("%Y-%m-%d")


def deduplicate_records(records):
    """
    同一个人在同一天出现多条记录时，只保留最后一条。
    去重依据：人员编号 + 工作日期
    """
    deduplicated = {}

    for record in records:
        fields = record.get("fields", {})
        person_id = fields.get("人员编号")
        work_date = fields.get("工作日期")

        if not person_id:
            continue

        key = (person_id, work_date)
        deduplicated[key] = record

    return list(deduplicated.values())


def build_summary(records):
    valid_records = [
        record
        for record in records
        if record.get("fields", {}).get("人员编号")
    ]

    deduplicated_records = deduplicate_records(valid_records)

    department_stats = defaultdict(
        lambda: {
            "人员编号": set(),
            "记录数": 0,
            "已交记录数": 0,
        }
    )

    normalized_records = []

    for record in deduplicated_records:
        fields = record.get("fields", {})

        person_id = fields.get("人员编号")
        department = fields.get("部门名称") or "未填写部门"
        status = fields.get("提交状态")

        department_stats[department]["人员编号"].add(person_id)
        department_stats[department]["记录数"] += 1

        if status == "已交":
            department_stats[department]["已交记录数"] += 1

        normalized_records.append(
            {
                # 保留飞书原始记录ID，方便后续追溯
                "source_record_id": record.get("record_id"),
                "记录编号": fields.get("记录编号"),
                "人员编号": person_id,
                "姓名": fields.get("姓名"),
                "部门编号": fields.get("部门编号"),
                "部门名称": department,
                "角色": fields.get("角色"),
                "是否为骨干": fields.get("是否为骨干"),
                "工作日期": format_date(fields.get("工作日期")),
                "日志内容": fields.get("日志内容"),
                "成果出处": fields.get("成果出处"),
                "提交状态": status,
                "来源记录编号": fields.get("来源记录编号"),
            }
        )

    normalized_records.sort(
        key=lambda item: (
            item.get("工作日期") or "",
            item.get("人员编号") or "",
        )
    )

    departments = {}

    for department, stats in sorted(department_stats.items()):
        departments[department] = {
            "人数": len(stats["人员编号"]),
            "人次": stats["记录数"],
            "已交记录数": stats["已交记录数"],
        }

    unique_people = {
        record["人员编号"]
        for record in normalized_records
        if record.get("人员编号")
    }

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "overall": {
            "接口有效记录数": len(valid_records),
            "去重后记录数": len(normalized_records),
            "人数": len(unique_people),
            "人次": len(normalized_records),
            "已交记录数": sum(
                1
                for record in normalized_records
                if record.get("提交状态") == "已交"
            ),
        },
        "departments": departments,
        "records": normalized_records,
        "notes": [
            "空记录已排除",
            "同一人员同一日期的重复记录已去重",
            "没有人员名单时，不能把无记录人员判断为未提交",
        ],
    }


def main():
    token = get_tenant_access_token()
    records = read_all_records(token)
    summary = build_summary(records)

    output_file = "daily_summary.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            summary,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("统计完成！")
    print("人数：", summary["overall"]["人数"])
    print("人次：", summary["overall"]["人次"])
    print("已交记录数：", summary["overall"]["已交记录数"])
    print("部门数量：", len(summary["departments"]))
    print("结果文件：", output_file)

    print()
    print("各部门统计：")

    for department, stats in summary["departments"].items():
        print(
            f"{department}："
            f"{stats['人数']} 人，"
            f"{stats['人次']} 人次，"
            f"{stats['已交记录数']} 条已交"
        )


if __name__ == "__main__":
    main()