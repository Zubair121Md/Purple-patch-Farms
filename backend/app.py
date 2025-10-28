from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
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
import io

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
    quantity = Column(Float)  # Outward quantity (sold)
    sale_price = Column(Float)
    direct_cost = Column(Float, default=0.0)
    inward_quantity = Column(Float, default=0.0)  # Inward quantity (purchased/grown)
    inward_rate = Column(Float, default=0.0)  # Inward rate per kg
    inward_value = Column(Float, default=0.0)  # Total inward value
    inhouse_production = Column(Float, default=0.0)  # Extra production (outward > inward)
    wastage = Column(Float, default=0.0)  # Wastage (inward > outward)
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
    
    # NEW: P&L classification fields
    pl_classification = Column(String, default=None)  # 'B', 'I', 'O'
    original_amount = Column(Float, default=None)     # Original P&L amount
    allocation_ratio = Column(Float, default=None)    # Ratio used for B items
    source_file = Column(String, default='manual')    # 'excel_upload' or 'manual'
    pl_period = Column(String, default=None)          # '1-Apr-24 to 30-Apr-24'
    
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
    quantity: float = Field(..., gt=0)  # Outward quantity
    sale_price: float = Field(..., gt=0)
    direct_cost: float = Field(default=0.0, ge=0)
    inward_quantity: float = Field(default=0.0, ge=0)
    inward_rate: float = Field(default=0.0, ge=0)
    inward_value: float = Field(default=0.0, ge=0)
    inhouse_production: float = Field(default=0.0, ge=0)
    wastage: float = Field(default=0.0, ge=0)

class MonthlySaleUpdate(BaseModel):
    quantity: Optional[float] = Field(None, gt=0)
    sale_price: Optional[float] = Field(None, gt=0)
    direct_cost: Optional[float] = Field(None, ge=0)
    inward_quantity: Optional[float] = Field(None, ge=0)
    inward_rate: Optional[float] = Field(None, ge=0)
    inward_value: Optional[float] = Field(None, ge=0)
    inhouse_production: Optional[float] = Field(None, ge=0)
    wastage: Optional[float] = Field(None, ge=0)

class MonthlySaleResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    month: str
    quantity: float
    sale_price: float
    direct_cost: float
    inward_quantity: float
    inward_rate: float
    inward_value: float
    inhouse_production: float
    wastage: float
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
    
    # NEW: P&L fields (optional)
    pl_classification: Optional[str] = Field(None, pattern="^[BIO]$")
    original_amount: Optional[float] = Field(None, ge=0)
    allocation_ratio: Optional[float] = Field(None, ge=0, le=1)
    source_file: Optional[str] = Field(default="manual", max_length=100)
    pl_period: Optional[str] = Field(None, max_length=100)

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
    
    # NEW: P&L fields
    pl_classification: Optional[str] = None
    original_amount: Optional[float] = None
    allocation_ratio: Optional[float] = None
    source_file: Optional[str] = None
    pl_period: Optional[str] = None
    
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

# Excel Upload Models
class ExcelRowData(BaseModel):
    month: str
    particulars: str
    type: str  # "In-house" or "Outsourced"
    inward_quantity: float
    inward_rate: float
    inward_value: float
    outward_quantity: float
    outward_rate: float
    outward_value: float
    inhouse_production: float = 0.0
    wastage: float = 0.0

class ExcelUploadResponse(BaseModel):
    success: bool
    message: str
    parsed_data: List[ExcelRowData]
    errors: List[str] = []
    products_created: int = 0
    sales_created: int = 0

