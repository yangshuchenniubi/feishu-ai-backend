import json
import os
import py_compile
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

REQUIRED_ENVIRONMENT_VARIABLES = [
    "FEISHU_APP_ID",
    "FEISHU_APP_SECRET",
    "FEISHU_APP_TOKEN",
    "FEISHU_TABLE_ID",
    "FEISHU_RECEIVER_OPEN_ID",
]

REQUIRED_PYTHON_FILES = [
    "create_record.py",
    "read_records.py",
    "update_record.py",
    "read_all_records.py",
    "query_records.py",
    "batch_create_records.py",
    "batch_update_records.py",
    "build_summary.py",
    "prepare_llm_request.py",
    "get_user_id.py",
    "get_user_info.py",
    "send_message.py",
    "notification_service.py",
    "mock_llm.py",
    "llm_client.py",
    "run_workflow.py",
]

JSON_OUTPUT_FILES = [
    "daily_summary.json",
    "llm_request.json",
    "llm_result.json",
]


def check_environment_variables():
    print("一、检查环境变量")
    errors = []

    for variable_name in REQUIRED_ENVIRONMENT_VARIABLES:
        value = (os.getenv(variable_name) or "").strip()

        if value:
            print(f"[通过] {variable_name}")
        else:
            print(f"[失败] {variable_name} 未填写")
            errors.append(variable_name)

    llm_mode = (os.getenv("LLM_MODE") or "mock").strip().lower()
    if llm_mode == "mock":
        print("[通过] LLM_MODE=mock，不会调用付费模型")
    elif llm_mode == "live":
        for variable_name in ["LLM_API_URL", "LLM_API_KEY", "LLM_MODEL"]:
            if not (os.getenv(variable_name) or "").strip():
                print(f"[失败] live 模式缺少 {variable_name}")
                errors.append(variable_name)
        if not errors:
            print("[通过] LLM live 模式配置完整")
    else:
        print("[失败] LLM_MODE 只能是 mock 或 live")
        errors.append("LLM_MODE")

    return errors


def check_required_files():
    print()
    print("二、检查程序文件")
    errors = []

    for file_name in REQUIRED_PYTHON_FILES:
        if Path(file_name).exists():
            print(f"[通过] {file_name}")
        else:
            print(f"[失败] 缺少 {file_name}")
            errors.append(file_name)

    return errors


def check_python_syntax():
    print()
    print("三、检查 Python 语法")
    errors = []

    for file_path in sorted(Path(".").glob("*.py")):
        try:
            py_compile.compile(str(file_path), doraise=True)
            print(f"[通过] {file_path.name}")
        except py_compile.PyCompileError as error:
            print(f"[失败] {file_path.name}")
            print(error)
            errors.append(file_path.name)

    return errors


def check_json_files():
    print()
    print("四、检查 JSON 输出文件")
    errors = []

    for file_name in JSON_OUTPUT_FILES:
        file_path = Path(file_name)

        if not file_path.exists():
            print(f"[失败] {file_name} 不存在，请先运行 run_workflow.py")
            errors.append(file_name)
            continue

        try:
            with file_path.open("r", encoding="utf-8") as file:
                json.load(file)
            print(f"[通过] {file_name}")
        except (OSError, json.JSONDecodeError) as error:
            print(f"[失败] {file_name}：{error}")
            errors.append(file_name)

    return errors


def main():
    all_errors = []
    all_errors.extend(check_environment_variables())
    all_errors.extend(check_required_files())
    all_errors.extend(check_python_syntax())
    all_errors.extend(check_json_files())

    print()
    print("=" * 50)

    if all_errors:
        print(f"自检未通过，共发现 {len(all_errors)} 个问题。")
        print("请修复以上标记为[失败]的项目。")
        raise SystemExit(1)

    print("项目自检全部通过！")
    print("未输出任何 App Secret、API Key 或 Token。")


if __name__ == "__main__":
    main()
