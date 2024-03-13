from googletrans import Translator, constants
# from .custom_error import CustomError


class LocalTranslator:
    translator: Translator

    # contructor
    def __init__(self) -> None:
        self.translator = Translator()
        print("Local Translator initialized")
        
    def translate(self, text:str, src:str, out:str)->str:
        # try:
        trans = self.translator.translate(text=text, src=src, dest=out)
        return trans.text
        # except :
        #     return 0
            # return CustomError(f"Could not translate {text} from {src} to {out}")
        

if __name__ == "__main__":
    translator = LocalTranslator()
    english = "How do you do"
    french = translator.translate(text=english, src="en", out="fr")
    print(f"{english} to french :-> {french}")