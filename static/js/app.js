/**
 * Rotax Pro Jet - Main JavaScript
 * 
 * This file contains all the client-side functionality for the Rotax Pro Jet web application.
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
  // Initialize the application
  initApp();
});

/**
 * Initialize the application
 */
function initApp() {
  // Set up event listeners
  setupEventListeners();
  
  // Initialize UI components
  initTooltips();
  initPopovers();
  
  // Check if we're on the calculator page
  if (document.getElementById('calculator-tabs')) {
    initCalculator();
  }
  
  // Check if we're on the settings page
  if (document.querySelector('.delete-setting')) {
    initSettingsPage();
  }
  
  // Check if we're on the pricing page
  if (document.getElementById('billingToggle')) {
    initPricingPage();
  }
}

/**
 * Set up event listeners for various UI elements
 */
function setupEventListeners() {
  // Mobile menu toggle
  const navbarToggler = document.querySelector('.navbar-toggler');
  if (navbarToggler) {
    navbarToggler.addEventListener('click', function() {
      const navbarCollapse = document.querySelector('.navbar-collapse');
      navbarCollapse.classList.toggle('show');
    });
  }
  
  // Contact form submission
  const contactForm = document.getElementById('contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // In a real implementation, we would send the form data to the server
      // For now, we'll just show a success message
      const successModal = new bootstrap.Modal(document.getElementById('successModal'));
      successModal.show();
      
      // Reset form
      contactForm.reset();
    });
  }
}

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function(tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
}

/**
 * Initialize Bootstrap popovers
 */
function initPopovers() {
  const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
  popoverTriggerList.map(function(popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
  });
}

/**
 * Initialize the calculator functionality
 */
function initCalculator() {
  // Toggle reference conditions inputs
  const useCustomRef = document.getElementById('use-custom-reference');
  if (useCustomRef) {
    useCustomRef.addEventListener('change', function() {
      const refInputs = document.getElementById('reference-conditions-inputs');
      if (this.checked) {
        refInputs.style.display = 'block';
      } else {
        refInputs.style.display = 'none';
      }
    });
  }
  
  // Current location button
  const currentLocationBtn = document.getElementById('current-location-btn');
  if (currentLocationBtn) {
    currentLocationBtn.addEventListener('click', getCurrentLocation);
  }
  
  // Search button
  const searchBtn = document.getElementById('search-btn');
  if (searchBtn) {
    searchBtn.addEventListener('click', searchLocations);
  }
  
  // Track search input
  const trackSearch = document.getElementById('track-search');
  if (trackSearch) {
    trackSearch.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        searchLocations();
      }
    });
  }
  
  // Calculate button
  const calculateBtn = document.getElementById('calculate-btn');
  if (calculateBtn) {
    calculateBtn.addEventListener('click', calculateJetting);
  }
  
  // Save settings button
  const saveSettingsBtn = document.getElementById('save-settings-btn');
  if (saveSettingsBtn) {
    saveSettingsBtn.addEventListener('click', showSaveSettingsModal);
  }
  
  // Save settings confirm button
  const saveSettingsConfirm = document.getElementById('save-settings-confirm');
  if (saveSettingsConfirm) {
    saveSettingsConfirm.addEventListener('click', saveSettings);
  }
  
  // Check URL parameters for loading saved settings
  const urlParams = new URLSearchParams(window.location.search);
  const loadSettingId = urlParams.get('load');
  if (loadSettingId) {
    loadSavedSetting(loadSettingId);
  }
}

/**
 * Get the user's current location
 */
function getCurrentLocation() {
  const button = document.getElementById('current-location-btn');
  const originalText = button.innerHTML;
  
  button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Getting location...';
  button.disabled = true;
  
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      // Success callback
      function(position) {
        const latitude = position.coords.latitude;
        const longitude = position.coords.longitude;
        
        // Fetch weather and location data
        fetchWeatherData(latitude, longitude)
          .then(data => {
            displaySelectedLocation(data);
            
            // Reset button
            button.innerHTML = originalText;
            button.disabled = false;
          })
          .catch(error => {
            console.error('Error fetching weather data:', error);
            alert('Error fetching weather data. Please try again or enter location manually.');
            
            // Reset button
            button.innerHTML = originalText;
            button.disabled = false;
          });
      },
      // Error callback
      function(error) {
        console.error('Geolocation error:', error);
        alert('Unable to get your location. Please allow location access or enter location manually.');
        
        // Reset button
        button.innerHTML = originalText;
        button.disabled = false;
      }
    );
  } else {
    alert('Geolocation is not supported by your browser. Please enter location manually.');
    button.innerHTML = originalText;
    button.disabled = false;
  }
}

