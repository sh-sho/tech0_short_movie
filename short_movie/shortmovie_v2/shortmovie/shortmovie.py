import streamlit as st
from moviepy.editor import *
import tempfile
import os
import random
import time


# タイトルを設定
st.title('ショートムービー再生アプリ')

# 音楽設定の選択肢
music_options = {
    "アゲ系": "age.mp3",  # 音楽ファイルを適切なものに置き換えてください
    "cafe": "cafe.mp3",   # 音楽ファイルを適切なものに置き換えてください
    "chill": "chill.mp3", # 音楽ファイルを適切なものに置き換えてください
    "cool": "cool.mp3"    # 音楽ファイルを適切なものに置き換えてください
}

# 解像度の選択肢
resolution_options = {
    "500": (500, 280),  # 解像度を適切な比に設定してください
    "700": (700, 394),  # 解像度を適切な比に設定してください
    "900": (900, 506)   # 解像度を適切な比に設定してください
}

# サイドバーのユーザー入力
# 一旦画像ファイル
uploaded_files = st.sidebar.file_uploader("動画ファイルをアップロードしてください", accept_multiple_files=True,type=["jpg","png","mp4", "mov"])

selected_music = st.sidebar.selectbox("音楽設定を選択してください", list(music_options.keys()))
selected_resolution = st.sidebar.selectbox("解像度を選択してください", list(resolution_options.keys()))
purpose_text = st.sidebar.text_input("動画のまとめて欲しい内容を教えてください")


# 全ての入力が完了しているか確認
all_inputs_provided = uploaded_files is not None and selected_music and selected_resolution and purpose_text

# 生成ボタン
generate_button = st.sidebar.button('動画を生成', disabled=not all_inputs_provided)

# 動画と音楽を結合して再生
if generate_button and all_inputs_provided:
    
    if len(uploaded_files) > 0:
        selected_files = random.sample(uploaded_files, min(len(uploaded_files), 20))
        # print(selected_files)
        st.write(purpose_text)
        with tempfile.TemporaryDirectory() as tmpdirname:
            clips = []
            for image_file in selected_files:
                print(image_file.name)
                # 一時ファイルを作成し、アップロードされたファイルの内容を書き込む
                temp_image_path = os.path.join(tmpdirname, image_file.name)
                with open(temp_image_path, "wb") as f:
                    f.write(image_file.read())
                # ImageClip を作成
                clip = ImageClip(temp_image_path, duration=3)
                clips.append(clip)
                
            # 画像クリップを結合
            final_clip = concatenate_videoclips(clips, method="compose")

            # 音楽ファイルのパスを取得
            music_file_path = music_options[selected_music]

            # 音楽クリップを作成
            audio_clip = AudioFileClip(music_file_path)

            # 音楽の長さを動画の長さに合わせる
            audio_clip = audio_clip.subclip(0, final_clip.duration)

            # 音楽を動画に設定
            final_clip = final_clip.set_audio(audio_clip)

            with st.spinner('Wait for it...'):
                # 動画を一時ファイルに書き出す
                temp_video_file = os.path.join(tmpdirname, 'temp_video.mp4')
                final_clip.write_videofile(temp_video_file, fps=24)
                time.sleep(2)
            st.success('Done!')


            # # 画像クリップを結合
            # final_clip = concatenate_videoclips(clips, method="compose")

            # with st.spinner('Wait for it...'):
            #     # 動画を一時ファイルに書き出す
            #     temp_video_file = os.path.join(tmpdirname, 'temp_video.mp4')
            #     final_clip.write_videofile(temp_video_file, fps=24)
            #     time.sleep(2)
            # st.success('Done!')

            st.video(temp_video_file)


else:
    if generate_button:
        st.sidebar.warning('すべての入力を完了してください。')
