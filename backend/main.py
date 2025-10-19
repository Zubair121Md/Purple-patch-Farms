from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd
import json

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./fruit_vegetable_costs.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    source = Column(String)  # "inhouse" or "outsourced"
    unit = Column(String, default="kg")
    extra_info = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    monthly_sales = relationship("MonthlySale", back_populates="product")
    allocations = relationship("Allocation", back_populates="product")

class MonthlySale(Base):
    __tablename__ = "monthly_sales"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    month = Column(String, index=True)  # Format: "2025-10"
    quantity = Column(Float)
    sale_price = Column(Float)
    direct_cost = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="monthly_sales")
    allocations = relationship("Allocation", back_populates="monthly_sale")

class Cost(Base):
    __tablename__ = "costs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    amount = Column(Float)
    applies_to = Column(String)  # "inhouse", "outsourced", "both", "all"
    cost_type = Column(String)  # "purchase-only", "sales-only", "common", "inhouse-only"
    basis = Column(String)  # "weight", "value", "trips"
    month = Column(String, index=True)
    is_fixed = Column(String, default="variable")  # "fixed" or "variable"
    created_at = Column(DateTime, default=datetime.utcnow)

class Allocation(Base):
    __tablename__ = "allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    monthly_sale_id = Column(Integer, ForeignKey("monthly_sales.id"))
    cost_id = Column(Integer, ForeignKey("costs.id"))
    month = Column(String, index=True)
    allocated_amount = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="allocations")
    monthly_sale = relationship("MonthlySale", back_populates="allocations")
    cost = relationship("Cost")

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class ProductCreate(BaseModel):
    name: str
    source: str  # "inhouse" or "outsourced"
    unit: str = "kg"
    extra_info: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    source: str
    unit: str
    extra_info: Optional[str] = None
    created_at: datetime

class MonthlySaleCreate(BaseModel):
    product_id: int
    month: str
    quantity: float
    sale_price: float
    direct_cost: float = 0.0

class MonthlySaleResponse(BaseModel):
    id: int
    product_id: int
    month: str
    quantity: float
    sale_price: float
    direct_cost: float
    created_at: datetime

class CostCreate(BaseModel):
    name: str
    amount: float
    applies_to: str  # "inhouse", "outsourced", "both", "all"
    cost_type: str  # "purchase-only", "sales-only", "common", "inhouse-only"
    basis: str  # "weight", "value", "trips"
    month: str
    is_fixed: str = "variable"

class CostResponse(BaseModel):
    id: int
    name: str
    amount: float
    applies_to: str
    cost_type: str
    basis: str
    month: str
    is_fixed: str
    created_at: datetime

class AllocationResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    month: str
    allocated_amount: float
    cost_name: str
    created_at: datetime

class MonthlyReport(BaseModel):
    month: str
    products: List[Dict[str, Any]]
    total_revenue: float
    total_costs: float
    total_profit: float
    inhouse_summary: Dict[str, float]
    outsourced_summary: Dict[str, float]

