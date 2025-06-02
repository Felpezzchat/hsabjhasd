// app/scripts/renderer.js
document.addEventListener('DOMContentLoaded', () => {
  const messageDiv = document.getElementById('message');
  if (messageDiv) {
    messageDiv.textContent = 'Electron Frontend Initialized. API server should be running at http://localhost:5001';
    messageDiv.style.display = 'block';
  }

  setupNavigation();
  loadView('dashboard'); // Load initial view
});

function setupNavigation() {
    const navLinks = {
        'nav-dashboard': 'dashboard',
        'nav-appointments': 'appointments',
        'nav-clients': 'clients',
        'nav-services': 'services',
        'nav-products': 'products',
        'nav-settings': 'settings'
    };

    for (const [navId, viewName] of Object.entries(navLinks)) {
        const element = document.getElementById(navId);
        if (element) {
            element.addEventListener('click', (e) => {
                e.preventDefault();
                loadView(viewName);
                setActiveNav(e.target);
            });
        } else {
            console.warn(`Navigation element with ID '${navId}' not found.`);
        }
    }
}

function setActiveNav(target) {
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => link.classList.remove('active'));
    if (target) {
        target.classList.add('active');
    }
}

async function loadView(viewName) {
    console.log(`Loading view: ${viewName}`);
    const mainContentArea = document.getElementById('main-content-area');
    if (!mainContentArea) {
        console.error("Element with ID 'main-content-area' not found!");
        return;
    }

    mainContentArea.innerHTML = ''; 
    const messageDiv = document.getElementById('message');
    if (messageDiv) messageDiv.style.display = 'none';

    if (viewName === 'dashboard') {
        mainContentArea.innerHTML = '<div class="p-5 mb-4 bg-light rounded-3"><div class="container-fluid py-5"> <h1 class="display-5 fw-bold">Dashboard</h1> <p class="col-md-8 fs-4">Overview of salon activities, upcoming appointments, and key metrics will be displayed here.</p></div></div>';
    } else if (viewName === 'appointments') {
        await loadHtmlIntoMainContent('./views/appointments-view.html', mainContentArea, setupAppointmentsView);
    } else if (viewName === 'clients') {
        await loadHtmlIntoMainContent('./views/clients-view.html', mainContentArea, setupClientsView); // This will now include photo modal setup
    } else if (viewName === 'services') {
        await loadHtmlIntoMainContent('./views/services-view.html', mainContentArea, setupServicesView);
    } else if (viewName === 'products') {
        await loadHtmlIntoMainContent('./views/products-view.html', mainContentArea, setupProductsView);
    } else if (viewName === 'settings') {
        mainContentArea.innerHTML = '<h1>Settings</h1><p>Configure application settings. (Functionality to be implemented)</p>';
    } else {
        mainContentArea.innerHTML = '<h1>Page Not Found</h1><p>The requested view could not be found.</p>';
    }
    // if (typeof feather !== 'undefined') { feather.replace(); } // For Feather Icons
}

async function loadHtmlIntoMainContent(filePath, targetElement, callback) {
    try {
        const response = await fetch(filePath);
        if (!response.ok) throw new Error(`Failed to load HTML from ${filePath}: ${response.statusText}`);
        targetElement.innerHTML = await response.text();
        if (callback && typeof callback === 'function') {
            callback(); 
        }
    } catch (error) {
        targetElement.innerHTML = `<div class="alert alert-danger" role="alert">Error loading view: ${error.message}</div>`;
        console.error('Error loading HTML:', error);
    }
}

// --- Client Management Specific Functions (Now includes Photo Management) ---
let clientModalInstance = null; 
let clientPhotosModalInstance = null; // For the new photos modal

