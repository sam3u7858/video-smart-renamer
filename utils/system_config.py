def get_system_prompt(transcript, visual_clues, filename, user_prompt):
    """
    Generate a system prompt for naming a video file based on provided transcript, visual clues, filename, and user prompt.

    Parameters:
    transcript (str): The transcript of the video content.
    visual_clues (str): Visual clues extracted from the video.
    filename (str): The original filename of the video.
    user_prompt (str): Additional context or prompt provided by the user.

    Returns:
    str: A formatted system prompt string to guide the naming of the video file.
    """
    system_prompt = f"""
    你是一個影片命名高手。你會為一個影片檔案，檔案結尾為.mp4命名。使用者會輸入一段影片內容、文字或轉錄檔。請根據這個線索為影片命名一個好檢索、突出、清楚的標題。包含關鍵字，方便剪輯者搜尋。
    同時，為了確認檔案內容，可以提問使用者 question，這些 question 是為了確認影片的人物名稱、地點、時間等，不要問太過於籠統的問題。
    規則：
    你的檔名可以以中文、英文命名。
    並且在30個字左右，檔名需要越詳細越好，不要過於籠統。
    請保留副檔名 (.mp4)
    不使用標點符號
    若可能，檔案包含個人化用語，盡可能使用影片中出現的台詞。以方便搜尋
    格式：
        filename : <NEW FILENAME>,
        reason: <REASON>
        tags: <TAGS, SPLIT with comma>
        question: <QUESTION>
    (格式是 json 格式)
    務必遵守格式，不要有任何其他字元

    ==
    轉錄檔案：
    {transcript}
    ==
    視覺提示：
    {visual_clues}
    ==
    原本的檔名：
    {filename}
    ==
    關於影片的 context：
    {user_prompt}
    ==
    """
    return system_prompt


def get_visual_getter_prompt():
    prompt = """
    請以30字以內描述這張圖片，並且用中文回答。
    提到角色名稱時，請用「角色」稱呼。 不要提到作品名稱。
    """
    return prompt


if __name__ == "__main__":
    print(get_visual_getter_prompt())
