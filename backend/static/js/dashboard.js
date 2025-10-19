// Dashboard JavaScript for Fruit & Vegetable Cost Allocation System
const API_BASE = '/api';
let currentTab = 'dashboard';
let charts = {};
let currentData = {};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeSidebar();
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
    
    // Update page title and subtitle
    const titles = {
        'dashboard': { title: 'Dashboard', subtitle: 'Overview & Analytics' },
        'products': { title: 'Products', subtitle: 'Manage Your Inventory' },
        'sales': { title: 'Sales', subtitle: 'Track Monthly Sales Data' },
        'costs': { title: 'Costs', subtitle: 'Manage Operational Costs' },
        'allocation': { title: 'Allocation', subtitle: 'Cost Distribution Analysis' },
        'reports': { title: 'Reports', subtitle: 'Generate & Export Reports' },
        'settings': { title: 'Settings', subtitle: 'System Configuration' }
    };
    
    const tabInfo = titles[tabName] || { title: 'Dashboard', subtitle: 'Overview & Analytics' };
    document.getElementById('page-title').textContent = tabInfo.title;
    document.getElementById('page-subtitle').textContent = tabInfo.subtitle;
    
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
            <tr data-sale-id="${sale.id}">
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
    // Reset to "Add" mode
    document.getElementById('product-modal-title').textContent = 'Add Product';
    document.getElementById('product-form').removeAttribute('data-edit-id');
    document.getElementById('product-form').reset();
    document.getElementById('product-modal').classList.add('active');
}

function showSalesForm() {
    // Reset to "Add" mode
    document.getElementById('sales-modal-title').textContent = 'Add Sales Data';
    document.getElementById('sales-form').removeAttribute('data-edit-id');
    document.getElementById('sales-form').reset();
    document.getElementById('sales-modal').classList.add('active');
}

function showCostForm() {
    // Reset to "Add" mode
    document.getElementById('cost-modal-title').textContent = 'Add Cost';
    document.getElementById('cost-form').removeAttribute('data-edit-id');
    document.getElementById('cost-form').reset();
    document.getElementById('cost-modal').classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
    // Reset forms when closing
    if (modalId === 'product-modal') {
        document.getElementById('product-form').reset();
        document.getElementById('product-form').removeAttribute('data-edit-id');
        // Reset title to "Add Product"
        document.getElementById('product-modal-title').textContent = 'Add Product';
    } else if (modalId === 'sales-modal') {
        document.getElementById('sales-form').reset();
        document.getElementById('sales-form').removeAttribute('data-edit-id');
        // Reset title to "Add Sales Data"
        document.getElementById('sales-modal-title').textContent = 'Add Sales Data';
    } else if (modalId === 'cost-modal') {
        document.getElementById('cost-form').reset();
        document.getElementById('cost-form').removeAttribute('data-edit-id');
        // Reset title to "Add Cost"
        document.getElementById('cost-modal-title').textContent = 'Add Cost';
    }
}

// Form submission functions
async function submitProductForm(event) {
    event.preventDefault();
    
    const formData = {
        name: document.getElementById('product-name').value,
        source: document.getElementById('product-source').value,
        unit: document.getElementById('product-unit').value,
        extra_info: document.getElementById('product-info').value
    };
    
    const editId = document.getElementById('product-form').getAttribute('data-edit-id');
    const isEdit = editId !== null;
    
    try {
        const url = isEdit ? `${API_BASE}/products/${editId}` : `${API_BASE}/products/`;
        const method = isEdit ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            showAlert(`Product ${isEdit ? 'updated' : 'added'} successfully!`, 'success');
            closeModal('product-modal');
            loadProducts();
        } else {
            const error = await response.json();
            showAlert(`Error: ${error.detail}`, 'error');
        }
    } catch (error) {
        showAlert(`Error ${isEdit ? 'updating' : 'adding'} product`, 'error');
    }
}