function setupClientsView() {
    console.log("Setting up Clients View...");
    populateClientsTable(); 

    const addClientBtn = document.getElementById('addClientBtn');
    if (addClientBtn) addClientBtn.addEventListener('click', openClientModalForAdd);
    
    const clientForm = document.getElementById('clientForm');
    if (clientForm) clientForm.addEventListener('submit', handleSaveClient);
    
    const clientModalElement = document.getElementById('clientModal');
    if (clientModalElement && !clientModalInstance) { // Initialize if not already
        clientModalInstance = new bootstrap.Modal(clientModalElement);
    }
    
    // Initialize Client Photos Modal
    const clientPhotosModalElement = document.getElementById('clientPhotosModal');
    if (clientPhotosModalElement && !clientPhotosModalInstance) { // Initialize if not already
         clientPhotosModalInstance = new bootstrap.Modal(clientPhotosModalElement);
    }
    const photoUploadForm = document.getElementById('photoUploadForm');
    if (photoUploadForm) {
        photoUploadForm.addEventListener('submit', handlePhotoUpload);
    }
    // if (typeof feather !== 'undefined') { feather.replace(); }
}

async function populateClientsTable() {
    const tableBody = document.getElementById('clientsTableBody');
    if (!tableBody) { console.error("Client table body not found!"); return; }
    tableBody.innerHTML = '<tr><td colspan="5" class="text-center">Loading clients...</td></tr>'; 
    try {
        const response = await fetch('http://localhost:5001/api/clients');
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({error: "Unknown server error"}));
            throw new Error(`HTTP error ${response.status}: ${errorData.error || response.statusText}`);
        }
        const clients = await response.json();
        tableBody.innerHTML = '';
        if (clients.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" class="text-center">No clients found. Add one!</td></tr>';
            return;
        }
        clients.forEach(client => {
            const row = tableBody.insertRow();
            row.insertCell().textContent = client.id;
            row.insertCell().textContent = client.name;
            row.insertCell().textContent = client.email || 'N/A';
            row.insertCell().textContent = client.phone || 'N/A';
            const actionsCell = row.insertCell();
            actionsCell.classList.add('text-end', 'text-nowrap');
            // Use JSON.stringify carefully, escape characters for HTML attribute
            const clientJsonString = JSON.stringify(client).replace(/"/g, '&quot;');
            actionsCell.innerHTML = `
                <button class="btn btn-sm btn-outline-secondary me-1" onclick="openClientModalForEdit(${clientJsonString})">Edit Info</button>
                <button class="btn btn-sm btn-outline-info me-1" onclick="openClientPhotosModal(${clientJsonString})">Photos</button>
                <button class="btn btn-sm btn-outline-danger" onclick="handleDeleteClient(${client.id}, '${client.name.replace(/'/g, "\\'")}')">Delete Client</button>
            `;
        });
    } catch (error) {
        console.error('Failed to fetch clients:', error);
        tableBody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">Error fetching clients: ${error.message}</td></tr>`;
    }
}

