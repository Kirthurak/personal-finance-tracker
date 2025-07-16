import csv
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict
from operator import itemgetter

DATA_FILE = 'transactions.csv'
def load_budgets():
    budgets = {}
    try:
        with open('budgets.csv', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                budgets[row['category']] = float(row['monthly_limit'])
    except FileNotFoundError:
        pass
    return budgets

def check_budget_warnings(transactions, budgets):
    monthly_spend = {}

    for t in transactions:
        if t['type'] == 'expense':
            month = t['date'][:7]  # 'YYYY-MM'
            key = (t['category'], month)
            monthly_spend[key] = monthly_spend.get(key, 0) + t['amount']

    for (cat, month), spent in monthly_spend.items():
        if cat in budgets and spent > budgets[cat]:
            print(f"\033[91m⚠️  WARNING: You spent ${spent:.2f} in {cat} for {month}, over your ${budgets[cat]:.2f} budget!\033[0m")




def load_transactions():
    transactions = []
    try:
        with open(DATA_FILE, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['amount'] = float(row['amount'])
                transactions.append(row)
    except FileNotFoundError:
        pass
    return transactions

def save_transaction(description, category, tx_type, amount):
    with open(DATA_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        date = datetime.now().strftime("%Y-%m-%d")
        writer.writerow([date, description, category, tx_type, amount])

def show_summary(transactions):
    income = sum(t['amount'] for t in transactions if t['type'] == 'income')
    expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
    balance = income - expense

    print(f"\nTotal Income: ${income:.2f}")
    print(f"Total Expenses: ${expense:.2f}")
    print(f"Balance: ${balance:.2f}")

def plot_expenses(transactions):
    expenses = {}
    for t in transactions:
        if t['type'] == 'expense':
            expenses[t['category']] = expenses.get(t['category'], 0) + t['amount']

    if not expenses:
        print("No expenses to plot.")
        return

    categories = list(expenses.keys())
    amounts = list(expenses.values())

    plt.bar(categories, amounts, color='red')
    plt.title("Expenses by Category")
    plt.ylabel("Amount ($)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def edit_budgets():
    budgets = load_budgets()
    print("\n--- Current Budgets ---")
    for category, limit in budgets.items():
        print(f"{category}: ${limit:.2f}")

    while True:
        print("\n1. Update a category")
        print("2. Add new category")
        print("3. Remove category")
        print("4. Back to main menu")
        choice = input("Choose an option: ")

        if choice == '1':
            cat = input("Category to update: ").strip()
            if cat in budgets:
                new_limit = float(input(f"New monthly limit for {cat}: $"))
                budgets[cat] = new_limit
                print(f"✅ Updated {cat} to ${new_limit:.2f}")
            else:
                print("⚠️ Category not found.")
        elif choice == '2':
            cat = input("New category name: ").strip()
            if cat in budgets:
                print("⚠️ Category already exists.")
            else:
                new_limit = float(input(f"Monthly limit for {cat}: $"))
                budgets[cat] = new_limit
                print(f"✅ Added {cat} with limit ${new_limit:.2f}")
        elif choice == '3':
            cat = input("Category to remove: ").strip()
            if cat in budgets:
                del budgets[cat]
                print(f"❌ Removed category {cat}.")
            else:
                print("⚠️ Category not found.")
        elif choice == '4':
            break
        else:
            print("Invalid option.")

    # Save the updated budgets
    with open('budgets.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['category', 'monthly_limit'])
        for category, limit in budgets.items():
            writer.writerow([category, limit])


def show_monthly_report(transactions, export=False):
    monthly_data = defaultdict(lambda: {'income': 0.0, 'expense': 0.0, 'categories': defaultdict(float)})

    for t in transactions:
        month = t['date'][:7]  # YYYY-MM
        amount = t['amount']
        cat = t['category']
        if t['type'] == 'income':
            monthly_data[month]['income'] += amount
        elif t['type'] == 'expense':
            monthly_data[month]['expense'] += amount
            monthly_data[month]['categories'][cat] += amount

    lines = []
    lines.append("📅 --- Monthly Summary Report ---\n")

    for month, data in sorted(monthly_data.items()):
        income = data['income']
        expense = data['expense']
        balance = income - expense

        lines.append(f"\n🗓 {month}")
        lines.append(f"  Income:  ${income:.2f}")
        lines.append(f"  Expense: ${expense:.2f}")
        lines.append(f"  Balance: ${balance:.2f}")

        top3 = sorted(data['categories'].items(), key=itemgetter(1), reverse=True)[:3]
        if top3:
            lines.append("  🔝 Top 3 Spending Categories:")
            for cat, amt in top3:
                lines.append(f"    - {cat}: ${amt:.2f}")
        lines.append("")  # Add space between months

    report_text = "\n".join(lines)

    print(report_text)

    if export:
        with open("monthly_report.txt", "w", encoding="utf-8") as f:
            f.write(report_text)
        print("✅ Monthly report saved as 'monthly_report.txt'")


def plot_monthly_pie_chart(transactions):
    month = input("Enter month (YYYY-MM): ").strip()

    category_totals = defaultdict(float)
    found_data = False

    for t in transactions:
        if t['type'] == 'expense' and t['date'].startswith(month):
            category_totals[t['category']] += t['amount']
            found_data = True

    if not found_data:
        print(f"⚠️ No expense data found for {month}.")
        return

    categories = list(category_totals.keys())
    amounts = list(category_totals.values())

    plt.figure(figsize=(6,6))
    plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
    plt.title(f"Expenses by Category - {month}")
    plt.axis('equal')

    # Save the figure
    filename = f"expenses_{month}.png"
    plt.savefig(filename, bbox_inches='tight')
    print(f"✅ Saved pie chart as '{filename}'")

    # Show the chart
    plt.show()



def main():
    while True:
        print("\n--- Personal Finance Tracker ---")
        print("1. Add transaction")
        print("2. View summary")
        print("3. Plot expenses")
        print("4. Exit")
        print("5. Edit budgets")
        print("6. Monthly report")
        print("7. Monthly pie chart")
        choice = input("Select an option: ")

        if choice == '1':
            desc = input("Description: ")
            cat = input("Category: ")
            tx_type = input("Type (income/expense): ").strip().lower()
            amt = float(input("Amount: "))
            save_transaction(desc, cat, tx_type, amt)
        elif choice == '2':
            txns = load_transactions()
            budgets = load_budgets()
            show_summary(txns)
            check_budget_warnings(txns, budgets)

        elif choice == '3':
            txns = load_transactions()
            plot_expenses(txns)
        elif choice == '4':
            break
        elif choice == '5':
            edit_budgets()
        elif choice == '6':
            txns = load_transactions()
            export = input("Export this report to a text file? (y/n): ").strip().lower()
            show_monthly_report(txns, export == 'y')
        elif choice == '7':
            txns = load_transactions()
            plot_monthly_pie_chart(txns)



    else:
            print("Invalid choice.")

if __name__ == '__main__':
    main()
