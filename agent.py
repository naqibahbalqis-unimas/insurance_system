from tabulate import tabulate
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from enum import Enum
from users import User, UserManager  # Add UserManager import
from auth import AuthenticationManager
from policy import Policy, PolicyType, PolicyStatus
import json
import os

class SaleStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class PerformanceLevel(Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"

class Sale:
    def __init__(self, sale_id: str, policy_id: str, customer_id: str, amount: float):
        self.sale_id = sale_id
        self.policy_id = policy_id
        self.customer_id = customer_id
        self.amount = amount
        self.commission_earned = 0.0
        self.sale_date = datetime.now()
        self.status = SaleStatus.PENDING.value

    def to_dict(self) -> Dict:
        return {
            'sale_id': self.sale_id,
            'policy_id': self.policy_id,
            'customer_id': self.customer_id,
            'amount': self.amount,
            'commission_earned': self.commission_earned,
            'sale_date': self.sale_date.isoformat(),
            'status': self.status
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Sale':
        sale = cls(
            data['sale_id'],
            data['policy_id'],
            data['customer_id'],
            data['amount']
        )
        sale.commission_earned = data['commission_earned']
        sale.sale_date = datetime.fromisoformat(data['sale_date'])
        sale.status = data['status']
        return sale

class Agent(User):
    """Implementation of insurance sales agent"""
    def __init__(self, user_id: str, name: str, email: str, password: str):
        super().__init__(user_id, name, email, password, access_level="Agent")
        self.commission_rate: float = 0.0
        self.sales_target: float = 0.0
        self.territory: str = ""
        self.specializations: List[str] = []
        self.current_performance_level: str = PerformanceLevel.BRONZE.value
        self.total_sales: float = 0.0
        self.sales_count: int = 0
        self.customer_satisfaction_score: float = 0.0

    def get_user_details(self) -> Dict:
        """Get agent details including performance metrics"""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "commission_rate": self.commission_rate,
            "sales_target": self.sales_target,
            "territory": self.territory,
            "specializations": self.specializations,
            "performance_level": self.current_performance_level,
            "total_sales": self.total_sales,
            "sales_count": self.sales_count,
            "customer_satisfaction": self.customer_satisfaction_score,
            "target_achievement": self.calculate_target_achievement()
        }

    def update_user_details(self, **kwargs) -> bool:
        """Update agent details"""
        try:
            if 'name' in kwargs and kwargs['name']:
                self.name = kwargs['name']
            if 'email' in kwargs and kwargs['email']:
                self.email = kwargs['email']
            if 'password' in kwargs and kwargs['password']:
                self.password = kwargs['password']
            if 'territory' in kwargs and kwargs['territory']:
                self.territory = kwargs['territory']
            if 'specializations' in kwargs and isinstance(kwargs['specializations'], list):
                self.specializations = kwargs['specializations']
            return True
        except Exception as e:
            print(f"Error updating user details: {str(e)}")
            return False

    def set_commission_rate(self, rate: float) -> bool:
        """Set agent's commission rate"""
        try:
            if rate < 0:
                raise ValueError("Commission rate cannot be negative.")
            self.commission_rate = rate
            return True
        except ValueError as e:
            print(f"Invalid commission rate: {str(e)}")
            return False

    def set_sales_target(self, target: float) -> bool:
        """Set agent's sales target"""
        try:
            if target < 0:
                raise ValueError("Sales target cannot be negative.")
            self.sales_target = target
            return True
        except ValueError as e:
            print(f"Invalid sales target: {str(e)}")
            return False

    def calculate_commission(self, sale_amount: float) -> float:
        """Calculate commission for a sale with performance bonuses"""
        try:
            if sale_amount < 0:
                raise ValueError("Sale amount cannot be negative.")
            base_commission = sale_amount * self.commission_rate
            # Add a small bonus for demonstration
            if self.current_performance_level == "GOLD":
                base_commission *= 1.05
            elif self.current_performance_level == "PLATINUM":
                base_commission *= 1.10
            return base_commission
        except Exception as e:
            print(f"Error calculating commission: {str(e)}")
            return 0.0

    def calculate_target_achievement(self) -> float:
        """Calculate percentage of sales target achieved"""
        try:
            if self.sales_target <= 0:
                return 0.0
            return self.total_sales / self.sales_target
        except Exception as e:
            print(f"Error calculating target achievement: {str(e)}")
            return 0.0

    def update_performance_level(self) -> bool:
        """Update performance level based on sales and satisfaction"""
        try:
            achievement = self.calculate_target_achievement()
            if achievement >= 1.0 and self.customer_satisfaction_score >= 4.5:
                self.current_performance_level = "PLATINUM"
            elif achievement >= 0.8:
                self.current_performance_level = "GOLD"
            elif achievement >= 0.5:
                self.current_performance_level = "SILVER"
            else:
                self.current_performance_level = "BRONZE"
            return True
        except Exception as e:
            print(f"Error updating performance level: {str(e)}")
            return False

    def record_sale(self, sale: Sale) -> bool:
        """Record a new sale"""
        try:
            commission = self.calculate_commission(sale.amount)
            sale.commission_earned = commission
            self.sales_count += 1
            self.total_sales += sale.amount
            return True
        except Exception as e:
            print(f"Error recording sale: {str(e)}")
            return False

class AgentCLI:
    """CLI interface for insurance agents"""
    def __init__(self, auth_manager: AuthenticationManager):
        self.auth_manager = auth_manager
        self.current_user: Optional[Agent] = None
        self.sales: Dict[str, Sale] = {}
        self.policies: Dict[str, Policy] = {}
        self.sales_data_file = "data/sales.json"
        self.user_manager = UserManager(auth_manager)  # Add UserManager instance
        self.customers: Dict[str, Dict] = {}  # Track created customers

    def load_data(self):
        """Load sales and policies data"""
        try:
            if os.path.exists(self.sales_data_file):
                with open(self.sales_data_file, 'r') as f:
                    sales_data = json.load(f)
                self.sales = {
                    sale_id: Sale.from_dict(data)
                    for sale_id, data in sales_data.items()
                }
        except Exception as e:
            print(f"Error loading data: {str(e)}")

    def save_data(self):
        """Save sales data"""
        try:
            os.makedirs('data', exist_ok=True)
            sales_data = {
                sale_id: sale.to_dict()
                for sale_id, sale in self.sales.items()
            }
            with open(self.sales_data_file, 'w') as f:
                json.dump(sales_data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving data: {str(e)}")
            return False

    def display_menu(self):
        menu_options = [
            ["1", "View Sales Dashboard"],
            ["2", "Record New Sale"],
            ["3", "View Performance Metrics"],
            ["4", "Manage Customers"],
            ["5", "Manage Policies"],
            ["6", "Update Profile"],
            ["7", "Generate Reports"],
            ["8", "Logout"]
        ]
        print("\n=== Insurance Agent Portal ===")
        print(tabulate(menu_options, headers=["Option", "Description"], tablefmt="grid"))

    def run(self):
        """Main CLI loop"""
        self.load_data()
        self.load_customer_data()  # Load customer data
        while True:
            self.display_menu()
            choice = input("\nEnter your choice (1-8): ").strip()

            if choice == "1":
                self.view_sales_dashboard()
            elif choice == "2":
                self.record_new_sale()
            elif choice == "3":
                self.view_performance_metrics()
            elif choice == "4":
                self.manage_customers()
            elif choice == "5":
                self.manage_policies()
            elif choice == "6":
                self.update_profile()
            elif choice == "7":
                self.generate_reports()
            elif choice == "8":
                self.save_data()
                self.logout()
                break
            else:
                print("Invalid choice. Please try again.")

    def view_sales_dashboard(self):
        if not self.current_user:
            print("Please log in first.")
            return

        print("\n=== Sales Dashboard ===")
        dashboard_data = [
            ["Total Sales", f"${self.current_user.total_sales:,.2f}"],
            ["Sales Count", self.current_user.sales_count],
            ["Target Achievement", f"{self.current_user.calculate_target_achievement():.1%}"],
            ["Performance Level", self.current_user.current_performance_level]
        ]
        print(tabulate(dashboard_data, headers=["Metric", "Value"], tablefmt="grid"))

        # Recent sales
        recent_sales = sorted(self.sales.values(), key=lambda x: x.sale_date, reverse=True)[:5]
        sales_table = [
            [sale.sale_id, f"${sale.amount:,.2f}", f"${sale.commission_earned:,.2f}", sale.sale_date.strftime("%Y-%m-%d")]
            for sale in recent_sales
        ]
        print("\nRecent Sales:")
        print(tabulate(sales_table, headers=["Sale ID", "Amount", "Commission", "Date"], tablefmt="grid"))

    def record_new_sale(self):
        """Record a new policy sale"""
        if not self.current_user:
            print("Please log in first.")
            return

        try:
            print("\n=== Record New Sale ===")
            
            # Get policy type
            print("\nAvailable Policy Types:")
            for policy_type in PolicyType:
                print(f"- {policy_type.name}")
            
            policy_type = input("Enter Policy Type: ").strip().upper()
            if policy_type not in PolicyType.__members__:
                print("Invalid policy type.")
                return
                
            # Get policy details
            policy_id = f"POL_{len(self.policies) + 1}"
            customer_id = input("Enter Customer ID: ").strip()
            premium = float(input("Enter Premium Amount: $"))
            
            # Create sale record
            sale_id = f"SALE_{len(self.sales) + 1}"
            sale = Sale(sale_id, policy_id, customer_id, premium)
            
            if self.current_user.record_sale(sale):
                self.sales[sale_id] = sale
                print(f"\nSale recorded successfully!")
                print(f"Commission Earned: ${sale.commission_earned:,.2f}")
                self.save_data()
            else:
                print("Failed to record sale.")
                
        except ValueError as e:
            print(f"Invalid input: {str(e)}")
        except Exception as e:
            print(f"Error recording sale: {str(e)}")

    def view_performance_metrics(self):
        if not self.current_user:
            print("Please log in first.")
            return

        print("\n=== Performance Metrics ===")
        metrics = self.current_user.get_user_details()
        metrics_table = [
            ["Sales Target", f"${metrics['sales_target']:,.2f}"],
            ["Total Sales", f"${metrics['total_sales']:,.2f}"],
            ["Target Achievement", f"{metrics['target_achievement']:.1%}"],
            ["Performance Level", metrics["performance_level"]],
            ["Customer Satisfaction", f"{metrics['customer_satisfaction']:.1f}/5.0"],
            ["Commission Rate", f"{metrics['commission_rate']:.1%}"]
        ]
        print(tabulate(metrics_table, headers=["Metric", "Value"], tablefmt="grid"))

        # Monthly breakdown
        print("\nMonthly Sales Breakdown:")
        monthly_sales = self._calculate_monthly_sales()
        sales_table = [[month, f"${amount:,.2f}"] for month, amount in monthly_sales.items()]
        print(tabulate(sales_table, headers=["Month", "Sales"], tablefmt="grid"))

    def _calculate_monthly_sales(self) -> Dict[str, float]:
        """Calculate sales by month"""
        monthly_sales = {}
        for sale in self.sales.values():
            month_key = sale.sale_date.strftime("%Y-%m")
            monthly_sales[month_key] = monthly_sales.get(month_key, 0) + sale.amount
        return dict(sorted(monthly_sales.items()))

    def manage_policies(self):
        """Manage policy-related tasks"""
        print("\n=== Policy Management ===")
        print("1. View Active Policies")
        print("2. Check Policy Status")
        print("3. Back")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            self._update_personal_details()
        elif choice == "2":
            self._update_territory()
        elif choice == "3":
            self._add_specialization()

    def _update_personal_details(self):
        """Update agent's personal information"""
        print("\n=== Update Personal Details ===")
        name = input("Enter new name (press Enter to skip): ").strip()
        email = input("Enter new email (press Enter to skip): ").strip()
        password = input("Enter new password (press Enter to skip): ").strip()

        updates = {}
        if name:
            updates['name'] = name
        if email:
            updates['email'] = email
        if password:
            updates['password'] = password

        if updates and self.current_user.update_user_details(**updates):
            print("Personal details updated successfully!")
        else:
            print("No changes made.")

    def _update_territory(self):
        """Update agent's territory"""
        print("\n=== Update Territory ===")
        territory = input("Enter new territory: ").strip()
        if territory:
            if self.current_user.update_user_details(territory=territory):
                print("Territory updated successfully!")
            else:
                print("Failed to update territory.")

    def _add_specialization(self):
        """Add a new specialization"""
        print("\n=== Add Specialization ===")
        print("Available specializations:")
        print("- Life Insurance")
        print("- Property Insurance")
        print("- Health Insurance")
        print("- Vehicle Insurance")
        
        spec = input("\nEnter specialization: ").strip()
        if spec:
            current_specs = self.current_user.specializations
            if spec not in current_specs:
                current_specs.append(spec)
                if self.current_user.update_user_details(specializations=current_specs):
                    print("Specialization added successfully!")
                else:
                    print("Failed to add specialization.")
            else:
                print("Specialization already exists.")

    def generate_reports(self):
        """Generate various sales and performance reports"""
        print("\n=== Generate Reports ===")
        print("1. Sales Performance Report")
        print("2. Commission Report")
        print("3. Customer Analysis Report")
        print("4. Back")

        choice = input("\nEnter choice (1-4): ").strip()

        if choice == "1":
            self._generate_sales_report()
        elif choice == "2":
            self._generate_commission_report()
        elif choice == "3":
            self._generate_customer_analysis()

    def _generate_sales_report(self):
        """Generate detailed sales performance report"""
        if not self.sales:
            print("No sales data available.")
            return

        print("\n=== Sales Performance Report ===")
        
        # Overall Performance
        target_achievement = self.current_user.calculate_target_achievement()
        print(f"\nOverall Performance:")
        print(f"Sales Target: ${self.current_user.sales_target:,.2f}")
        print(f"Total Sales: ${self.current_user.total_sales:,.2f}")
        print(f"Achievement: {target_achievement:.1%}")
        print(f"Performance Level: {self.current_user.current_performance_level}")

        # Monthly Breakdown
        print("\nMonthly Sales Breakdown:")
        monthly_sales = self._calculate_monthly_sales()
        for month, amount in monthly_sales.items():
            print(f"{month}: ${amount:,.2f}")

        # Policy Type Distribution
        print("\nSales by Policy Type:")
        policy_sales = self._calculate_sales_by_policy_type()
        for policy_type, amount in policy_sales.items():
            print(f"{policy_type}: ${amount:,.2f}")

        # Save report
        self._save_report("sales_performance", {
            "target_achievement": target_achievement,
            "total_sales": self.current_user.total_sales,
            "monthly_sales": monthly_sales,
            "policy_sales": policy_sales
        })

    def _generate_commission_report(self):
        """Generate commission earnings report"""
        if not self.sales:
            print("No commission data available.")
            return

        print("\n=== Commission Report ===")
        
        # Total Commission
        total_commission = sum(sale.commission_earned for sale in self.sales.values())
        print(f"\nTotal Commission Earned: ${total_commission:,.2f}")
        print(f"Base Commission Rate: {self.current_user.commission_rate:.1%}")

        # Monthly Commission
        print("\nMonthly Commission Breakdown:")
        monthly_commission = {}
        for sale in self.sales.values():
            month_key = sale.sale_date.strftime("%Y-%m")
            monthly_commission[month_key] = monthly_commission.get(month_key, 0) + sale.commission_earned
        
        for month, amount in sorted(monthly_commission.items()):
            print(f"{month}: ${amount:,.2f}")

        # Performance Bonuses
        print("\nPerformance Bonuses:")
        print(f"Level Bonus: {self._calculate_level_bonus():.1%}")
        if self.current_user.calculate_target_achievement() >= 1.0:
            print("Target Achievement Bonus: 10%")

        # Save report
        self._save_report("commission", {
            "total_commission": total_commission,
            "monthly_commission": monthly_commission,
            "base_rate": self.current_user.commission_rate,
            "bonuses": self._calculate_level_bonus()
        })

    def _generate_customer_analysis(self):
        """Generate customer analysis report"""
        if not self.sales:
            print("No customer data available.")
            return

        print("\n=== Customer Analysis Report ===")
        
        # Customer Distribution
        customers = {}
        for sale in self.sales.values():
            if sale.customer_id not in customers:
                customers[sale.customer_id] = {
                    "total_purchases": 0,
                    "total_value": 0.0,
                    "policies": set()
                }
            customers[sale.customer_id]["total_purchases"] += 1
            customers[sale.customer_id]["total_value"] += sale.amount
            customers[sale.customer_id]["policies"].add(sale.policy_id)

        # Summary Statistics
        print(f"\nTotal Customers: {len(customers)}")
        avg_purchase = sum(c["total_value"] for c in customers.values()) / len(customers)
        print(f"Average Purchase Value: ${avg_purchase:,.2f}")
        
        # Top Customers
        print("\nTop 5 Customers by Value:")
        top_customers = sorted(
            customers.items(),
            key=lambda x: x[1]["total_value"],
            reverse=True
        )[:5]
        
        for customer_id, data in top_customers:
            print(f"\nCustomer ID: {customer_id}")
            print(f"Total Purchases: {data['total_purchases']}")
            print(f"Total Value: ${data['total_value']:,.2f}")
            print(f"Number of Policies: {len(data['policies'])}")

        # Save report
        self._save_report("customer_analysis", {
            "total_customers": len(customers),
            "average_purchase": avg_purchase,
            "top_customers": [
                {
                    "id": cid,
                    "data": {
                        "purchases": d["total_purchases"],
                        "value": d["total_value"],
                        "policy_count": len(d["policies"])
                    }
                }
                for cid, d in top_customers
            ]
        })

    def _calculate_sales_by_policy_type(self) -> Dict[str, float]:
        """Calculate sales amount by policy type"""
        policy_sales = {}
        for sale in self.sales.values():
            policy = self.policies.get(sale.policy_id)
            if policy:
                policy_type = policy.get_policy_type().value
                policy_sales[policy_type] = policy_sales.get(policy_type, 0) + sale.amount
        return policy_sales

    def _calculate_level_bonus(self) -> float:
        """Calculate performance level bonus percentage"""
        bonus_rates = {
            PerformanceLevel.BRONZE.value: 0.0,
            PerformanceLevel.SILVER.value: 0.1,
            PerformanceLevel.GOLD.value: 0.2,
            PerformanceLevel.PLATINUM.value: 0.3
        }
        return bonus_rates.get(self.current_user.current_performance_level, 0.0)

    def _save_report(self, report_type: str, data: Dict):
        """Save report to file"""
        try:
            os.makedirs('reports', exist_ok=True)
            filename = f"reports/{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            report_data = {
                "report_type": report_type,
                "agent_id": self.current_user.user_id,
                "generated_at": datetime.now().isoformat(),
                "data": data
            }
            
            with open(filename, 'w') as f:
                json.dump(report_data, f, indent=4)
            print(f"\nReport saved to {filename}")
        except Exception as e:
            print(f"Error saving report: {str(e)}")

    def manage_customer_communications(self):
        """Handle customer communications and follow-ups"""
        print("\n=== Customer Communications ===")
        print("1. View Customer List")
        print("2. Schedule Follow-up")
        print("3. View Follow-up Tasks")
        print("4. Record Customer Feedback")
        print("5. Back")

        choice = input("\nEnter choice (1-5): ").strip()

        if choice == "1":
            self._view_customer_list()
        elif choice == "2":
            self._schedule_followup()
        elif choice == "3":
            self._view_followup_tasks()
        elif choice == "4":
            self._record_customer_feedback()

    def _view_customer_list(self):
        """Display list of customers and their policies"""
        customer_data = {}
        for sale in self.sales.values():
            if sale.customer_id not in customer_data:
                customer_data[sale.customer_id] = {
                    'policies': [],
                    'total_value': 0.0,
                    'last_interaction': None
                }
            customer_data[sale.customer_id]['policies'].append(sale.policy_id)
            customer_data[sale.customer_id]['total_value'] += sale.amount
            sale_date = sale.sale_date
            if not customer_data[sale.customer_id]['last_interaction'] or \
               sale_date > customer_data[sale.customer_id]['last_interaction']:
                customer_data[sale.customer_id]['last_interaction'] = sale_date

        print("\n=== Customer List ===")
        for customer_id, data in customer_data.items():
            print(f"\nCustomer ID: {customer_id}")
            print(f"Number of Policies: {len(data['policies'])}")
            print(f"Total Value: ${data['total_value']:,.2f}")
            print(f"Last Interaction: {data['last_interaction'].strftime('%Y-%m-%d')}")

    def _schedule_followup(self):
        """Schedule a follow-up task with a customer"""
        customer_id = input("\nEnter Customer ID: ").strip()
        if customer_id not in {sale.customer_id for sale in self.sales.values()}:
            print("Customer not found.")
            return

        date_str = input("Enter follow-up date (YYYY-MM-DD): ").strip()
        try:
            followup_date = datetime.strptime(date_str, "%Y-%m-%d")
            task_description = input("Enter task description: ").strip()

            if not hasattr(self, 'followup_tasks'):
                self.followup_tasks = []

            self.followup_tasks.append({
                'customer_id': customer_id,
                'date': followup_date,
                'description': task_description,
                'status': 'PENDING'
            })
            print("Follow-up task scheduled successfully!")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

    def _view_followup_tasks(self):
        """View scheduled follow-up tasks"""
        if not hasattr(self, 'followup_tasks') or not self.followup_tasks:
            print("\nNo follow-up tasks scheduled.")
            return

        print("\n=== Follow-up Tasks ===")
        for task in sorted(self.followup_tasks, key=lambda x: x['date']):
            print(f"\nCustomer ID: {task['customer_id']}")
            print(f"Date: {task['date'].strftime('%Y-%m-%d')}")
            print(f"Description: {task['description']}")
            print(f"Status: {task['status']}")

    def _record_customer_feedback(self):
        """Record customer feedback and satisfaction"""
        customer_id = input("\nEnter Customer ID: ").strip()
        if customer_id not in {sale.customer_id for sale in self.sales.values()}:
            print("Customer not found.")
            return

        try:
            satisfaction_score = float(input("Enter satisfaction score (1-5): "))
            if not 1 <= satisfaction_score <= 5:
                print("Score must be between 1 and 5.")
                return

            feedback_text = input("Enter feedback comments: ").strip()

            if not hasattr(self, 'customer_feedback'):
                self.customer_feedback = {}

            self.customer_feedback[customer_id] = {
                'score': satisfaction_score,
                'feedback': feedback_text,
                'date': datetime.now()
            }

            # Update agent's customer satisfaction score
            all_scores = [f['score'] for f in self.customer_feedback.values()]
            self.current_user.customer_satisfaction_score = sum(all_scores) / len(all_scores)
            
            print("Customer feedback recorded successfully!")
        except ValueError:
            print("Invalid satisfaction score. Please enter a number between 1 and 5.")

    def calculate_performance_metrics(self) -> Dict:
        """Calculate comprehensive performance metrics"""
        metrics = {
            'sales_metrics': {
                'total_sales': self.current_user.total_sales,
                'sales_count': self.current_user.sales_count,
                'avg_sale_value': self.current_user.total_sales / self.current_user.sales_count if self.current_user.sales_count > 0 else 0,
                'target_achievement': self.current_user.calculate_target_achievement()
            },
            'commission_metrics': {
                'total_commission': sum(sale.commission_earned for sale in self.sales.values()),
                'avg_commission_rate': self.current_user.commission_rate,
                'performance_bonus': self._calculate_level_bonus()
            },
            'customer_metrics': {
                'total_customers': len(set(sale.customer_id for sale in self.sales.values())),
                'satisfaction_score': self.current_user.customer_satisfaction_score,
                'active_policies': len(self.policies)
            },
            'performance_level': {
                'current_level': self.current_user.current_performance_level,
                'progression_to_next': self._calculate_level_progression()
            }
        }
        return metrics

    def _calculate_level_progression(self) -> float:
        """Calculate progression towards next performance level"""
        current_level = self.current_user.current_performance_level
        target_achievement = self.current_user.calculate_target_achievement()
        
        level_thresholds = {
            PerformanceLevel.BRONZE.value: (0.0, 0.5),
            PerformanceLevel.SILVER.value: (0.5, 0.75),
            PerformanceLevel.GOLD.value: (0.75, 0.9),
            PerformanceLevel.PLATINUM.value: (0.9, 1.0)
        }

        current_threshold = level_thresholds.get(current_level)
        if not current_threshold:
            return 0.0

        min_threshold, max_threshold = current_threshold
        if target_achievement < min_threshold:
            return 0.0
        elif target_achievement > max_threshold:
            return 1.0
        else:
            return (target_achievement - min_threshold) / (max_threshold - min_threshold)

    def logout(self):
        """Logout and cleanup"""
        if self.current_user:
            self.save_data()
            self.current_user = None
        print("\nLogged out successfully!")
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            self._view_active_policies()
        elif choice == "2":
            self._check_policy_status()

    def _view_active_policies(self):
        """Display active policies"""
        active_policies = [p for p in self.policies.values() 
                         if p.get_status() == PolicyStatus.ACTIVE]
        
        if not active_policies:
            print("\nNo active policies found.")
            return
            
        print("\n=== Active Policies ===")
        for policy in active_policies:
            print(f"\nPolicy ID: {policy.get_policy_id()}")
            print(f"Type: {policy.get_policy_type().value}")
            print(f"Premium: ${policy.get_premium():,.2f}")

    def _check_policy_status(self):
        """Check status of a specific policy"""
        policy_id = input("\nEnter Policy ID: ").strip()
        policy = self.policies.get(policy_id)
        
        if policy:
            print(f"\nStatus: {policy.get_status().value}")
            print(f"Type: {policy.get_policy_type().value}")
            print(f"Premium: ${policy.get_premium():,.2f}")
        else:
            print("Policy not found.")

    def update_profile(self):
        """Update agent profile"""
        if not self.current_user:
            print("Please log in first.")
            return

        print("\n=== Update Profile ===")
        print("1. Update Personal Details")
        print("2. Update Territory")
        print("3. Add Specialization")
        print("4. Back")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            self._update_personal_details()
        elif choice == "2":
            self._update_territory()
        elif choice == "3":
            self._add_specialization()
    
    def view_reports(self):
        """View saved reports"""
        try:
            report_dir = 'reports'
            if not os.path.exists(report_dir):
                print("No reports found.")
                return

            reports = [f for f in os.listdir(report_dir) if f.endswith('.json')]
            if not reports:
                print("No reports found.")
                return

            print("\n=== Available Reports ===")
            for i, report in enumerate(reports, 1):
                print(f"{i}. {report}")

            choice = input("\nEnter report number to view (or 0 to go back): ").strip()
            try:
                choice_idx = int(choice) - 1
                if choice_idx < -1 or choice_idx >= len(reports):
                    print("Invalid choice.")
                    return
                if choice_idx == -1:
                    return

                report_path = os.path.join(report_dir, reports[choice_idx])
                with open(report_path, 'r') as f:
                    report_data = json.load(f)
                    
                print(f"\n=== Report: {reports[choice_idx]} ===")
                print(f"Type: {report_data['report_type']}")
                print(f"Generated: {report_data['generated_at']}")
                print("\nData:")
                self._print_report_data(report_data['data'])

            except ValueError:
                print("Invalid input.")
            except Exception as e:
                print(f"Error reading report: {str(e)}")

        except Exception as e:
            print(f"Error accessing reports: {str(e)}")

    def _print_report_data(self, data: Dict, indent: int = 0):
        """Helper method to print nested report data"""
        indent_str = "  " * indent
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"{indent_str}{key}:")
                self._print_report_data(value, indent + 1)
            elif isinstance(value, list):
                print(f"{indent_str}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        self._print_report_data(item, indent + 1)
                    else:
                        print(f"{indent_str}  {item}")
            elif isinstance(value, float):
                if "rate" in key.lower() or "percentage" in key.lower():
                    print(f"{indent_str}{key}: {value:.1%}")
                else:
                    print(f"{indent_str}{key}: ${value:,.2f}")
            else:
                print(f"{indent_str}{key}: {value}")

    def handle_notifications(self):
        """Process and display agent notifications"""
        notifications = []

        # Check for pending follow-ups
        if hasattr(self, 'followup_tasks'):
            today = datetime.now().date()
            pending_followups = [
                task for task in self.followup_tasks 
                if task['status'] == 'PENDING' and task['date'].date() <= today
            ]
            if pending_followups:
                notifications.extend([
                    f"Pending follow-up for Customer {task['customer_id']} due on {task['date'].strftime('%Y-%m-%d')}"
                    for task in pending_followups
                ])

        # Check sales targets
        target_achievement = self.current_user.calculate_target_achievement()
        if target_achievement < 0.5 and self.current_user.sales_target > 0:
            notifications.append(f"Warning: Sales target achievement is low ({target_achievement:.1%})")

        # Display notifications
        if notifications:
            print("\n=== Notifications ===")
            for notification in notifications:
                print(f"- {notification}")
        else:
            print("\nNo pending notifications.")

    def export_data(self):
        """Export agent data to various formats"""
        print("\n=== Export Data ===")
        print("1. Export Sales Data")
        print("2. Export Performance Metrics")
        print("3. Export Customer Data")
        print("4. Back")

        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            self._export_sales_data()
        elif choice == "2":
            self._export_performance_metrics()
        elif choice == "3":
            self._export_customer_data()

    def _export_sales_data(self):
        """Export sales data to JSON"""
        try:
            filename = f"exports/sales_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs('exports', exist_ok=True)
            
            export_data = {
                'sales': {
                    sale_id: sale.to_dict()
                    for sale_id, sale in self.sales.items()
                },
                'total_sales': self.current_user.total_sales,
                'sales_count': self.current_user.sales_count,
                'export_date': datetime.now().isoformat()
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=4)
            print(f"\nSales data exported to {filename}")
            
        except Exception as e:
            print(f"Error exporting sales data: {str(e)}")

    def manage_customers(self):
        """Customer management menu"""
        print("\n=== Customer Management ===")
        print("1. Create New Customer")
        print("2. View Customer Details")
        print("3. Search Customer")
        print("4. List All Customers")  # Added
        print("5. Back")

        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            self.create_new_customer()
        elif choice == "2":
            self.view_customer_details()
        elif choice == "3":
            self.search_customer()
        elif choice == "4":
            self.list_all_customers()

    def create_new_customer(self):
        """Create a new customer account"""
        print("\n=== Create New Customer ===")
        email = input("Enter customer email: ").strip()
        password = input("Enter customer password: ").strip()
        name = input("Enter customer name: ").strip()
        
        success, message = self.user_manager.create_user(email, password)
        if success:
            user = self.user_manager.get_user(email)
            if user:
                print(f"\nCustomer created successfully!")
                print(f"Customer ID: {email}")  # Use email as customer ID
                print("Please save this ID for future reference")
                
                # Update customer details
                contact = input("Enter contact number: ").strip()
                address = input("Enter address: ").strip()
                
                try:
                    credit_score = float(input("Enter credit score (0-850): ").strip())
                except ValueError:
                    credit_score = 0.0
                
                success, message = self.user_manager.update_user(
                    email,
                    name=name,
                    _contact_number=contact,
                    address=address,
                    credit_score=credit_score
                )
                
                if success:
                    print("Customer details updated successfully!")
                    # Store customer in agent's customer list
                    self.customers[email] = {
                        'name': name,
                        'contact': contact,
                        'address': address,
                        'credit_score': credit_score,
                        'creation_date': datetime.now().isoformat()
                    }
                    self.save_customer_data()
                else:
                    print(f"Failed to update customer details: {message}")
            else:
                print("Error creating customer profile")
        else:
            print(f"Failed to create customer: {message}")

    def view_customer_details(self):
        """View customer details"""
        customer_id = input("\nEnter Customer ID (email): ").strip()
        customer_info = self.user_manager.lookup_customer(customer_id)
        
        if customer_info:
            print("\n=== Customer Details ===")
            for key, value in customer_info.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
            
            # Show associated policies and sales
            policies = [p for p in self.policies.values() if p.get_customer_id() == customer_id]
            sales = [s for s in self.sales.values() if s.customer_id == customer_id]
            
            if policies:
                print("\nAssociated Policies:")
                for policy in policies:
                    print(f"- Policy ID: {policy.get_policy_id()}, "
                          f"Type: {policy.get_policy_type().name}, "
                          f"Status: {policy.get_status().name}")
            
            if sales:
                print("\nSales History:")
                for sale in sales:
                    print(f"- Sale ID: {sale.sale_id}, "
                          f"Amount: ${sale.amount:,.2f}, "
                          f"Date: {sale.sale_date.strftime('%Y-%m-%d')}")
        else:
            print("Customer not found")

    def list_all_customers(self):
        """Display list of all customers"""
        customers = self.user_manager.users
        if not customers:
            print("\nNo customers found.")
            return
            
        print("\n=== Customer List ===")
        for email, user in customers.items():
            print(f"\nCustomer ID: {email}")
            if hasattr(user, 'name'):
                print(f"Name: {user.name}")
            print(f"Contact: {user.get_contact_number()}")
            print("-" * 30)

    def save_customer_data(self):
        """Save customer data to file"""
        try:
            os.makedirs('data', exist_ok=True)
            with open('data/customers.json', 'w') as f:
                json.dump(self.customers, f, indent=4)
        except Exception as e:
            print(f"Error saving customer data: {str(e)}")

    def load_customer_data(self):
        """Load customer data from file"""
        try:
            if os.path.exists('data/customers.json'):
                with open('data/customers.json', 'r') as f:
                    self.customers = json.load(f)
        except Exception as e:
            print(f"Error loading customer data: {str(e)}")

    def __str__(self):
        """String representation of the Agent CLI"""
        return (f"AgentCLI - User: {self.current_user.name if self.current_user else 'None'}, "
                f"Active Sales: {len(self.sales)}, Active Policies: {len(self.policies)}")