class ExcelPreviewData(BaseModel):
    products: List[Dict[str, Any]]
    sales: List[Dict[str, Any]]
    summary: Dict[str, Any]

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
        """Enhanced allocation function - works with all data regardless of month"""
        
        try:
            # Get all active products (ignore month)
            products = self.db.query(Product).filter(Product.is_active == True).all()
            product_map = {p.id: p for p in products}
            
            # Get all monthly sales (ignore month)
            monthly_sales = self.db.query(MonthlySale).all()
            sales_map = {s.product_id: s for s in monthly_sales}
            
            # Get all costs (ignore month)
            costs = self.db.query(Cost).all()
            
            if not costs:
                raise HTTPException(
                    status_code=400, 
                    detail="No costs found. Please add costs before running allocation."
                )
            
            if not monthly_sales:
                raise HTTPException(
                    status_code=400, 
                    detail="No sales data found. Please add sales data before running allocation."
                )
            
            # Clear existing allocations (ignore month)
            self.db.query(Allocation).delete()
            
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
        # Get product to access unit information
        product = sale.product
        
        # Unit conversion factors (EA to grams)
        UNIT_CONVERSIONS = {
            'Button Mushroom': 3.0,  # 3 grams per EA
            'Baby Corn': 170.0  # 170 grams per EA
        }
        
        if cost.basis == "weight":
            # Check if this EA product has a weight conversion
            if hasattr(product, 'unit') and product.unit and product.unit.upper() in ['EA', 'EACH', 'PC', 'PCS', 'UNIT', 'UNITS']:
                # Check if product has a conversion factor
                product_name = product.name.lower()
                for key, grams_per_ea in UNIT_CONVERSIONS.items():
                    if key.lower() in product_name:
                        # Convert EA to grams, then to kg
                        return (sale.quantity * grams_per_ea) / 1000.0
                
                # No conversion factor, use value-based allocation
                return sale.quantity * sale.sale_price
            return sale.quantity
        elif cost.basis == "value":
            return sale.quantity * sale.sale_price
        elif cost.basis == "trips":
            # For trips, use value-based to avoid unit issues
            if hasattr(product, 'unit') and product.unit and product.unit.upper() in ['EA', 'EACH', 'PC', 'PCS', 'UNIT', 'UNITS']:
                return sale.quantity * sale.sale_price
            return sale.quantity
        return 0.0
    
    def _generate_monthly_report(self, month: str, product_map: Dict, sales_map: Dict) -> Dict[str, Any]:
        """Generate comprehensive report with enhanced analytics (ignores month)"""
        
        # Get all allocations (ignore month)
        allocations = self.db.query(Allocation).all()
        
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
    
    # Product stats
    total_products = db.query(Product).count()
    active_products = db.query(Product).filter(Product.is_active == True).count()
    
    # Revenue and cost stats for ALL data (no month filtering)
    sales = db.query(MonthlySale).all()
    costs = db.query(Cost).all()
    
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


@app.get("/api/sales", response_model=List[MonthlySaleResponse])
async def get_all_sales(db: Session = Depends(get_db)):
    """Get all sales data - no month filtering"""
    sales = db.query(MonthlySale).all()
    
    # Add product names to response
    sales_with_names = []
    for sale in sales:
        product = db.query(Product).filter(Product.id == sale.product_id).first()
        sales_with_names.append(MonthlySaleResponse(
            **sale.__dict__,
            product_name=product.name if product else "Unknown"
        ))
    
    return sales_with_names

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

@app.get("/api/costs", response_model=List[CostResponse])
async def get_all_costs(db: Session = Depends(get_db)):
    """Get all costs data - no month filtering"""
    return db.query(Cost).order_by(Cost.created_at.desc()).all()

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

