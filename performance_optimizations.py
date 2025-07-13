import os
import json
import sqlite3
from typing import List, Dict, Any, Optional
import pandas as pd
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import asyncio
import aiohttp

@dataclass
class InsurancePlan:
    """Structured data class for insurance plans"""
    plan_name: str
    carrier: str
    plan_type: str
    monthly_premium: float
    deductible_individual: float
    deductible_family: float
    max_out_of_pocket_individual: float
    max_out_of_pocket_family: float
    hsa_eligible: bool
    network_type: str
    content_hash: str
    raw_content: str

class DatabaseOptimizer:
    """SQLite database for fast plan queries and filtering"""
    
    def __init__(self, db_path: str = "insurance_plans.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with optimized schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_name TEXT NOT NULL,
                carrier TEXT NOT NULL,
                plan_type TEXT NOT NULL,
                monthly_premium REAL NOT NULL,
                deductible_individual REAL NOT NULL,
                deductible_family REAL NOT NULL,
                max_out_of_pocket_individual REAL NOT NULL,
                max_out_of_pocket_family REAL NOT NULL,
                hsa_eligible BOOLEAN NOT NULL,
                network_type TEXT NOT NULL,
                content_hash TEXT UNIQUE NOT NULL,
                raw_content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for fast queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_carrier ON plans(carrier)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_plan_type ON plans(plan_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_premium ON plans(monthly_premium)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_deductible ON plans(deductible_individual)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_hsa ON plans(hsa_eligible)')
        
        conn.commit()
        conn.close()
    
    def insert_plan(self, plan: InsurancePlan):
        """Insert a single plan into database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO plans 
            (plan_name, carrier, plan_type, monthly_premium, deductible_individual, 
             deductible_family, max_out_of_pocket_individual, max_out_of_pocket_family,
             hsa_eligible, network_type, content_hash, raw_content)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            plan.plan_name, plan.carrier, plan.plan_type, plan.monthly_premium,
            plan.deductible_individual, plan.deductible_family,
            plan.max_out_of_pocket_individual, plan.max_out_of_pocket_family,
            plan.hsa_eligible, plan.network_type, plan.content_hash, plan.raw_content
        ))
        
        conn.commit()
        conn.close()
    
    def bulk_insert_plans(self, plans: List[InsurancePlan]):
        """Bulk insert plans for better performance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.executemany('''
            INSERT OR REPLACE INTO plans 
            (plan_name, carrier, plan_type, monthly_premium, deductible_individual, 
             deductible_family, max_out_of_pocket_individual, max_out_of_pocket_family,
             hsa_eligible, network_type, content_hash, raw_content)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', [(
            plan.plan_name, plan.carrier, plan.plan_type, plan.monthly_premium,
            plan.deductible_individual, plan.deductible_family,
            plan.max_out_of_pocket_individual, plan.max_out_of_pocket_family,
            plan.hsa_eligible, plan.network_type, plan.content_hash, plan.raw_content
        ) for plan in plans])
        
        conn.commit()
        conn.close()
    
    def query_plans(self, filters: Dict[str, Any] = None) -> List[InsurancePlan]:
        """Query plans with filters for fast retrieval"""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM plans WHERE 1=1"
        params = []
        
        if filters:
            if 'carrier' in filters:
                query += " AND carrier = ?"
                params.append(filters['carrier'])
            
            if 'plan_type' in filters:
                query += " AND plan_type = ?"
                params.append(filters['plan_type'])
            
            if 'max_premium' in filters:
                query += " AND monthly_premium <= ?"
                params.append(filters['max_premium'])
            
            if 'max_deductible' in filters:
                query += " AND deductible_individual <= ?"
                params.append(filters['max_deductible'])
            
            if 'hsa_eligible' in filters:
                query += " AND hsa_eligible = ?"
                params.append(filters['hsa_eligible'])
        
        # Add ordering for consistent results
        query += " ORDER BY monthly_premium ASC"
        
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        plans = []
        for row in rows:
            plan = InsurancePlan(
                plan_name=row[1],
                carrier=row[2],
                plan_type=row[3],
                monthly_premium=row[4],
                deductible_individual=row[5],
                deductible_family=row[6],
                max_out_of_pocket_individual=row[7],
                max_out_of_pocket_family=row[8],
                hsa_eligible=bool(row[9]),
                network_type=row[10],
                content_hash=row[11],
                raw_content=row[12]
            )
            plans.append(plan)
        
        return plans

class CachingLayer:
    """Redis-like caching for frequently accessed data"""
    
    def __init__(self):
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            self.cache_hits += 1
            return self.cache[key]
        self.cache_misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL"""
        self.cache[key] = value
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        total = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total * 100) if total > 0 else 0
        return {
            'hits': self.cache_hits,
            'misses': self.cache_misses,
            'hit_rate': hit_rate,
            'size': len(self.cache)
        }

class PlanRecommender:
    """Fast plan recommendation engine using structured data"""
    
    def __init__(self, db_optimizer: DatabaseOptimizer, cache: CachingLayer):
        self.db = db_optimizer
        self.cache = cache
    
    def recommend_by_cost(self, family_size: int = 1, max_monthly_budget: float = None) -> List[InsurancePlan]:
        """Recommend plans based on cost optimization"""
        cache_key = f"cost_recommendation_{family_size}_{max_monthly_budget}"
        
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Query database
        filters = {}
        if max_monthly_budget:
            filters['max_premium'] = max_monthly_budget
        
        plans = self.db.query_plans(filters)
        
        # Score plans based on total cost
        scored_plans = []
        for plan in plans:
            if family_size == 1:
                total_cost = plan.monthly_premium * 12 + plan.deductible_individual
            else:
                total_cost = plan.monthly_premium * 12 + plan.deductible_family
            
            scored_plans.append((plan, total_cost))
        
        # Sort by total cost
        scored_plans.sort(key=lambda x: x[1])
        
        # Return top 5 plans
        result = [plan for plan, _ in scored_plans[:5]]
        
        # Cache result
        self.cache.set(cache_key, result, ttl=1800)  # 30 minutes
        
        return result
    
    def recommend_by_features(self, features: Dict[str, Any]) -> List[InsurancePlan]:
        """Recommend plans based on specific features"""
        cache_key = f"feature_recommendation_{hash(str(features))}"
        
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Build filters from features
        filters = {}
        if 'carrier' in features:
            filters['carrier'] = features['carrier']
        if 'plan_type' in features:
            filters['plan_type'] = features['plan_type']
        if 'hsa_eligible' in features:
            filters['hsa_eligible'] = features['hsa_eligible']
        if 'max_premium' in features:
            filters['max_premium'] = features['max_premium']
        
        plans = self.db.query_plans(filters)
        
        # Score based on feature preferences
        scored_plans = []
        for plan in plans:
            score = 0
            
            # HSA bonus
            if features.get('prefer_hsa') and plan.hsa_eligible:
                score += 10
            
            # Plan type preference
            if features.get('preferred_plan_type') == plan.plan_type:
                score += 5
            
            # Cost efficiency
            total_cost = plan.monthly_premium * 12 + plan.deductible_individual
            score += max(0, 1000 - total_cost) / 100  # Higher score for lower cost
            
            scored_plans.append((plan, score))
        
        # Sort by score
        scored_plans.sort(key=lambda x: x[1], reverse=True)
        
        result = [plan for plan, _ in scored_plans[:5]]
        self.cache.set(cache_key, result, ttl=1800)
        
        return result

def create_performance_report(db_optimizer: DatabaseOptimizer, cache: CachingLayer):
    """Generate performance report"""
    print("=== PERFORMANCE REPORT ===")
    
    # Database stats
    conn = sqlite3.connect(db_optimizer.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM plans")
    total_plans = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(monthly_premium) FROM plans")
    avg_premium = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"Total Plans in Database: {total_plans}")
    print(f"Average Monthly Premium: ${avg_premium:.2f}")
    
    # Cache stats
    cache_stats = cache.get_stats()
    print(f"Cache Hit Rate: {cache_stats['hit_rate']:.1f}%")
    print(f"Cache Size: {cache_stats['size']} entries")
    
    print("=== END REPORT ===")

# Usage example
if __name__ == "__main__":
    # Initialize components
    db_optimizer = DatabaseOptimizer()
    cache = CachingLayer()
    recommender = PlanRecommender(db_optimizer, cache)
    
    # Example recommendations
    print("Cost-based recommendations for family of 4:")
    cost_plans = recommender.recommend_by_cost(family_size=4, max_monthly_budget=800)
    for plan in cost_plans:
        print(f"- {plan.plan_name}: ${plan.monthly_premium}/month")
    
    print("\nFeature-based recommendations:")
    feature_plans = recommender.recommend_by_features({
        'prefer_hsa': True,
        'preferred_plan_type': 'HMO',
        'max_premium': 600
    })
    for plan in feature_plans:
        print(f"- {plan.plan_name}: ${plan.monthly_premium}/month, HSA: {plan.hsa_eligible}")
    
    # Performance report
    create_performance_report(db_optimizer, cache) 