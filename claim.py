from datetime import datetime, date
from typing import Dict, Optional, List
from enum import Enum
import json
import os

class ClaimStatus(Enum):
    PENDING = "PENDING"
    REVIEWING = "REVIEWING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SETTLED = "SETTLED"

class Claim:
    def __init__(self, claim_id: str, policy_id: str, customer_id: str):
        self.claim_id = claim_id
        self.policy_id = policy_id
        self.customer_id = customer_id
        self.amount: float = 0.0
        self.status: str = ClaimStatus.PENDING.value
        self.description: str = ""
        self.evidence_documents: List[str] = []
        self.date_filed: date = date.today()
        
    def get_claim_id(self) -> str:
        return self.claim_id
        
    def get_policy_id(self) -> str:
        return self.policy_id
        
    def get_customer_id(self) -> str:
        return self.customer_id
        
    def get_amount(self) -> float:
        return self.amount
        
    def get_status(self) -> str:
        return self.status
        
    def get_description(self) -> str:
        return self.description

    def set_amount(self, amount: float) -> bool:
        """Set claim amount with validation"""
        try:
            if amount <= 0:
                return False
            self.amount = amount
            return True
        except ValueError:
            return False

    def set_status(self, status: str) -> bool:
        """Update claim status with validation"""
        try:
            if status in [s.value for s in ClaimStatus]:
                self.status = status
                return True
            return False
        except ValueError:
            return False

    def set_description(self, description: str) -> bool:
        """Set claim description"""
        try:
            if description.strip():
                self.description = description.strip()
                return True
            return False
        except Exception:
            return False

    def add_evidence(self, document_id: str) -> bool:
        """Add supporting document to claim"""
        try:
            if document_id not in self.evidence_documents:
                self.evidence_documents.append(document_id)
                return True
            return False
        except Exception:
            return False

    def calculate_claim(self) -> float:
        """Calculate final claim amount based on evidence and policy limits"""
        try:
            # Base calculation factors
            evidence_factor = len(self.evidence_documents) * 0.05  # 5% increase per evidence
            time_factor = self._calculate_time_factor()
            
            # Adjust claim amount based on factors
            adjusted_amount = self.amount * (1 + evidence_factor) * time_factor
            
            # Apply maximum limit (example: 150% of original claim)
            max_limit = self.amount * 1.5
            return min(adjusted_amount, max_limit)
        except Exception:
            return 0.0

    def _calculate_time_factor(self) -> float:
        """Calculate time-based adjustment factor"""
        try:
            days_since_filing = (date.today() - self.date_filed).days
            if days_since_filing <= 30:  # Within 30 days
                return 1.0
            elif days_since_filing <= 60:  # 30-60 days
                return 0.95  # 5% reduction
            else:  # Over 60 days
                return 0.90  # 10% reduction
        except Exception:
            return 1.0

    def validate_claim(self, policies: Dict) -> bool:
        """Validate claim details including policy and customer validation"""
        try:
            # Basic validation
            if not all([
                self.claim_id and self.policy_id and self.customer_id,  # Required fields
                self.amount > 0,                                        # Positive amount
                self.description.strip(),                              # Non-empty description
                len(self.evidence_documents) > 0                       # At least one evidence
            ]):
                return False
                
            # Validate policy exists and is active
            policy = policies.get(self.policy_id)
            if not policy:
                return False
                
            # Validate customer matches policy
            if policy.get_customer_id() != self.customer_id:
                return False
                
            # Validate claim amount against policy coverage
            if self.amount > policy.get_coverage_amount():
                return False
                
            # Validate policy status
            if policy.get_status().value not in ["ACTIVE"]:
                return False
                
            return True
                
        except Exception:
            return False

    def to_dict(self) -> Dict:
        """Convert claim to dictionary for serialization"""
        return {
            'claim_id': self.claim_id,
            'policy_id': self.policy_id,
            'customer_id': self.customer_id,
            'amount': self.amount,
            'status': self.status,
            'description': self.description,
            'evidence_documents': self.evidence_documents,
            'date_filed': self.date_filed.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Claim':
        """Create claim instance from dictionary"""
        claim = cls(
            claim_id=data['claim_id'],
            policy_id=data['policy_id'],
            customer_id=data['customer_id']
        )
        claim.amount = data['amount']
        claim.status = data['status']
        claim.description = data['description']
        claim.evidence_documents = data['evidence_documents']
        claim.date_filed = datetime.fromisoformat(data['date_filed']).date()
        return claim

    def __str__(self) -> str:
        """String representation of the claim"""
        return (f"Claim {self.claim_id} - Policy: {self.policy_id}, "
                f"Amount: ${self.amount:.2f}, Status: {self.status}")

class ClaimJSONHandler:
    """Handler for saving and loading claims from JSON files"""
    
    @staticmethod
    def save_claims_to_json(claims: Dict[str, Claim], filename: str) -> bool:
        """Save claims to a JSON file"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            # Convert claims to dictionary format
            claims_data = {
                claim_id: claim.to_dict() 
                for claim_id, claim in claims.items()
            }
            
            # Ensure .json extension
            if not filename.endswith('.json'):
                filename += '.json'
                
            # Save to file
            filepath = os.path.join('data', filename)
            with open(filepath, 'w') as f:
                json.dump(claims_data, f, indent=4)
            
            return True
            
        except Exception as e:
            print(f"Error saving claims: {str(e)}")
            return False

    @staticmethod
    def load_claims_from_json(filename: str) -> Optional[Dict[str, Claim]]:
        """Load claims from a JSON file"""
        try:
            # Ensure .json extension
            if not filename.endswith('.json'):
                filename += '.json'
                
            filepath = os.path.join('data', filename)
            
            # Check if file exists
            if not os.path.exists(filepath):
                return None
                
            # Load and parse JSON
            with open(filepath, 'r') as f:
                claims_data = json.load(f)
                
            # Convert back to Claim objects
            claims = {
                claim_id: Claim.from_dict(claim_data)
                for claim_id, claim_data in claims_data.items()
            }
            
            return claims
            
        except Exception as e:
            print(f"Error loading claims: {str(e)}")
            return None