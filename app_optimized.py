import os
import json
import re
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import hashlib

class OptimizedHealthInsuranceRAG:
    def __init__(self, openai_api_key: str, persist_directory: str = "optimized_db"):
        self.openai_api_key = openai_api_key
        self.persist_directory = persist_directory
        self.embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.vectordb = None
        self.plan_cache = {}
        
    def parse_insurance_plans(self, markdown_content: str) -> List[Dict[str, Any]]:
        """Parse markdown content into structured plan data"""
        plans = []
        
        # Find all plan sections with more specific pattern
        plan_pattern = r'###\s+([^$]+?\$\d+\.?\d*/Person)'
        plan_matches = re.finditer(plan_pattern, markdown_content)
        
        for match in plan_matches:
            plan_name = match.group(1).strip()
            start_pos = match.end()
            next_match = re.search(plan_pattern, markdown_content[start_pos:])
            end_pos = start_pos + next_match.start() if next_match else len(markdown_content)
            plan_content = markdown_content[start_pos:end_pos].strip()

            # Robust extraction for premium, type, carrier, deductible, max out of pocket
            premium = self._extract_premium(plan_name, plan_content)
            plan_type = self._extract_plan_type(plan_name, plan_content)
            carrier = self._extract_carrier(plan_name, plan_content)
            deductible = self._extract_deductible(plan_name, plan_content)
            max_oop = self._extract_max_out_of_pocket(plan_name, plan_content)

            plan_data = {
                'plan_name': plan_name,
                'content': plan_content,
                'monthly_premium': premium,
                'deductible': deductible,
                'max_out_of_pocket': max_oop,
                'carrier': carrier,
                'plan_type': plan_type,
                'hsa_eligible': self._extract_hsa_eligibility(plan_content)
            }
            print(f"[DEBUG] HSA eligibility for {plan_name[:50]}: {plan_data['hsa_eligible']}")
            plans.append(plan_data)
        # Debug print: show the first 3 parsed plans
        print("\n[DEBUG] First 3 parsed plans:")
        for p in plans[:3]:
            print(json.dumps(p, indent=2))
        return plans

    def _extract_premium(self, plan_name: str, content: str) -> float:
        """Extract monthly premium from content or plan name"""
        # The monthly premium is in the content section, not the plan name
        # Look for pattern like "### 529.37 Blue Cross Blue HMO/Bronze^"
        match = re.search(r'###\s+\$?(\d+\.?\d*)', content)
        if match:
            return float(match.group(1))
        
        # Fallback: try to find any dollar amount in content that could be premium
        match = re.search(r'\$(\d+\.?\d*)', content)
        if match:
            return float(match.group(1))
        
        # Last resort: try plan name (but this is usually the deductible)
        match = re.search(r'\$(\d+\.?\d*)/Person', plan_name)
        if match:
            return float(match.group(1))
        
        return 0.0

    def _extract_deductible(self, plan_name: str, content: str) -> float:
        """Extract deductible from plan name or content"""
        print(f"\n[DEBUG] Extracting deductible for plan: {plan_name[:50]}...")
        
        # Try content for yearly deductible first (most accurate)
        match = re.search(r'Yearly deductible\s+\$(\d+\.?\d*)/\$?(\d+\.?\d*)', content)
        if match:
            result = float(match.group(1))
            print(f"[DEBUG] Found deductible in content (pattern 1): ${result}")
            return result
        
        # Try content for yearly deductible (single value)
        match = re.search(r'Yearly deductible\s+\$(\d+\.?\d*)', content)
        if match:
            result = float(match.group(1))
            print(f"[DEBUG] Found deductible in content (pattern 2): ${result}")
            return result
        
        # The deductible is in the plan name (the $.../Person part)
        match = re.search(r'\$(\d+\.?\d*)/Person', plan_name)
        if match:
            result = float(match.group(1))
            print(f"[DEBUG] Found deductible in plan name: ${result}")
            return result
        
        # Try any $... in plan name
        match = re.search(r'\$(\d+\.?\d*)', plan_name)
        if match:
            result = float(match.group(1))
            print(f"[DEBUG] Found deductible in plan name (fallback): ${result}")
            return result
        
        # Try any $... in content
        match = re.search(r'\$(\d+\.?\d*)', content)
        if match:
            result = float(match.group(1))
            print(f"[DEBUG] Found deductible in content (fallback): ${result}")
            return result
        
        print(f"[DEBUG] No deductible found, returning 0")
        return 0.0

    def _extract_max_out_of_pocket(self, plan_name: str, content: str) -> float:
        """Extract max out of pocket from content or plan name"""
        print(f"\n[DEBUG] Extracting max out of pocket for plan: {plan_name[:50]}...")
        
        # The max out of pocket is in the content section (most accurate)
        match = re.search(r'Max\. out of pocket cost\s+\$(\d+\.?\d*)/\$?(\d+\.?\d*)', content)
        if match:
            result = float(match.group(1))
            print(f"[DEBUG] Found max OOP in content (pattern 1): ${result}")
            return result
        
        # Try content for max out of pocket (single value)
        match = re.search(r'Max\. out of pocket cost\s+\$(\d+\.?\d*)', content)
        if match:
            result = float(match.group(1))
            print(f"[DEBUG] Found max OOP in content (pattern 2): ${result}")
            return result
        
        # Try to find any $.../$... pattern in content (second value)
        match = re.search(r'\$(\d+\.?\d*)/\$?(\d+\.?\d*)', content)
        if match:
            result = float(match.group(2))
            print(f"[DEBUG] Found max OOP in content (pattern 3): ${result}")
            return result
        
        # Try any $... in content (second value if present)
        matches = re.findall(r'\$(\d+\.?\d*)', content)
        if len(matches) > 1:
            result = float(matches[1])
            print(f"[DEBUG] Found max OOP in content (pattern 4): ${result}")
            return result
        
        # Last resort: try plan name (but this is usually the deductible)
        match = re.search(r'\$(\d+\.?\d*)/Person', plan_name)
        if match:
            result = float(match.group(1))
            print(f"[DEBUG] Found max OOP in plan name (fallback): ${result}")
            return result
        
        print(f"[DEBUG] No max OOP found, returning 0")
        return 0.0

    def _extract_carrier(self, plan_name: str, content: str) -> str:
        """Extract insurance carrier from plan name or content"""
        known_carriers = [
            'Blue Cross Blue', 'Aetna', 'UnitedHealth', 'Cigna', 'Humana', 'Kaiser', 'Anthem',
            'Tufts', 'WellSense', 'Select', 'Community', 'Complete', 'UHC', 'Harvard Pilgrim'
        ]
        plan_name_lower = plan_name.lower()
        for carrier in known_carriers:
            if carrier.lower() in plan_name_lower:
                return carrier
        # Fallback to content
        content_lower = content.lower()
        for carrier in known_carriers:
            if carrier.lower() in content_lower:
                return carrier
        return "Unknown Carrier"

    def _extract_plan_type(self, plan_name: str, content: str) -> str:
        """Extract plan type (HMO, PPO, etc.) from plan name or content"""
        plan_types = ['HMO', 'PPO', 'EPO', 'POS', 'HDHP']
        plan_name_upper = plan_name.upper()
        for plan_type in plan_types:
            if plan_type in plan_name_upper:
                return plan_type
        # Fallback to content
        content_upper = content.upper()
        for plan_type in plan_types:
            if plan_type in content_upper:
                return plan_type
        # Metal tier heuristics
        plan_name_lower = plan_name.lower()
        if 'bronze' in plan_name_lower:
            return "HDHP"
        elif 'silver' in plan_name_lower:
            return "HMO"
        elif 'gold' in plan_name_lower:
            return "PPO"
        elif 'platinum' in plan_name_lower:
            return "PPO"
        return "Unknown Type"
    
    def _extract_hsa_eligibility(self, content: str) -> bool:
        """Extract HSA eligibility"""
        content_lower = content.lower()
        # Look for HSA eligibility patterns
        if 'hsa eligible? yes' in content_lower:
            return True
        elif 'hsa eligible? no' in content_lower:
            return False
        # Fallback patterns
        elif 'hsa' in content_lower and 'eligible' in content_lower and 'no' not in content_lower:
            return True
        return False
    
    def create_optimized_documents(self, plans: List[Dict[str, Any]]) -> List[Document]:
        """Create optimized documents with better chunking strategy"""
        documents = []
        
        for plan in plans:
            # Create a structured summary for each plan
            summary = f"""
            PLAN NAME: {plan['plan_name']}
            Carrier: {plan['carrier']}
            Type: {plan['plan_type']}
            Monthly Premium: ${plan['monthly_premium']}
            Deductible: ${plan['deductible']}
            Max Out of Pocket: ${plan['max_out_of_pocket']}
            HSA Eligible: {plan['hsa_eligible']}
            
            Detailed Information:
            {plan['content'][:1000]}  # Limit content length for efficiency
            """
            
            # Create document with metadata for better retrieval
            doc = Document(
                page_content=summary,
                metadata={
                    'plan_name': plan['plan_name'],
                    'carrier': plan['carrier'],
                    'plan_type': plan['plan_type'],
                    'monthly_premium': plan['monthly_premium'],
                    'deductible': plan['deductible'],
                    'max_out_of_pocket': plan['max_out_of_pocket'],
                    'hsa_eligible': plan['hsa_eligible'],
                    'content_hash': hashlib.md5(plan['content'].encode()).hexdigest()
                }
            )
            documents.append(doc)
        
        return documents
    
    def setup_vectorstore(self, documents: List[Document], force_rebuild: bool = False):
        """Setup optimized vector store with persistence"""
        if not force_rebuild and os.path.exists(self.persist_directory):
            print("Loading existing vector database...")
            self.vectordb = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embedding
            )
        else:
            print("Creating new optimized vector database...")
            # Use smaller chunks for better performance
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=256,  # Reduced from 512
                chunk_overlap=25,  # Reduced from 50
                separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
            )
            
            split_docs = splitter.split_documents(documents)
            print(f"Created {len(split_docs)} optimized chunks from {len(documents)} plans")
            
            self.vectordb = Chroma.from_documents(
                split_docs, 
                self.embedding, 
                persist_directory=self.persist_directory
            )
            # self.vectordb.persist()  # Removed as not needed with langchain_chroma
    
    def create_optimized_chain(self):
        """Create optimized QA chain with better prompt and retrieval"""
        custom_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
            You are a health insurance expert. Analyze the following insurance plans and provide the best recommendation based on the user's needs.

            Available Plans Information:
            {context}

            Instructions:
            1. Compare plans based on cost (premium + deductible + max out-of-pocket)
            2. Consider plan type (HMO vs PPO) and network flexibility
            3. Factor in HSA eligibility for tax benefits
            4. Provide specific plan recommendations with reasoning
            5. ALWAYS use the complete plan names as shown in the context, never use generic labels like "Plan A" or "Plan B"

            Question: {question}

            Please provide your analysis in this format:
            **Cost Analysis**: [Compare total costs using actual plan names]
            **Plan Recommendations**: [Top 2-3 plans with complete plan names and specific reasons]
            **Final Recommendation**: [Best overall plan with complete plan name and key benefits]
            
            IMPORTANT: Always refer to plans by their full names (e.g., "Standard High Bronze: HMO" not "Plan A")
            """
        )

        llm = ChatOpenAI(
            temperature=0.2,  # Reduced for more consistent responses
            model="gpt-4o-mini",
            openai_api_key=self.openai_api_key
        )

        # Optimized retriever with better search parameters
        retriever = self.vectordb.as_retriever(
            search_type="mmr",  # Maximum Marginal Relevance for diversity
            search_kwargs={
                "k": 4,  # Reduced from 8 for faster retrieval
                "fetch_k": 8,  # Fetch more initially, then select best 4
                "lambda_mult": 0.7  # Balance between relevance and diversity
            }
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            chain_type="stuff",
            chain_type_kwargs={"prompt": custom_prompt},
            return_source_documents=True
        )
        
        return qa_chain
    
    def query_plans(self, question: str) -> Dict[str, Any]:
        """Query the optimized RAG system"""
        if not self.vectordb:
            raise ValueError("Vector database not initialized. Call setup_vectorstore() first.")
        
        qa_chain = self.create_optimized_chain()
        result = qa_chain({"query": question})
        return result

def main():
    # Set your API key
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError("OPENAI_API_KEY is not set")

    # Initialize optimized RAG system
    rag_system = OptimizedHealthInsuranceRAG(openai_key)
    
    # Load and parse markdown content
    print("Loading and parsing insurance plans...")
    with open("sample_plan.md", "r", encoding="utf-8") as f:
        md_content = f.read()
    
    # Parse plans into structured data
    plans = rag_system.parse_insurance_plans(md_content)
    print(f"Parsed {len(plans)} insurance plans")
    
    # Create optimized documents
    documents = rag_system.create_optimized_documents(plans)
    
    # Setup vector store (will use cached version if available)
    rag_system.setup_vectorstore(documents)
    
    # Test queries
    test_questions = [
        "Compare HMO vs PPO plans available",
        "Give me the names of all the avaiable plans"
    ]
    
    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"{'='*60}")
        
        result = rag_system.query_plans(question)
        print(result["result"])
        print(f"\nSources: {len(result['source_documents'])} documents retrieved")

if __name__ == "__main__":
    main() 