import requests
import json

def test_local():
    url = "http://localhost:8000/api/collect"
    try:
        print("Sending GET request...")
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Collected: {data.get('count')} posts")
            posts = data.get('posts', [])
            if posts:
                print("First post title:", posts[0].get('title'))
        else:
            print(response.text)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    test_local()
