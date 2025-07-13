#!/usr/bin/env python3
"""
Efficient plan addition script for the optimized RAG system
This script allows you to add new plans without rebuilding the entire system
"""

import os
import json
import time
from typing import List, Dict, Any
from app_optimized import OptimizedHealthInsuranceRAG
from performance_optimizations import DatabaseOptimizer, InsurancePlan
from langchain_core.documents import Document

class PlanAdder:
    """Efficiently add new plans to the optimized system"""
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        self.optimized_rag = OptimizedHealthInsuranceRAG(openai_api_key, "migrated_db")
        self.db_optimizer = DatabaseOptimizer("migrated_insurance_plans.db")
    
    def add_plans_from_markdown(self, markdown_content: str, plan_source: str = "manual"):
        """Add new plans from markdown content"""
        print(f"Adding plans from {plan_source}...")
        
        # Parse new plans
        new_plans = self.optimized_rag.parse_insurance_plans(markdown_content)
        print(f"Found {len(new_plans)} new plans to add")
        
        # Convert to InsurancePlan objects
        insurance_plans = []
        for plan_data in new_plans:
            try:
                plan = InsurancePlan(
                    plan_name=plan_data['plan_name'],
                    carrier=plan_data['carrier'],
                    plan_type=plan_data['plan_type'],
                    monthly_premium=float(plan_data['monthly_premium']) if plan_data['monthly_premium'] != 'N/A' else 0.0,
                    deductible_individual=float(plan_data['deductible']) if plan_data['deductible'] != 'N/A' else 0.0,
                    deductible_family=float(plan_data['deductible']) * 2 if plan_data['deductible'] != 'N/A' else 0.0,
                    max_out_of_pocket_individual=float(plan_data['max_out_of_pocket']) if plan_data['max_out_of_pocket'] != 'N/A' else 0.0,
                    max_out_of_pocket_family=float(plan_data['max_out_of_pocket']) * 2 if plan_data['max_out_of_pocket'] != 'N/A' else 0.0,
                    hsa_eligible=plan_data['hsa_eligible'],
                    network_type=plan_data['plan_type'],
                    content_hash=plan_data.get('content_hash', ''),
                    raw_content=plan_data['content']
                )
                insurance_plans.append(plan)
            except Exception as e:
                print(f"Error processing plan {plan_data.get('plan_name', 'Unknown')}: {e}")
        
        # Add to database
        self.db_optimizer.bulk_insert_plans(insurance_plans)
        print(f"Added {len(insurance_plans)} plans to database")
        
        # Add to vector store (incremental)
        self._add_to_vectorstore(new_plans)
        
        return len(insurance_plans)
    
    def _add_to_vectorstore(self, new_plans: List[Dict[str, Any]]):
        """Add new plans to vector store incrementally"""
        print("Adding to vector store...")
        
        # Create documents for new plans
        documents = self.optimized_rag.create_optimized_documents(new_plans)
        
        # Add to existing vector store
        if self.optimized_rag.vectordb is None:
            # Initialize if not exists
            self.optimized_rag.setup_vectorstore(documents)
        else:
            # Add incrementally
            self.optimized_rag.vectordb.add_documents(documents)
            self.optimized_rag.vectordb.persist()
        
        print(f"Added {len(documents)} documents to vector store")
    
    def add_plan_manually(self, plan_data: Dict[str, Any]):
        """Add a single plan manually"""
        try:
            plan = InsurancePlan(
                plan_name=plan_data['plan_name'],
                carrier=plan_data['carrier'],
                plan_type=plan_data['plan_type'],
                monthly_premium=float(plan_data['monthly_premium']),
                deductible_individual=float(plan_data['deductible_individual']),
                deductible_family=float(plan_data['deductible_family']),
                max_out_of_pocket_individual=float(plan_data['max_out_of_pocket_individual']),
                max_out_of_pocket_family=float(plan_data['max_out_of_pocket_family']),
                hsa_eligible=plan_data['hsa_eligible'],
                network_type=plan_data['network_type'],
                content_hash=plan_data.get('content_hash', ''),
                raw_content=plan_data['raw_content']
            )
            
            # Add to database
            self.db_optimizer.insert_plan(plan)
            
            # Add to vector store
            doc = Document(
                page_content=f"""
                Plan: {plan.plan_name}
                Carrier: {plan.carrier}
                Type: {plan.plan_type}
                Monthly Premium: ${plan.monthly_premium}
                Deductible: ${plan.deductible_individual}
                Max Out of Pocket: ${plan.max_out_of_pocket_individual}
                HSA Eligible: {plan.hsa_eligible}
                
                {plan.raw_content[:1000]}
                """,
                metadata={
                    'plan_name': plan.plan_name,
                    'carrier': plan.carrier,
                    'plan_type': plan.plan_type,
                    'monthly_premium': plan.monthly_premium,
                    'deductible': plan.deductible_individual,
                    'max_out_of_pocket': plan.max_out_of_pocket_individual,
                    'hsa_eligible': plan.hsa_eligible,
                    'content_hash': plan.content_hash
                }
            )
            
            self.optimized_rag.vectordb.add_documents([doc])
            self.optimized_rag.vectordb.persist()
            
            print(f"Successfully added plan: {plan.plan_name}")
            return True
            
        except Exception as e:
            print(f"Error adding plan: {e}")
            return False
    
    def get_system_stats(self):
        """Get current system statistics"""
        conn = self.db_optimizer.db.connect(self.db_optimizer.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM plans")
        total_plans = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT carrier) FROM plans")
        unique_carriers = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(monthly_premium) FROM plans")
        avg_premium = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(monthly_premium), MAX(monthly_premium) FROM plans")
        min_premium, max_premium = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_plans': total_plans,
            'unique_carriers': unique_carriers,
            'avg_premium': avg_premium,
            'premium_range': f"${min_premium:.2f} - ${max_premium:.2f}"
        }

