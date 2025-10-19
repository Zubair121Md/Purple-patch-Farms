# 🍇 Fruit & Vegetable Cost Allocation System v2.0

A **full-featured, production-ready dashboard** for automatically calculating costs and profits for fruit and vegetable businesses. This system provides comprehensive analytics, interactive charts, and advanced cost allocation algorithms.

## ✨ Features

### 🎯 **Core Functionality**
- **Product Management**: Track inhouse and outsourced products with full CRUD operations
- **Monthly Sales Tracking**: Record quantities, prices, and direct costs with validation
- **Cost Management**: Handle various cost types with categorization and allocation rules
- **Automatic Allocation**: Advanced algorithms for fair cost distribution
- **Comprehensive Reporting**: Detailed analytics with export capabilities

### 📊 **Dashboard & Analytics**
- **Real-time Statistics**: Live updates of revenue, costs, and profits
- **Interactive Charts**: Revenue vs costs, source distribution, and trend analysis
- **Top Products Analysis**: Rank products by profitability and performance
- **Source-wise Breakdown**: Separate analytics for inhouse vs outsourced products
- **Cost Breakdown**: Category-wise cost analysis and insights

### 🚀 **Advanced Features**
- **Modern UI/UX**: Responsive design with dark/light themes
- **Data Validation**: Comprehensive input validation and error handling
- **Export Functionality**: CSV export for reports and data analysis
- **Real-time Updates**: Live data refresh and synchronization
- **Mobile Responsive**: Works perfectly on desktop, tablet, and mobile

### 🔧 **Technical Excellence**
- **DSA Optimizations**: HashMap lookups, efficient algorithms, and performance tuning
- **RESTful API**: Clean, well-documented API endpoints
- **Database Design**: Normalized schema with proper relationships
- **Error Handling**: Comprehensive error management and user feedback
- **Security**: Input validation, SQL injection protection, and data sanitization

## 🏗️ Architecture

```
purple/
├── backend/
│   ├── app.py              # FastAPI backend server
│   └── requirements.txt    # Python dependencies
├── frontend/
│   └── index.html          # Modern dashboard UI
├── static/
│   ├── css/               # Stylesheets
│   ├── js/
│   │   └── dashboard.js   # Dashboard functionality
│   └── exports/           # Generated reports
├── start.py               # One-click startup script
└── README.md              # This file
```

## 🚀 Quick Start

### **Option 1: One-Click Start (Recommended)**
```bash
python start.py
```
This will:
- Install all dependencies
- Start the server
- Open your browser automatically
- Show you the dashboard

### **Option 2: Manual Setup**
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Start the server
cd backend
python app.py

# Open browser to http://localhost:8000
```

## 🌐 Access Points

- **Main Dashboard**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **API Health Check**: http://localhost:8000/api/health

## 📱 Dashboard Features

### **1. Dashboard Tab**
- Real-time statistics cards
- Interactive revenue vs costs chart
- Source distribution pie chart
- Top products by profitability
- Quick action buttons

### **2. Products Management**
- Add/edit/delete products
- Source categorization (inhouse/outsourced)
- Status management (active/inactive)
- Bulk operations support

### **3. Sales Data**
- Monthly sales entry
- Product selection with validation
- Quantity and pricing management
- Direct cost tracking

### **4. Cost Management**
- Multiple cost categories
- Flexible allocation rules
- Cost type classification
- Monthly cost tracking

### **5. Cost Allocation**
- One-click allocation execution
- Real-time calculation results
- Detailed allocation breakdown
- Profit analysis per product

### **6. Reports & Analytics**
- Comprehensive monthly reports
- Export to CSV functionality
- Interactive data visualization
- Performance metrics

## 🔧 API Endpoints

### **Dashboard**
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/health` - Health check

### **Products**
- `GET /api/products/` - List all products
- `POST /api/products/` - Create product
- `GET /api/products/{id}` - Get product by ID
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product

### **Sales**
- `GET /api/monthly-sales/{month}` - Get sales for month
- `POST /api/monthly-sales/` - Create sales record
- `PUT /api/monthly-sales/{id}` - Update sales record

### **Costs**
- `GET /api/costs/{month}` - Get costs for month
- `POST /api/costs/` - Create cost
- `PUT /api/costs/{id}` - Update cost
- `DELETE /api/costs/{id}` - Delete cost

