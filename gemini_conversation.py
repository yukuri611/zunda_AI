import google.generativeai as genai
import requests
import json
import subprocess
import tempfile
import os
import argparse

# --- 設定項目 ---
# 生成AI関連
# xport GEMINI_API_KEY="your_api"でAPIキーを事前に設定
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 
GEMINI_MODEL = "gemini-2.0-flash"

# VOICEVOX関連
VOICEVOX_URL = "http://127.0.0.1:50021"
DEFAULT_SPEAKER_ID = 1 # デフォルトの話者ID（ずんだもん）

# --- 1. 生成AIからの回答取得機能 ---
def generate_llm_response(user_prompt: str, model: genai.GenerativeModel, speaker_id, speaker_list) -> str:
  """
  Geminiモデルを使用して、ユーザーのプロンプトに対する応答を生成する。
  """
  try:
    full_prompt = (
      f"あなたは、ユーザーにとって「親しみやすいけど、とても丁寧な友人」です。名前は{speaker_list[speaker_id][0]}です。年齢は12歳です\n"
      "以下のルールを守って、優しく心地よい会話をしてください。\n\n"
      "【ルール】\n"
      "1. **口調:** 丁寧な言葉遣いをしてください。ただし、事務的にならないように、柔らかく、温かい雰囲気で話すことを心がけてください。「〜じゃん」のような砕けすぎた言葉は使いません。\n"
      "2. **役割:** ユーザーの話に優しく耳を傾け、肯定的に相槌を打つような、聞き上手なパートナーとして振る舞ってください。\n"
      "3. **回答の長さ:** 回答は常に短く、2〜3文程度にまとめてください。\n"
      "4. **形式:** 箇条書きや番号リストは絶対に使わないでください。\n\n"
      f"ユーザー: {user_prompt}\n"
      "アシスタント:"
    )

    # テキスト生成のパラメータを設定
    generation_config = {
      "temperature": 0.7,
      "top_p": 0.9,
      "max_output_tokens": 512,
    }
    response = model.generate_content(
      full_prompt,
      generation_config=generation_config
    )
    return response.text.strip()
  except Exception as e:
    print(f"Gemini APIの呼び出し中にエラーが発生しました: {e}")
    return ""

def synthesize_and_play_voice(text: str, speaker_id: int, speaker_list) -> None:
  """
  VOICEVOX Engineを使用してテキストを音声に変換し、再生する。
  """
  
  try:
    # 1. audio_query (音声合成用のクエリを作成)
    query_params = {"text": text, "speaker": speaker_id}
    response_query = requests.post(f"{VOICEVOX_URL}/audio_query", params=query_params, timeout=10)
    response_query.raise_for_status()
    audio_query_data = response_query.json()
    audio_query_data['speedScale'] = speaker_list[speaker_id][1]  # 音声の速度を調整
    audio_query_data['pitchScale'] = 0.03 # 音声のピッチを調整
    audio_query_data['pauseLength'] = 0.3   # ポーズの長さを設定

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

  if not GEMINI_API_KEY:
    print("エラー: 環境変数 'GEMINI_API_KEY' が設定されていません。")
    return
  
  try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    print(f"Geminiモデル ({GEMINI_MODEL}) の準備ができました。\n")
  except Exception as e:
    print(f"Geminiの初期化中にエラーが発生しました: {e}")
    return
  
  # ---- 処理の実行 ----
  speaker_parameter = {
    0: ["四国めたん", 1], # name, speed, 
    1: ["ずんだもん", 1.5],
    2: ["春日部つむぎ", 1.3],
  }
  while True:
    try:
      # ユーザーからの入力を取得
      prompt = input("入力: ")
      if prompt.lower() == "exit":
        print("プログラムを終了します。")
        break
      # 1. AIの応答を生成
      ai_response = generate_llm_response(prompt, model, args.speaker, speaker_parameter)
      print(f"応答: {ai_response}")
      if ai_response:
        synthesize_and_play_voice(ai_response, args.speaker, speaker_parameter)
      else:
        print("AIの応答を生成できませんでした。音声再生をスキップします。")
    except KeyboardInterrupt:
      print("\nプログラムを終了します。")
      break

if __name__ == "__main__":
  main()
