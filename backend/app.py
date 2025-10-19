from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
import pandas as pd
import json
import os
from pathlib import Path

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
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
    category = Column(String, default="general")  # "transport", "marketing", "storage", etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    source: str = Field(..., pattern="^(inhouse|outsourced)$")
    unit: str = Field(default="kg", max_length=20)
    extra_info: Optional[str] = Field(None, max_length=500)

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    source: Optional[str] = Field(None, pattern="^(inhouse|outsourced)$")
    unit: Optional[str] = Field(None, max_length=20)
    extra_info: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    source: str
    unit: str
    extra_info: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

class MonthlySaleCreate(BaseModel):
    product_id: int
    month: str = Field(..., pattern="^\\d{4}-\\d{2}$")
    quantity: float = Field(..., gt=0)
    sale_price: float = Field(..., gt=0)
    direct_cost: float = Field(default=0.0, ge=0)

class MonthlySaleUpdate(BaseModel):
    quantity: Optional[float] = Field(None, gt=0)
    sale_price: Optional[float] = Field(None, gt=0)
    direct_cost: Optional[float] = Field(None, ge=0)

class MonthlySaleResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    month: str
    quantity: float
    sale_price: float
    direct_cost: float
    created_at: datetime

class CostCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0)
    applies_to: str = Field(..., pattern="^(inhouse|outsourced|both|all)$")
    cost_type: str = Field(..., pattern="^(purchase-only|sales-only|common|inhouse-only)$")
    basis: str = Field(..., pattern="^(weight|value|trips)$")
    month: str = Field(..., pattern="^\\d{4}-\\d{2}$")
    is_fixed: str = Field(default="variable", pattern="^(fixed|variable)$")
    category: str = Field(default="general", max_length=50)

class CostUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    amount: Optional[float] = Field(None, gt=0)
    applies_to: Optional[str] = Field(None, pattern="^(inhouse|outsourced|both|all)$")
    cost_type: Optional[str] = Field(None, pattern="^(purchase-only|sales-only|common|inhouse-only)$")
    basis: Optional[str] = Field(None, pattern="^(weight|value|trips)$")
    is_fixed: Optional[str] = Field(None, pattern="^(fixed|variable)$")
    category: Optional[str] = Field(None, max_length=50)

class CostResponse(BaseModel):
    id: int
    name: str
    amount: float
    applies_to: str
    cost_type: str
    basis: str
    month: str
    is_fixed: str
    category: str
    created_at: datetime

class AllocationResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    month: str
    allocated_amount: float
    cost_name: str
    cost_category: str
    created_at: datetime

class DashboardStats(BaseModel):
    total_products: int
    active_products: int
    total_revenue: float
    total_costs: float
    total_profit: float
    profit_margin: float
    inhouse_revenue: float
    outsourced_revenue: float
    inhouse_profit: float
    outsourced_profit: float

class MonthlyReport(BaseModel):
    month: str
    products: List[Dict[str, Any]]
    total_revenue: float
    total_costs: float
    total_profit: float
    profit_margin: float
    inhouse_summary: Dict[str, float]
    outsourced_summary: Dict[str, float]
    cost_breakdown: Dict[str, float]
    top_products: List[Dict[str, Any]]

