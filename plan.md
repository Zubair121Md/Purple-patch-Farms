# 🍇 Fruit & Vegetable Cost Allocation System

## Phase 1 — Understanding the Problem (Very Simple)

You sell fruits and vegetables.

Some you grow yourself (inhouse), some you buy from market (outsourced).

Every month, costs happen:

Buying, cultivating, marketing, loading/unloading, truck fees, wastage…

Each product has different quantity & price every month.

Goal: Figure out how much each product costs and your profit automatically.

Challenge: Shared costs like loading trucks or marketing should be split fairly.

Analogy:
Imagine you bought candies for a party and shared the cost among friends according to how many candies each friend got. Same idea here, but for fruits and vegetables.

## Phase 2 — Decide What We Need

We need 4 things:

Products – info about fruits/veggies

Name, source (inhouse/outsourced), unit (kg), extra info

Monthly Sales – how much we sold each month

Quantity, sale price, direct cost (like purchase cost or cultivation cost)

Costs – all the money we spent

Name, amount, which products it applies to (inhouse/outsourced/all), type (purchase-only, sales-only, common), month, fixed or variable

Allocations – calculated cost share for each product

Example: Strawberry loading ₹85.71, Banana ₹214.29

DSA Tip:

Use dictionaries/maps to look up products quickly.

Use arrays/lists to store monthly data.

Use prefix sums if you want to compute cumulative cost efficiently.

## Phase 3 — Data Structures (Simple Explanation)

We can store info like this:

Products
products = {
  1: {"name":"Strawberry", "source":"outsourced"},
  2: {"name":"Banana", "source":"outsourced"},
  3: {"name":"Apple", "source":"inhouse"}
}

Monthly Sales
monthly_sales = {
  "2025-10": {
    1: {"qty":10, "sale_price":200, "direct_cost":1500},
    2: {"qty":25, "sale_price":150, "direct_cost":2000},
    3: {"qty":30, "sale_price":100, "direct_cost":0}
  }
}

Costs
costs = {
  "2025-10": [
    {"name":"Purchase Loading", "amount":300, "applies_to":"outsourced", "basis":"weight"},
    {"name":"Sales Loading", "amount":700, "applies_to":"both", "basis":"weight"}
  ]
}

DSA tip:

Use hashmaps (dict) for O(1) lookup of product info.

Use arrays/lists to loop over costs for allocation.

## Phase 4 — Allocation Logic (The Core)

Step 1: Decide which products are affected

purchase-only → only outsourced

sales-only → all sold products

inhouse-only → only inhouse

common → all products

Step 2: Compute total "basis"

If basis = weight → sum of product quantities for that cost

If basis = value → sum of (qty * sale_price)

If basis = trips → sum of trips info (for trucks)

Step 3: Allocate cost proportionally
For each product:

share = (product_qty / total_qty) * cost_amount

Store share in allocation table/dictionary.

Step 4: Compute total cost per product

total_cost = direct_cost + sum(allocated_costs)
cost_per_kg = total_cost / qty
profit = (qty * sale_price) - total_cost

DSA tip:

Using maps to store product → allocation makes it fast.

For large data, you can use prefix sums to compute cumulative costs efficiently.

## Phase 5 — Example Calculation (Very Simple)

Input:

Purchase Loading ₹300 for outsourced items:

Strawberry 10kg

Banana 25kg

Sales Loading ₹700 for all sold items:

Strawberry 10kg (outsourced)

Banana 25kg (outsourced)

Apple 30kg (inhouse)

Step 1: Purchase Loading Allocation

Total qty = 10 + 25 = 35kg

Strawberry: 10/35 * 300 = 85.71

Banana: 25/35 * 300 = 214.29

Step 2: Sales Loading Allocation

Total qty = 10 + 25 + 30 = 65kg

Strawberry: 10/65 * 700 = 107.69

Banana: 25/65 * 700 = 269.23

Apple: 30/65 * 700 = 323.08

Step 3: Total Allocation per Product

Strawberry = 85.71 + 107.69 = 193.40

Banana = 214.29 + 269.23 = 483.52

Apple = 323.08

## Phase 6 — Monthly Workflow

Add products (name, source)

Add monthly sales (qty, sale price, direct cost)

Add monthly costs (amount, type, basis)

Run allocation engine → system calculates allocations automatically

View monthly report → cost per product, profit, cost/kg, source-wise summary

DSA Tip:

Sorting products by name or source can help quickly generate reports.

Use heap/priority queue if you want top profitable products fast.

## Phase 7 — Reports and Insights

Monthly product cost sheet

Profit per product

Inhouse vs Outsourced P&L

Expense breakdown by category

Export CSV/Excel

## Phase 8 — Advanced DSA Usage

HashMap / Dictionary → O(1) product lookup

Prefix sum / cumulative sum → fast cost aggregation

Sorting → rank products by cost/kg or profit

Weighted allocation formula → optimize cost sharing

share = (product_qty * weight) / sum(product_qty * weight) * cost_amount

## Phase 9 — Backend & API

Endpoints:

Add/Edit/Delete Products, Monthly Sales, Costs

Allocate costs for a month

Fetch allocation tables and reports

Sample API Calls

POST /products → add product

POST /monthly_sales → add sales

POST /costs → add cost

POST /allocate?month=2025-10 → run allocation

GET /report/monthly?month=2025-10 → view report

## Phase 10 — Frontend

Forms for Products, Sales, Costs

Button: "Allocate Costs"

Display table: per-product cost + profit

Graphs: Profit by product, Inhouse vs Outsourced

## Phase 11 — Edge Cases

Zero qty → skip allocation

Partial season → only allocate to available products

Fixed costs → auto copy to next months

Wastage → cost entry or adjust qty

## Phase 12 — Step-By-Step Execution

Add products

Add monthly sales

Add costs

Run allocation

View reports

Export CSV/Excel

## 📌 Notes for Cursor

Implement backend first (FastAPI + SQLAlchemy)

Use dicts/maps for fast product & allocation lookups

Apply DSA techniques for cumulative totals & weighted allocation

Test example: Strawberry, Banana, Apple with loading/unloading costs
