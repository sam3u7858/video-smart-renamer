import os
import shutil
from pathlib import Path
import argparse
import requests

# @GPT-4o: This script renames video files based on content and copies them to an output directory.


def rename_and_copy_videos(source_dir: Path, output_dir: Path, user_prompt: str = ""):
    if not source_dir.is_dir():
        print(f"錯誤: 來源目錄 '{source_dir}' 不存在或不是一個目錄。")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    video_files = [f for f in os.listdir(source_dir) if (source_dir / f).is_file(
    ) and (source_dir / f).suffix.lower() in [".mp4", ".mov", ".avi", ".mkv"]]
    total_files = len(video_files)

    print(f"在 '{source_dir}' 中找到 {total_files} 個影片檔案。")

    for i, item in enumerate(video_files):
        file_path = source_dir / item
        print(f"\n[{i+1}/{total_files}] 正在處理檔案: {file_path.name}")

        try:
            api_url = "http://localhost:8000/upload_video/"
            payload = {"filename": str(file_path), "user_prompt": user_prompt}
            response = requests.post(api_url, params=payload)
            response.raise_for_status()

            response_data = response.json()
            new_filename_base = response_data.get('filename', '')
            reason = response_data.get('reason', '')
            tags = response_data.get('tags', '')

            if not new_filename_base:
                print(f"從 API 未能取得新檔名，跳過檔案: {file_path.name}")
                continue

            new_filename = f"{new_filename_base}{file_path.suffix.lower()}"

            # @gemini-2.5-pro: Check file size and decide to move or copy.
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > 200:
                print(f"  - 檔案大小 ({file_size_mb:.2f}MB) 超過 200MB，將直接重新命名。")
                destination_path = source_dir / new_filename
                os.rename(file_path, destination_path)
                print(
                    f"  - 檔案 '{file_path.name}' 已在來源目錄中重新命名為 '{new_filename}'.")
            else:
                destination_path = output_dir / new_filename
                shutil.copy2(file_path, destination_path)
                print(
                    f"  - 檔案 '{file_path.name}' 已複製並重新命名為 '{new_filename}' 到 '{output_dir}'.")

            print(f"  - 理由: {reason}, 標籤: {tags}")

        except requests.exceptions.RequestException as e:
            print(f"  - 呼叫 API 時發生錯誤: {e}")
        except Exception as e:
            print(f"  - 處理檔案 '{file_path.name}' 時發生錯誤: {e}")

    print("\n所有影片檔案處理完畢。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="根據影片內容重新命名並複製影片檔案。")
    parser.add_argument("--source_directory", type=str,
                        default="./test/input", help="包含影片檔案的來源目錄路徑。預設為 ./test/input")
    parser.add_argument("--output_directory", type=str,
                        default="./test/output", help="重新命名後檔案的輸出目錄路徑。預設為 ./test/output")
    parser.add_argument("--user_prompt", type=str,
                        default="", help="提供給 LLM 的額外使用者提示。")

    args = parser.parse_args()

    source_path = Path(args.source_directory)
    output_path = Path(args.output_directory)

    rename_and_copy_videos(source_path, output_path, args.user_prompt)
