from deep_translator import GoogleTranslator
import json

suported_lang = GoogleTranslator().get_supported_languages(as_dict=True)

formated_output = json.dumps(suported_lang, indent=4)
french = GoogleTranslator(target="zh-CN", source="en").translate(text="How do you do")

print(french)