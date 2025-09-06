from typing import List
from pydantic import BaseModel
from src.constants.enums import Theme

class NameRules(BaseModel):
    cap_slots:bool=True
    folder_name_format:str=""
    display_name_format:str=""

class SortRule(BaseModel):
    name:str=""
    priority:int=0
    asc:bool=True

class Settings(BaseModel):
    root_dir:str=""
    cache_dir:str=""
    workspace:str="Default"
    custom_elements:List[str]=[]
    hidden_folders:List[str]=[]
    theme:Theme=Theme.DARK
    name_rules:NameRules=NameRules()
    sort_rules:List[SortRule]=[]