from typing import Dict, Any, List, Optional
from datetime import datetime
from users import User
from auth import AuthenticationManager
from claim import Claim, ClaimJSONHandler
from policy import Policy
from enum import Enum

class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class ClaimAdjuster(User):
    """
    Concrete implementation of the User class for Claim Adjusters.
    """
    def __init__(self, user_id: str, name: str, email: str, password: str):
        super().__init__(user_id, name, email, password, access_level="Claim Adjuster")
        self.specialization: str = ""
        self.cases_handled: int = 0
        self.certification: str = ""
        self.experience_years: int = 0
        self.success_rate: float = 0.0

    def get_user_details(self) -> Dict[str, Any]:
        """Get claim adjuster details"""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "access_level": self.access_level,
            "specialization": self.specialization,
            "cases_handled": self.cases_handled,
            "certification": self.certification,
            "experience_years": self.experience_years,
            "success_rate": self.success_rate
        }

    def update_user_details(self, name: str = None, email: str = None, 
                          password: str = None, specialization: str = None, 
                          certification: str = None) -> bool:
        """Update claim adjuster details"""
        try:
            if name:
                self.name = name
            if email:
                self.email = email
            if password:
                self.set_password(password)
            if specialization:
                self.specialization = specialization
            if certification:
                self.certification = certification
            return True
        except Exception:
            return False

    def get_specialization(self) -> str:
        """Get adjuster's specialization"""
        return self.specialization

    def set_certification(self, cert: str) -> bool:
        """Set adjuster's certification"""
        try:
            self.certification = cert
            return True
        except Exception:
            return False

    def get_experience_years(self) -> int:
        """Get years of experience"""
        return self.experience_years

    def assess_claim_risk(self, claim: Claim, policy: Policy) -> RiskLevel:
        """Assess risk level of a claim"""
        try:
            # Calculate risk score based on multiple factors
            risk_score = 0
            
            # Factor 1: Claim amount relative to policy coverage
            coverage_ratio = claim.get_amount() / policy.get_coverage_amount()
            if coverage_ratio > 0.8:
                risk_score += 3
            elif coverage_ratio > 0.5:
                risk_score += 2
            else:
                risk_score += 1

            # Factor 2: Evidence documents
            if len(claim.evidence_documents) < 2:
                risk_score += 2
            
            # Factor 3: Time since policy start
            policy_start = policy.start_date
            claim_date = claim.date_filed
            days_active = (claim_date - policy_start.date()).days
            if days_active < 30:
                risk_score += 2
            elif days_active < 90:
                risk_score += 1

            # Determine risk level based on score
            if risk_score >= 6:
                return RiskLevel.HIGH
            elif risk_score >= 4:
                return RiskLevel.MEDIUM
            else:
                return RiskLevel.LOW

        except Exception:
            return RiskLevel.HIGH

    def validate_claim_details(self, claim: Claim) -> Dict[str, bool]:
        """Validate claim details"""
        validation_results = {
            "amount_valid": claim.amount > 0,
            "description_valid": bool(claim.description.strip()),
            "evidence_valid": len(claim.evidence_documents) > 0,
            "status_valid": claim.status in [s.value for s in Claim.ClaimStatus]
        }
        return validation_results

    def calculate_claim_payout(self, claim: Claim, policy: Policy) -> float:
        """Calculate claim payout amount"""
        try:
            # Base calculation
            base_amount = min(claim.get_amount(), policy.get_coverage_amount())
            
            # Adjustments based on risk assessment
            risk_level = self.assess_claim_risk(claim, policy)
            risk_multiplier = {
                RiskLevel.LOW: 1.0,
                RiskLevel.MEDIUM: 0.9,
                RiskLevel.HIGH: 0.8
            }.get(risk_level, 0.8)
            
            # Apply evidence bonus (if applicable)
            evidence_bonus = len(claim.evidence_documents) * 0.02  # 2% per evidence
            
            # Calculate final payout
            payout = base_amount * risk_multiplier * (1 + evidence_bonus)
            
            # Ensure payout doesn't exceed policy coverage
            return min(payout, policy.get_coverage_amount())
            
        except Exception:
            return 0.0

    def update_claim_status(self, claim: Claim, new_status: str) -> bool:
        """Update claim status after review"""
        try:
            if claim.set_status(new_status):
                self.cases_handled += 1
                return True
            return False
        except Exception:
            return False

    def generate_assessment_report(self, claim: Claim, policy: Policy) -> Dict:
        """Generate detailed claim assessment report"""
        risk_level = self.assess_claim_risk(claim, policy)
        payout = self.calculate_claim_payout(claim, policy)
        validation = self.validate_claim_details(claim)
        
        return {
            "claim_id": claim.get_claim_id(),
            "policy_id": policy.get_policy_id(),
            "risk_level": risk_level.value,
            "recommended_payout": payout,
            "validation_results": validation,
            "adjuster_id": self.user_id,
            "assessment_date": datetime.now().isoformat(),
            "notes": {
                "coverage_ratio": claim.get_amount() / policy.get_coverage_amount(),
                "evidence_count": len(claim.evidence_documents),
                "claim_status": claim.get_status()
            }
        }

