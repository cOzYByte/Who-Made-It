import requests
import sys
import json
from datetime import datetime

class InventorGenderAPITester:
    def __init__(self, base_url="https://inventor-gender.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    Details: {details}")

    def test_root_endpoint(self):
        """Test root API endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
            self.log_test("Root endpoint", success, details)
            return success
        except Exception as e:
            self.log_test("Root endpoint", False, f"Error: {str(e)}")
            return False

    def test_analyze_endpoint(self, input_text="iPhone"):
        """Test analyze endpoint with sample input"""
        try:
            payload = {"input_text": input_text}
            response = requests.post(f"{self.api_url}/analyze", json=payload, timeout=30)
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                required_fields = ['id', 'input_text', 'result', 'creator_name', 'category', 'explanation']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details += f", Missing fields: {missing_fields}"
                else:
                    details += f", Result: {data.get('result')}, Creator: {data.get('creator_name')}, Category: {data.get('category')}"
                    
                    # Validate result is man/woman/unknown
                    if data.get('result') not in ['man', 'woman', 'unknown']:
                        success = False
                        details += f", Invalid result value: {data.get('result')}"
            else:
                try:
                    error_data = response.json()
                    details += f", Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details += f", Response: {response.text[:100]}"
            
            self.log_test(f"Analyze endpoint ({input_text})", success, details)
            return success, response.json() if success else None
            
        except Exception as e:
            self.log_test(f"Analyze endpoint ({input_text})", False, f"Error: {str(e)}")
            return False, None

    def test_stats_endpoint(self):
        """Test stats endpoint"""
        try:
            response = requests.get(f"{self.api_url}/stats", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                required_fields = ['total_queries', 'men_count', 'women_count']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details += f", Missing fields: {missing_fields}"
                else:
                    details += f", Total: {data.get('total_queries')}, Men: {data.get('men_count')}, Women: {data.get('women_count')}"
            
            self.log_test("Stats endpoint", success, details)
            return success
            
        except Exception as e:
            self.log_test("Stats endpoint", False, f"Error: {str(e)}")
            return False

    def test_queries_endpoint(self):
        """Test queries endpoint"""
        try:
            response = requests.get(f"{self.api_url}/queries?limit=5", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                if isinstance(data, list):
                    details += f", Returned {len(data)} queries"
                    if len(data) > 0:
                        sample_query = data[0]
                        required_fields = ['id', 'input_text', 'result', 'creator_name', 'category']
                        missing_fields = [field for field in required_fields if field not in sample_query]
                        if missing_fields:
                            success = False
                            details += f", Missing fields in query: {missing_fields}"
                else:
                    success = False
                    details += ", Response is not a list"
            
            self.log_test("Queries endpoint", success, details)
            return success
            
        except Exception as e:
            self.log_test("Queries endpoint", False, f"Error: {str(e)}")
            return False

    def test_categories_endpoint(self):
        """Test categories endpoint"""
        try:
            response = requests.get(f"{self.api_url}/categories", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                if isinstance(data, list):
                    details += f", Returned {len(data)} categories"
                    if len(data) > 0:
                        sample_category = data[0]
                        required_fields = ['category', 'count', 'men_count', 'women_count']
                        missing_fields = [field for field in required_fields if field not in sample_category]
                        if missing_fields:
                            success = False
                            details += f", Missing fields in category: {missing_fields}"
                else:
                    success = False
                    details += ", Response is not a list"
            
            self.log_test("Categories endpoint", success, details)
            return success
            
        except Exception as e:
            self.log_test("Categories endpoint", False, f"Error: {str(e)}")
            return False

    def test_multiple_inventions(self):
        """Test multiple different inventions"""
        test_inventions = [
            "Radium",
            "Telephone", 
            "DNA Structure",
            "Computer Programming"
        ]
        
        all_passed = True
        for invention in test_inventions:
            success, _ = self.test_analyze_endpoint(invention)
            if not success:
                all_passed = False
        
        return all_passed

    def run_all_tests(self):
        """Run all backend tests"""
        print("🧪 Starting Backend API Tests...")
        print("=" * 50)
        
        # Test basic connectivity
        if not self.test_root_endpoint():
            print("❌ Root endpoint failed - stopping tests")
            return False
        
        # Test core functionality
        self.test_analyze_endpoint("iPhone")
        self.test_stats_endpoint()
        self.test_queries_endpoint()
        self.test_categories_endpoint()
        
        # Test with multiple inventions
        print("\n🔬 Testing multiple inventions...")
        self.test_multiple_inventions()
        
        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 Backend Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("✅ All backend tests passed!")
            return True
        else:
            print(f"❌ {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    tester = InventorGenderAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'total_tests': tester.tests_run,
                'passed_tests': tester.tests_passed,
                'success_rate': (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0,
                'timestamp': datetime.now().isoformat()
            },
            'detailed_results': tester.test_results
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())