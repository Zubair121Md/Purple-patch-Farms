// Dashboard JavaScript for Fruit & Vegetable Cost Allocation System
const API_BASE = '/api';
let currentTab = 'dashboard';
let charts = {};
let currentData = {};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    loadDashboardData();
    setupEventListeners();
});

// Initialize dashboard components
function initializeDashboard() {
    // Set current month
    const currentMonth = new Date().toISOString().slice(0, 7);
    document.getElementById('current-month').textContent = `Current Month: ${currentMonth}`;
    
    // Initialize charts
    initializeCharts();
    
    // Load initial data
    loadProducts();
    loadSales();
    loadCosts();
}

// Setup event listeners
function setupEventListeners() {
    // Tab navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const tab = this.getAttribute('data-tab');
            showTab(tab);
        });
    });
    
    // Form submissions
    document.getElementById('product-form').addEventListener('submit', handleProductSubmit);
    document.getElementById('sales-form').addEventListener('submit', handleSalesSubmit);
    document.getElementById('cost-form').addEventListener('submit', handleCostSubmit);
    
    // Month filters
    document.getElementById('sales-month-filter').addEventListener('change', loadSales);
    document.getElementById('costs-month-filter').addEventListener('change', loadCosts);
}

// Tab switching
function showTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Show selected tab content
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked nav item
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Update page title
    const titles = {
        'dashboard': 'Dashboard',
        'products': 'Products Management',
        'sales': 'Sales Data',
        'costs': 'Cost Management',
        'allocation': 'Cost Allocation',
        'reports': 'Reports & Analytics',
        'settings': 'System Settings'
    };
    document.getElementById('page-title').textContent = titles[tabName] || 'Dashboard';
    
    currentTab = tabName;
    
    // Load data for specific tabs
    if (tabName === 'dashboard') {
        loadDashboardData();
    } else if (tabName === 'products') {
        loadProducts();
    } else if (tabName === 'sales') {
        loadSales();
    } else if (tabName === 'costs') {
        loadCosts();
    }
}

// Load dashboard data
async function loadDashboardData() {
    try {
        showLoading('stats-grid');
        
        // Load dashboard stats
        const statsResponse = await fetch(`${API_BASE}/dashboard/stats`);
        const stats = await statsResponse.json();
        
        displayDashboardStats(stats);
        
        // Load top products
        await loadTopProducts();
        
        // Update charts
        updateCharts(stats);
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showAlert('Error loading dashboard data', 'error');
    }
}

// Display dashboard statistics
function displayDashboardStats(stats) {
    const statsGrid = document.getElementById('stats-grid');
    
    const statsHTML = `
        <div class="stat-card products">
            <div class="stat-header">
                <span class="stat-title">Total Products</span>
                <i class="fas fa-apple-alt stat-icon"></i>
            </div>
            <div class="stat-value">${stats.total_products}</div>
            <div class="stat-change positive">
                <i class="fas fa-arrow-up"></i>
                ${stats.active_products} active
            </div>
        </div>
        
        <div class="stat-card revenue">
            <div class="stat-header">
                <span class="stat-title">Total Revenue</span>
                <i class="fas fa-chart-line stat-icon"></i>
            </div>
            <div class="stat-value">₹${formatNumber(stats.total_revenue)}</div>
            <div class="stat-change positive">
                <i class="fas fa-arrow-up"></i>
                +${stats.profit_margin.toFixed(1)}% margin
            </div>
        </div>
        
        <div class="stat-card costs">
            <div class="stat-header">
                <span class="stat-title">Total Costs</span>
                <i class="fas fa-dollar-sign stat-icon"></i>
            </div>
            <div class="stat-value">₹${formatNumber(stats.total_costs)}</div>
            <div class="stat-change">
                <i class="fas fa-info-circle"></i>
                All categories
            </div>
        </div>
        
        <div class="stat-card profit">
            <div class="stat-header">
                <span class="stat-title">Net Profit</span>
                <i class="fas fa-trophy stat-icon"></i>
            </div>
            <div class="stat-value">₹${formatNumber(stats.total_profit)}</div>
            <div class="stat-change ${stats.total_profit >= 0 ? 'positive' : 'negative'}">
                <i class="fas fa-${stats.total_profit >= 0 ? 'arrow-up' : 'arrow-down'}"></i>
                ${stats.profit_margin.toFixed(1)}% margin
            </div>
        </div>
    `;
    
    statsGrid.innerHTML = statsHTML;
}

