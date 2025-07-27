#!/usr/bin/env python3
"""
Backend API Testing for Crime Reporting and Area-wise Prediction Portal
Tests all backend endpoints with realistic crime data
"""

import requests
import json
import time
from datetime import datetime
import uuid

# Backend URL from frontend/.env
BACKEND_URL = "https://7b5be203-4f72-469f-90f1-4dd2784f8696.preview.emergentagent.com/api"

# Test data - realistic crime reports
SAMPLE_CRIME_REPORTS = [
    {
        "crime_type": "Theft",
        "area": "Downtown",
        "location": "Main Street near City Mall",
        "description": "Bicycle stolen from bike rack outside shopping center. Black mountain bike with red accents.",
        "reported_by": "John Smith"
    },
    {
        "crime_type": "Burglary",
        "area": "Residential District",
        "location": "Oak Avenue, House #245",
        "description": "Break-in occurred during daytime hours. Electronics and jewelry reported missing.",
        "reported_by": "Sarah Johnson"
    },
    {
        "crime_type": "Assault",
        "area": "Park Area",
        "location": "Central Park near playground",
        "description": "Physical altercation between two individuals. One person sustained minor injuries.",
        "reported_by": "Mike Wilson"
    },
    {
        "crime_type": "Vandalism",
        "area": "Commercial District",
        "location": "Business Plaza parking lot",
        "description": "Graffiti spray-painted on multiple storefronts and vehicles.",
        "reported_by": "Lisa Chen"
    },
    {
        "crime_type": "Drug-related",
        "area": "Industrial Zone",
        "location": "Warehouse District, 5th Street",
        "description": "Suspicious activity reported involving drug transactions near abandoned building.",
        "reported_by": "Anonymous"
    }
]

