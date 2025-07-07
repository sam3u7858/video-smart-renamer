import os
from openai import OpenAI

''' 用法 : 先 get_client 取得 client ，再使用 chat_completion 呼叫 API
```python
from llm_tools import get_client, chat_completion
client = get_client(mode="Local")
messages = [{"role": "user", "content": "Hello"}]
result = chat_completion(client, messages)
print(result)
```

'''


def get_client(mode="Local"):
    '''
    Get the client for the OpenAI API
    '''

    client = None
    # @bmon : Set the API key for the OpenAI API
    if (mode != "Local"):
        API_KEY = os.environ.get("API_KEY", "")
        client = OpenAI(api_key=API_KEY)
    else:
        # @gemini-2.5-pro: Use environment variable for the base URL to make it configurable in Docker.
        base_url = os.environ.get(
            "LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
        client = OpenAI(base_url=base_url,
                        api_key="lm-studio")

    return client


def chat_completion(client, messages, model="google/gemma-3-12b"):
    '''
    Call the OpenAI API to get the response
    '''
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[Error] Chat completion failed: {str(e)}"


if __name__ == "__main__":
    # Simple Test

    client = get_client(mode="Local")
    messages = [{"role": "user", "content": "Hello"}]
    result = chat_completion(client, messages)
    print(result)

    # Test with image
    image_path = "./test/sample.jpg"

    import base64

    def image_to_base64(image_path) -> str:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")

    image_base64 = image_to_base64(image_path)
    result = chat_completion(client, [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "用兩句話描述這張圖片，使用繁體中文。"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_base64}"
                    }
                }
            ]
        }
    ])

    print(result)
