# Purple Patch Farms Cost Allocation System

A comprehensive cost allocation system for fruit and vegetable farming operations.

## Project Structure

```
purple/
├── backend/
│   ├── app.py              # FastAPI backend application
│   ├── index.html          # Frontend dashboard
│   ├── requirements.txt    # Python dependencies
│   ├── fruit_vegetable_costs.db  # SQLite database
│   └── static/
│       ├── css/            # Stylesheets
│       ├── images/         # Images (PP.jpg logo)
│       └── js/
│           └── dashboard.js # Frontend JavaScript
├── plan.md                 # Project documentation
└── README.md              # This file
```

## Features

- **Product Management**: Add, edit, and manage fruits and vegetables
- **Sales Tracking**: Record monthly sales data with quantities and prices
- **Cost Management**: Track operational costs and allocate them to products
- **Excel Upload**: Upload monthly Excel sheets with automatic parsing
- **Cost Allocation**: Automatically calculate cost per product using various allocation methods
- **Reports**: Generate comprehensive reports and export to CSV
- **Dashboard**: Real-time statistics and insights

## Quick Start

1. **Install Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   cd backend
   python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Access the Dashboard**:
   Open your browser and go to `http://localhost:8000`

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript
- **Charts**: Chart.js
- **File Processing**: Pandas, Openpyxl

## License

This project is proprietary to Purple Patch Farms.

