// Global variables
let userLocation = null;
const BACKEND_URL = 'http://localhost:5000';

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Symptom page loaded');
    
    // Load saved language preference
    const savedLanguage = localStorage.getItem('preferredLanguage') || 'en';
    console.log('Language preference:', savedLanguage);
    
    // Set up event listeners
    setupEventListeners();
    
    // Get user location if permitted
    getUserLocation();
});

function setupEventListeners() {
    // Analyze button
    document.getElementById('analyzeBtn').addEventListener('click', analyzeSymptoms);
    
    // Back button
    document.getElementById('backBtn').addEventListener('click', () => {
        window.location.href = 'index.html';
    });
    
    // Ayushman card toggle
    document.getElementById('ayushmanCard').addEventListener('change', function() {
        const detailsDiv = document.getElementById('ayushmanDetails');
        detailsDiv.classList.toggle('hidden', !this.checked);
    });
    
    // Share location toggle
    document.getElementById('shareLocation').addEventListener('change', function() {
        if (this.checked && !userLocation) {
            getUserLocation();
        }
    });
}

async function analyzeSymptoms() {
    const symptomsText = document.getElementById('symptomsText').value.trim();
    const ayushmanCard = document.getElementById('ayushmanCard').checked;
    const language = localStorage.getItem('preferredLanguage') || 'en';
    
    if (!symptomsText) {
        alert('Please describe your symptoms or use voice recording');
        return;
    }
    
    console.log('Starting symptom analysis...');
    console.log('Symptoms:', symptomsText);
    console.log('Ayushman Card:', ayushmanCard);
    console.log('Language:', language);
    
    // Show loading
    const loading = document.getElementById('loading');
    loading.classList.remove('hidden');
    
    try {
        const requestData = {
            symptoms: symptomsText,
            language: language,
            ayushman_card: ayushmanCard,
            location: userLocation || { lat: 28.6139, lng: 77.2090 } // Default Delhi
        };
        
        console.log('Sending request to backend...', requestData);
        
        const response = await fetch(`${BACKEND_URL}/triage`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Backend response:', result);
        
        if (result.error) {
            throw new Error(result.error);
        }
        
        // Store result and redirect to results page
        localStorage.setItem('triageResult', JSON.stringify(result));
        window.location.href = 'results.html';
        
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to analyze symptoms. Please check if backend is running and try again.\n\nError: ' + error.message);
    } finally {
        loading.classList.add('hidden');
    }
}

function getUserLocation() {
    if (!navigator.geolocation) {
        console.log("Geolocation is not supported by this browser.");
        alert("Geolocation is not supported by your browser. Using default location.");
        userLocation = { lat: 28.6139, lng: 77.2090 }; // Default to Delhi
        return;
    }
    
    console.log("Requesting user location...");
    
    navigator.geolocation.getCurrentPosition(
        (position) => {
            userLocation = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };
            console.log("Location obtained:", userLocation);
            alert("Location accessed successfully! We'll find hospitals near you.");
        },
        (error) => {
            console.log("Error getting location:", error.message);
            userLocation = { lat: 28.6139, lng: 77.2090 }; // Default to Delhi
            alert("Could not access your location. Using default location for hospital search.");
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 60000
        }
    );
}

// Enter key support for textarea
document.getElementById('symptomsText').addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.key === 'Enter') {
        analyzeSymptoms();
    }
});