// Load top products
async function loadTopProducts() {
    try {
        const currentMonth = new Date().toISOString().slice(0, 7);
        const response = await fetch(`${API_BASE}/report/${currentMonth}`);
        const report = await response.json();
        
        displayTopProducts(report.top_products || []);
    } catch (error) {
        console.error('Error loading top products:', error);
        document.getElementById('top-products-table').innerHTML = '<p>No data available</p>';
    }
}

// Display top products
function displayTopProducts(products) {
    const container = document.getElementById('top-products-table');
    
    if (products.length === 0) {
        container.innerHTML = '<p>No products data available</p>';
        return;
    }
    
    let tableHTML = `
        <table class="table">
            <thead>
                <tr>
                    <th>Product</th>
                    <th>Source</th>
                    <th>Revenue</th>
                    <th>Costs</th>
                    <th>Profit</th>
                    <th>Margin</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    products.forEach(product => {
        tableHTML += `
            <tr>
                <td><strong>${product.product_name}</strong></td>
                <td><span class="badge ${product.source === 'inhouse' ? 'badge-success' : 'badge-info'}">${product.source}</span></td>
                <td>₹${formatNumber(product.revenue)}</td>
                <td>₹${formatNumber(product.total_cost)}</td>
                <td class="${product.profit >= 0 ? 'text-success' : 'text-danger'}">₹${formatNumber(product.profit)}</td>
                <td>${product.profit_margin.toFixed(1)}%</td>
            </tr>
        `;
    });
    
    tableHTML += '</tbody></table>';
    container.innerHTML = tableHTML;
}

// Initialize charts
function initializeCharts() {
    // Revenue vs Costs Chart
    const revenueCtx = document.getElementById('revenueChart').getContext('2d');
    charts.revenue = new Chart(revenueCtx, {
        type: 'bar',
        data: {
            labels: ['Revenue', 'Costs', 'Profit'],
            datasets: [{
                label: 'Amount (₹)',
                data: [0, 0, 0],
                backgroundColor: [
                    'rgba(33, 150, 243, 0.8)',
                    'rgba(244, 67, 54, 0.8)',
                    'rgba(76, 175, 80, 0.8)'
                ],
                borderColor: [
                    'rgba(33, 150, 243, 1)',
                    'rgba(244, 67, 54, 1)',
                    'rgba(76, 175, 80, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + formatNumber(value);
                        }
                    }
                }
            }
        }
    });
    
    // Source Distribution Chart
    const sourceCtx = document.getElementById('sourceChart').getContext('2d');
    charts.source = new Chart(sourceCtx, {
        type: 'doughnut',
        data: {
            labels: ['Inhouse', 'Outsourced'],
            datasets: [{
                data: [0, 0],
                backgroundColor: [
                    'rgba(76, 175, 80, 0.8)',
                    'rgba(255, 152, 0, 0.8)'
                ],
                borderColor: [
                    'rgba(76, 175, 80, 1)',
                    'rgba(255, 152, 0, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Update charts with data
function updateCharts(stats) {
    // Update revenue chart
    charts.revenue.data.datasets[0].data = [
        stats.total_revenue,
        stats.total_costs,
        stats.total_profit
    ];
    charts.revenue.update();
    
    // Update source chart
    charts.source.data.datasets[0].data = [
        stats.inhouse_revenue,
        stats.outsourced_revenue
    ];
    charts.source.update();
}

// Load products
async function loadProducts() {
    try {
        showLoading('products-table');
        
        const response = await fetch(`${API_BASE}/products/`);
        const products = await response.json();
        
        displayProducts(products);
        
        // Update product dropdowns
        updateProductDropdowns(products);
        
    } catch (error) {
        console.error('Error loading products:', error);
        showAlert('Error loading products', 'error');
    }
}

// Display products
function displayProducts(products) {
    const container = document.getElementById('products-table');
    
    if (products.length === 0) {
        container.innerHTML = '<p>No products found. Add some products to get started!</p>';
        return;
    }
    
    let tableHTML = `
        <table class="table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Source</th>
                    <th>Unit</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    products.forEach(product => {
        tableHTML += `
            <tr>
                <td>${product.id}</td>
                <td><strong>${product.name}</strong></td>
                <td><span class="badge ${product.source === 'inhouse' ? 'badge-success' : 'badge-info'}">${product.source}</span></td>
                <td>${product.unit}</td>
                <td><span class="badge ${product.is_active ? 'badge-success' : 'badge-danger'}">${product.is_active ? 'Active' : 'Inactive'}</span></td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="editProduct(${product.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteProduct(${product.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    tableHTML += '</tbody></table>';
    container.innerHTML = tableHTML;
}

// Load sales data
async function loadSales() {
    try {
        showLoading('sales-table');
        
        const month = document.getElementById('sales-month-filter').value;
        const response = await fetch(`${API_BASE}/monthly-sales/${month}`);
        const sales = await response.json();
        
        displaySales(sales);
        
    } catch (error) {
        console.error('Error loading sales:', error);
        showAlert('Error loading sales data', 'error');
    }
}

// Display sales data
function displaySales(sales) {
    const container = document.getElementById('sales-table');
    
    if (sales.length === 0) {
        container.innerHTML = '<p>No sales data found for this month. Add some sales data!</p>';
        return;
    }
    
    let tableHTML = `
        <table class="table">
            <thead>
                <tr>
                    <th>Product</th>
                    <th>Quantity</th>
                    <th>Sale Price</th>
                    <th>Direct Cost</th>
                    <th>Revenue</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    sales.forEach(sale => {
        const revenue = sale.quantity * sale.sale_price;
        tableHTML += `
            <tr>
                <td><strong>${sale.product_name}</strong></td>
                <td>${sale.quantity} kg</td>
                <td>₹${sale.sale_price}</td>
                <td>₹${sale.direct_cost}</td>
                <td>₹${formatNumber(revenue)}</td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="editSales(${sale.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    tableHTML += '</tbody></table>';
    container.innerHTML = tableHTML;
}

// Load costs
async function loadCosts() {
    try {
        showLoading('costs-table');
        
        const month = document.getElementById('costs-month-filter').value;
        const response = await fetch(`${API_BASE}/costs/${month}`);
        const costs = await response.json();
        
        displayCosts(costs);
        
    } catch (error) {
        console.error('Error loading costs:', error);
        showAlert('Error loading costs', 'error');
    }
}

// Display costs
function displayCosts(costs) {
    const container = document.getElementById('costs-table');
    
    if (costs.length === 0) {
        container.innerHTML = '<p>No costs found for this month. Add some costs!</p>';
        return;
    }
    
    let tableHTML = `
        <table class="table">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Amount</th>
                    <th>Applies To</th>
                    <th>Type</th>
                    <th>Basis</th>
                    <th>Category</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    costs.forEach(cost => {
        tableHTML += `
            <tr>
                <td><strong>${cost.name}</strong></td>
                <td>₹${formatNumber(cost.amount)}</td>
                <td><span class="badge badge-info">${cost.applies_to}</span></td>
                <td>${cost.cost_type}</td>
                <td>${cost.basis}</td>
                <td><span class="badge badge-secondary">${cost.category}</span></td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="editCost(${cost.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteCost(${cost.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    tableHTML += '</tbody></table>';
    container.innerHTML = tableHTML;
}

// Form handlers
function handleProductSubmit(e) {
    e.preventDefault();
    
    const productData = {
        name: document.getElementById('product-name').value,
        source: document.getElementById('product-source').value,
        unit: document.getElementById('product-unit').value,
        extra_info: document.getElementById('product-info').value || null
    };
    
    createProduct(productData);
}

function handleSalesSubmit(e) {
    e.preventDefault();
    
    const salesData = {
        product_id: parseInt(document.getElementById('sales-product').value),
        month: document.getElementById('sales-month').value,
        quantity: parseFloat(document.getElementById('sales-quantity').value),
        sale_price: parseFloat(document.getElementById('sales-price').value),
        direct_cost: parseFloat(document.getElementById('sales-direct-cost').value) || 0
    };
    
    createSales(salesData);
}

function handleCostSubmit(e) {
    e.preventDefault();
    
    const costData = {
        name: document.getElementById('cost-name').value,
        amount: parseFloat(document.getElementById('cost-amount').value),
        applies_to: document.getElementById('cost-applies-to').value,
        cost_type: document.getElementById('cost-type').value,
        basis: document.getElementById('cost-basis').value,
        month: document.getElementById('cost-month').value,
        is_fixed: document.getElementById('cost-fixed').value,
        category: document.getElementById('cost-category').value
    };
    
    createCost(costData);
}

// API calls
async function createProduct(productData) {
    try {
        const response = await fetch(`${API_BASE}/products/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(productData)
        });
        
        if (response.ok) {
            showAlert('Product created successfully!', 'success');
            closeModal('product-modal');
            document.getElementById('product-form').reset();
            loadProducts();
        } else {
            const error = await response.json();
            showAlert(error.detail || 'Error creating product', 'error');
        }
    } catch (error) {
        showAlert('Error connecting to server', 'error');
    }
}

async function createSales(salesData) {
    try {
        const response = await fetch(`${API_BASE}/monthly-sales/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(salesData)
        });
        
        if (response.ok) {
            showAlert('Sales data created successfully!', 'success');
            closeModal('sales-modal');
            document.getElementById('sales-form').reset();
            loadSales();
        } else {
            const error = await response.json();
            showAlert(error.detail || 'Error creating sales data', 'error');
        }
    } catch (error) {
        showAlert('Error connecting to server', 'error');
    }
}

async function createCost(costData) {
    try {
        const response = await fetch(`${API_BASE}/costs/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(costData)
        });
        
        if (response.ok) {
            showAlert('Cost created successfully!', 'success');
            closeModal('cost-modal');
            document.getElementById('cost-form').reset();
            loadCosts();
        } else {
            const error = await response.json();
            showAlert(error.detail || 'Error creating cost', 'error');
        }
    } catch (error) {
        showAlert('Error connecting to server', 'error');
    }
}

// Modal functions
function showProductForm() {
    document.getElementById('product-modal').classList.add('active');
}

function showSalesForm() {
    document.getElementById('sales-modal').classList.add('active');
}

function showCostForm() {
    document.getElementById('cost-modal').classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Update product dropdowns
function updateProductDropdowns(products) {
    const salesProductSelect = document.getElementById('sales-product');
    salesProductSelect.innerHTML = '<option value="">Select Product</option>';
    
    products.forEach(product => {
        if (product.is_active) {
            const option = document.createElement('option');
            option.value = product.id;
            option.textContent = `${product.name} (${product.source})`;
            salesProductSelect.appendChild(option);
        }
    });
}

// Allocation functions
async function runAllocation() {
    const month = document.getElementById('allocation-month').value;
    
    if (!month) {
        showAlert('Please select a month', 'error');
        return;
    }
    
    try {
        showLoading('allocation-results');
        
        const response = await fetch(`${API_BASE}/allocate/${month}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const result = await response.json();
            displayAllocationResults(result);
            showAlert('Allocation completed successfully!', 'success');
        } else {
            const error = await response.json();
            showAlert(error.detail || 'Error running allocation', 'error');
        }
    } catch (error) {
        showAlert('Error connecting to server', 'error');
    }
}

function displayAllocationResults(result) {
    const container = document.getElementById('allocation-results');
    
    let html = `
        <div class="stats-grid" style="margin-bottom: 20px;">
            <div class="stat-card revenue">
                <div class="stat-header">
                    <span class="stat-title">Total Revenue</span>
                    <i class="fas fa-chart-line stat-icon"></i>
                </div>
                <div class="stat-value">₹${formatNumber(result.total_revenue)}</div>
            </div>
            <div class="stat-card costs">
                <div class="stat-header">
                    <span class="stat-title">Total Costs</span>
                    <i class="fas fa-dollar-sign stat-icon"></i>
                </div>
                <div class="stat-value">₹${formatNumber(result.total_costs)}</div>
            </div>
            <div class="stat-card profit">
                <div class="stat-header">
                    <span class="stat-title">Net Profit</span>
                    <i class="fas fa-trophy stat-icon"></i>
                </div>
                <div class="stat-value">₹${formatNumber(result.total_profit)}</div>
            </div>
        </div>
        
        <h3>Product-wise Allocation Results</h3>
        <table class="table">
            <thead>
                <tr>
                    <th>Product</th>
                    <th>Source</th>
                    <th>Qty</th>
                    <th>Price</th>
                    <th>Direct Cost</th>
                    <th>Allocated</th>
                    <th>Total Cost</th>
                    <th>Revenue</th>
                    <th>Profit</th>
                    <th>Margin</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    result.products.forEach(product => {
        html += `
            <tr>
                <td><strong>${product.product_name}</strong></td>
                <td><span class="badge ${product.source === 'inhouse' ? 'badge-success' : 'badge-info'}">${product.source}</span></td>
                <td>${product.quantity} kg</td>
                <td>₹${product.sale_price}</td>
                <td>₹${formatNumber(product.direct_cost)}</td>
                <td>₹${formatNumber(product.allocated_costs)}</td>
                <td>₹${formatNumber(product.total_cost)}</td>
                <td>₹${formatNumber(product.revenue)}</td>
                <td class="${product.profit >= 0 ? 'text-success' : 'text-danger'}">₹${formatNumber(product.profit)}</td>
                <td>${product.profit_margin.toFixed(1)}%</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

// Report functions
async function generateReport() {
    const month = document.getElementById('report-month').value;
    
    if (!month) {
        showAlert('Please select a month', 'error');
        return;
    }
    
    try {
        showLoading('report-results');
        
        const response = await fetch(`${API_BASE}/report/${month}`);
        
        if (response.ok) {
            const result = await response.json();
            displayReportResults(result);
        } else {
            const error = await response.json();
            showAlert(error.detail || 'Error generating report', 'error');
        }
    } catch (error) {
        showAlert('Error connecting to server', 'error');
    }
}

function displayReportResults(result) {
    const container = document.getElementById('report-results');
    
    let html = `
        <div class="stats-grid" style="margin-bottom: 20px;">
            <div class="stat-card revenue">
                <div class="stat-header">
                    <span class="stat-title">Total Revenue</span>
                    <i class="fas fa-chart-line stat-icon"></i>
                </div>
                <div class="stat-value">₹${formatNumber(result.total_revenue)}</div>
            </div>
            <div class="stat-card costs">
                <div class="stat-header">
                    <span class="stat-title">Total Costs</span>
                    <i class="fas fa-dollar-sign stat-icon"></i>
                </div>
                <div class="stat-value">₹${formatNumber(result.total_costs)}</div>
            </div>
            <div class="stat-card profit">
                <div class="stat-header">
                    <span class="stat-title">Net Profit</span>
                    <i class="fas fa-trophy stat-icon"></i>
                </div>
                <div class="stat-value">₹${formatNumber(result.total_profit)}</div>
            </div>
            <div class="stat-card products">
                <div class="stat-header">
                    <span class="stat-title">Profit Margin</span>
                    <i class="fas fa-percentage stat-icon"></i>
                </div>
                <div class="stat-value">${result.profit_margin.toFixed(1)}%</div>
            </div>
        </div>
        
        <h3>Detailed Product Analysis</h3>
        <table class="table">
            <thead>
                <tr>
                    <th>Product</th>
                    <th>Source</th>
                    <th>Qty</th>
                    <th>Price</th>
                    <th>Direct Cost</th>
                    <th>Allocated</th>
                    <th>Total Cost</th>
                    <th>Revenue</th>
                    <th>Profit</th>
                    <th>Margin</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    result.products.forEach(product => {
        html += `
            <tr>
                <td><strong>${product.product_name}</strong></td>
                <td><span class="badge ${product.source === 'inhouse' ? 'badge-success' : 'badge-info'}">${product.source}</span></td>
                <td>${product.quantity} kg</td>
                <td>₹${product.sale_price}</td>
                <td>₹${formatNumber(product.direct_cost)}</td>
                <td>₹${formatNumber(product.allocated_costs)}</td>
                <td>₹${formatNumber(product.total_cost)}</td>
                <td>₹${formatNumber(product.revenue)}</td>
                <td class="${product.profit >= 0 ? 'text-success' : 'text-danger'}">₹${formatNumber(product.profit)}</td>
                <td>${product.profit_margin.toFixed(1)}%</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

// Export functions
async function exportReport() {
    const month = document.getElementById('report-month').value;
    
    if (!month) {
        showAlert('Please select a month', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/export/${month}/csv`);
        const result = await response.json();
        
        if (response.ok) {
            // Create download link
            const link = document.createElement('a');
            link.href = result.download_url;
            link.download = `report_${month}.csv`;
            link.click();
            
            showAlert('Report exported successfully!', 'success');
        } else {
            showAlert('Error exporting report', 'error');
        }
    } catch (error) {
        showAlert('Error exporting report', 'error');
    }
}

// Utility functions
function formatNumber(num) {
    return new Intl.NumberFormat('en-IN').format(num.toFixed(2));
}

function showLoading(containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>Loading...</p>
        </div>
    `;
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        ${message}
    `;
    
    const content = document.querySelector('.content-area');
    content.insertBefore(alertDiv, content.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function refreshData() {
    if (currentTab === 'dashboard') {
        loadDashboardData();
    } else if (currentTab === 'products') {
        loadProducts();
    } else if (currentTab === 'sales') {
        loadSales();
    } else if (currentTab === 'costs') {
        loadCosts();
    }
}

// Placeholder functions for edit/delete operations
function editProduct(id) {
    showAlert('Edit functionality coming soon!', 'info');
}

function deleteProduct(id) {
    if (confirm('Are you sure you want to delete this product?')) {
        showAlert('Delete functionality coming soon!', 'info');
    }
}

function editSales(id) {
    showAlert('Edit functionality coming soon!', 'info');
}

function editCost(id) {
    showAlert('Edit functionality coming soon!', 'info');
}

function deleteCost(id) {
    if (confirm('Are you sure you want to delete this cost?')) {
        showAlert('Delete functionality coming soon!', 'info');
    }
}

function saveSettings() {
    showAlert('Settings saved successfully!', 'success');
}