# Excel Upload endpoints
@app.post("/api/upload-excel")
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """BULLETPROOF Excel upload - handles all edge cases and data formats"""
    
    print(f"🚀 BULLETPROOF Excel upload starting for: {file.filename}")
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        return {
            "success": False,
            "message": "File must be an Excel file (.xlsx or .xls)",
            "products_created": 0,
            "sales_created": 0,
            "parsed_data": [],
            "errors": ["Invalid file type"]
        }
    
    try:
        # Read Excel file
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        print(f"📋 Excel columns: {list(df.columns)}")
        print(f"📊 Total rows: {len(df)}")
        print(f"📋 Sample data:")
        print(df.head(2).to_string())
        
        # BULLETPROOF column matching - handles any variation
        column_mapping = {
            'month': ['Month', 'month', 'MONTH', 'Date', 'date'],
            'particulars': ['Particulars', 'particulars', 'PARTICULARS', 'Product', 'product', 'Item', 'item'],
            'type': ['Type', 'type', 'TYPE', 'Source', 'source'],
            'inward_qty': ['Inward Quantity', 'inward quantity', 'INWARD QUANTITY', 'Inward Qty', 'inward qty', 'Inward', 'inward'],
            'inward_rate': ['Inward Eff. Rate', 'inward eff. rate', 'INWARD EFF. RATE', 'Inward Rate', 'inward rate', 'Inward Price', 'inward price'],
            'inward_value': ['Inward Value', 'inward value', 'INWARD VALUE', 'Inward Total', 'inward total'],
            'outward_qty': ['Outward Quantity', 'outward quantity', 'OUTWARD QUANTITY', 'Outward Qty', 'outward qty', 'Outward', 'outward', 'Sold', 'sold'],
            'outward_rate': ['Outward Eff. Rate', 'outward eff. rate', 'OUTWARD EFF. RATE', 'Outward Rate', 'outward rate', 'Outward Price', 'outward price', 'Selling Price', 'selling price'],
            'outward_value': ['Outward Value', 'outward value', 'OUTWARD VALUE', 'Outward Total', 'outward total', 'Sales Value', 'sales value']
        }
        
        # Find matching columns with fuzzy matching
        found_columns = {}
        for key, possible_names in column_mapping.items():
            for col_name in df.columns:
                col_clean = str(col_name).strip().lower()
                for possible in possible_names:
                    if col_clean == possible.lower() or col_clean in possible.lower() or possible.lower() in col_clean:
                        found_columns[key] = col_name
                        print(f"✅ Mapped '{col_name}' -> {key}")
                        break
                if key in found_columns:
                    break
        
        print(f"📋 Final column mapping: {found_columns}")
        
        # Check required columns
        required_keys = ['particulars', 'outward_qty', 'outward_rate']
        missing_keys = [key for key in required_keys if key not in found_columns]
        
        if missing_keys:
            return {
                "success": False,
                "message": f"Missing required columns: {', '.join(missing_keys)}. Found: {', '.join(df.columns)}",
                "products_created": 0,
                "sales_created": 0,
                "parsed_data": [],
                "errors": [f"Missing columns: {', '.join(missing_keys)}"]
            }
        
        parsed_data = []
        errors = []
        products_created = 0
        sales_created = 0
        
        print(f"🔄 Processing {len(df)} rows...")
        
        for index, row in df.iterrows():
            try:
                # Extract and clean data
                month = str(row[found_columns['month']]).strip() if found_columns.get('month') else "2025-04"
                particulars = str(row[found_columns['particulars']]).strip()
                product_type = str(row[found_columns['type']]).strip() if found_columns.get('type') else "Outsourced"
                
                # Skip empty rows
                if not particulars or particulars.lower() in ['', 'nan', 'none']:
                    print(f"⚠️  Skipping row {index + 2}: Empty particulars")
                    continue
                
                # Extract quantities with unit detection
                inward_qty_raw = row[found_columns['inward_qty']] if found_columns.get('inward_qty') else ""
                outward_qty_raw = row[found_columns['outward_qty']] if found_columns.get('outward_qty') else ""
                
                # Parse quantities and detect units
                inward_qty, inward_unit = parse_quantity_with_unit(inward_qty_raw)
                outward_qty, outward_unit = parse_quantity_with_unit(outward_qty_raw)
                
                # Extract rates and values
                inward_rate = parse_numeric(row[found_columns['inward_rate']]) if found_columns.get('inward_rate') else 0.0
                inward_value = parse_numeric(row[found_columns['inward_value']]) if found_columns.get('inward_value') else 0.0
                outward_rate = parse_numeric(row[found_columns['outward_rate']]) if found_columns.get('outward_rate') else 0.0
                outward_value = parse_numeric(row[found_columns['outward_value']]) if found_columns.get('outward_value') else 0.0
                
                # Skip rows with no meaningful data
                if outward_qty <= 0 and inward_qty <= 0:
                    print(f"⚠️  Skipping row {index + 2}: {particulars} - No quantity data")
                    continue
                
                # Handle missing outward data (use inward as outward)
                if outward_qty <= 0 and inward_qty > 0:
                    outward_qty = inward_qty
                    outward_rate = inward_rate
                    outward_value = inward_value
                    outward_unit = inward_unit
                    print(f"🔄 Row {index + 2}: Using inward as outward for {particulars}")
                
                # Handle missing inward data (set to 0)
                if inward_qty <= 0:
                    inward_qty = 0.0
                    inward_rate = 0.0
                    inward_value = 0.0
                
                print(f"✅ Processing row {index + 2}: {particulars}")
                print(f"   📦 Inward: {inward_qty} {inward_unit} @ ₹{inward_rate}")
                print(f"   📤 Outward: {outward_qty} {outward_unit} @ ₹{outward_rate}")
                
                # Calculate production and wastage
                diff = outward_qty - inward_qty
                inhouse_production = max(0, diff)
                wastage = max(0, -diff)
                
                # Normalize product type
                source = "inhouse" if product_type.lower() in ["in-house", "inhouse", "in house"] else "outsourced"
                
                # Apply split logic for OutwardQty > InwardQty
                if diff > 0 and source == "outsourced":
                    # Split into Outsourced + Inhouse portions
                    print(f"   🔄 Splitting {particulars}: {inward_qty} outsourced + {diff} inhouse")
                    
                    # Create records for both portions
                    records = split_inhouse_outsourced({
                        'month': month,
                        'particulars': particulars,
                        'inward_qty': inward_qty,
                        'outward_qty': outward_qty,
                        'inward_rate': inward_rate,
                        'outward_rate': outward_rate,
                        'outward_value': outward_value,
                        'inward_unit': inward_unit,
                        'outward_unit': outward_unit
                    })
                    
                    for record in records:
                        # Create or get product
                        product_name = f"{record['particulars']} ({record['type'].title()})"
                        product = db.query(Product).filter(Product.name == product_name).first()
                        if not product:
                            product = Product(
                                name=product_name,
                                source=record['type'].lower(),
                                unit=record['unit']
                            )
                            db.add(product)
                            db.commit()
                            db.refresh(product)
                            products_created += 1
                            print(f"   📦 Created product: {product_name}")
                        
                        # Create monthly sale record
                        monthly_sale = MonthlySale(
                            product_id=product.id,
                            month=record['month'],
                            quantity=record['outward_qty'],
                            sale_price=record['outward_rate'],
                            direct_cost=record['inward_value'],
                            inward_quantity=record['inward_qty'],
                            inward_rate=record['inward_rate'],
                            inward_value=record['inward_value'],
                            inhouse_production=record['inhouse_production'],
                            wastage=record['wastage']
                        )
                        
                        db.add(monthly_sale)
                        sales_created += 1
                        print(f"   💰 Created sale: {record['outward_qty']}{record['unit']} @ ₹{record['outward_rate']} ({record['type']})")
                        
                        # Add to parsed data
                        parsed_data.append(ExcelRowData(
                            month=record['month'],
                            particulars=record['particulars'],
                            type=record['type'],
                            inward_quantity=record['inward_qty'],
                            inward_rate=record['inward_rate'],
                            inward_value=record['inward_value'],
                            outward_quantity=record['outward_qty'],
                            outward_rate=record['outward_rate'],
                            outward_value=record['outward_value'],
                            inhouse_production=record['inhouse_production'],
                            wastage=record['wastage']
                        ))
                else:
                    # Single record (no split needed)
                    product_name = f"{particulars} ({source.title()})"
                    
                    # Create or get product
                    product = db.query(Product).filter(Product.name == product_name).first()
                    if not product:
                        product = Product(
                            name=product_name,
                            source=source,
                            unit=outward_unit if outward_unit else "kg"
                        )
                        db.add(product)
                        db.commit()
                        db.refresh(product)
                        products_created += 1
                        print(f"   📦 Created product: {product_name}")
                    
                    # Create monthly sale record
                    monthly_sale = MonthlySale(
                        product_id=product.id,
                        month=month,
                        quantity=outward_qty,
                        sale_price=outward_rate,
                        direct_cost=inward_value if inward_value > 0 else (inward_qty * inward_rate),
                        inward_quantity=inward_qty,
                        inward_rate=inward_rate,
                        inward_value=inward_value,
                        inhouse_production=inhouse_production,
                        wastage=wastage
                    )
                    
                    db.add(monthly_sale)
                    sales_created += 1
                    print(f"   💰 Created sale: {outward_qty}{outward_unit} @ ₹{outward_rate}")
                    
                    # Add to parsed data
                    parsed_data.append(ExcelRowData(
                        month=month,
                        particulars=particulars,
                        type=product_type,
                        inward_quantity=inward_qty,
                        inward_rate=inward_rate,
                        inward_value=inward_value,
                        outward_quantity=outward_qty,
                        outward_rate=outward_rate,
                        outward_value=outward_value,
                        inhouse_production=inhouse_production,
                        wastage=wastage
                    ))
                
            except Exception as e:
                error_msg = f"Row {index + 2}: {str(e)}"
                errors.append(error_msg)
                print(f"❌ Error processing row {index + 2}: {error_msg}")
                continue
        
        db.commit()
        
        print(f"✅ BULLETPROOF upload completed!")
        print(f"   📦 Products created: {products_created}")
        print(f"   💰 Sales created: {sales_created}")
        print(f"   📊 Rows processed: {len(parsed_data)}")
        
        return {
            "success": True,
            "message": f"Successfully processed {len(parsed_data)} rows",
            "products_created": products_created,
            "sales_created": sales_created,
            "parsed_data": [data.dict() for data in parsed_data],
            "errors": errors
        }
        
    except Exception as e:
        print(f"💥 BULLETPROOF upload failed: {str(e)}")
        return {
            "success": False,
            "message": f"Upload failed: {str(e)}",
            "products_created": 0,
            "sales_created": 0,
            "parsed_data": [],
            "errors": [str(e)]
        }