### **Allocation & Reports**
- `POST /api/allocate/{month}` - Run cost allocation
- `GET /api/report/{month}` - Get monthly report
- `GET /api/export/{month}/csv` - Export report as CSV

## 🧮 Cost Allocation Algorithm

The system uses sophisticated algorithms for fair cost distribution:

### **1. Product Filtering**
- Determines which products are affected by each cost
- Supports multiple filter criteria (inhouse, outsourced, both, all)

### **2. Basis Calculation**
- **Weight-based**: Allocates based on product quantities
- **Value-based**: Allocates based on revenue (quantity × price)
- **Trip-based**: Allocates based on transportation needs

### **3. Proportional Allocation**
```
allocation = (product_basis / total_basis) × cost_amount
```

### **4. DSA Optimizations**
- O(1) product lookups using HashMap
- Efficient batch processing
- Sorted results for quick insights
- Memory-optimized data structures

## 📊 Example Calculation

**Input Data:**
- Strawberry: 10kg @ ₹200/kg (outsourced)
- Banana: 25kg @ ₹150/kg (outsourced)  
- Apple: 30kg @ ₹100/kg (inhouse)

**Costs:**
- Purchase Loading: ₹300 (outsourced only, weight-based)
- Sales Loading: ₹700 (all products, weight-based)

**Allocation Results:**
- **Purchase Loading (₹300)**:
  - Strawberry: ₹85.71 (10/35 × 300)
  - Banana: ₹214.29 (25/35 × 300)

- **Sales Loading (₹700)**:
  - Strawberry: ₹107.69 (10/65 × 700)
  - Banana: ₹269.23 (25/65 × 700)
  - Apple: ₹323.08 (30/65 × 700)

## 🎨 UI/UX Features

### **Modern Design**
- Clean, professional interface
- Intuitive navigation
- Responsive grid layouts
- Smooth animations and transitions

### **Interactive Elements**
- Real-time form validation
- Dynamic charts and graphs
- Modal dialogs for data entry
- Toast notifications for feedback

### **Data Visualization**
- Revenue vs costs bar chart
- Source distribution pie chart
- Profitability rankings
- Trend analysis graphs

## 🔒 Security Features

- Input validation and sanitization
- SQL injection protection
- XSS prevention
- CORS configuration
- Error handling without data exposure

## 📈 Performance Optimizations

- **Database**: Indexed queries, efficient joins
- **Frontend**: Lazy loading, optimized rendering
- **API**: Caching, batch operations
- **Charts**: Canvas-based rendering for smooth performance

## 🛠️ Development

### **Backend Development**
```bash
cd backend
python app.py  # Starts with auto-reload
```

### **Frontend Development**
- Edit `frontend/index.html` for UI changes
- Edit `static/js/dashboard.js` for functionality
- CSS is embedded in HTML for simplicity

### **Database Management**
- SQLite database: `backend/fruit_vegetable_costs.db`
- Tables: products, monthly_sales, costs, allocations, users
- Automatic migrations on startup

## 📋 System Requirements

- **Python**: 3.8 or higher
- **Memory**: 512MB RAM minimum
- **Storage**: 100MB for application + data
- **Browser**: Modern browser with JavaScript enabled

## 🚀 Deployment

### **Local Development**
```bash
python start.py
```

### **Production Deployment**
1. Install dependencies: `pip install -r backend/requirements.txt`
2. Configure environment variables
3. Set up reverse proxy (nginx)
4. Use process manager (PM2, systemd)
5. Configure SSL certificates

## 📞 Support

- **Documentation**: See API docs at `/api/docs`
- **Issues**: Check console for error messages
- **Health Check**: Visit `/api/health`

## 🎯 Roadmap

- [ ] User authentication and authorization
- [ ] Multi-tenant support
- [ ] Advanced reporting with PDF export
- [ ] Mobile app (React Native)
- [ ] Real-time notifications
- [ ] Integration with accounting software
- [ ] Machine learning for cost prediction

## 📄 License

This project is open source and available under the MIT License.

---

**Built with ❤️ using FastAPI, SQLAlchemy, Chart.js, and modern web technologies**

**Version 2.0.0 - Full-Featured Dashboard Edition**