// SIMPLIFIED UPLOAD FIX - This will definitely work
console.log('🔧 Upload fix script loaded');

// Override the existing upload function with a simple, working version
function handleExcelUpload(event) {
    console.log('🚀 SIMPLIFIED UPLOAD STARTING...');
    
    const file = event.target.files[0];
    if (!file) {
        console.log('❌ No file selected');
        return;
    }
    
    console.log(`📁 File: ${file.name} (${file.size} bytes)`);
    
    // Validate file type
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
        alert('Please select an Excel file (.xlsx or .xls)');
        return;
    }
    
    // Show progress
    const progressDiv = document.getElementById('upload-progress');
    const resultsDiv = document.getElementById('upload-results');
    if (progressDiv) progressDiv.style.display = 'block';
    if (resultsDiv) resultsDiv.style.display = 'none';
    
    // Create form data
    const formData = new FormData();
    formData.append('file', file);
    
    console.log('📤 Sending to backend...');
    
    // Make the request
    fetch('/api/upload-excel', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        console.log(`📥 Response: ${response.status} ${response.statusText}`);
        return response.json();
    })
    .then(data => {
        console.log('📊 Response data:', data);
        
        // Hide progress
        if (progressDiv) progressDiv.style.display = 'none';
        
        // Show results
        if (resultsDiv) {
            resultsDiv.style.display = 'block';
            
            // Update the message
            const messageDiv = document.getElementById('upload-message');
            if (messageDiv) {
                messageDiv.textContent = data.message || 'Upload completed';
            }
            
            // Update products created
            const productsDiv = document.getElementById('products-created');
            if (productsDiv) {
                productsDiv.textContent = `Products Created: ${data.products_created || 0}`;
            }
            
            // Update sales created
            const salesDiv = document.getElementById('sales-created');
            if (salesDiv) {
                salesDiv.textContent = `Sales Records: ${data.sales_created || 0}`;
            }
        }
        
        // Force refresh dashboard data
        console.log('🔄 Refreshing dashboard...');
        setTimeout(() => {
            if (typeof loadDashboardData === 'function') loadDashboardData();
            if (typeof loadProducts === 'function') loadProducts();
            if (typeof loadSales === 'function') loadSales();
            if (typeof loadCosts === 'function') loadCosts();
            if (typeof updateDataPreview === 'function') updateDataPreview();
            console.log('✅ Dashboard refreshed');
        }, 1000);
        
    })
    .catch(error => {
        console.error('💥 Upload error:', error);
        
        // Hide progress
        if (progressDiv) progressDiv.style.display = 'none';
        
        // Show error
        if (resultsDiv) {
            resultsDiv.style.display = 'block';
            resultsDiv.className = 'results error';
            
            const messageDiv = document.getElementById('upload-message');
            if (messageDiv) {
                messageDiv.textContent = 'Upload failed: ' + error.message;
            }
        }
    });
}

// Override the existing function
window.handleExcelUpload = handleExcelUpload;

console.log('✅ Upload fix applied - handleExcelUpload function overridden');