# FastAPI app
app = FastAPI(title="Fruit & Vegetable Cost Allocation System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Cost Allocation Engine
class CostAllocationEngine:
    def __init__(self, db: Session):
        self.db = db
    
    def allocate_costs_for_month(self, month: str) -> Dict[str, Any]:
        """Main allocation function using DSA optimizations"""
        
        # Get all products for the month (O(1) lookup optimization)
        products = self.db.query(Product).all()
        product_map = {p.id: p for p in products}
        
        # Get monthly sales for the month
        monthly_sales = self.db.query(MonthlySale).filter(MonthlySale.month == month).all()
        sales_map = {s.product_id: s for s in monthly_sales}
        
        # Get all costs for the month
        costs = self.db.query(Cost).filter(Cost.month == month).all()
        
        # Clear existing allocations for the month
        self.db.query(Allocation).filter(Allocation.month == month).delete()
        
        # Process each cost
        for cost in costs:
            self._allocate_single_cost(cost, product_map, sales_map, month)
        
        self.db.commit()
        
        # Generate report
        return self._generate_monthly_report(month, product_map, sales_map)
    
    def _allocate_single_cost(self, cost: Cost, product_map: Dict, sales_map: Dict, month: str):
        """Allocate a single cost to applicable products"""
        
        # Step 1: Determine which products are affected
        applicable_products = self._get_applicable_products(cost, product_map, sales_map)
        
        if not applicable_products:
            return
        
        # Step 2: Compute total basis
        total_basis = self._compute_total_basis(cost, applicable_products, sales_map)
        
        if total_basis == 0:
            return
        
        # Step 3: Allocate cost proportionally
        for product_id, product in applicable_products.items():
            if product_id not in sales_map:
                continue
                
            sale = sales_map[product_id]
            product_basis = self._compute_product_basis(cost, sale)
            
            if product_basis > 0:
                allocated_amount = (product_basis / total_basis) * cost.amount
                
                # Store allocation
                allocation = Allocation(
                    product_id=product_id,
                    monthly_sale_id=sale.id,
                    cost_id=cost.id,
                    month=month,
                    allocated_amount=allocated_amount
                )
                self.db.add(allocation)
    
    def _get_applicable_products(self, cost: Cost, product_map: Dict, sales_map: Dict) -> Dict:
        """Get products that this cost applies to"""
        applicable = {}
        
        for product_id, product in product_map.items():
            if product_id not in sales_map:
                continue
                
            if cost.applies_to == "all":
                applicable[product_id] = product
            elif cost.applies_to == "inhouse" and product.source == "inhouse":
                applicable[product_id] = product
            elif cost.applies_to == "outsourced" and product.source == "outsourced":
                applicable[product_id] = product
            elif cost.applies_to == "both" and product.source in ["inhouse", "outsourced"]:
                applicable[product_id] = product
        
        return applicable
    
    def _compute_total_basis(self, cost: Cost, applicable_products: Dict, sales_map: Dict) -> float:
        """Compute total basis for allocation"""
        total = 0.0
        
        for product_id in applicable_products:
            if product_id in sales_map:
                sale = sales_map[product_id]
                total += self._compute_product_basis(cost, sale)
        
        return total
    
    def _compute_product_basis(self, cost: Cost, sale: MonthlySale) -> float:
        """Compute basis for a single product"""
        if cost.basis == "weight":
            return sale.quantity
        elif cost.basis == "value":
            return sale.quantity * sale.sale_price
        elif cost.basis == "trips":
            # For trips, we'll use quantity as a proxy (can be enhanced)
            return sale.quantity
        return 0.0
    
    def _generate_monthly_report(self, month: str, product_map: Dict, sales_map: Dict) -> Dict[str, Any]:
        """Generate comprehensive monthly report"""
        
        # Get all allocations for the month
        allocations = self.db.query(Allocation).filter(Allocation.month == month).all()
        
        # Group allocations by product
        product_allocations = {}
        for allocation in allocations:
            if allocation.product_id not in product_allocations:
                product_allocations[allocation.product_id] = []
            product_allocations[allocation.product_id].append(allocation)
        
        # Calculate per-product costs and profits
        products_data = []
        total_revenue = 0.0
        total_costs = 0.0
        
        inhouse_revenue = 0.0
        inhouse_costs = 0.0
        outsourced_revenue = 0.0
        outsourced_costs = 0.0
        
        for product_id, sale in sales_map.items():
            product = product_map[product_id]
            allocated_costs = product_allocations.get(product_id, [])
            
            total_allocated = sum(a.allocated_amount for a in allocated_costs)
            total_cost = sale.direct_cost + total_allocated
            revenue = sale.quantity * sale.sale_price
            profit = revenue - total_cost
            cost_per_kg = total_cost / sale.quantity if sale.quantity > 0 else 0
            
            product_data = {
                "product_id": product_id,
                "product_name": product.name,
                "source": product.source,
                "quantity": sale.quantity,
                "sale_price": sale.sale_price,
                "direct_cost": sale.direct_cost,
                "allocated_costs": total_allocated,
                "total_cost": total_cost,
                "revenue": revenue,
                "profit": profit,
                "cost_per_kg": cost_per_kg,
                "profit_margin": (profit / revenue * 100) if revenue > 0 else 0
            }
            
            products_data.append(product_data)
            total_revenue += revenue
            total_costs += total_cost
            
            if product.source == "inhouse":
                inhouse_revenue += revenue
                inhouse_costs += total_cost
            else:
                outsourced_revenue += revenue
                outsourced_costs += total_cost
        
        # Sort products by profit (DSA optimization)
        products_data.sort(key=lambda x: x["profit"], reverse=True)
        
        return {
            "month": month,
            "products": products_data,
            "total_revenue": total_revenue,
            "total_costs": total_costs,
            "total_profit": total_revenue - total_costs,
            "inhouse_summary": {
                "revenue": inhouse_revenue,
                "costs": inhouse_costs,
                "profit": inhouse_revenue - inhouse_costs
            },
            "outsourced_summary": {
                "revenue": outsourced_revenue,
                "costs": outsourced_costs,
                "profit": outsourced_revenue - outsourced_costs
            }
        }

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Fruit & Vegetable Cost Allocation System API"}

@app.post("/products/", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products/", response_model=List[ProductResponse])
async def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@app.post("/monthly-sales/", response_model=MonthlySaleResponse)
async def create_monthly_sale(sale: MonthlySaleCreate, db: Session = Depends(get_db)):
    db_sale = MonthlySale(**sale.model_dump())
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale

@app.get("/monthly-sales/{month}", response_model=List[MonthlySaleResponse])
async def get_monthly_sales(month: str, db: Session = Depends(get_db)):
    return db.query(MonthlySale).filter(MonthlySale.month == month).all()

@app.post("/costs/", response_model=CostResponse)
async def create_cost(cost: CostCreate, db: Session = Depends(get_db)):
    db_cost = Cost(**cost.model_dump())
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)
    return db_cost

@app.get("/costs/{month}", response_model=List[CostResponse])
async def get_costs(month: str, db: Session = Depends(get_db)):
    return db.query(Cost).filter(Cost.month == month).all()

@app.post("/allocate/{month}")
async def allocate_costs(month: str, db: Session = Depends(get_db)):
    engine = CostAllocationEngine(db)
    result = engine.allocate_costs_for_month(month)
    return result

@app.get("/report/{month}")
async def get_monthly_report(month: str, db: Session = Depends(get_db)):
    engine = CostAllocationEngine(db)
    return engine._generate_monthly_report(month, {}, {})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
