import json
from typing import Dict, List

class CategoryManager:
    def __init__(self):
        self.categories = self._load_categories()
        self.default_categories = set(['Food & Dining', 'Transportation', 'Shopping', 
                                     'Bills & Utilities', 'Entertainment', 'Healthcare', 
                                     'Travel', 'Other'])
    
    def _load_categories(self) -> Dict:
        """Load default categories from JSON file"""
        try:
            with open('assets/default_categories.json', 'r') as f:
                return json.load(f)['categories']
        except FileNotFoundError:
            return {}
    
    def get_all_categories(self) -> List[str]:
        """Return list of all category names"""
        return list(self.categories.keys())
    
    def is_default_category(self, category_name: str) -> bool:
        """Check if category is a default category"""
        return category_name in self.default_categories
    
    def add_category(self, category_name: str, keywords: List[str]) -> tuple[bool, str]:
        """Add new category with keywords"""
        if not category_name.strip():
            return False, "Category name cannot be empty"
        
        if category_name in self.categories:
            return False, "Category already exists"
            
        # Basic validation of category name
        if len(category_name) > 50:
            return False, "Category name too long (max 50 characters)"
            
        self.categories[category_name] = keywords
        self._save_categories()
        return True, "Category added successfully"
    
    def remove_category(self, category_name: str) -> tuple[bool, str]:
        """Remove category if it exists and is not a default category"""
        if category_name in self.default_categories:
            return False, "Cannot remove default category"
            
        if category_name in self.categories:
            del self.categories[category_name]
            self._save_categories()
            return True, "Category removed successfully"
        return False, "Category not found"
    
    def add_keyword(self, category: str, keyword: str) -> tuple[bool, str]:
        """Add keyword to existing category"""
        if not keyword.strip():
            return False, "Keyword cannot be empty"
            
        if category in self.categories:
            if keyword in self.categories[category]:
                return False, "Keyword already exists in category"
                
            self.categories[category].append(keyword.strip().lower())
            self._save_categories()
            return True, "Keyword added successfully"
        return False, "Category not found"
    
    def remove_keyword(self, category: str, keyword: str) -> tuple[bool, str]:
        """Remove keyword from category"""
        if category in self.categories and keyword in self.categories[category]:
            self.categories[category].remove(keyword)
            self._save_categories()
            return True, "Keyword removed successfully"
        return False, "Keyword not found"
    
    def get_category_keywords(self, category: str) -> List[str]:
        """Get all keywords for a category"""
        return self.categories.get(category, [])
    
    def _save_categories(self) -> None:
        """Save categories back to JSON file"""
        with open('assets/default_categories.json', 'w') as f:
            json.dump({'categories': self.categories}, f, indent=4)
