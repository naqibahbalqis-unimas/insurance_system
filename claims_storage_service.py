from datetime import datetime
import json
import os
from typing import Dict, Optional
from claim import Claim, ClaimStatus

class ClaimsStorageService:
    """Service to handle claims storage and retrieval"""
    CLAIMS_FILE = "data/claims_data.json"

    @staticmethod
    def ensure_data_directory():
        """Ensure the data directory exists"""
        directory = os.path.dirname(ClaimsStorageService.CLAIMS_FILE)
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def save_claim(claim: Claim) -> bool:
        """Save a claim to the claims data file"""
        try:
            ClaimsStorageService.ensure_data_directory()
            
            # Load existing claims
            existing_claims = ClaimsStorageService.load_all_claims()
            
            # Add or update the new claim
            claim_dict = claim.to_dict()
            existing_claims[claim.get_claim_id()] = claim_dict
            
            # Save back to file
            with open(ClaimsStorageService.CLAIMS_FILE, 'w') as f:
                json.dump(existing_claims, f, indent=4, default=str)
            
            return True
        except Exception as e:
            print(f"Error saving claim: {str(e)}")
            return False

    @staticmethod
    def load_all_claims() -> Dict:
        """Load all claims from the claims data file"""
        try:
            if os.path.exists(ClaimsStorageService.CLAIMS_FILE):
                with open(ClaimsStorageService.CLAIMS_FILE, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading claims: {str(e)}")
            return {}

    @staticmethod
    def get_pending_claims() -> Dict:
        """Get all pending claims that need adjuster review"""
        all_claims = ClaimsStorageService.load_all_claims()
        return {
            claim_id: claim_data 
            for claim_id, claim_data in all_claims.items() 
            if claim_data.get('status') == 'PENDING'
        }