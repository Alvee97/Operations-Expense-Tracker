#!/usr/bin/env python3
"""
Operations & Expense Tracking Tool
A comprehensive system for tracking receipts and managing expense reports
"""

import json
import csv
import os
from datetime import datetime, date
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import uuid

@dataclass
class Receipt:
    """Data structure for individual receipts"""
    id: str
    date: str
    vendor: str
    amount: float
    category: str
    description: str
    payment_method: str
    receipt_image_path: Optional[str] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class ExpenseReport:
    """Data structure for expense reports"""
    id: str
    title: str
    period_start: str
    period_end: str
    employee_name: str
    department: str
    receipt_ids: List[str]
    total_amount: float
    status: str  # draft, submitted, approved, rejected
    created_at: str = None
    submitted_at: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

class ExpenseTracker:
    """Main class for managing expenses and receipts"""
    
    def __init__(self, data_directory: str = "expense_data"):
        self.data_dir = Path(data_directory)
        self.data_dir.mkdir(exist_ok=True)
        
        # File paths
        self.receipts_file = self.data_dir / "receipts.json"
        self.reports_file = self.data_dir / "expense_reports.json"
        
        # Load existing data
        self.receipts = self._load_receipts()
        self.expense_reports = self._load_reports()
        
        # Expense categories
        self.categories = [
            "Office Supplies", "Travel", "Meals & Entertainment", 
            "Software/Subscriptions", "Equipment", "Marketing", 
            "Professional Services", "Utilities", "Other"
        ]
    
    def _load_receipts(self) -> Dict[str, Receipt]:
        """Load receipts from JSON file"""
        if self.receipts_file.exists():
            with open(self.receipts_file, 'r') as f:
                data = json.load(f)
                return {k: Receipt(**v) for k, v in data.items()}
        return {}
    
    def _load_reports(self) -> Dict[str, ExpenseReport]:
        """Load expense reports from JSON file"""
        if self.reports_file.exists():
            with open(self.reports_file, 'r') as f:
                data = json.load(f)
                return {k: ExpenseReport(**v) for k, v in data.items()}
        return {}
    
    def _save_receipts(self):
        """Save receipts to JSON file"""
        data = {k: asdict(v) for k, v in self.receipts.items()}
        with open(self.receipts_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _save_reports(self):
        """Save expense reports to JSON file"""
        data = {k: asdict(v) for k, v in self.expense_reports.items()}
        with open(self.reports_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def add_receipt(self, vendor: str, amount: float, category: str, 
                   description: str, payment_method: str, 
                   receipt_date: Optional[str] = None,
                   image_path: Optional[str] = None) -> str:
        """Add a new receipt"""
        receipt_id = str(uuid.uuid4())[:8]
        
        if receipt_date is None:
            receipt_date = date.today().isoformat()
        
        receipt = Receipt(
            id=receipt_id,
            date=receipt_date,
            vendor=vendor,
            amount=amount,
            category=category,
            description=description,
            payment_method=payment_method,
            receipt_image_path=image_path
        )
        
        self.receipts[receipt_id] = receipt
        self._save_receipts()
        
        print(f"✅ Receipt added successfully! ID: {receipt_id}")
        return receipt_id
    
    def get_receipt(self, receipt_id: str) -> Optional[Receipt]:
        """Get a receipt by ID"""
        return self.receipts.get(receipt_id)
    
    def list_receipts(self, category: Optional[str] = None, 
                     start_date: Optional[str] = None,
                     end_date: Optional[str] = None) -> List[Receipt]:
        """List receipts with optional filtering"""
        receipts = list(self.receipts.values())
        
        if category:
            receipts = [r for r in receipts if r.category == category]
        
        if start_date:
            receipts = [r for r in receipts if r.date >= start_date]
            
        if end_date:
            receipts = [r for r in receipts if r.date <= end_date]
        
        return sorted(receipts, key=lambda x: x.date, reverse=True)
    
    def delete_receipt(self, receipt_id: str) -> bool:
        """Delete a receipt"""
        if receipt_id in self.receipts:
            del self.receipts[receipt_id]
            self._save_receipts()
            print(f"✅ Receipt {receipt_id} deleted successfully!")
            return True
        print(f"❌ Receipt {receipt_id} not found!")
        return False
    
    def create_expense_report(self, title: str, employee_name: str, 
                            department: str, period_start: str, 
                            period_end: str, receipt_ids: List[str]) -> str:
        """Create a new expense report"""
        report_id = str(uuid.uuid4())[:8]
        
        # Validate receipt IDs and calculate total
        valid_receipts = []
        total_amount = 0
        
        for rid in receipt_ids:
            if rid in self.receipts:
                valid_receipts.append(rid)
                total_amount += self.receipts[rid].amount
            else:
                print(f"⚠️ Warning: Receipt ID {rid} not found, skipping...")
        
        report = ExpenseReport(
            id=report_id,
            title=title,
            period_start=period_start,
            period_end=period_end,
            employee_name=employee_name,
            department=department,
            receipt_ids=valid_receipts,
            total_amount=total_amount,
            status="draft"
        )
        
        self.expense_reports[report_id] = report
        self._save_reports()
        
        print(f"✅ Expense report created successfully! ID: {report_id}")
        print(f"   Total amount: ${total_amount:.2f}")
        return report_id
    
    def submit_expense_report(self, report_id: str) -> bool:
        """Submit an expense report for approval"""
        if report_id in self.expense_reports:
            report = self.expense_reports[report_id]
            report.status = "submitted"
            report.submitted_at = datetime.now().isoformat()
            self._save_reports()
            print(f"✅ Expense report {report_id} submitted for approval!")
            return True
        print(f"❌ Expense report {report_id} not found!")
        return False
    
    def approve_expense_report(self, report_id: str) -> bool:
        """Approve an expense report"""
        if report_id in self.expense_reports:
            self.expense_reports[report_id].status = "approved"
            self._save_reports()
            print(f"✅ Expense report {report_id} approved!")
            return True
        print(f"❌ Expense report {report_id} not found!")
        return False
    
    def reject_expense_report(self, report_id: str) -> bool:
        """Reject an expense report"""
        if report_id in self.expense_reports:
            self.expense_reports[report_id].status = "rejected"
            self._save_reports()
            print(f"❌ Expense report {report_id} rejected!")
            return True
        print(f"❌ Expense report {report_id} not found!")
        return False
    
    def get_expense_report(self, report_id: str) -> Optional[ExpenseReport]:
        """Get an expense report by ID"""
        return self.expense_reports.get(report_id)
    
    def list_expense_reports(self, status: Optional[str] = None) -> List[ExpenseReport]:
        """List expense reports with optional status filtering"""
        reports = list(self.expense_reports.values())
        
        if status:
            reports = [r for r in reports if r.status == status]
        
        return sorted(reports, key=lambda x: x.created_at, reverse=True)
    
    def generate_summary_report(self, start_date: str, end_date: str) -> Dict:
        """Generate a summary report for a date range"""
        receipts = self.list_receipts(start_date=start_date, end_date=end_date)
        
        # Calculate totals by category
        category_totals = {}
        total_amount = 0
        
        for receipt in receipts:
            category = receipt.category
            amount = receipt.amount
            
            if category not in category_totals:
                category_totals[category] = 0
            category_totals[category] += amount
            total_amount += amount
        
        # Count receipts by payment method
        payment_methods = {}
        for receipt in receipts:
            method = receipt.payment_method
            if method not in payment_methods:
                payment_methods[method] = 0
            payment_methods[method] += 1
        
        summary = {
            "period": f"{start_date} to {end_date}",
            "total_receipts": len(receipts),
            "total_amount": total_amount,
            "category_breakdown": category_totals,
            "payment_method_counts": payment_methods,
            "average_receipt_amount": total_amount / len(receipts) if receipts else 0
        }
        
        return summary
    
    def export_to_csv(self, filename: str, start_date: Optional[str] = None, 
                     end_date: Optional[str] = None):
        """Export receipts to CSV file"""
        receipts = self.list_receipts(start_date=start_date, end_date=end_date)
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['id', 'date', 'vendor', 'amount', 'category', 
                         'description', 'payment_method', 'created_at']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for receipt in receipts:
                row = asdict(receipt)
                row.pop('receipt_image_path', None)  # Remove image path from CSV
                writer.writerow(row)
        
        print(f"✅ Exported {len(receipts)} receipts to {filename}")
    
    def print_receipt_summary(self, receipt: Receipt):
        """Print a formatted receipt summary"""
        print(f"\n📄 Receipt {receipt.id}")
        print(f"   Date: {receipt.date}")
        print(f"   Vendor: {receipt.vendor}")
        print(f"   Amount: ${receipt.amount:.2f}")
        print(f"   Category: {receipt.category}")
        print(f"   Description: {receipt.description}")
        print(f"   Payment Method: {receipt.payment_method}")
    
    def print_report_summary(self, report: ExpenseReport):
        """Print a formatted expense report summary"""
        print(f"\n📊 Expense Report {report.id}")
        print(f"   Title: {report.title}")
        print(f"   Employee: {report.employee_name} ({report.department})")
        print(f"   Period: {report.period_start} to {report.period_end}")
        print(f"   Status: {report.status.upper()}")
        print(f"   Total Amount: ${report.total_amount:.2f}")
        print(f"   Receipts: {len(report.receipt_ids)} items")

def main():
    """Interactive command-line interface"""
    tracker = ExpenseTracker()
    
    print("🏢 Operations & Expense Tracking Tool")
    print("=====================================")
    
    while True:
        print("\n📋 Main Menu:")
        print("1. Add Receipt")
        print("2. List Receipts")
        print("3. Create Expense Report")
        print("4. List Expense Reports")
        print("5. Submit/Approve Report")
        print("6. Generate Summary")
        print("7. Export to CSV")
        print("8. View Categories")
        print("9. Exit")
        
        choice = input("\nSelect an option (1-9): ").strip()
        
        try:
            if choice == "1":
                print("\n➕ Add New Receipt")
                vendor = input("Vendor name: ").strip()
                amount = float(input("Amount ($): "))
                
                print(f"Categories: {', '.join(tracker.categories)}")
                category = input("Category: ").strip()
                
                description = input("Description: ").strip()
                payment_method = input("Payment method (Cash/Credit/Debit/Other): ").strip()
                receipt_date = input("Date (YYYY-MM-DD, or press Enter for today): ").strip()
                
                if not receipt_date:
                    receipt_date = None
                
                tracker.add_receipt(vendor, amount, category, description, 
                                  payment_method, receipt_date)
            
            elif choice == "2":
                print("\n📄 Recent Receipts:")
                receipts = tracker.list_receipts()[:10]  # Show last 10
                if not receipts:
                    print("No receipts found.")
                else:
                    for receipt in receipts:
                        tracker.print_receipt_summary(receipt)
            
            elif choice == "3":
                print("\n📊 Create Expense Report")
                title = input("Report title: ").strip()
                employee_name = input("Employee name: ").strip()
                department = input("Department: ").strip()
                period_start = input("Period start (YYYY-MM-DD): ").strip()
                period_end = input("Period end (YYYY-MM-DD): ").strip()
                
                print("\nAvailable receipts:")
                receipts = tracker.list_receipts(start_date=period_start, end_date=period_end)
                for receipt in receipts:
                    tracker.print_receipt_summary(receipt)
                
                receipt_ids = input("\nEnter receipt IDs (comma-separated): ").strip().split(",")
                receipt_ids = [rid.strip() for rid in receipt_ids if rid.strip()]
                
                tracker.create_expense_report(title, employee_name, department,
                                            period_start, period_end, receipt_ids)
            
            elif choice == "4":
                print("\n📊 Expense Reports:")
                reports = tracker.list_expense_reports()
                if not reports:
                    print("No expense reports found.")
                else:
                    for report in reports:
                        tracker.print_report_summary(report)
            
            elif choice == "5":
                print("\n🔄 Submit/Approve Report")
                report_id = input("Enter report ID: ").strip()
                action = input("Action (submit/approve/reject): ").strip().lower()
                
                if action == "submit":
                    tracker.submit_expense_report(report_id)
                elif action == "approve":
                    tracker.approve_expense_report(report_id)
                elif action == "reject":
                    tracker.reject_expense_report(report_id)
                else:
                    print("Invalid action!")
            
            elif choice == "6":
                print("\n📈 Generate Summary Report")
                start_date = input("Start date (YYYY-MM-DD): ").strip()
                end_date = input("End date (YYYY-MM-DD): ").strip()
                
                summary = tracker.generate_summary_report(start_date, end_date)
                
                print(f"\n📊 Summary Report ({summary['period']})")
                print(f"Total Receipts: {summary['total_receipts']}")
                print(f"Total Amount: ${summary['total_amount']:.2f}")
                print(f"Average Receipt: ${summary['average_receipt_amount']:.2f}")
                
                print("\n💰 By Category:")
                for category, amount in summary['category_breakdown'].items():
                    print(f"   {category}: ${amount:.2f}")
                
                print("\n💳 Payment Methods:")
                for method, count in summary['payment_method_counts'].items():
                    print(f"   {method}: {count} receipts")
            
            elif choice == "7":
                print("\n📤 Export to CSV")
                filename = input("Filename (e.g., expenses.csv): ").strip()
                start_date = input("Start date (YYYY-MM-DD, or press Enter for all): ").strip()
                end_date = input("End date (YYYY-MM-DD, or press Enter for all): ").strip()
                
                tracker.export_to_csv(filename, 
                                    start_date if start_date else None,
                                    end_date if end_date else None)
            
            elif choice == "8":
                print(f"\n📂 Available Categories:")
                for i, category in enumerate(tracker.categories, 1):
                    print(f"   {i}. {category}")
            
            elif choice == "9":
                print("👋 Goodbye! Your data has been saved.")
                break
            
            else:
                print("❌ Invalid option! Please select 1-9.")
        
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Your data has been saved.")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main()