def parse_quantity_with_unit(value):
    """Parse quantity and extract unit from string like '53.500 Kg' or '855 EA'"""
    if pd.isna(value) or value == "" or str(value).strip() == "":
        return 0.0, "kg"
    
    value_str = str(value).strip()
    
    # Extract number and unit
    import re
    match = re.match(r'([\d,]+\.?\d*)\s*([A-Za-z]*)', value_str)
    
    if match:
        quantity_str = match.group(1).replace(',', '')
        unit = match.group(2).strip().upper()
        
        try:
            quantity = float(quantity_str)
            return quantity, unit if unit else "kg"
        except ValueError:
            return 0.0, "kg"
    
    # Try to parse as pure number
    try:
        quantity = float(value_str)
        return quantity, "kg"
    except ValueError:
        return 0.0, "kg"

def parse_numeric(value):
    """Parse numeric value, handling empty cells and various formats"""
    if pd.isna(value) or value == "" or str(value).strip() == "":
        return 0.0
    
    try:
        # Remove commas and convert to float
        value_str = str(value).replace(',', '').strip()
        return float(value_str)
    except (ValueError, TypeError):
        return 0.0

def split_inhouse_outsourced(row):
    """Split a product into outsourced and inhouse portions when OutwardQty > InwardQty"""
    records = []
    
    diff = row['outward_qty'] - row['inward_qty']
    
    if diff > 0:
        # 1️⃣ Outsourced portion
        outsourced_part = {
            'month': row['month'],
            'particulars': row['particulars'],
            'type': 'Outsourced',
            'inward_qty': row['inward_qty'],
            'outward_qty': row['inward_qty'],  # same as inward
            'inward_rate': row['inward_rate'],
            'outward_rate': row['outward_rate'],
            'inward_value': row['inward_qty'] * row['inward_rate'],
            'outward_value': row['inward_qty'] * row['outward_rate'],
            'inhouse_production': 0,
            'wastage': 0,
            'unit': row['outward_unit']
        }
        
        # 2️⃣ Inhouse portion
        inhouse_part = {
            'month': row['month'],
            'particulars': row['particulars'],
            'type': 'Inhouse',
            'inward_qty': 0,
            'outward_qty': diff,  # the excess produced internally
            'inward_rate': row['inward_rate'],  # use same cost rate for now
            'outward_rate': row['outward_rate'],
            'inward_value': 0,
            'outward_value': diff * row['outward_rate'],
            'inhouse_production': diff,
            'wastage': 0,
            'unit': row['outward_unit']
        }
        
        records.extend([outsourced_part, inhouse_part])
        print(f"   🔄 Split: {row['inward_qty']} outsourced + {diff} inhouse")
    else:
        # No split needed - single record
        records.append({
            'month': row['month'],
            'particulars': row['particulars'],
            'type': 'Outsourced',
            'inward_qty': row['inward_qty'],
            'outward_qty': row['outward_qty'],
            'inward_rate': row['inward_rate'],
            'outward_rate': row['outward_rate'],
            'inward_value': row['inward_qty'] * row['inward_rate'],
            'outward_value': row['outward_qty'] * row['outward_rate'],
            'inhouse_production': 0,
            'wastage': abs(diff) if diff < 0 else 0,
            'unit': row['outward_unit']
        })
    
    return records