class ClaimAdjusterCLI:
    """CLI interface for Claim Adjusters"""
    def __init__(self, auth_manager: AuthenticationManager):
        self.auth_manager = auth_manager
        self.current_user: Optional[ClaimAdjuster] = None
        self.claims: Dict[str, Claim] = {}
        self.policies: Dict[str, Policy] = {}

    def load_data(self):
        """Load claims and policies data"""
        try:
            self.claims = ClaimJSONHandler.load_claims_from_json("claims.json") or {}
            # Assuming similar PolicyJSONHandler exists
            # self.policies = PolicyJSONHandler.load_policies_from_json("policies.json") or {}
        except Exception as e:
            print(f"Error loading data: {str(e)}")

    def display_menu(self):
        """Display main menu"""
        print("\n=== Claim Adjuster System ===")
        print("1. View All Claims")
        print("2. Process Claim")
        print("3. Generate Assessment Report")
        print("4. Update Profile")
        print("5. View Statistics")
        print("6. Save Changes")
        print("7. Logout")

    def run(self):
        """Main CLI loop"""
        self.load_data()
        while True:
            self.display_menu()
            choice = input("\nEnter your choice (1-7): ").strip()

            if choice == "1":
                self.view_all_claims()
            elif choice == "2":
                self.process_claim()
            elif choice == "3":
                self.generate_report()
            elif choice == "4":
                self.update_profile()
            elif choice == "5":
                self.view_statistics()
            elif choice == "6":
                self.save_changes()
            elif choice == "7":
                self.logout()
                break
            else:
                print("Invalid choice. Please try again.")

    def view_all_claims(self):
        """Display all claims"""
        if not self.claims:
            print("\nNo claims found.")
            return

        print("\n=== All Claims ===")
        for claim in self.claims.values():
            print(f"\nClaim ID: {claim.get_claim_id()}")
            print(f"Status: {claim.get_status()}")
            print(f"Amount: ${claim.get_amount():,.2f}")
            print(f"Description: {claim.get_description()}")

    def process_claim(self):
        """Process a specific claim"""
        claim_id = input("\nEnter Claim ID: ").strip()
        claim = self.claims.get(claim_id)
        
        if not claim:
            print("Claim not found.")
            return

        policy = self.policies.get(claim.get_policy_id())
        if not policy:
            print("Associated policy not found.")
            return

        print(f"\nCurrent Status: {claim.get_status()}")
        risk_level = self.current_user.assess_claim_risk(claim, policy)
        print(f"Risk Level: {risk_level.value}")
        
        action = input("Action (APPROVE/REJECT/REVIEW): ").strip().upper()
        if action in ["APPROVE", "REJECT", "REVIEW"]:
            if self.current_user.update_claim_status(claim, action):
                print(f"Claim status updated to {action}")
                if action == "APPROVE":
                    payout = self.current_user.calculate_claim_payout(claim, policy)
                    print(f"Recommended Payout: ${payout:,.2f}")
            else:
                print("Failed to update claim status")

    def generate_report(self):
        """Generate assessment report for a claim"""
        claim_id = input("\nEnter Claim ID: ").strip()
        claim = self.claims.get(claim_id)
        
        if not claim:
            print("Claim not found.")
            return

        policy = self.policies.get(claim.get_policy_id())
        if not policy:
            print("Associated policy not found.")
            return

        report = self.current_user.generate_assessment_report(claim, policy)
        
        print("\n=== Assessment Report ===")
        for key, value in report.items():
            if isinstance(value, dict):
                print(f"\n{key.replace('_', ' ').title()}:")
                for k, v in value.items():
                    print(f"  {k.replace('_', ' ').title()}: {v}")
            else:
                print(f"{key.replace('_', ' ').title()}: {value}")

    def update_profile(self):
        """Update adjuster's profile"""
        if not self.current_user:
            print("Please log in first.")
            return

        print("\n=== Update Profile ===")
        print("1. Update Name")
        print("2. Update Email")
        print("3. Update Specialization")
        print("4. Update Certification")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            name = input("Enter new name: ").strip()
            if name:
                self.current_user.update_user_details(name=name)
                print("Name updated successfully!")
        elif choice == "2":
            email = input("Enter new email: ").strip()
            if email:
                self.current_user.update_user_details(email=email)
                print("Email updated successfully!")
        elif choice == "3":
            spec = input("Enter new specialization: ").strip()
            if spec:
                self.current_user.update_user_details(specialization=spec)
                print("Specialization updated successfully!")
        elif choice == "4":
            cert = input("Enter new certification: ").strip()
            if cert:
                self.current_user.update_user_details(certification=cert)
                print("Certification updated successfully!")

    def view_statistics(self):
        """View adjuster's performance statistics"""
        if not self.current_user:
            print("Please log in first.")
            return

        print("\n=== Adjuster Statistics ===")
        details = self.current_user.get_user_details()
        print(f"Cases Handled: {details['cases_handled']}")
        print(f"Success Rate: {details['success_rate']:.1f}%")
        print(f"Specialization: {details['specialization']}")
        print(f"Experience: {details['experience_years']} years")
        print(f"Certification: {details['certification']}")

    def save_changes(self):
        """Save current state to files"""
        try:
            if ClaimJSONHandler.save_claims_to_json(self.claims, "claims.json"):
                print("Changes saved successfully!")
            else:
                print("Failed to save changes.")
        except Exception as e:
            print(f"Error saving changes: {str(e)}")

    def logout(self):
        """Logout current user"""
        self.current_user = None
        print("\nLogged out successfully!")