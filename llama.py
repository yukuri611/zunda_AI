import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# 1. モデルとトークナイザーの準備
# ---------------------------------
# Hugging Face HubのモデルIDを指定
model_id = "meta-llama/Meta-Llama-3-8B-Instruct"

# トークナイザーをロード
tokenizer = AutoTokenizer.from_pretrained(model_id)

# モデルをロード
# load_in_4bit=True で4-bit量子化を有効にし、VRAM使用量を削減
# device_map="auto" で自動的にGPUを割り当てる
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    load_in_4bit=True,
)

# 2. チャット形式のプロンプトを作成
# ---------------------------------
# Llama 3 Instructモデルは特定のチャット形式に従うことで性能を発揮します。
# tokenizer.apply_chat_template を使うと、この形式を簡単に作成できます。
messages = [
    {"role": "system", "content": "You are a helpful assistant. Please respond in Japanese."},
    {"role": "user", "content": "こんにちは。"},
]

# モデルへの入力を準備
prompt = tokenizer.apply_chat_template(
    messages, 
    tokenize=False, 
    add_generation_prompt=True
)

# 3. テキスト生成パイプラインの作成と実行
# ---------------------------------
# Hugging Faceのpipelineを使うと、テキスト生成が簡単に実行できます。
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
)

# パイプラインを実行してテキストを生成
outputs = pipe(
    prompt,
    max_new_tokens=512,  # 生成する最大トークン数
    do_sample=True,
    temperature=0.6,
    top_p=0.9,
)

# 4. 結果の表示
# ---------------------------------
# 生成されたテキスト全体から、プロンプト部分を除いてアシスタントの応答だけを表示
assistant_response = outputs[0]["generated_text"][len(prompt):]
print(assistant_response)