function openClientModalForAdd() { /* ... (same as before) ... */ if (!clientModalInstance) return; document.getElementById('clientForm').reset(); document.getElementById('clientId').value = ''; document.getElementById('clientModalLabel').textContent = 'Add New Client'; displayClientFormAlert(null); clientModalInstance.show(); }
function openClientModalForEdit(client) { /* ... (same as before) ... */ if (!clientModalInstance) return; document.getElementById('clientForm').reset(); displayClientFormAlert(null); document.getElementById('clientId').value = client.id; document.getElementById('clientModalLabel').textContent = `Edit Client - ${client.name}`; document.getElementById('clientNameModal').value = client.name || ''; document.getElementById('clientEmailModal').value = client.email || ''; document.getElementById('clientPhoneModal').value = client.phone || ''; document.getElementById('clientAddressModal').value = client.address || ''; document.getElementById('clientNotesModal').value = client.notes || ''; clientModalInstance.show(); }
async function handleSaveClient(event) { /* ... (same as before, with saveButton logic) ... */ event.preventDefault(); displayClientFormAlert(null); const clientId = document.getElementById('clientId').value; const clientData = { name: document.getElementById('clientNameModal').value.trim(), email: document.getElementById('clientEmailModal').value.trim(), phone: document.getElementById('clientPhoneModal').value.trim(), address: document.getElementById('clientAddressModal').value.trim(), notes: document.getElementById('clientNotesModal').value.trim(), }; if (!clientData.name) { displayClientFormAlert("Client name is required.", "warning"); return; } const url = clientId ? `http://localhost:5001/api/clients/${clientId}` : 'http://localhost:5001/api/clients'; const method = clientId ? 'PUT' : 'POST'; const saveButton = document.getElementById('saveClientBtn'); saveButton.disabled = true; saveButton.innerHTML = clientId ? 'Saving...' : 'Adding...'; try { const response = await fetch(url, { method: method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(clientData), }); const responseData = await response.json(); if (!response.ok) throw new Error(responseData.error || responseData.details || `HTTP error ${response.status}`); displayClientFormAlert(`Client ${clientId ? 'updated' : 'added'} successfully!`, "success"); await populateClientsTable(); setTimeout(() => { if (clientModalInstance) clientModalInstance.hide(); displayClientFormAlert(null); }, 1500); } catch (error) { console.error('Failed to save client:', error); displayClientFormAlert(`Error: ${error.message}`, "danger"); } finally { saveButton.disabled = false; saveButton.innerHTML = 'Save Client'; } }
async function handleDeleteClient(clientId, clientName) { /* ... (same as before, with showTemporaryAlert) ... */ if (confirm(`Are you sure you want to delete client "${clientName}" (ID: ${clientId})?`)) { try { const response = await fetch(`http://localhost:5001/api/clients/${clientId}`, { method: 'DELETE' }); if (!response.ok) { const rd = await response.json().catch(()=>({})); throw new Error(rd.error||rd.details||`HTTP error ${response.status}`); } showTemporaryAlert(`Client "${clientName}" deleted successfully.`, 'success'); await populateClientsTable(); } catch (error) { console.error('Failed to delete client:', error); showTemporaryAlert(`Error deleting client: ${error.message}`, 'danger'); } } }
function displayClientFormAlert(message, type = 'danger', autoHide = false) { /* ... (same as before) ... */ const alertDiv = document.getElementById('clientFormAlert'); if (!alertDiv) return; if (!message) { alertDiv.style.display = 'none'; alertDiv.className = 'alert mt-3'; return; } alertDiv.textContent = message; alertDiv.className = `alert alert-${type} mt-3`; alertDiv.style.display = 'block'; if (autoHide) setTimeout(() => { alertDiv.style.display = 'none'; }, 3000); }

// --- Client Photo Management Functions ---
async function openClientPhotosModal(client) {
    if (!clientPhotosModalInstance) { console.error("Client Photos Modal not initialized."); return; }
    document.getElementById('photosModalClientId').value = client.id;
    document.getElementById('photosModalClientName').textContent = client.name;
    document.getElementById('photoUploadForm').reset();
    displayPhotoUploadAlert(null);
    
    await loadClientPhotos(client.id);
    clientPhotosModalInstance.show();
}

async function loadClientPhotos(clientId) {
    const container = document.getElementById('existingPhotosContainer');
    const noPhotosMsg = document.getElementById('noPhotosMessage');
    container.innerHTML = ''; // Clear previous photos
    noPhotosMsg.textContent = 'Loading photos...';
    noPhotosMsg.style.display = 'block';

    try {
        const response = await fetch(`http://localhost:5001/api/clients/${clientId}/photos`);
        if (!response.ok) throw new Error(`Failed to fetch photos: ${response.statusText}`);
        const photos = await response.json();

        if (photos.length === 0) {
            noPhotosMsg.textContent = 'No photos uploaded yet for this client.';
            return;
        }
        noPhotosMsg.style.display = 'none'; // Hide message if photos exist
        
        photos.forEach(photo => {
            const col = document.createElement('div');
            col.classList.add('col');
            const card = document.createElement('div');
            card.classList.add('card', 'h-100', 'shadow-sm');
            
            const img = document.createElement('img');
            // Use the image_url provided by the backend (which points to /api/photos/...)
            img.src = photo.image_url || `http://localhost:5001/api/photos/${photo.image_path}`; 
            img.classList.add('card-img-top');
            img.alt = photo.description || photo.photo_type || 'Client Photo';
            img.style.height = '180px'; 
            img.style.objectFit = 'cover';
            img.onerror = () => { img.alt = 'Error loading image'; img.src = './assets/placeholder-image.png'; }; // Placeholder on error

            const cardBody = document.createElement('div');
            cardBody.classList.add('card-body', 'p-2');
            
            const typeText = document.createElement('p');
            typeText.classList.add('card-text', 'mb-1');
            typeText.innerHTML = `<small class="text-muted">Type:</small> <strong>${photo.photo_type || 'N/A'}</strong>`;
            
            const descText = document.createElement('p');
            descText.classList.add('card-text', 'small', 'mb-1');
            descText.innerHTML = `<small class="text-muted">Desc:</small> ${photo.description || 'No description.'}`;
            
            const deletePhotoBtn = document.createElement('button');
            deletePhotoBtn.classList.add('btn', 'btn-sm', 'btn-outline-danger', 'mt-2', 'w-100');
            deletePhotoBtn.textContent = 'Delete Photo';
            deletePhotoBtn.onclick = () => handleDeleteClientPhoto(photo.id, clientId, photo.image_path);

            cardBody.appendChild(typeText);
            cardBody.appendChild(descText);
            cardBody.appendChild(deletePhotoBtn);
            card.appendChild(img);
            card.appendChild(cardBody);
            col.appendChild(card);
            container.appendChild(col);
        });

    } catch (error) {
        console.error("Error loading client photos:", error);
        noPhotosMsg.textContent = `Error loading photos: ${error.message}`;
        noPhotosMsg.classList.add('text-danger');
    }
}