async function submitSalesForm(event) {
    event.preventDefault();
    
    const formData = {
        product_id: parseInt(document.getElementById('sales-product').value),
        month: document.getElementById('sales-month').value,
        quantity: parseFloat(document.getElementById('sales-quantity').value),
        sale_price: parseFloat(document.getElementById('sales-price').value),
        direct_cost: parseFloat(document.getElementById('sales-direct-cost').value)
    };
    
    const editId = document.getElementById('sales-form').getAttribute('data-edit-id');
    const isEdit = editId !== null;
    
    try {
        const url = isEdit ? `${API_BASE}/monthly-sales/${editId}` : `${API_BASE}/monthly-sales/`;
        const method = isEdit ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            showAlert(`Sales ${isEdit ? 'updated' : 'added'} successfully!`, 'success');
            closeModal('sales-modal');
            loadSales();
        } else {
            const error = await response.json();
            showAlert(`Error: ${error.detail}`, 'error');
        }
    } catch (error) {
        showAlert(`Error ${isEdit ? 'updating' : 'adding'} sales`, 'error');
    }
}

async function submitCostForm(event) {
    event.preventDefault();
    
    const formData = {
        name: document.getElementById('cost-name').value,
        amount: parseFloat(document.getElementById('cost-amount').value),
        applies_to: document.getElementById('cost-applies-to').value,
        cost_type: document.getElementById('cost-type').value,
        basis: document.getElementById('cost-basis').value,
        month: document.getElementById('cost-month').value,
        category: document.getElementById('cost-category').value,
        is_fixed: document.getElementById('cost-fixed').value
    };
    
    const editId = document.getElementById('cost-form').getAttribute('data-edit-id');
    const isEdit = editId !== null;
    
    try {
        const url = isEdit ? `${API_BASE}/costs/${editId}` : `${API_BASE}/costs/`;
        const method = isEdit ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            showAlert(`Cost ${isEdit ? 'updated' : 'added'} successfully!`, 'success');
            closeModal('cost-modal');
            loadCosts();
        } else {
            const error = await response.json();
            showAlert(`Error: ${error.detail}`, 'error');
        }
    } catch (error) {
        showAlert(`Error ${isEdit ? 'updating' : 'adding'} cost`, 'error');
    }
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

// Edit/Delete functions
async function editProduct(id) {
    try {
        const response = await fetch(`${API_BASE}/products/${id}`);
        if (response.ok) {
            const product = await response.json();
            
            // Change title to "Edit Product"
            document.getElementById('product-modal-title').textContent = 'Edit Product';
            
            // Populate form with existing data
            document.getElementById('product-name').value = product.name;
            document.getElementById('product-source').value = product.source;
            document.getElementById('product-unit').value = product.unit;
            document.getElementById('product-info').value = product.extra_info || '';
            
            // Store the ID for update
            document.getElementById('product-form').setAttribute('data-edit-id', id);
            
            // Show the modal
            document.getElementById('product-modal').classList.add('active');
        } else {
            showAlert('Error loading product data', 'error');
        }
    } catch (error) {
        showAlert('Error loading product data', 'error');
    }
}