class CrimePortalTester:
    def __init__(self):
        self.session = requests.Session()
        self.created_report_ids = []
        self.test_results = {
            "crud_api": {"passed": 0, "failed": 0, "errors": []},
            "ai_prediction": {"passed": 0, "failed": 0, "errors": []},
            "openai_integration": {"passed": 0, "failed": 0, "errors": []},
            "statistics_api": {"passed": 0, "failed": 0, "errors": []}
        }

    def log_result(self, category, test_name, success, error_msg=None):
        """Log test results"""
        if success:
            self.test_results[category]["passed"] += 1
            print(f"✅ {test_name}")
        else:
            self.test_results[category]["failed"] += 1
            self.test_results[category]["errors"].append(f"{test_name}: {error_msg}")
            print(f"❌ {test_name}: {error_msg}")

    def test_api_root(self):
        """Test API root endpoint"""
        print("\n🔍 Testing API Root Endpoint...")
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            if response.status_code == 200:
                data = response.json()
                if "Crime Reporting" in data.get("message", ""):
                    self.log_result("crud_api", "API Root Endpoint", True)
                    return True
                else:
                    self.log_result("crud_api", "API Root Endpoint", False, "Unexpected message content")
            else:
                self.log_result("crud_api", "API Root Endpoint", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("crud_api", "API Root Endpoint", False, str(e))
        return False

    def test_create_crime_reports(self):
        """Test POST /api/reports - Create crime reports"""
        print("\n🔍 Testing Crime Report Creation...")
        
        for i, report_data in enumerate(SAMPLE_CRIME_REPORTS):
            try:
                response = self.session.post(
                    f"{BACKEND_URL}/reports",
                    json=report_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "id" in data and data["crime_type"] == report_data["crime_type"]:
                        self.created_report_ids.append(data["id"])
                        self.log_result("crud_api", f"Create Crime Report {i+1}", True)
                    else:
                        self.log_result("crud_api", f"Create Crime Report {i+1}", False, "Invalid response structure")
                else:
                    self.log_result("crud_api", f"Create Crime Report {i+1}", False, f"Status code: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                self.log_result("crud_api", f"Create Crime Report {i+1}", False, str(e))

    def test_get_all_reports(self):
        """Test GET /api/reports - Get all crime reports"""
        print("\n🔍 Testing Get All Crime Reports...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/reports")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    # Check if our created reports are in the list
                    found_reports = sum(1 for report in data if report.get("id") in self.created_report_ids)
                    if found_reports > 0:
                        self.log_result("crud_api", "Get All Crime Reports", True)
                    else:
                        self.log_result("crud_api", "Get All Crime Reports", False, "Created reports not found in list")
                else:
                    self.log_result("crud_api", "Get All Crime Reports", False, "Empty or invalid response")
            else:
                self.log_result("crud_api", "Get All Crime Reports", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("crud_api", "Get All Crime Reports", False, str(e))

    def test_get_reports_by_area(self):
        """Test GET /api/reports with area filter"""
        print("\n🔍 Testing Get Reports by Area...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/reports?area=Downtown")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Check if filtered results contain only Downtown reports
                    downtown_reports = [r for r in data if "Downtown" in r.get("area", "")]
                    if len(downtown_reports) > 0:
                        self.log_result("crud_api", "Get Reports by Area Filter", True)
                    else:
                        self.log_result("crud_api", "Get Reports by Area Filter", False, "No Downtown reports found")
                else:
                    self.log_result("crud_api", "Get Reports by Area Filter", False, "Invalid response format")
            else:
                self.log_result("crud_api", "Get Reports by Area Filter", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("crud_api", "Get Reports by Area Filter", False, str(e))

    def test_get_specific_report(self):
        """Test GET /api/reports/{id} - Get specific crime report"""
        print("\n🔍 Testing Get Specific Crime Report...")
        
        if not self.created_report_ids:
            self.log_result("crud_api", "Get Specific Crime Report", False, "No report IDs available for testing")
            return
            
        report_id = self.created_report_ids[0]
        try:
            response = self.session.get(f"{BACKEND_URL}/reports/{report_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("id") == report_id:
                    self.log_result("crud_api", "Get Specific Crime Report", True)
                else:
                    self.log_result("crud_api", "Get Specific Crime Report", False, "Report ID mismatch")
            elif response.status_code == 404:
                self.log_result("crud_api", "Get Specific Crime Report", False, "Report not found (404)")
            else:
                self.log_result("crud_api", "Get Specific Crime Report", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("crud_api", "Get Specific Crime Report", False, str(e))

    def test_crime_statistics(self):
        """Test GET /api/stats - Crime statistics"""
        print("\n🔍 Testing Crime Statistics API...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/stats")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_reports", "by_area", "by_type"]
                
                if all(field in data for field in required_fields):
                    if (isinstance(data["by_area"], list) and 
                        isinstance(data["by_type"], list) and 
                        isinstance(data["total_reports"], int)):
                        self.log_result("statistics_api", "Crime Statistics Structure", True)
                        
                        # Check if we have some data
                        if data["total_reports"] > 0:
                            self.log_result("statistics_api", "Crime Statistics Data", True)
                        else:
                            self.log_result("statistics_api", "Crime Statistics Data", False, "No statistics data available")
                    else:
                        self.log_result("statistics_api", "Crime Statistics Structure", False, "Invalid data types")
                else:
                    self.log_result("statistics_api", "Crime Statistics Structure", False, f"Missing fields: {set(required_fields) - set(data.keys())}")
            else:
                self.log_result("statistics_api", "Crime Statistics API", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("statistics_api", "Crime Statistics API", False, str(e))

    def test_ai_prediction_basic(self):
        """Test POST /api/predict - Basic AI prediction"""
        print("\n🔍 Testing AI Crime Prediction (Basic)...")
        
        try:
            prediction_request = {"area": "Downtown"}
            response = self.session.post(
                f"{BACKEND_URL}/predict",
                json=prediction_request,
                headers={"Content-Type": "application/json"},
                timeout=60  # AI requests can take longer
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "prediction_text", "insights", "confidence"]
                
                if all(field in data for field in required_fields):
                    if (data["prediction_text"] and 
                        isinstance(data["insights"], list) and 
                        data["confidence"] in ["High", "Medium", "Low"]):
                        self.log_result("ai_prediction", "AI Prediction Basic Structure", True)
                        self.log_result("openai_integration", "OpenAI Integration Working", True)
                        
                        # Check prediction quality
                        if len(data["prediction_text"]) > 50:
                            self.log_result("ai_prediction", "AI Prediction Content Quality", True)
                        else:
                            self.log_result("ai_prediction", "AI Prediction Content Quality", False, "Prediction text too short")
                    else:
                        self.log_result("ai_prediction", "AI Prediction Basic Structure", False, "Invalid field values")
                        self.log_result("openai_integration", "OpenAI Integration Working", False, "Invalid response structure")
                else:
                    self.log_result("ai_prediction", "AI Prediction Basic Structure", False, f"Missing fields: {set(required_fields) - set(data.keys())}")
                    self.log_result("openai_integration", "OpenAI Integration Working", False, "Missing required fields")
            elif response.status_code == 500:
                error_detail = response.json().get("detail", "Unknown error")
                if "OpenAI API key not configured" in error_detail:
                    self.log_result("openai_integration", "OpenAI API Key Configuration", False, "API key not configured")
                else:
                    self.log_result("ai_prediction", "AI Prediction Basic", False, f"Server error: {error_detail}")
                    self.log_result("openai_integration", "OpenAI Integration Working", False, f"Server error: {error_detail}")
            else:
                self.log_result("ai_prediction", "AI Prediction Basic", False, f"Status code: {response.status_code}")
                self.log_result("openai_integration", "OpenAI Integration Working", False, f"Status code: {response.status_code}")
                
        except requests.exceptions.Timeout:
            self.log_result("ai_prediction", "AI Prediction Basic", False, "Request timeout (>60s)")
            self.log_result("openai_integration", "OpenAI Integration Working", False, "Request timeout")
        except Exception as e:
            self.log_result("ai_prediction", "AI Prediction Basic", False, str(e))
            self.log_result("openai_integration", "OpenAI Integration Working", False, str(e))

    def test_ai_prediction_no_area(self):
        """Test POST /api/predict without area filter"""
        print("\n🔍 Testing AI Crime Prediction (No Area Filter)...")
        
        try:
            prediction_request = {}  # No area specified
            response = self.session.post(
                f"{BACKEND_URL}/predict",
                json=prediction_request,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("prediction_text") and data.get("area") is None:
                    self.log_result("ai_prediction", "AI Prediction No Area Filter", True)
                else:
                    self.log_result("ai_prediction", "AI Prediction No Area Filter", False, "Invalid response for no area filter")
            else:
                self.log_result("ai_prediction", "AI Prediction No Area Filter", False, f"Status code: {response.status_code}")
                
        except requests.exceptions.Timeout:
            self.log_result("ai_prediction", "AI Prediction No Area Filter", False, "Request timeout")
        except Exception as e:
            self.log_result("ai_prediction", "AI Prediction No Area Filter", False, str(e))

    def test_get_predictions(self):
        """Test GET /api/predictions - Get stored predictions"""
        print("\n🔍 Testing Get Stored Predictions...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/predictions")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("ai_prediction", "Get Stored Predictions", True)
                    
                    # Check if we have predictions with proper structure
                    if len(data) > 0:
                        prediction = data[0]
                        required_fields = ["id", "prediction_text", "insights", "confidence", "timestamp"]
                        if all(field in prediction for field in required_fields):
                            self.log_result("ai_prediction", "Prediction Storage Structure", True)
                        else:
                            self.log_result("ai_prediction", "Prediction Storage Structure", False, "Invalid stored prediction structure")
                else:
                    self.log_result("ai_prediction", "Get Stored Predictions", False, "Invalid response format")
            else:
                self.log_result("ai_prediction", "Get Stored Predictions", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("ai_prediction", "Get Stored Predictions", False, str(e))

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Crime Portal Backend API Tests...")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Test API connectivity first
        if not self.test_api_root():
            print("\n❌ API Root endpoint failed - backend may not be running")
            return self.generate_summary()
        
        # Test Crime Report CRUD API
        print("\n" + "="*60)
        print("📋 TESTING CRIME REPORT CRUD API")
        print("="*60)
        self.test_create_crime_reports()
        time.sleep(1)  # Brief pause between tests
        self.test_get_all_reports()
        self.test_get_reports_by_area()
        self.test_get_specific_report()
        
        # Test Crime Statistics API
        print("\n" + "="*60)
        print("📊 TESTING CRIME STATISTICS API")
        print("="*60)
        self.test_crime_statistics()
        
        # Test AI Prediction API and OpenAI Integration
        print("\n" + "="*60)
        print("🤖 TESTING AI PREDICTION API & OPENAI INTEGRATION")
        print("="*60)
        self.test_ai_prediction_basic()
        time.sleep(2)  # Pause between AI requests
        self.test_ai_prediction_no_area()
        time.sleep(1)
        self.test_get_predictions()
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "="*60)
        print("📋 TEST SUMMARY")
        print("="*60)
        
        total_passed = sum(result["passed"] for result in self.test_results.values())
        total_failed = sum(result["failed"] for result in self.test_results.values())
        
        print(f"Total Tests: {total_passed + total_failed}")
        print(f"✅ Passed: {total_passed}")
        print(f"❌ Failed: {total_failed}")
        print()
        
        # Detailed breakdown
        categories = {
            "crud_api": "Crime Report CRUD API",
            "statistics_api": "Crime Statistics API", 
            "ai_prediction": "AI Crime Prediction API",
            "openai_integration": "OpenAI Integration"
        }
        
        for key, name in categories.items():
            result = self.test_results[key]
            status = "✅ WORKING" if result["failed"] == 0 and result["passed"] > 0 else "❌ FAILING"
            print(f"{name}: {status} ({result['passed']} passed, {result['failed']} failed)")
            
            if result["errors"]:
                for error in result["errors"]:
                    print(f"  - {error}")
        
        return self.test_results

if __name__ == "__main__":
    tester = CrimePortalTester()
    results = tester.run_all_tests()