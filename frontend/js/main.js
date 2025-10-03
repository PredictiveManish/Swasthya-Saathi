// Global variables
let userLocation = null;
const BACKEND_URL = 'http://localhost:5000';

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    // Load saved language preference
    const savedLanguage = localStorage.getItem('preferredLanguage') || 'en';
    
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
    
    // Show loading
    const loading = document.getElementById('loading');
    loading.classList.remove('hidden');
    
    try {
        const requestData = {
            symptoms: symptomsText,
            language: language,
            ayushman_card: ayushmanCard,
            location: userLocation
        };
        
        const response = await fetch(`${BACKEND_URL}/triage`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Store result and redirect to results page
            localStorage.setItem('triageResult', JSON.stringify(result));
            window.location.href = 'results.html';
        } else {
            throw new Error(result.error || 'Analysis failed');
        }
        
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to analyze symptoms. Please try again.');
    } finally {
        loading.classList.add('hidden');
    }
}

function getUserLocation() {
    if (!navigator.geolocation) {
        console.log("Geolocation is not supported by this browser.");
        return;
    }
    
    navigator.geolocation.getCurrentPosition(
        (position) => {
            userLocation = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };
            console.log("Location obtained:", userLocation);
        },
        (error) => {
            console.log("Error getting location:", error.message);
            // Use default location (Delhi)
            userLocation = { lat: 28.6139, lng: 77.2090 };
        }
    );
}