async function handlePhotoUpload(event) {
    event.preventDefault();
    const form = event.target;
    const clientId = document.getElementById('photosModalClientId').value;
    const photoFile = document.getElementById('photoFile').files[0];
    const photoType = document.getElementById('photoType').value;
    const photoDescription = document.getElementById('photoDescription').value;

    if (!photoFile) {
        displayPhotoUploadAlert("Please select a photo file.", "warning");
        return;
    }

    const formData = new FormData();
    formData.append('photo', photoFile);
    formData.append('photo_type', photoType);
    formData.append('description', photoDescription);
    
    displayPhotoUploadAlert("Uploading...", "info");
    const uploadButton = form.querySelector('button[type="submit"]');
    uploadButton.disabled = true;

    try {
        const response = await fetch(`http://localhost:5001/api/clients/${clientId}/photos`, {
            method: 'POST', body: formData,
        });
        const responseData = await response.json();
        if (!response.ok) throw new Error(responseData.error || responseData.details || `HTTP error ${response.status}`);
        
        displayPhotoUploadAlert("Photo uploaded successfully!", "success", true);
        form.reset(); 
        await loadClientPhotos(clientId);
    } catch (error) {
        console.error("Photo upload failed:", error);
        displayPhotoUploadAlert(`Upload failed: ${error.message}`, "danger");
    } finally {
        uploadButton.disabled = false;
    }
}

async function handleDeleteClientPhoto(photoId, clientId, photoPathForLog = 'N/A') {
    if (confirm(`Are you sure you want to delete this photo (ID: ${photoId})?`)) {
        try {
            const response = await fetch(`http://localhost:5001/api/clients/photos/${photoId}`, { method: 'DELETE' });
            const responseData = await response.json();
            if (!response.ok && response.status !== 207) { // 207 is partial success (DB deleted, file not)
                throw new Error(responseData.error || responseData.details || `HTTP error ${response.status}`);
            }
            showTemporaryAlert(responseData.message || "Photo deletion process completed.", response.status === 207 ? "warning" : "success");
            await loadClientPhotos(clientId); // Refresh photo list
        } catch (error) {
            console.error(`Error deleting photo ID ${photoId} (Path: ${photoPathForLog}):`, error);
            showTemporaryAlert(`Failed to delete photo: ${error.message}`, 'danger');
        }
    }
}

function displayPhotoUploadAlert(message, type = 'info', autoDismiss = false) {
    const alertDiv = document.getElementById('photoUploadAlert');
    if (!alertDiv) return;
    if (!message) { alertDiv.style.display = 'none'; alertDiv.className = 'alert mt-2'; return; }
    alertDiv.textContent = message;
    alertDiv.className = `alert alert-${type} mt-2`;
    alertDiv.style.display = 'block';
    if (autoDismiss) setTimeout(() => { alertDiv.style.display = 'none'; }, 3000);
}