/**
 * Search for locations based on user input
 */
function searchLocations() {
  const searchInput = document.getElementById('track-search');
  const searchResults = document.getElementById('search-results');
  
  if (!searchInput || !searchResults) return;
  
  const query = searchInput.value.trim();
  
  if (query.length < 2) {
    searchResults.style.display = 'none';
    return;
  }
  
  // Show loading indicator
  searchResults.innerHTML = '<div class="p-3 text-center"><i class="fas fa-spinner fa-spin me-2"></i>Searching...</div>';
  searchResults.style.display = 'block';
  
  // Fetch locations from API
  fetch(`/api/weather/search?query=${encodeURIComponent(query)}`)
    .then(response => response.json())
    .then(data => {
      if (data.length === 0) {
        searchResults.innerHTML = '<div class="p-3 text-center">No locations found. Try a different search term.</div>';
        return;
      }
      
      // Display search results
      let resultsHtml = '<div class="list-group">';
      data.forEach(location => {
        resultsHtml += `
          <button type="button" class="list-group-item list-group-item-action location-result" 
                  data-lat="${location.latitude}" data-lng="${location.longitude}">
            <strong>${location.name}</strong>, ${location.country}
          </button>
        `;
      });
      resultsHtml += '</div>';
      
      searchResults.innerHTML = resultsHtml;
      
      // Add click event to result items
      const resultItems = document.querySelectorAll('.location-result');
      resultItems.forEach(item => {
        item.addEventListener('click', function() {
          const lat = this.getAttribute('data-lat');
          const lng = this.getAttribute('data-lng');
          
          // Fetch weather data for selected location
          fetchWeatherData(lat, lng)
            .then(data => {
              displaySelectedLocation(data);
              searchResults.style.display = 'none';
              searchInput.value = `${data.location.name}, ${data.location.country}`;
            })
            .catch(error => {
              console.error('Error fetching weather data:', error);
              alert('Error fetching weather data. Please try again.');
            });
        });
      });
    })
    .catch(error => {
      console.error('Error searching locations:', error);
      searchResults.innerHTML = '<div class="p-3 text-center text-danger">Error searching locations. Please try again.</div>';
    });
}

/**
 * Fetch weather data for a given location
 * @param {number} latitude - The latitude coordinate
 * @param {number} longitude - The longitude coordinate
 * @returns {Promise} - Promise resolving to weather data
 */
async function fetchWeatherData(latitude, longitude) {
  // Fetch weather data
  const weatherResponse = await fetch(`/api/weather/current?latitude=${latitude}&longitude=${longitude}`);
  const weatherData = await weatherResponse.json();
  
  // Fetch elevation data
  const elevationResponse = await fetch(`/api/weather/elevation?latitude=${latitude}&longitude=${longitude}`);
  const elevationData = await elevationResponse.json();
  
  // Combine the data
  return {
    ...weatherData,
    elevation: elevationData.elevation
  };
}

/**
 * Display the selected location data
 * @param {Object} data - The location and weather data
 */
function displaySelectedLocation(data) {
  const selectedLocation = document.getElementById('selected-location');
  
  if (!selectedLocation) return;
  
  const html = `
    <h5>${data.location.name}, ${data.location.country}</h5>
    <div class="row g-2">
      <div class="col-md-3">
        <div class="d-flex align-items-center">
          <i class="fas fa-thermometer-half text-primary me-2"></i>
          <span>Temperature: ${data.temperature.toFixed(1)}°C</span>
        </div>
      </div>
      <div class="col-md-3">
        <div class="d-flex align-items-center">
          <i class="fas fa-tachometer-alt text-primary me-2"></i>
          <span>Pressure: ${data.pressure.toFixed(1)} hPa</span>
        </div>
      </div>
      <div class="col-md-3">
        <div class="d-flex align-items-center">
          <i class="fas fa-water text-primary me-2"></i>
          <span>Humidity: ${data.humidity}%</span>
        </div>
      </div>
      <div class="col-md-3">
        <div class="d-flex align-items-center">
          <i class="fas fa-mountain text-primary me-2"></i>
          <span>Elevation: ${data.elevation} m</span>
        </div>
      </div>
    </div>
    <div class="mt-2 text-muted">
      <small><i class="fas fa-clock me-1"></i> Last Updated: ${new Date(data.timestamp).toLocaleString()}</small>
    </div>
  `;
  
  selectedLocation.innerHTML = html;
  selectedLocation.style.display = 'block';
  
  // Auto-fill the manual inputs with the current weather data
  document.getElementById('temperature').value = data.temperature.toFixed(1);
  document.getElementById('pressure').value = data.pressure.toFixed(1);
  document.getElementById('humidity').value = data.humidity;
  document.getElementById('altitude').value = data.elevation;
}

