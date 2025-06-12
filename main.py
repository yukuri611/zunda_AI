import requests
import json
import io
import subprocess
import tempfile
import os

# --- 設定項目 ---
text = "こんにちは、ずんだもんなのだ。今日はVOICEVOXの音声合成を試しているのだ。"
speaker_id = 1
voicevox_url = "http://0.0.0.0:50021"
# -----------------

def play_voice():
    try:
        # 1. audio_query (音声合成用のクエリを作成)
        print("ステップ1: audio_query を実行中...")
        query_params = {"text": text, "speaker": speaker_id}
        response_query = requests.post(f"{voicevox_url}/audio_query", params=query_params)
        
        response_query.raise_for_status()
        audio_query_data = response_query.json()
        print("audio_query に成功しました。")

        # 2. synthesis (音声合成を実行)
        print("ステップ2: synthesis を実行中...")
        synth_params = {"speaker": speaker_id}
        
        response_synth = requests.post(
            f"{voicevox_url}/synthesis",
            params=synth_params,
            data=json.dumps(audio_query_data)
        )
        
        response_synth.raise_for_status()
        audio_data = response_synth.content



        print("ステップ3: 音声をファイルに保存して再生します...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
            tmp_wav.write(audio_data)
            temp_filename = tmp_wav.name
        
        try:
            # 音声ファイルを再生
            print(f"一時ファイル {temp_filename} を再生中...")
            subprocess.run(['aplay', temp_filename], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("再生が完了しました。")
        finally:
            # 一時ファイルを削除
            os.remove(temp_filename)
            print(f"一時ファイル {temp_filename} を削除しました。")

    except requests.exceptions.RequestException as e:
        print(f"エラー: VOICEVOX Engineに接続できませんでした。")
        print("Dockerコンテナが起動しているか、URLが正しいか確認してください。")       
        print(f"詳細: {e}")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")

if __name__ == "__main__":
    play_voice()
