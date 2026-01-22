import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

st.title("🧳 旅行持ち物プランナー")

st.write("旅行に必要な持ち物をAIがおすすめしてくれます。")
st.write("宿泊日数または季節を選択して、さらに詳細情報を入力してください。")

# 選択モードの設定
selection_mode = st.radio(
    "計画方法を選択してください。",
    ["宿泊日数で計画", "季節で計画"]
)

st.divider()

# 入力フォームの配置
col1, col2 = st.columns(2)

with col1:
    if selection_mode == "宿泊日数で計画":
        days = st.number_input(
            "宿泊日数を入力してください（日）",
            min_value=1,
            max_value=365,
            value=3
        )
        mode_info = f"宿泊日数: {days}日"
    else:
        season = st.selectbox(
            "季節を選択してください。",
            ["春", "夏", "秋", "冬"]
        )
        mode_info = f"季節: {season}"

with col2:
    destination = st.text_input(
        "旅行先を入力してください（例：京都、沖縄）",
        placeholder="例：京都"
    )
    trip_type = st.selectbox(
        "旅のタイプを選択してください。",
        ["ビジネス出張", "家族旅行", "友人との旅", "一人旅", "ハネムーン"]
    )

# 追加の詳細情報
st.divider()
st.subheader("追加情報（任意）")

additional_info = st.text_area(
    "その他、参考になる情報を入力してください。（例：アクティビティ、体調など）",
    placeholder="例：トレッキングを予定しています",
    height=100
)

st.divider()

# 実行ボタン
if st.button("📋 持ち物リストを生成", use_container_width=True):
    if not destination:
        st.error("旅行先を入力してください。")
    else:
        # プロンプトの構築
        if selection_mode == "宿泊日数で計画":
            duration_info = f"宿泊日数は{days}日"
            # 旅行専門のプランナーペルソナ
            prompt_template = ChatPromptTemplate.from_template(
                """あなたは20年の経験を持つ旅行プランナーです。豊富な旅行経験から、効率的で実践的な持ち物リストを作成することが得意です。以下の条件に基づいて、旅行に必要な持ち物リストを作成してください。

【旅行情報】
- 旅行先: {destination}
- {duration_info}
- 旅のタイプ: {trip_type}
- 追加情報: {additional_info}

【指示】
1. 旅行日数に合わせた効率的な持ち物リストを作成してください
2. 必須アイテム、推奨アイテム、あると便利なアイテムに分類してください
3. 各持ち物の推奨数量または量を明確に記載してください
4. カテゴリ別（衣類、衛生用品、電子機器、旅行用品、その他）に分類して表示してください
5. 旅行日数から予想される移動パターンや活動に合わせた持ち物を提案してください
6. 旅の種類に特化した必須アイテムの説明も含めてください
7. 荷物管理のコツやパッキングのアドバイスも含めてください

実用的で、無駄のない持ち物リストを提供してください。"""
            )
        else:
            duration_info = f"季節は{season}"
            # 天気に詳しいプランナーペルソナ
            prompt_template = ChatPromptTemplate.from_template(
                """あなたは気象学の知識を持つ天気専門の旅行プランナーです。季節ごとの気象パターンに詳しく、その時期の天気変化に対応した最適な持ち物を提案することが得意です。以下の条件に基づいて、旅行に必要な持ち物リストを作成してください。

【旅行情報】
- 旅行先: {destination}
- 季節: {season}
- 旅のタイプ: {trip_type}
- 追加情報: {additional_info}

【指示】
1. {season}の気象特性と予想される気象パターンを踏まえた持ち物リストを作成してください
2. その季節特有の気象リスク（雨、雪、風、紫外線など）に対応する持ち物を強調してください
3. 旅行先の気候と{season}の気象を組み合わせた適切な衣類を提案してください
4. 各持ち物と気象条件の関連性を説明してください
5. カテゴリ別（衣類・防具、天気対策、衛生用品、電子機器、その他）に分類して表示してください
6. 天気急変時の対策や応急グッズも含めてください
7. 旅行中の天気予報確認方法やアプリの利用についてもアドバイスしてください

気象知識に基づいた、季節に最適化した持ち物リストを提供してください。"""
            )
        
        # LLMの初期化とチェーンの構築
        try:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
            chain = prompt_template | llm
            
            # スピナーを表示しながら処理
            with st.spinner("🤔 持ち物リストを生成中..."):
                if selection_mode == "宿泊日数で計画":
                    response = chain.invoke({
                        "destination": destination,
                        "duration_info": duration_info,
                        "trip_type": trip_type,
                        "additional_info": additional_info if additional_info else "なし"
                    })
                else:
                    response = chain.invoke({
                        "destination": destination,
                        "season": season,
                        "trip_type": trip_type,
                        "additional_info": additional_info if additional_info else "なし"
                    })
            
            # 結果を表示
            st.divider()
            st.success("✅ 持ち物リストが生成されました！")
            st.markdown(response.content)
            
            # ダウンロード機能用にセッション状態に保存
            st.session_state.generated_list = response.content
            
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
            st.info("OpenAI APIキーが正しく設定されているか確認してください。")