async function deleteProduct(id) {
    if (confirm('Are you sure you want to delete this product?')) {
        try {
            const response = await fetch(`${API_BASE}/products/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                showAlert('Product deleted successfully!', 'success');
                loadProducts();
            } else {
                showAlert('Error deleting product', 'error');
            }
        } catch (error) {
            showAlert('Error deleting product', 'error');
        }
    }
}

async function editSales(id) {
    try {
        // Get data from the table row instead of API call
        const row = document.querySelector(`tr[data-sale-id="${id}"]`);
        if (!row) {
            showAlert('Sales data not found in table', 'error');
            return;
        }
        
        // Extract data from table row
        const cells = row.querySelectorAll('td');
        const productName = cells[0].textContent.trim();
        const quantity = parseFloat(cells[1].textContent.replace(' kg', ''));
        const salePrice = parseFloat(cells[2].textContent.replace('₹', ''));
        const directCost = parseFloat(cells[3].textContent.replace('₹', ''));
        
        // Get product ID from the product name
        const productSelect = document.getElementById('sales-product');
        let productId = '';
        for (let option of productSelect.options) {
            if (option.textContent.trim() === productName) {
                productId = option.value;
                break;
            }
        }
        
        // Change title to "Edit Sales Data"
        document.getElementById('sales-modal-title').textContent = 'Edit Sales Data';
        
        // Populate form with existing data
        document.getElementById('sales-product').value = productId;
        document.getElementById('sales-month').value = '2025-10'; // Default month
        document.getElementById('sales-quantity').value = quantity;
        document.getElementById('sales-price').value = salePrice;
        document.getElementById('sales-direct-cost').value = directCost;
        
        // Store the ID for update
        document.getElementById('sales-form').setAttribute('data-edit-id', id);
        
        // Show the modal
        document.getElementById('sales-modal').classList.add('active');
    } catch (error) {
        showAlert('Error loading sales data', 'error');
    }
}

async function editCost(id) {
    try {
        const response = await fetch(`${API_BASE}/costs/id/${id}`);
        if (response.ok) {
            const cost = await response.json();
            
            // Change title to "Edit Cost"
            document.getElementById('cost-modal-title').textContent = 'Edit Cost';
            
            // Populate form with existing data
            document.getElementById('cost-name').value = cost.name;
            document.getElementById('cost-amount').value = cost.amount;
            document.getElementById('cost-applies-to').value = cost.applies_to;
            document.getElementById('cost-type').value = cost.cost_type;
            document.getElementById('cost-basis').value = cost.basis;
            document.getElementById('cost-month').value = cost.month;
            document.getElementById('cost-category').value = cost.category;
            document.getElementById('cost-fixed').value = cost.is_fixed;
            
            // Store the ID for update
            document.getElementById('cost-form').setAttribute('data-edit-id', id);
            
            // Show the modal
            document.getElementById('cost-modal').classList.add('active');
        } else {
            showAlert('Error loading cost data', 'error');
        }
    } catch (error) {
        showAlert('Error loading cost data', 'error');
    }
}

async function deleteCost(id) {
    if (confirm('Are you sure you want to delete this cost?')) {
        try {
            const response = await fetch(`${API_BASE}/costs/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                showAlert('Cost deleted successfully!', 'success');
                loadCosts();
            } else {
                showAlert('Error deleting cost', 'error');
            }
        } catch (error) {
            showAlert('Error deleting cost', 'error');
        }
    }
}

function saveSettings() {
    showAlert('Settings saved successfully!', 'success');
}

// Reset database functionality
async function resetDatabase() {
    if (confirm('⚠️ WARNING: This will permanently delete ALL data from the database!\n\nThis action cannot be undone. Are you sure you want to continue?')) {
        if (confirm('🚨 FINAL CONFIRMATION: This will delete ALL products, sales, costs, and allocations!\n\nType "RESET" to confirm (case sensitive):')) {
            const confirmation = prompt('Type "RESET" to confirm database reset:');
            if (confirmation === 'RESET') {
                try {
                    showAlert('Resetting database...', 'info');
                    
                    const response = await fetch(`${API_BASE}/reset-database`, {
                        method: 'POST'
                    });
                    
                    if (response.ok) {
                        showAlert('Database reset successfully! All data has been cleared.', 'success');
                        
                        // Refresh all data
                        loadDashboardData();
                        loadProducts();
                        loadSales();
                        loadCosts();
                        
                        // Clear any charts
                        if (charts.revenueChart) {
                            charts.revenueChart.destroy();
                        }
                        if (charts.sourceChart) {
                            charts.sourceChart.destroy();
                        }
                        
                    } else {
                        showAlert('Error resetting database', 'error');
                    }
                } catch (error) {
                    showAlert('Error resetting database: ' + error.message, 'error');
                }
            } else {
                showAlert('Reset cancelled - confirmation text did not match', 'warning');
            }
        } else {
            showAlert('Reset cancelled', 'info');
        }
    } else {
        showAlert('Reset cancelled', 'info');
    }
}

// Sidebar toggle functionality
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (sidebar && mainContent) {
        sidebar.classList.toggle('collapsed');
        mainContent.classList.toggle('sidebar-collapsed');
        
        // Store the state in localStorage
        const isCollapsed = sidebar.classList.contains('collapsed');
        localStorage.setItem('sidebarCollapsed', isCollapsed);
    }
}

// Initialize sidebar state from localStorage
function initializeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');
    const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    
    if (sidebar && mainContent) {
        if (isCollapsed) {
            sidebar.classList.add('collapsed');
            mainContent.classList.add('sidebar-collapsed');
        }
    }
}
