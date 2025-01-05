import openai
import base64

from .config import OPENAI_API_KEY

client = openai.OpenAI(api_key=OPENAI_API_KEY)
model = "gpt-4o-mini-2024-07-18"

def summarize_table(element):
    # Prompt
    prompt_text = f"""
    # Your Role: あなたは画像で示された表をテキストに変換するアシスタントです。
    # Instructions: 画像の内容は表あるいは表に付随するテキストです。
        表をMarkdown形式に変換して示してください。

    + 回答は表のみとしてください。そのほかのコメントは省略してください。
    + 表の前後にメッセージを付加しないでください。表のみでOKです。

    Table or text chunk: {element.text}
    """
    image_base64 = element.metadata.image_base64

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt_text
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                },
            ],
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens = 1000,
        temperature=0.0,
    )

    return response

def summarize_image(element, caption):
    prompt_template = f"""
    # Your role: Document Analyst
    # Instructions for the Document Analyst: あなたの任務は会社のマニュアル
        から提供された画像を徹底的に調査し、詳細な説明を提供することです。
        以下のリストを遵守して、画像の内容とそのマニュアルにおける関連性を包括的に
        理解できるようにしてください。

    1. キャプションについて
        + キャプションをヒントにして回答を生成してください。
            + 図中に専門用語などあればキャプションと表記を統一してください。
            + キャプションはプロンプトの末尾に記載します。
            + キャプションがない場合は本項目を無視してください。

    1. 視覚的な補助および注釈
        + コンテンツをよりよく説明するために使用される視覚的な補助、矢印、注釈を指摘します。
            + 例: 矢印は手順の順序あるいは指示箇所の強調を示します。
            + 例: 注釈は各インターフェイス部分の追加の説明を示します。

    # Caption: {caption}
    """

    # with open(file_path, 'rb') as image_file:
    #     encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    image_base64 = element.metadata.image_base64
    # decoded_image = base64.b64decode(image_base64)
    # image = Image.open(io.BytesIO(decoded_image))

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt_template
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                },
            ],
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens = 1000,
        temperature=0.0,
    )

    return response
