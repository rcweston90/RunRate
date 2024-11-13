import json
from typing import Dict, List

class CategoryManager:
    def __init__(self):
        self.categories = self._load_categories()
    
    def _load_categories(self) -> Dict:
        """Load default categories from JSON file"""
        with open('assets/default_categories.json', 'r') as f:
            return json.load(f)['categories']
    
    def get_all_categories(self) -> List[str]:
        """Return list of all category names"""
        return list(self.categories.keys())
    
    def add_category(self, category_name: str, keywords: List[str]) -> None:
        """Add new category with keywords"""
        self.categories[category_name] = keywords
        self._save_categories()
    
    def remove_category(self, category_name: str) -> bool:
        """Remove category if it exists"""
        if category_name in self.categories:
            del self.categories[category_name]
            self._save_categories()
            return True
        return False
    
    def add_keyword(self, category: str, keyword: str) -> bool:
        """Add keyword to existing category"""
        if category in self.categories:
            if keyword not in self.categories[category]:
                self.categories[category].append(keyword)
                self._save_categories()
            return True
        return False
    
    def _save_categories(self) -> None:
        """Save categories back to JSON file"""
        with open('assets/default_categories.json', 'w') as f:
            json.dump({'categories': self.categories}, f, indent=4)
