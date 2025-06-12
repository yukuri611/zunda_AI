import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import requests
import json
import subprocess
import tempfile
import os
import argparse

# --- 設定項目 ---
# 生成AI関連
MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"

# VOICEVOX関連
VOICEVOX_URL = "http://127.0.0.1:50021"
DEFAULT_SPEAKER_ID = 1 # デフォルトの話者ID（ずんだもん）

# --- 1. 生成AIからの回答取得機能 ---
def generate_llm_response(user_prompt: str, pipe: pipeline) -> str:
  """
  指定されたパイプラインを使用して、ユーザーのプロンプトに対するLLMの応答を生成する。
  """
  messages = [
    {"role": "system", "content": "You are a helpful assistant. Please respond in Japanese."},
    {"role": "user", "content": user_prompt},
  ]

  prompt = pipe.tokenizer.apply_chat_template(
    messages, 
    tokenize=False, 
    add_generation_prompt=True
  )

  outputs = pipe(
    prompt,
    max_new_tokens=512,
    do_sample=True,
    temperature=0.7,
    top_p=0.9,
  )

  assistant_response = outputs[0]["generated_text"][len(prompt):].strip()
  return assistant_response

def synthesize_and_play_voice(text: str, speaker_id: int):
  """
  VOICEVOX Engineを使用してテキストを音声に変換し、再生する。
  """
  try:
    # 1. audio_query (音声合成用のクエリを作成)
    query_params = {"text": text, "speaker": speaker_id}
    response_query = requests.post(f"{VOICEVOX_URL}/audio_query", params=query_params, timeout=10)
    response_query.raise_for_status()
    audio_query_data = response_query.json()

    # 2. synthesis (音声合成を実行)
    synth_params = {"speaker": speaker_id}
    response_synth = requests.post(
      f"{VOICEVOX_URL}/synthesis",
      params=synth_params,
      data=json.dumps(audio_query_data),
      timeout=30
    )
    response_synth.raise_for_status()
    audio_data = response_synth.content

    # 3. 一時ファイルに保存して再生
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
      tmp_wav.write(audio_data)
      temp_filename = tmp_wav.name
    try:
      subprocess.run(['aplay', temp_filename], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
      os.remove(temp_filename) # 再生後、一時ファイルを確実に削除

  except requests.exceptions.RequestException as e:
    print(f"エラー: VOICEVOX Engineに接続できませんでした。")
    print("   Dockerコンテナが起動しているか、URLが正しいか確認してください。")
    print(f"   詳細: {e}")
  except subprocess.CalledProcessError:
    print("エラー: 音声の再生に失敗しました。'aplay'コマンドがインストールされていますか？")
  except Exception as e:
    print(f"予期せぬエラーが発生しました: {e}")


# --- 3. メイン処理 ---
def main():
  # コマンドライン引数の設定
  parser = argparse.ArgumentParser(description="生成AIの応答を音声で出力するプログラム")
  parser.add_argument("--speaker", type=int, default=DEFAULT_SPEAKER_ID, help=f"VOICEVOXの話者ID (デフォルト: {DEFAULT_SPEAKER_ID})")
  args = parser.parse_args()

  from transformers import logging, BitsAndBytesConfig
  logging.set_verbosity_error()

  # モデルのロード
  try:
    quantization_config = BitsAndBytesConfig(load_in_4bit=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
      MODEL_ID,
      torch_dtype=torch.bfloat16,
      device_map="auto",
      quantization_config=quantization_config,
    )
    # テキスト生成パイプラインを作成
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
  except Exception as e:
    print(f"モデルのロード中にエラーが発生しました: {e}")
    return
  print("LLMのロードが完了しました。\n")

  # ---- 処理の実行 ----
  while True:
    # ユーザーからの入力を取得
    prompt = input("入力: ")
    if prompt == "exit":
      print("プログラムを終了します。")
      break
    # 1. AIの応答を生成
    ai_response = generate_llm_response(prompt, pipe)
    print(f"応答: {ai_response}")
    if ai_response:
      synthesize_and_play_voice(ai_response, args.speaker)
    else:
      print("AIの応答を生成できませんでした。音声再生をスキップします。")
    

if __name__ == "__main__":
  main()