def parse_purple_patch_pl(file_path, db):
    """Parse Purple Patch P&L Excel and create enhanced Cost records"""
    
    print(f"📊 Parsing Purple Patch P&L: {file_path}")
    
    # Items to EXCLUDE (revenue/trading account items)
    exclude_items = {
        # Sales/Revenue items
        'Hamper Sales (B to C)', 'Karnataka Sales', 'Kerala Sales B', 'Tamilnadu Sales B', 
        'Complement Sales', 'Complement Sales B', 'Customer Quality Issue and Damage B to B', 
        'Customer Quality Issue and Damage B to B  B', 'Customer Quality Issue and Damage(B to C) B',
        'Customer Quality Issue and Damage (B to C)', 'Sales Return',
        'Discount Rate( B to B Rate) B', 'Discount Rate (B to B Rate)', 'DISCOUNT', 'Free Hamper',
        # Trading Account items (NOT actual expenses to allocate)
        'Opening Stock', 'Add: Purchase Accounts', 'Less: Closing Stock', 'Direct Expenses'
    }
    
    # Fixed template mapping
    template_mapping = {
        'Cultivation Expenses I': 'I',
        'Rejection Own Farm Harvest I': 'I',
        'Wastage-in Farm (Quality Check) I': 'I',
        'Entry Fee- Ooty Market O': 'O',
        'Loading and Unloading - Vegetable Purchase & Fruits O': 'O',
        'Drivers Betta B': 'B',
        'ELECTRICITY CHARGES B': 'B',
        'Employee Benefits Expenses B': 'B',
        'Freight Charges B': 'B',
        'Office & Administrative Expenses B': 'B',
        'Running & Maintanance B': 'B',
        'Software Maintananace B': 'B',
        'Transportation Exp B': 'B',
        'Travelling Allowance -Staff B': 'B',
        'Vehicle Fuels B': 'B',
        'Vehicle Maintanance B': 'B',
        'Vehicle Taxes &Insurance B': 'B',
        'Loading Charges Others B': 'B',
        'Miscellaneous Exp B': 'B',
        'Packing Materials Issued A/c B': 'B',
        'Staff House Rent B': 'B',
        'Tea and Food Exp-Staff B': 'B',
        'Delivery Charges': 'B',
        'INTEREST ON INCOME TAX REFUND': 'B',
        'Packing & Forwarding Charges': 'B',
        'Banking Charges': 'B',
        'Distribution Expenses': 'B',
        'Employee Cost': 'B',
        'Finance Cost': 'B',
        'Rates & Taxes': 'B',
        'Rent': 'B',
        'Sales Expenditure': 'B',
        'CDSL DEMAT Charges': 'B',
        'Company Secretary & MCA Filing Charges': 'B',
        'Courier and Postage Charges': 'B',
        'DEMAT of Shares Charges': 'B',
        'Depreciation A/c': 'B',
        'DISCOUNT': 'B',
        'Free Hamper': 'B',
        'FSSAI License Fees': 'B',
        'Interest on Late Payment of TDS': 'B',
        'Interest on Loan From Feroke Boards': 'B',
        'Interest on MA Ashraf Loan': 'B',
        'Interest on MP Cherian Loan': 'B',
        'Land Subdivision Fee': 'B',
        'Legal Expenses': 'B',
        'Loading and Unloading - Sales': 'B',
        'Round Off': 'B',
        'Salary and Allowances': 'B',
        'TDS Filing Charges': 'B',
        'TDS Service Charges': 'B',
        'Trade Mark Registration Consultancy Fee': 'B',
        'Trade Mark Registration Fee': 'B',
        'Wastage - in Dispatch': 'B',
        'Wastage-in Dispatch': 'B'
    }
    
    try:
        # Read Excel file
        df = pd.read_excel(file_path, header=None)
        print(f"📋 Excel loaded: {len(df)} rows, {len(df.columns)} columns")
        
        # Find the period from the data
        period = "Unknown"
        for idx, row in df.iterrows():
            for col in df.columns:
                if pd.notna(row[col]) and 'Apr-24' in str(row[col]):
                    period = str(row[col])
                    break
            if period != "Unknown":
                break
        
        print(f"📅 Period detected: {period}")
        
        # Extract data rows
        data_rows = []
        for idx, row in df.iterrows():
            # Look for rows with data in first two columns
            if len(row) >= 2 and pd.notna(row.iloc[0]) and pd.notna(row.iloc[1]):
                particulars = str(row.iloc[0]).strip()
                amount_str = str(row.iloc[1]).strip()
                
                # Skip empty or header rows
                if particulars in ['', 'nan', 'PURPLE PATCH FARMS INTERNATIONAL PVT.LTD -FARM', 'Particulars', 'Trading Account:', 'Income Statement:']:
                    continue
                
                # Try to parse amount
                try:
                    # Clean amount string
                    amount_str = amount_str.replace(',', '').replace('₹', '').strip()
                    if amount_str and amount_str != 'nan':
                        amount = float(amount_str)
                        if particulars and amount != 0:
                            # Skip revenue/trading account items
                            if particulars in exclude_items:
                                print(f"   ⏭️  Skipped revenue item: {particulars}")
                                continue
                            
                            # Only include actual expenses (costs)
                            data_rows.append({
                                'particulars': particulars,
                                'amount': amount,
                                'type': template_mapping.get(particulars, 'B')  # Default to B if not found
                            })
                            print(f"   📊 Found: {particulars} = ₹{amount:,.2f} ({template_mapping.get(particulars, 'B')})")
                except ValueError:
                    continue
        
        print(f"📊 Found {len(data_rows)} data rows")
        
        # Calculate ratio based on ACTUAL SALES DATA from database
        from sqlalchemy import func
        
        sales = db.query(MonthlySale).join(Product).all()
        
        # Calculate based on revenue (quantity * sale_price)
        inhouse_sales_total = sum(s.quantity * s.sale_price for s in sales if s.product.source == "inhouse")
        outsourced_sales_total = sum(s.quantity * s.sale_price for s in sales if s.product.source == "outsourced")
        total_sales = inhouse_sales_total + outsourced_sales_total
        
        # Calculate dynamic ratio based on actual revenue
        if total_sales > 0:
            inhouse_ratio = inhouse_sales_total / total_sales
            outsourced_ratio = outsourced_sales_total / total_sales
            print(f"📊 Using REVENUE-BASED ratio - Inhouse: {inhouse_ratio:.4f}, Outsourced: {outsourced_ratio:.4f}")
            print(f"   💰 Inhouse Revenue: ₹{inhouse_sales_total:,.2f} | Outsourced Revenue: ₹{outsourced_sales_total:,.2f}")
        else:
            # Fallback to quantity-based ratio
            inhouse_qty = sum(s.quantity for s in sales if s.product.source == "inhouse")
            outsourced_qty = sum(s.quantity for s in sales if s.product.source == "outsourced")
            total_qty = inhouse_qty + outsourced_qty
            
            if total_qty > 0:
                inhouse_ratio = inhouse_qty / total_qty
                outsourced_ratio = outsourced_qty / total_qty
                print(f"📊 Using QUANTITY-BASED ratio - Inhouse: {inhouse_ratio:.4f}, Outsourced: {outsourced_ratio:.4f}")
                print(f"   📦 Inhouse Qty: {inhouse_qty:,.2f} | Outsourced Qty: {outsourced_qty:,.2f}")
            else:
                inhouse_ratio = 0.1822  # Default ratio
                outsourced_ratio = 0.8178
                print(f"📊 Using DEFAULT ratio - Inhouse: {inhouse_ratio:.4f}, Outsourced: {outsourced_ratio:.4f}")
        
        # Create Cost records
        costs_created = 0
        for row in data_rows:
            particulars = row['particulars']
            amount = row['amount']
            item_type = row['type']
            
            if item_type == 'I':
                # 100% inhouse
                cost = Cost(
                    name=particulars,
                    amount=amount,
                    applies_to="inhouse",
                    cost_type="common",
                    basis="value",
                    month="2025-04-24 00:00:00",  # Match sales data format
                    is_fixed="variable",
                    category="pl_import",
                    pl_classification="I",
                    original_amount=amount,
                    allocation_ratio=1.0,
                    source_file="pl_upload",
                    pl_period=period
                )
                db.add(cost)
                costs_created += 1
                print(f"   📦 Created I cost: {particulars} = ₹{amount:,.2f} (100% inhouse)")
                
            elif item_type == 'O':
                # 100% outsourced
                cost = Cost(
                    name=particulars,
                    amount=amount,
                    applies_to="outsourced",
                    cost_type="common",
                    basis="value",
                    month="2025-04",
                    is_fixed="variable",
                    category="pl_import",
                    pl_classification="O",
                    original_amount=amount,
                    allocation_ratio=1.0,
                    source_file="pl_upload",
                    pl_period=period
                )
                db.add(cost)
                costs_created += 1
                print(f"   📦 Created O cost: {particulars} = ₹{amount:,.2f} (100% outsourced)")
                
            else:  # B - split by ratio
                # Inhouse portion
                inhouse_amount = amount * inhouse_ratio
                cost_inhouse = Cost(
                    name=f"{particulars} (Inhouse)",
                    amount=inhouse_amount,
                    applies_to="inhouse",
                    cost_type="common",
                    basis="value",
                    month="2025-04",
                    is_fixed="variable",
                    category="pl_import",
                    pl_classification="B",
                    original_amount=amount,
                    allocation_ratio=inhouse_ratio,
                    source_file="pl_upload",
                    pl_period=period
                )
                db.add(cost_inhouse)
                costs_created += 1
                
                # Outsourced portion
                outsourced_amount = amount * outsourced_ratio
                cost_outsourced = Cost(
                    name=f"{particulars} (Outsourced)",
                    amount=outsourced_amount,
                    applies_to="outsourced",
                    cost_type="common",
                    basis="value",
                    month="2025-04",
                    is_fixed="variable",
                    category="pl_import",
                    pl_classification="B",
                    original_amount=amount,
                    allocation_ratio=outsourced_ratio,
                    source_file="pl_upload",
                    pl_period=period
                )
                db.add(cost_outsourced)
                costs_created += 1
                
                print(f"   📦 Created B cost: {particulars} = ₹{amount:,.2f} → Inhouse: ₹{inhouse_amount:,.2f}, Outsourced: ₹{outsourced_amount:,.2f}")
        
        db.commit()
        
        print(f"✅ P&L parsing completed!")
        print(f"   📦 Costs created: {costs_created}")
        print(f"   📊 Period: {period}")
        print(f"   📈 Ratios: Inhouse {inhouse_ratio:.2%}, Outsourced {outsourced_ratio:.2%}")
        
        return {
            "success": True,
            "message": f"Successfully processed P&L with {costs_created} cost records",
            "costs_created": costs_created,
            "period": period,
            "ratios": {
                "inhouse": inhouse_ratio,
                "outsourced": outsourced_ratio
            },
            "data_rows": len(data_rows)
        }
        
    except Exception as e:
        print(f"💥 Error parsing P&L: {str(e)}")
        return {
            "success": False,
            "message": f"Error parsing P&L: {str(e)}",
            "costs_created": 0
        }

