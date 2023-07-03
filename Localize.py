import bpy
translation_dict = {
    "en_US": {
        "Dress Up": "Dress Up",
        "Undress": "Undress",
        "Remove All": "Remove All",
        "Cloth": "Cloth",
        "Vertex Groups": "Vertex Groups",
        "Clean": "Clean",
        "Auto Clean Vertex Groups": "Auto Clean Vertex Groups",
        "Apply Transform": "Apply Transform",
        "All selected objects are not applicable.": "All selected objects are not applicable. If you want to dress up again, please undress first.",
    },
    "ja_JP": {
        "Dress Up": "着せる",
        "Undress": "脱がす",
        "Remove All": "全削除",
        "Cloth": "衣装",
        "Vertex Groups": "頂点グループ",
        "Clean": "クリーン",
        "Auto Clean Vertex Groups": "必要な頂点グループのみを残す",
        "Apply Transform": "衣装のトランスフォームを適応",
        "All selected objects are not applicable.": "選択されたすべてのオブジェクトはすでに着せられています。もし、再度着せ直したい場合は、一度脱がせてください。",
    }
}

def __get_translation_table() -> dict[str, str]:
    locale = bpy.app.translations.locale or "en_US"
    if locale in translation_dict:
        return translation_dict[locale]
    else:
        return translation_dict["en_US"]

translation_table: dict[str, str] = __get_translation_table()

def localize(string: str) -> str:
    if string in translation_table:
        return translation_table[string]
    else:
        return string

