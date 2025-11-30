import requests
import json
import time

def test_local():
    # Retry logic because server might need a second to start
    url = "http://localhost:8000"
    max_retries = 5
    for i in range(max_retries):
        try:
            print(f"Sending GET request (Attempt {i+1})...")
            response = requests.get(url)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Collected: {data.get('count')} posts")
                
                analysis = data.get('analysis', [])
                if analysis:
                    print("\n--- Analysis Results (First Item) ---")
                    first = analysis[0]
                    print(f"Title (Translated): {first.get('title')}")
                    print(f"Summary (Translated): {first.get('summary')}")
                    print(f"Category (Translated): {first.get('category')}")
                    print("-------------------------------------\n")
                else:
                    print("No analysis results found.")
                
                return # Success
            else:
                print(f"Error response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("Server not ready yet...")
            time.sleep(2)
        except Exception as e:
            print(f"Error: {e}")
            break
            
    print("Failed to connect after retries.")

if __name__ == "__main__":
    test_local()