@app.post("/api/upload-pl")
async def upload_pl(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and parse Purple Patch P&L Excel file"""
    
    print(f"🚀 Starting P&L upload for file: {file.filename}")
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        return {
            "success": False,
            "message": "File must be an Excel file (.xlsx or .xls)",
            "costs_created": 0
        }
    
    try:
        # Save uploaded file temporarily
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Parse P&L file
        result = parse_purple_patch_pl(tmp_file_path, db)
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        
        return result
        
    except Exception as e:
        print(f"💥 P&L upload failed: {str(e)}")
        return {
            "success": False,
            "message": f"P&L upload failed: {str(e)}",
            "costs_created": 0
        }

@app.get("/api/wastage")
async def get_wastage_data(db: Session = Depends(get_db)):
    """Get wastage data for all products"""
    try:
        # Get all sales with wastage > 0
        wastage_sales = db.query(MonthlySale).filter(MonthlySale.wastage > 0).all()
        
        wastage_data = []
        for sale in wastage_sales:
            product = db.query(Product).filter(Product.id == sale.product_id).first()
            if product:
                wastage_percentage = (sale.wastage / sale.inward_quantity * 100) if sale.inward_quantity > 0 else 0
                
                wastage_data.append({
                    "id": sale.id,
                    "product_name": product.name,
                    "product_type": product.source,
                    "month": sale.month,
                    "inward_quantity": sale.inward_quantity,
                    "outward_quantity": sale.quantity,
                    "wastage_quantity": sale.wastage,
                    "wastage_percentage": round(wastage_percentage, 2),
                    "wastage_value": sale.wastage * sale.inward_rate,
                    "unit": product.unit
                })
        
        # Sort by wastage percentage descending
        wastage_data.sort(key=lambda x: x['wastage_percentage'], reverse=True)
        
        return {
            "success": True,
            "wastage_data": wastage_data,
            "total_wastage_items": len(wastage_data),
            "total_wastage_quantity": sum(item['wastage_quantity'] for item in wastage_data),
            "total_wastage_value": sum(item['wastage_value'] for item in wastage_data)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error fetching wastage data: {str(e)}",
            "wastage_data": []
        }

@app.get("/api/excel-preview", response_model=ExcelPreviewData)
async def get_excel_preview(month: str, db: Session = Depends(get_db)):
    """Get preview of parsed Excel data for a specific month"""
    
    # Get products and sales for the month
    products = db.query(Product).filter(Product.is_active == True).all()
    sales = db.query(MonthlySale).filter(MonthlySale.month == month).all()
    
    # Format products data
    products_data = []
    for product in products:
        products_data.append({
            "id": product.id,
            "name": product.name,
            "source": product.source,
            "unit": product.unit,
            "is_active": product.is_active
        })
    
    # Format sales data
    sales_data = []
    for sale in sales:
        sales_data.append({
            "id": sale.id,
            "product_id": sale.product_id,
            "product_name": sale.product.name,
            "month": sale.month,
            "quantity": sale.quantity,
            "sale_price": sale.sale_price,
            "direct_cost": sale.direct_cost,
            "inward_quantity": sale.inward_quantity,
            "inward_rate": sale.inward_rate,
            "inward_value": sale.inward_value,
            "inhouse_production": sale.inhouse_production,
            "wastage": sale.wastage
        })
    
    # Calculate summary
    total_products = len(products)
    total_sales = len(sales)
    total_revenue = sum(sale.quantity * sale.sale_price for sale in sales)
    total_inhouse_production = sum(sale.inhouse_production for sale in sales)
    total_wastage = sum(sale.wastage for sale in sales)
    
    summary = {
        "total_products": total_products,
        "total_sales": total_sales,
        "total_revenue": total_revenue,
        "total_inhouse_production": total_inhouse_production,
        "total_wastage": total_wastage
    }
    
    return ExcelPreviewData(
        products=products_data,
        sales=sales_data,
        summary=summary
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
