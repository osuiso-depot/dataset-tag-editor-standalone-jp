import json
import os
from typing import Dict, Any, Optional

import gradio as gr

# グローバルなI18nインスタンス
_i18n_instance: Optional[gr.I18n] = None

# グローバルな翻訳辞書
_translations: Dict[str, Dict[str, str]] = {}
_current_locale: str = "en"

# サポートされる言語のリスト
SUPPORTED_LANGS: Dict[str, str] = {
    "en": "English",
    "ja": "日本語",
}

def load_translations(lang: str) -> None:
    """
    指定された言語の翻訳ファイルをロードする。
    """
    global _translations, _current_locale

    locales_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "locales"
    )

    _translations.clear()
    _current_locale = lang if lang in SUPPORTED_LANGS else "en"

    # 全言語の翻訳ファイルをロード（フォールバック用）
    for code in SUPPORTED_LANGS.keys():
        file_path = os.path.join(locales_dir, f"{code}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                _translations[code] = json.load(f)
        else:
            _translations[code] = {}

def t(key: str, **kwargs) -> str:
    """
    翻訳キーに対応するテキストを取得するヘルパー関数。
    kwargsで渡されたパラメータは文字列内の{param}を置換する。
    """
    # 現在のロケールから翻訳を取得
    translation = _translations.get(_current_locale, {}).get(key)

    # 見つからない場合は英語（フォールバック）
    if translation is None:
        translation = _translations.get("en", {}).get(key)

    # それでも見つからない場合はキーをそのまま返す
    if translation is None:
        print(f"Warning: Translation not found for key: {key}")
        return key

    # パラメータ置換
    try:
        return translation.format(**kwargs)
    except KeyError as e:
        print(f"Warning: Missing parameter {e} for key: {key}")
        return translation

def build_i18n(lang: str):
    """
    翻訳データをロードする。
    Gradio用のI18nインスタンスは必要に応じて別途作成。
    """
    load_translations(lang)

def set_translator(i18n_instance: gr.I18n):
    """
    グローバルなI18nインスタンスを設定する。
    """
    global _i18n_instance
    _i18n_instance = i18n_instance
