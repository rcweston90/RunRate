import os
from datetime import datetime
import psycopg2
from typing import Dict, List, Tuple, Optional

class BudgetManager:
    def __init__(self):
        self.db_url = os.environ['DATABASE_URL']
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database tables"""
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    # Drop existing table if it exists
                    cur.execute("DROP TABLE IF EXISTS budgets CASCADE;")
                    conn.commit()
                    
                    # Create table with new schema
                    cur.execute("""
                        CREATE TABLE budgets (
                            id SERIAL PRIMARY KEY,
                            category VARCHAR(50) UNIQUE NOT NULL,
                            amount DECIMAL(10,2) NOT NULL,
                            period VARCHAR(10) NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """)
                    conn.commit()
        except Exception as e:
            print(f"Database initialization error: {str(e)}")
    
    def set_budget(self, category: str, amount: float, period: str = 'monthly') -> Tuple[bool, str]:
        """Set or update budget for a category"""
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO budgets (category, amount, period)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (category) 
                        DO UPDATE SET amount = EXCLUDED.amount, period = EXCLUDED.period;
                    """, (category, amount, period))
                    conn.commit()
                    return True, "Budget set successfully"
        except Exception as e:
            return False, f"Error setting budget: {str(e)}"
    
    def get_budget(self, category: str) -> Optional[Dict]:
        """Get budget for a specific category"""
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT amount, period FROM budgets WHERE category = %s",
                        (category,)
                    )
                    result = cur.fetchone()
                    if result:
                        return {
                            'category': category,
                            'amount': float(result[0]),
                            'period': result[1]
                        }
                    return None
        except Exception:
            return None
    
    def get_all_budgets(self) -> List[Dict]:
        """Get all budgets"""
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT category, amount, period FROM budgets")
                    return [{
                        'category': row[0],
                        'amount': float(row[1]),
                        'period': row[2]
                    } for row in cur.fetchall()]
        except Exception:
            return []
    
    def remove_budget(self, category: str) -> Tuple[bool, str]:
        """Remove budget for a category"""
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM budgets WHERE category = %s", (category,))
                    if cur.rowcount > 0:
                        conn.commit()
                        return True, "Budget removed successfully"
                    return False, "Budget not found"
        except Exception as e:
            return False, f"Error removing budget: {str(e)}"
    
    def get_budget_status(self, category: str, current_spending: float) -> Dict:
        """Get budget status including remaining amount and percentage used"""
        budget = self.get_budget(category)
        if not budget:
            return {
                'has_budget': False,
                'budget_amount': 0,
                'spent': current_spending,
                'remaining': 0,
                'percentage_used': 100 if current_spending > 0 else 0
            }
        
        remaining = budget['amount'] - current_spending
        percentage_used = (current_spending / budget['amount'] * 100) if budget['amount'] > 0 else 100
        
        return {
            'has_budget': True,
            'budget_amount': budget['amount'],
            'spent': current_spending,
            'remaining': remaining,
            'percentage_used': min(percentage_used, 100)
        }
