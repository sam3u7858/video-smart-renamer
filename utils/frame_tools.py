from utils.llm_tools import chat_completion
import base64
from pathlib import Path
import cv2
from PIL import Image
from datetime import timedelta
from utils.system_config import get_visual_getter_prompt
visualGetterPrompt = get_visual_getter_prompt()

'''

This file is used to get the visual clues from the video file.
We will call chat_completion to get the visual clues. The default API is in the config.py
'''


class VisualClueExtractor:
    def __init__(self, client=None):
        self.client = client

    def image_to_base64(self, image_path: Path) -> str:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")

    def frame_to_base64(self, frame) -> str:
        from io import BytesIO
        import numpy as np
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame)
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def format_timestamp(self, ms: int) -> str:
        td = timedelta(milliseconds=ms)
        return str(td)[:-3]

    def call_llm_with_image(self, base64_images: list[str], system_prompt="") -> str:
        # @gemini-2.5-pro: The system prompt text is now added to the content.
        content: list[dict] = [
            {"type": "text", "text": system_prompt}
        ]

        for base64_image in base64_images:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                }
            })

        return chat_completion(self.client, [
            {
                "role": "user",
                "content": content
            }
        ])

    def get_visual_clues(self, file_path: Path, max_frames: int = 2) -> str:
        # @gemini-2.5-pro: Ensure file_path is a Path object for compatibility.
        if not isinstance(file_path, Path):
            file_path = Path(file_path)

        ext = file_path.suffix.lower()

        if ext in [".jpg", ".jpeg", ".png", ".webp"]:
            b64_img = self.image_to_base64(file_path)
            desc = self.call_llm_with_image([b64_img])
            return f"00:00:00:000,{desc.strip()}"

        elif ext in [".mp4", ".mov", ".avi", ".mkv"]:
            cap = cv2.VideoCapture(str(file_path))
            if not cap.isOpened():
                raise RuntimeError("Cannot open video file")

            total_frames_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            if fps == 0:
                raise RuntimeError("Cannot get video FPS.")

            total_ms = total_frames_count / fps * 1000

            visual_clues = []

            # @gemini-2.5-pro: Calculate timestamps for max_frames to be evenly distributed.
            if max_frames <= 1:
                timestamps = [int(total_ms / 2)]  # Take the middle frame
            else:
                timestamps = [int(total_ms * i / (max_frames - 1))
                              for i in range(max_frames)]

            print(
                f"[frame_tools] 正在為 '{file_path.name}' 提取視覺線索，共 {len(timestamps)} 個影格...")

            last_desc = ""
            for i, ts in enumerate(timestamps):
                print(f"[frame_tools] 正在處理第 {i+1}/{len(timestamps)} 個影格...")
                cap.set(cv2.CAP_PROP_POS_MSEC, ts)
                ret, frame = cap.read()
                if not ret:
                    continue
                b64_frame = self.frame_to_base64(frame)
                desc = self.call_llm_with_image(
                    [b64_frame], visualGetterPrompt).strip()

                if last_desc == "" or self.compute_similarity(desc, last_desc) < 0.8:
                    visual_clues.append(f"{self.format_timestamp(ts)},{desc}")
                    last_desc = desc
            cap.release()
            print(f"[frame_tools] '{file_path.name}' 的視覺線索提取完成。")
            return "\n".join(visual_clues)

        else:
            raise ValueError("Unsupported file type")

    def compute_similarity(self, text1: str, text2: str) -> float:
        return 0.0


'''Usage example:

簡單來說，在 Server 或是執行的程式中，我們需要使用 VisualClueExtractor 來取得視覺的提示
用法: (1) 取得 client (2) 建立 VisualClueExtractor 實例 (3) 呼叫 get_visual_clues 方法
輸出: 視覺的提示 (in python list, string)

English:
In the Server or the program, we need to use VisualClueExtractor to get the visual clues.
Usage: (1) Get the client (2) Create an instance of VisualClueExtractor (3) Call the get_visual_clues method
```python
client = get_client(mode="Local")
extractor = VisualClueExtractor(client=client)
file_path = Path("path/to/your/image_or_video")
visual_clues = extractor.get_visual_clues(file_path)
print(visual_clues)
```

@GPT-4o: Added usage example for 'VisualClueExtractor' class .
'''
