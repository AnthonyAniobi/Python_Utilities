import re
import os
import json
import time
import tkinter as tk
from tkinter.filedialog import askopenfilename
from deep_translator import GoogleTranslator




class LocalTranslator:
    def __init__(self) -> None:
        os.environ['TK_SILENCE_DEPRECATION'] = "1" # remove deprecated tkinter

    def __check_l10n_path(self, path:str)->bool:
        sep:str = os.sep
        dirs = path.split(sep=sep)
        if(dirs[-2] == 'l10n'):
            return True
        else:
            return False
    
    def __path_is_arb(self, path:str)->bool:
        file_name = path.split(sep=os.sep)[-1]
        pattern = r"app_..\.arb"
        match = re.fullmatch(pattern, file_name)
        if(match):
            return True
        else:
            return False
    

    def __pick_file(self)->str:
        root = tk.Tk()
        root.withdraw() # minimize tk window
        time.sleep(3) # sleep for 1
        path = askopenfilename() # open dialog
        if(len(path)<= 0):
            raise Exception("Failed to pick file")
        return path


    def __get_all_files(self, path:str)->dict[str, str]:
        lang_data: dict[str, str] = dict()
        for p in os.listdir(path):
            if(p.split('.')[-1] == 'arb'):
                lang_path = os.path.join(path, p)
                lang_code = p[4:6]
                lang_data[lang_code] = lang_path
        return lang_data


    def __arb_to_dict(self, path:str)-> dict[str, str]:
        with open(path, "r") as file:
            data:dict[str, str] = json.loads(file.read())
            return data

    def __dict_to_arb(self, data: dict[str, str], path: str, lang_code: str)->None:
        encoded_data = json.dumps(data, indent=4)
        full_path = os.path.join(path, f"app_{lang_code}.arb")
        with open(full_path, "w") as file:
            file.write(encoded_data)

    def __translate(self, text:str, src:str, out:str)->str:
        return GoogleTranslator(source="en", target="fr").translate(text=text)
    
    def translate(self, gui_picker:bool=True, lang_codes:list[str]=[]):
        ref_file_path:str # path of the reference file
        if(gui_picker):
            ref_file_path = self.__pick_file()
        else:
            ref_file_path = input("Enter the path: ")
        
        # check if file is the current file path
        if(not self.__check_l10n_path(ref_file_path)):
            raise Exception("Folder in Path is not 'l10n'")
        elif(not self.__path_is_arb(ref_file_path)):
            raise Exception("File in not a '.arb' file")
        
        # get folder path of the l10n directory
        folder_path_list =  ref_file_path.split(os.sep)[:-1]
        folder_path = os.sep.join(folder_path_list)
        
        # get dict of path and 
        code_and_path_dict:dict[str, str] = self.__get_all_files(folder_path)

        # get language code and data of the reference
        ref_code = ref_file_path.split(os.sep)[-1][4:6]
        ref_data = self.__arb_to_dict(code_and_path_dict[ref_code])

        # add codes to lang_codes
        for l_c in lang_codes:
            if(code_and_path_dict[l_c] is not None):
                code_and_path_dict[l_c] = {}

        # delete reference lang code from dictionary of code and path
        code_and_path_dict.pop(ref_code)


        for k,v in code_and_path_dict.items():
            l_code: str = k
            l_data: dict[str, str] = self.__arb_to_dict(v)
            # translate all items
            for _k, _v in ref_data.items():
                # if value in reference data is not in l_data
                if(l_data[_k] is None):
                    # translate the value of the ref to the language of the current
                    output = self.__translate(text=_v, src=ref_code, out=l_code)
                    # add the output of the translation to the data
                    l_data[_k] = output
            print(f"Translated {l_code}")
            # write the data to file
            self.__dict_to_arb(data=l_data, path=folder_path, lang_code=l_code)
                