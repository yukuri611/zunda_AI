import requests
import json
import io
from pydub import AudioSegment
from pydub.playback import play

# --- 設定項目 ---
text = "こんにちは、ボイスボックスです。"
speaker_id = 1
voicevox_url = "  https://923d-59-158-102-54.ngrok-free.app"
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


        print("ステップ3: 音声を再生します...")
        audio_data = response_synth.content
        song = AudioSegment.from_file(io.BytesIO(audio_data), format="wav")
        play(song)
        print("再生が完了しました。")

    except requests.exceptions.RequestException as e:
        print(f"エラー: VOICEVOX Engineに接続できませんでした。")
        print("プロキシ設定やファイアウォールが原因の可能性があります。")
        print(f"詳細: {e}")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")

if __name__ == "__main__":
    play_voice()
