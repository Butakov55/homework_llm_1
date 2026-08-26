import pytest
import requests

def test_get_all_posts(base_url):
    """Тест на получение всех постов"""
    response = requests.get(f"{base_url}/posts")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    posts = response.json()
    assert isinstance(posts, list), "Response should be a list"
    assert len(posts) > 0, "Posts list should not be empty"
    
    # Проверка структуры первого поста
    first_post = posts[0]
    required_fields = ['userId', 'id', 'title', 'body']
    for field in required_fields:
        assert field in first_post, f"Field '{field}' is missing in post"
    
    print(f"✅ Found {len(posts)} posts")

def test_create_new_post(base_url):
    """Тест на создание нового поста"""
    new_post = {
        "userId": 1,
        "title": "Test Post from Automated Test",
        "body": "This is a test post created by automated tests"
    }
    
    response = requests.post(f"{base_url}/posts", json=new_post)
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    
    created_post = response.json()
    required_fields = ['userId', 'id', 'title', 'body']
    for field in required_fields:
        assert field in created_post, f"Field '{field}' is missing"
    
    assert created_post['userId'] == new_post['userId'], "UserId mismatch"
    assert created_post['title'] == new_post['title'], "Title mismatch"
    assert created_post['body'] == new_post['body'], "Body mismatch"
    
    print(f"✅ Post created with ID: {created_post['id']}")

@pytest.mark.parametrize("post_id", [1, 2, 3])
def test_get_specific_post(base_url, post_id):
    """Тест на получение конкретного поста"""
    response = requests.get(f"{base_url}/posts/{post_id}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    post = response.json()
    assert post['id'] == post_id, f"Expected id {post_id}, got {post['id']}"
    
    required_fields = ['userId', 'id', 'title', 'body']
    for field in required_fields:
        assert field in post, f"Field '{field}' is missing"
    
    print(f"✅ Retrieved post {post_id}")

def test_filter_posts_by_user(base_url):
    """Тест на фильтрацию постов по userId"""
    user_id = 1
    response = requests.get(f"{base_url}/posts", params={"userId": user_id})
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    posts = response.json()
    assert isinstance(posts, list), "Response should be a list"
    assert len(posts) > 0, "User should have posts"
    
    # Проверяем, что все посты принадлежат пользователю
    for post in posts:
        assert post['userId'] == user_id, f"Post {post['id']} belongs to different user"
    
    print(f"✅ Found {len(posts)} posts for user {user_id}")