/**
 * Calculate jetting based on input values
 */
function calculateJetting() {
  // Get input values
  const temperature = parseFloat(document.getElementById('temperature').value);
  const pressure = parseFloat(document.getElementById('pressure').value);
  const humidity = parseFloat(document.getElementById('humidity').value);
  const altitude = parseFloat(document.getElementById('altitude').value);
  const engineType = document.getElementById('engine-type').value;
  const referenceJet = document.getElementById('reference-jet').value ? parseInt(document.getElementById('reference-jet').value) : null;
  
  // Validate inputs
  if (isNaN(temperature) || isNaN(pressure) || isNaN(humidity) || isNaN(altitude)) {
    alert('Please enter valid values for all environmental parameters.');
    return;
  }
  
  // Check if using custom reference conditions
  let referenceConditions = null;
  const useCustomRef = document.getElementById('use-custom-reference');
  
  if (useCustomRef && useCustomRef.checked) {
    const refTemperature = parseFloat(document.getElementById('ref-temperature').value);
    const refPressure = parseFloat(document.getElementById('ref-pressure').value);
    const refHumidity = parseFloat(document.getElementById('ref-humidity').value);
    const refAltitude = parseFloat(document.getElementById('ref-altitude').value);
    
    if (isNaN(refTemperature) || isNaN(refPressure) || isNaN(refHumidity) || isNaN(refAltitude)) {
      alert('Please enter valid values for all reference conditions.');
      return;
    }
    
    referenceConditions = {
      temperature: refTemperature,
      pressure: refPressure,
      humidity: refHumidity,
      altitude: refAltitude
    };
  }
  
  // Prepare data for API request
  const data = {
    temperature,
    pressure,
    humidity,
    altitude,
    engine_type: engineType,
    reference_jet: referenceJet,
    reference_conditions: referenceConditions
  };
  
  // Show loading indicator
  const button = document.getElementById('calculate-btn');
  const originalText = button.innerHTML;
  button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Calculating...';
  button.disabled = true;
  
  // Send request to API
  fetch('/api/calculate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
    .then(response => response.json())
    .then(result => {
      // Display results
      displayResults(result);
      
      // Reset button
      button.innerHTML = originalText;
      button.disabled = false;
    })
    .catch(error => {
      console.error('Error calculating jetting:', error);
      alert('Error calculating jetting. Please try again.');
      
      // Reset button
      button.innerHTML = originalText;
      button.disabled = false;
    });
}

/**
 * Display jetting calculation results
 * @param {Object} result - The calculation results
 */
function displayResults(result) {
  const resultsContainer = document.getElementById('results-container');
  
  if (!resultsContainer) return;
  
  // Update result values
  document.getElementById('result-main-jet').textContent = result.recommendations.main_jet;
  document.getElementById('result-needle-position').textContent = result.recommendations.needle_position;
  document.getElementById('result-float-height').textContent = result.recommendations.float_height.toFixed(1);
  document.getElementById('result-needle-type').textContent = result.recommendations.needle_type;
  
  // Update calculation details
  document.getElementById('result-current-density').textContent = `${result.calculations.current_air_density.toFixed(3)} kg/m³`;
  document.getElementById('result-reference-density').textContent = `${result.calculations.reference_air_density.toFixed(3)} kg/m³`;
  document.getElementById('result-density-ratio').textContent = result.calculations.density_ratio.toFixed(3);
  
  // Update timestamp
  document.getElementById('results-timestamp').textContent = `Calculated on ${new Date().toLocaleString()}`;
  
  // Handle warnings
  const warningsContainer = document.getElementById('warnings-container');
  const warningsList = document.getElementById('warnings-list');
  
  if (result.warnings && result.warnings.length > 0) {
    let warningsHtml = '';
    result.warnings.forEach(warning => {
      warningsHtml += `<li>${warning.message}</li>`;
    });
    warningsList.innerHTML = warningsHtml;
    warningsContainer.style.display = 'block';
  } else {
    warningsContainer.style.display = 'none';
  }
  
  // Show results container
  resultsContainer.style.display = 'block';
  
  // Scroll to results
  resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Show the save settings modal
 */
function showSaveSettingsModal() {
  // Check if user is logged in
  const saveSettingsBtn = document.getElementById('save-settings-btn');
  if (saveSettingsBtn.disabled) {
    alert('Please log in to save your settings.');
    return;
  }
  
  // Check if results are available
  const resultsContainer = document.getElementById('results-container');
  if (resultsContainer.style.display === 'none') {
    alert('Please calculate jetting before saving settings.');
    return;
  }
  
  // Show modal
  const saveSettingsModal = new bootstrap.Modal(document.getElementById('saveSettingsModal'));
  saveSettingsModal.show();
}

/**
 * Save the current settings
 */
function saveSettings() {
  const settingsName = document.getElementById('settings-name').value.trim();
  const settingsNotes = document.getElementById('settings-notes').value.trim();
  
  if (!settingsName) {
    alert('Please enter a name for your settings.');
    return;
  }
  
  // Get current settings
  const settings = {
    temperature: parseFloat(document.getElementById('temperature').value),
    pressure: parseFloat(document.getElementById('pressure').value),
    humidity: parseFloat(document.getElementById('humidity').value),
    altitude: parseFloat(document.getElementById('altitude').value),
    engine_type: document.getElementById('engine-type').value,
    reference_jet: document.getElementById('reference-jet').value ? parseInt(document.getElementById('reference-jet').value) : null
  };
  
  // Get results
  const results = {
    main_jet: parseInt(document.getElementById('result-main-jet').textContent),
    needle_position: parseInt(document.getElementById('result-needle-position').textContent),
    float_height: parseFloat(document.getElementById('result-float-height').textContent),
    needle_type: document.getElementById('result-needle-type').textContent
  };
  
  // Prepare data for API request
  const data = {
    name: settingsName,
    notes: settingsNotes,
    settings: settings,
    results: results
  };
  
  // Send request to API
  fetch('/api/settings/save', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
    .then(response => response.json())
    .then(result => {
      // Close modal
      const saveSettingsModal = bootstrap.Modal.getInstance(document.getElementById('saveSettingsModal'));
      saveSettingsModal.hide();
      
      // Show success message
      alert('Settings saved successfully!');
    })
    .catch(error => {
      console.error('Error saving settings:', error);
      alert('Error saving settings. Please try again.');
    });
}

/**
 * Load a saved setting
 * @param {string} settingId - The ID of the setting to load
 */
function loadSavedSetting(settingId) {
  // In a real implementation, we would fetch the setting from the server
  // For now, we'll just show a message
  alert(`Loading setting ${settingId}. This functionality would be implemented in a production environment.`);
}

/**
 * Initialize the settings page functionality
 */
function initSettingsPage() {
  // Delete setting confirmation
  let settingToDelete = null;
  const deleteModal = new bootstrap.Modal(document.getElementById('deleteSettingModal'));
  
  // Delete setting buttons
  const deleteButtons = document.querySelectorAll('.delete-setting');
  deleteButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      settingToDelete = this.getAttribute('data-id');
      deleteModal.show();
    });
  });
  
  // Confirm delete button
  const confirmDeleteBtn = document.getElementById('confirm-delete');
  if (confirmDeleteBtn) {
    confirmDeleteBtn.addEventListener('click', function() {
      if (settingToDelete) {
        // Send request to API
        fetch(`/api/settings/${settingToDelete}/delete`, {
          method: 'DELETE'
        })
          .then(response => response.json())
          .then(result => {
            // Close modal
            deleteModal.hide();
            
            // Show success message
            alert('Setting deleted successfully!');
            
            // Reload page
            location.reload();
          })
          .catch(error => {
            console.error('Error deleting setting:', error);
            alert('Error deleting setting. Please try again.');
            
            // Close modal
            deleteModal.hide();
          });
      }
    });
  }
  
  // Load setting buttons
  const loadButtons = document.querySelectorAll('.load-setting');
  loadButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      const settingId = this.getAttribute('data-id');
      window.location.href = `/calculator?load=${settingId}`;
    });
  });
}

/**
 * Initialize the pricing page functionality
 */
function initPricingPage() {
  // Billing toggle
  const billingToggle = document.getElementById('billingToggle');
  billingToggle.addEventListener('change', function() {
    const isAnnual = this.checked;
    
    // Update prices
    const amounts = document.querySelectorAll('.amount');
    amounts.forEach(amount => {
      const monthlyPrice = amount.getAttribute('data-monthly');
      const annualPrice = amount.getAttribute('data-annual');
      amount.textContent = isAnnual ? annualPrice : monthlyPrice;
    });
    
    // Update periods
    const periods = document.querySelectorAll('.period');
    periods.forEach(period => {
      const monthlyPeriod = period.getAttribute('data-monthly');
      const annualPeriod = period.getAttribute('data-annual');
      period.textContent = isAnnual ? annualPeriod : monthlyPeriod;
    });
  });
}