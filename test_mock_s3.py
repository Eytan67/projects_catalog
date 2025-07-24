#!/usr/bin/env python3
"""
Simple test script to demonstrate mock S3 functionality
"""
import requests
import json

# Test data
project_data = {
    "title": "Test Project with Mock S3",
    "description": "Testing mock S3 image upload",
    "category": "web_development",
    "status": "Development"
}

# API endpoints
base_url = "http://localhost:8000"
projects_url = f"{base_url}/projects/?sso_id=1234"

def test_mock_s3():
    print("🧪 Testing Mock S3 Service")
    print("=" * 50)
    
    # Test 1: Create project without image
    print("\n1. Creating project without image...")
    response = requests.post(
        projects_url,
        data={"project_data": json.dumps(project_data)}
    )
    
    if response.status_code == 201:
        project = response.json()
        print(f"✅ Project created: {project['title']}")
        print(f"   ID: {project['id']}")
        print(f"   Image URL: {project.get('image_url', 'None')}")
        return project['id']
    else:
        print(f"❌ Failed to create project: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def test_with_image(project_id=None):
    print("\n2. Testing image upload capability...")
    
    # Create a simple test "image" (just some bytes)
    test_image_data = b"fake-image-data-for-testing"
    
    files = {
        'project_data': (None, json.dumps(project_data)),
        'image': ('test.jpg', test_image_data, 'image/jpeg')
    }
    
    try:
        response = requests.post(projects_url, files=files)
        
        if response.status_code == 201:
            project = response.json()
            print(f"✅ Project with mock image created: {project['title']}")
            print(f"   ID: {project['id']}")
            print(f"   Mock Image URL: {project.get('image_url', 'None')}")
            
            # Test accessing the mock image URL
            if project.get('image_url'):
                img_response = requests.get(project['image_url'])
                print(f"   Image accessible: {img_response.status_code == 200}")
            
        else:
            print(f"❌ Failed to create project with image: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing image upload: {str(e)}")

def check_admin():
    print("\n0. Checking admin status...")
    admin_url = f"{base_url}/admin/check?sso_id=1234"
    
    try:
        response = requests.get(admin_url)
        if response.status_code == 200:
            result = response.json()
            print(f"   Admin check: {result}")
            return result.get('is_admin', False)
        else:
            print(f"❌ Admin check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking admin: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Mock S3 Service Test")
    print("This test demonstrates the mock S3 functionality")
    print("- Images are stored locally in /app/uploads/")
    print("- Image URLs point to http://localhost:8000/uploads/")
    print("- No AWS credentials needed!")
    
    # Check if admin exists
    is_admin = check_admin()
    if not is_admin:
        print("\n⚠️  Admin with sso_id '1234' not found.")
        print("   Run this SQL to create admin:")
        print("   INSERT INTO admins (sso_id, is_active) VALUES ('1234', true);")
        exit(1)
    
    # Run tests
    project_id = test_mock_s3()
    test_with_image()
    
    print("\n🎉 Mock S3 test completed!")
    print("Check the Docker logs to see mock S3 operations.")