# FastAPI app
app = FastAPI(
    title="🍇 Fruit & Vegetable Cost Allocation System",
    description="A comprehensive system for calculating costs and profits for fruit and vegetable businesses",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Enhanced Cost Allocation Engine
class CostAllocationEngine:
    def __init__(self, db: Session):
        self.db = db
    
    def allocate_costs_for_month(self, month: str) -> Dict[str, Any]:
        """Enhanced allocation function with better error handling and reporting"""
        
        try:
            # Get all active products for the month
            products = self.db.query(Product).filter(Product.is_active == True).all()
            product_map = {p.id: p for p in products}
            
            # Get monthly sales for the month
            monthly_sales = self.db.query(MonthlySale).filter(MonthlySale.month == month).all()
            sales_map = {s.product_id: s for s in monthly_sales}
            
            # Get all costs for the month
            costs = self.db.query(Cost).filter(Cost.month == month).all()
            
            if not costs:
                raise HTTPException(
                    status_code=400, 
                    detail=f"No costs found for month {month}. Please add costs before running allocation."
                )
            
            if not monthly_sales:
                raise HTTPException(
                    status_code=400, 
                    detail=f"No sales data found for month {month}. Please add sales data before running allocation."
                )
            
            # Clear existing allocations for the month
            self.db.query(Allocation).filter(Allocation.month == month).delete()
            
            # Process each cost
            for cost in costs:
                self._allocate_single_cost(cost, product_map, sales_map, month)
            
            self.db.commit()
            
            # Generate comprehensive report
            return self._generate_monthly_report(month, product_map, sales_map)
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Allocation failed: {str(e)}")
    
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
        """Generate comprehensive monthly report with enhanced analytics"""
        
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
        
        cost_breakdown = {}
        
        for product_id, sale in sales_map.items():
            product = product_map[product_id]
            allocated_costs = product_allocations.get(product_id, [])
            
            total_allocated = sum(a.allocated_amount for a in allocated_costs)
            total_cost = sale.direct_cost + total_allocated
            revenue = sale.quantity * sale.sale_price
            profit = revenue - total_cost
            cost_per_kg = total_cost / sale.quantity if sale.quantity > 0 else 0
            profit_margin = (profit / revenue * 100) if revenue > 0 else 0
            
            # Cost breakdown by category
            for allocation in allocated_costs:
                category = allocation.cost.category
                if category not in cost_breakdown:
                    cost_breakdown[category] = 0.0
                cost_breakdown[category] += allocation.allocated_amount
            
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
                "profit_margin": profit_margin,
                "allocations": [
                    {
                        "cost_name": a.cost.name,
                        "category": a.cost.category,
                        "amount": a.allocated_amount
                    } for a in allocated_costs
                ]
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
        
        # Calculate top products
        top_products = products_data[:5]  # Top 5 by profit
        
        return {
            "month": month,
            "products": products_data,
            "total_revenue": total_revenue,
            "total_costs": total_costs,
            "total_profit": total_revenue - total_costs,
            "profit_margin": ((total_revenue - total_costs) / total_revenue * 100) if total_revenue > 0 else 0,
            "inhouse_summary": {
                "revenue": inhouse_revenue,
                "costs": inhouse_costs,
                "profit": inhouse_revenue - inhouse_costs,
                "profit_margin": ((inhouse_revenue - inhouse_costs) / inhouse_revenue * 100) if inhouse_revenue > 0 else 0
            },
            "outsourced_summary": {
                "revenue": outsourced_revenue,
                "costs": outsourced_costs,
                "profit": outsourced_revenue - outsourced_costs,
                "profit_margin": ((outsourced_revenue - outsourced_costs) / outsourced_revenue * 100) if outsourced_revenue > 0 else 0
            },
            "cost_breakdown": cost_breakdown,
            "top_products": top_products
        }

# API Endpoints
@app.get("/")
async def root():
    return FileResponse("index.html")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/api/reset-database")
async def reset_database(db: Session = Depends(get_db)):
    """Reset the entire database by deleting all records"""
    try:
        # Delete all records from all tables
        db.query(MonthlySale).delete()
        db.query(Cost).delete()
        db.query(Product).delete()
        
        # Commit the changes
        db.commit()
        
        return {"message": "Database reset successfully", "timestamp": datetime.utcnow()}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error resetting database: {str(e)}")

# Dashboard endpoints
@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get overall dashboard statistics"""
    
    # Get current month
    current_month = datetime.now().strftime("%Y-%m")
    
    # Product stats
    total_products = db.query(Product).count()
    active_products = db.query(Product).filter(Product.is_active == True).count()
    
    # Revenue and cost stats for current month
    sales = db.query(MonthlySale).filter(MonthlySale.month == current_month).all()
    costs = db.query(Cost).filter(Cost.month == current_month).all()
    
    total_revenue = sum(s.quantity * s.sale_price for s in sales)
    total_direct_costs = sum(s.direct_cost for s in sales)
    total_shared_costs = sum(c.amount for c in costs)
    total_costs = total_direct_costs + total_shared_costs
    total_profit = total_revenue - total_costs
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # Source-wise breakdown
    inhouse_sales = [s for s in sales if s.product.source == "inhouse"]
    outsourced_sales = [s for s in sales if s.product.source == "outsourced"]
    
    inhouse_revenue = sum(s.quantity * s.sale_price for s in inhouse_sales)
    outsourced_revenue = sum(s.quantity * s.sale_price for s in outsourced_sales)
    
    inhouse_direct_costs = sum(s.direct_cost for s in inhouse_sales)
    outsourced_direct_costs = sum(s.direct_cost for s in outsourced_sales)
    
    # Simple allocation for dashboard (50-50 split for shared costs)
    inhouse_shared_costs = total_shared_costs * 0.5
    outsourced_shared_costs = total_shared_costs * 0.5
    
    inhouse_costs = inhouse_direct_costs + inhouse_shared_costs
    outsourced_costs = outsourced_direct_costs + outsourced_shared_costs
    
    inhouse_profit = inhouse_revenue - inhouse_costs
    outsourced_profit = outsourced_revenue - outsourced_costs
    
    return DashboardStats(
        total_products=total_products,
        active_products=active_products,
        total_revenue=total_revenue,
        total_costs=total_costs,
        total_profit=total_profit,
        profit_margin=profit_margin,
        inhouse_revenue=inhouse_revenue,
        outsourced_revenue=outsourced_revenue,
        inhouse_profit=inhouse_profit,
        outsourced_profit=outsourced_profit
    )

# Product endpoints
@app.post("/api/products/", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    # Check if product already exists
    existing = db.query(Product).filter(Product.name == product.name).first()
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Product '{product.name}' already exists"
        )
    
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/api/products/", response_model=List[ProductResponse])
async def get_products(active_only: bool = True, db: Session = Depends(get_db)):
    query = db.query(Product)
    if active_only:
        query = query.filter(Product.is_active == True)
    return query.order_by(Product.name).all()

@app.get("/api/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/api/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product_update: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product)
    return product

@app.delete("/api/products/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Soft delete
    product.is_active = False
    product.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Product deactivated successfully"}

# Monthly Sales endpoints
@app.post("/api/monthly-sales/", response_model=MonthlySaleResponse)
async def create_monthly_sale(sale: MonthlySaleCreate, db: Session = Depends(get_db)):
    # Verify product exists
    product = db.query(Product).filter(Product.id == sale.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if sale already exists for this product and month
    existing = db.query(MonthlySale).filter(
        MonthlySale.product_id == sale.product_id,
        MonthlySale.month == sale.month
    ).first()
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Sales data already exists for {product.name} in {sale.month}"
        )
    
    db_sale = MonthlySale(**sale.model_dump())
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    
    # Add product name to response
    sale_response = MonthlySaleResponse(
        **db_sale.__dict__,
        product_name=product.name
    )
    return sale_response


@app.get("/api/monthly-sales/{param}", response_model=Union[MonthlySaleResponse, List[MonthlySaleResponse]])
async def get_monthly_sales_or_by_id(param: str, db: Session = Depends(get_db)):
    print(f"DEBUG: Received param: '{param}'")
    
    # Check if param is a number (ID) or string (month)
    # If it's a single digit or number, treat as ID
    # If it contains dashes (like 2025-10), treat as month
    if param.isdigit():
        print(f"DEBUG: Treating '{param}' as ID")
        # It's an ID, get single sale
        sale_id = int(param)
        sale = db.query(MonthlySale).filter(MonthlySale.id == sale_id).first()
        if not sale:
            print(f"DEBUG: Sale not found for ID {sale_id}")
            raise HTTPException(status_code=404, detail="Sales record not found")
        
        # Add product name to response
        product = db.query(Product).filter(Product.id == sale.product_id).first()
        sale_response = MonthlySaleResponse(
            **sale.__dict__,
            product_name=product.name if product else "Unknown"
        )
        print(f"DEBUG: Returning single sale: {sale_response}")
        return sale_response
    else:
        print(f"DEBUG: Treating '{param}' as month")
        # It's a month string, get all sales for that month
        sales = db.query(MonthlySale).filter(MonthlySale.month == param).all()
        print(f"DEBUG: Found {len(sales)} sales for month {param}")
        
        # Add product names to response
        sales_with_names = []
        for sale in sales:
            product = db.query(Product).filter(Product.id == sale.product_id).first()
            sales_with_names.append(MonthlySaleResponse(
                **sale.__dict__,
                product_name=product.name if product else "Unknown"
            ))
        
        return sales_with_names

@app.get("/api/sales/{sale_id}", response_model=MonthlySaleResponse)
async def get_sale_by_id(sale_id: int, db: Session = Depends(get_db)):
    print(f"DEBUG: Getting sale with ID {sale_id}")
    sale = db.query(MonthlySale).filter(MonthlySale.id == sale_id).first()
    if not sale:
        print(f"DEBUG: Sale not found for ID {sale_id}")
        raise HTTPException(status_code=404, detail="Sales record not found")
    
    # Add product name to response
    product = db.query(Product).filter(Product.id == sale.product_id).first()
    sale_response = MonthlySaleResponse(
        **sale.__dict__,
        product_name=product.name if product else "Unknown"
    )
    print(f"DEBUG: Returning sale: {sale_response}")
    return sale_response

@app.put("/api/monthly-sales/{sale_id}", response_model=MonthlySaleResponse)
async def update_monthly_sale(sale_id: int, sale_update: MonthlySaleUpdate, db: Session = Depends(get_db)):
    sale = db.query(MonthlySale).filter(MonthlySale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sales record not found")
    
    update_data = sale_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sale, field, value)
    
    sale.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(sale)
    
    # Add product name to response
    product = db.query(Product).filter(Product.id == sale.product_id).first()
    return MonthlySaleResponse(
        **sale.__dict__,
        product_name=product.name if product else "Unknown"
    )

# Cost endpoints
@app.post("/api/costs/", response_model=CostResponse)
async def create_cost(cost: CostCreate, db: Session = Depends(get_db)):
    db_cost = Cost(**cost.model_dump())
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)
    return db_cost

@app.get("/api/costs/{month}", response_model=List[CostResponse])
async def get_costs(month: str, db: Session = Depends(get_db)):
    return db.query(Cost).filter(Cost.month == month).order_by(Cost.created_at.desc()).all()

@app.get("/api/costs/id/{cost_id}", response_model=CostResponse)
async def get_cost_by_id(cost_id: int, db: Session = Depends(get_db)):
    cost = db.query(Cost).filter(Cost.id == cost_id).first()
    if not cost:
        raise HTTPException(status_code=404, detail="Cost not found")
    return cost

@app.put("/api/costs/{cost_id}", response_model=CostResponse)
async def update_cost(cost_id: int, cost_update: CostUpdate, db: Session = Depends(get_db)):
    cost = db.query(Cost).filter(Cost.id == cost_id).first()
    if not cost:
        raise HTTPException(status_code=404, detail="Cost not found")
    
    update_data = cost_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cost, field, value)
    
    cost.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(cost)
    return cost

@app.delete("/api/costs/{cost_id}")
async def delete_cost(cost_id: int, db: Session = Depends(get_db)):
    cost = db.query(Cost).filter(Cost.id == cost_id).first()
    if not cost:
        raise HTTPException(status_code=404, detail="Cost not found")
    
    db.delete(cost)
    db.commit()
    return {"message": "Cost deleted successfully"}

# Allocation and Reports
@app.post("/api/allocate/{month}")
async def allocate_costs(month: str, db: Session = Depends(get_db)):
    engine = CostAllocationEngine(db)
    result = engine.allocate_costs_for_month(month)
    return result

@app.get("/api/report/{month}")
async def get_monthly_report(month: str, db: Session = Depends(get_db)):
    engine = CostAllocationEngine(db)
    return engine._generate_monthly_report(month, {}, {})

# Export endpoints
@app.get("/api/export/{month}/csv")
async def export_monthly_csv(month: str, db: Session = Depends(get_db)):
    """Export monthly report as CSV"""
    engine = CostAllocationEngine(db)
    report = engine._generate_monthly_report(month, {}, {})
    
    # Create DataFrame
    df = pd.DataFrame(report['products'])
    
    # Save to CSV
    csv_path = f"static/exports/report_{month}.csv"
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    df.to_csv(csv_path, index=False)
    
    return {"download_url": f"/static/exports/report_{month}.csv"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
