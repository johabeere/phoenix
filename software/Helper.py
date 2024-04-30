from colorama import Fore, Back, Style

def pprint(text:str, Color:str = "GREEN", *kwargs):
    print(eval('Fore.'+Color))
    print(text, *kwargs) 
    print(Style.RESET_ALL)