def create_plan_template():
    """Create a template for adding new plans"""
    template = {
        "plan_name": "Example Plan Name",
        "carrier": "Example Carrier",
        "plan_type": "HMO/PPO/EPO",
        "monthly_premium": 500.0,
        "deductible_individual": 2000.0,
        "deductible_family": 4000.0,
        "max_out_of_pocket_individual": 8000.0,
        "max_out_of_pocket_family": 16000.0,
        "hsa_eligible": True,
        "network_type": "HMO",
        "raw_content": "Detailed plan information goes here..."
    }
    
    with open("plan_template.json", "w") as f:
        json.dump(template, f, indent=2)
    
    print("Created plan_template.json - use this as a template for new plans")

def main():
    """Main function for adding plans"""
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError("OPENAI_API_KEY is not set")
    
    plan_adder = PlanAdder(openai_key)
    
    print("=== HEALTH INSURANCE PLAN ADDER ===")
    print("1. Add plans from markdown file")
    print("2. Add single plan manually")
    print("3. View system statistics")
    print("4. Create plan template")
    print("5. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            file_path = input("Enter markdown file path: ").strip()
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                added_count = plan_adder.add_plans_from_markdown(content, file_path)
                print(f"Successfully added {added_count} plans")
            else:
                print("File not found!")
        
        elif choice == "2":
            print("Enter plan details:")
            plan_data = {}
            plan_data['plan_name'] = input("Plan name: ").strip()
            plan_data['carrier'] = input("Carrier: ").strip()
            plan_data['plan_type'] = input("Plan type (HMO/PPO/EPO): ").strip()
            plan_data['monthly_premium'] = float(input("Monthly premium: "))
            plan_data['deductible_individual'] = float(input("Individual deductible: "))
            plan_data['deductible_family'] = float(input("Family deductible: "))
            plan_data['max_out_of_pocket_individual'] = float(input("Individual max out of pocket: "))
            plan_data['max_out_of_pocket_family'] = float(input("Family max out of pocket: "))
            plan_data['hsa_eligible'] = input("HSA eligible (y/n): ").lower() == 'y'
            plan_data['network_type'] = input("Network type: ").strip()
            plan_data['raw_content'] = input("Detailed content: ").strip()
            
            success = plan_adder.add_plan_manually(plan_data)
            if success:
                print("Plan added successfully!")
        
        elif choice == "3":
            stats = plan_adder.get_system_stats()
            print("\n=== SYSTEM STATISTICS ===")
            print(f"Total Plans: {stats['total_plans']}")
            print(f"Unique Carriers: {stats['unique_carriers']}")
            print(f"Average Premium: ${stats['avg_premium']:.2f}")
            print(f"Premium Range: {stats['premium_range']}")
        
        elif choice == "4":
            create_plan_template()
        
        elif choice == "5":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main() 