from typing import Dict, List, NamedTuple
from dataclasses import dataclass

import g_sheets as gsh


@dataclass
class Category(NamedTuple):
    codename: str
    name: List[str]
    
class Categories:
    def __init__(self):
        self.codename = self._load_categories()
           
    def _load_categories(self) -> List:
        categories = gsh._load_categories()
        return categories.keys()

    def _load_name(self) -> Dict:
        name = gsh._load_categories()
        return name
       
    def get_category(self, name: str) -> Category:
        names = name.split(' ')
        for codename, value in self._load_name().items():    
            for i in names:
                if i in value:
                    return codename
                else:
                    continue
        else:
            codename = 'Other expenses'
        return codename                                     
            
                