// --- Service Management (condensed) ---
let serviceModalInstance = null;
function setupServicesView() { /* ... (same as before) ... */ }
async function populateServicesTable() { /* ... (same as before) ... */ }
function openServiceModalForAdd() { /* ... (same as before) ... */ }
function openServiceModalForEdit(service) { /* ... (same as before) ... */ }
async function handleSaveService(event) { /* ... (same as before) ... */ }
async function handleDeleteService(serviceId, serviceName) { /* ... (same as before) ... */ }
async function handleToggleServiceActive(serviceId, setActive) { /* ... (same as before) ... */ }
function displayServiceFormAlert(message, type = 'danger', autoHide = false) { /* ... (same as before) ... */ }

// --- Appointment Management (condensed) ---
let appointmentModalInstance = null;
let allServicesCache = [];
function setupAppointmentsView() { /* ... (same as before) ... */ }
async function populateAppointmentsTable() { /* ... (same as before) ... */ }
function getStatusBadgeClass(status) { /* ... (same as before) ... */ }
async function populateAppointmentModalDropdowns(selectedCustomerId = null, selectedServiceId = null) { /* ... (same as before) ... */ }
function updatePriceOnServiceChangeInModal() { /* ... (same as before) ... */ }
async function openAppointmentModalForAdd() { /* ... (same as before) ... */ }
async function openAppointmentModalForEdit(appointment) { /* ... (same as before) ... */ }
async function handleSaveAppointment(event) { /* ... (same as before) ... */ }
async function handleDeleteAppointment(appointmentId) { /* ... (same as before) ... */ }
function displayAppointmentFormAlert(message, type = 'danger', autoHide = false) { /* ... (same as before) ... */ }

// --- Product Management (condensed) ---
let productModalInstance = null;
function setupProductsView() { /* ... (same as before) ... */ }
async function populateProductsTable() { /* ... (same as before) ... */ }
function openProductModalForAdd() { /* ... (same as before) ... */ }
function openProductModalForEdit(product) { /* ... (same as before) ... */ }
async function handleSaveProduct(event) { /* ... (same as before) ... */ }
async function handleDeleteProduct(productId, productName) { /* ... (same as before) ... */ }
function displayProductFormAlert(message, type = 'danger', autoHide = false) { /* ... (same as before) ... */ }

// --- Utility Functions ---
function showTemporaryAlert(message, type = 'info', duration = 3500) { // Increased duration slightly
    const alertContainer = document.body; // Append to body to ensure visibility over modals
    
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show p-3`; // Added padding
    alertElement.role = 'alert';
    // Fixed-top styling for general alerts
    alertElement.style.position = 'fixed';
    alertElement.style.top = '1rem';
    alertElement.style.right = '1rem'; // Position to top-right
    alertElement.style.zIndex = '1060'; // Higher than Bootstrap modals (1050-1055)
    alertElement.style.minWidth = '250px'; // Ensure readability
    alertElement.style.maxWidth = '90%';

    alertElement.innerHTML = `${message} <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;
    
    alertContainer.appendChild(alertElement);

    setTimeout(() => {
        const alertInstance = bootstrap.Alert.getOrCreateInstance(alertElement);
        if (alertInstance) {
            alertInstance.close();
        } else if (alertElement.parentNode) { // Fallback if instance not found (e.g. element removed by other means)
            alertElement.remove();
        }
    }, duration);
}

// Example of using an exposed API from preload.js for testing IPC
async function testElectronGetAppPath() {
  if (window.electronAPI && window.electronAPI.invoke) {
    try {
      const appPath = await window.electronAPI.invoke('get-app-path');
      console.log('App Path from main process via IPC invoke:', appPath);
      const messageDiv = document.getElementById('message');
      if (messageDiv && !messageDiv.textContent.includes('App Path')) {
            messageDiv.textContent += ` | App Path (IPC): ${appPath}`;
            messageDiv.style.display = 'block';
      }
    } catch (error) { console.error('Error invoking get-app-path:', error); }
  } else { console.warn('electronAPI.invoke or get-app-path not found.'); }
}
// testElectronGetAppPath();
