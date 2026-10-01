import json
from pathlib import Path

from build_summary import build_summary
from create_record import get_tenant_access_token
from llm_client import analyze_summary
from read_all_records import read_all_records
from send_message import (
    RECEIVER_OPEN_ID,
    send_text_message,
)


def save_json(file_name, data):
    output_path = Path(file_name)

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return output_path


def run_workflow():
    print("步骤 1/5：获取飞书访问凭证")
    token = get_tenant_access_token()

    print("步骤 2/5：读取全部表格记录")
    records = read_all_records(token)

    print("步骤 3/5：去重、统计并生成材料")
    summary = build_summary(records)
    save_json("daily_summary.json", summary)

    print("步骤 4/5：运行 LLM 分析适配器")
    llm_request, analysis_result, analysis_mode = analyze_summary(summary)
    save_json("llm_request.json", llm_request)
    save_json("llm_result.json", analysis_result)

    if analysis_mode == "mock":
        analysis_label = "模拟分析"
    else:
        analysis_label = "真实模型分析"

    print(f"分析模式：{analysis_label}")
    print("步骤 5/5：发送待确认通知")

    overall = summary.get("overall", {})
    notification_text = (
        "⏳【待确认】\n"
        "事项：日报材料分析\n"
        f"分析模式：{analysis_label}\n"
        f"人数：{overall.get('人数', 0)}\n"
        f"人次：{overall.get('人次', 0)}\n"
        f"已交记录：{overall.get('已交记录数', 0)}\n"
        "说明：分析结果已经生成，"
        "请人工确认后再进入正式汇总。\n"
        "结果文件：llm_result.json\n"
        "状态：pending_confirmation"
    )

    message_result = send_text_message(
        token,
        RECEIVER_OPEN_ID,
        notification_text,
    )

    print()
    print("完整工作流运行成功！")
    print("输出文件：")
    print("- daily_summary.json")
    print("- llm_request.json")
    print("- llm_result.json")
    print(
        "通知 message_id =",
        message_result.get("message_id"),
    )


def send_error_notification(token, error):
    if not token or not RECEIVER_OPEN_ID:
        return

    error_text = str(error)[:300]

    try:
        send_text_message(
            token,
            RECEIVER_OPEN_ID,
            (
                "⚠️【运行异常】\n"
                "事项：日报工作流\n"
                f"错误：{error_text}\n"
                "状态：需要检查"
            ),
        )
    except Exception:
        pass


def main():
    token = None

    try:
        run_workflow()
    except Exception as error:
        print()
        print("工作流运行失败：", error)

        try:
            token = get_tenant_access_token()
        except Exception:
            token = None

        send_error_notification(token, error)
        raise


if __name__ == "__main__":
    main()
