import pytest
import requests

def test_get_all_users(base_url):
    """Тест на получение всех пользователей"""
    response = requests.get(f"{base_url}/users")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    users = response.json()
    assert isinstance(users, list), "Users should be a list"
    assert len(users) > 0, "Users list should not be empty"
    
    # Проверка структуры первого пользователя
    first_user = users[0]
    required_fields = ['id', 'name', 'username', 'email', 'address', 'phone', 'website', 'company']
    for field in required_fields:
        assert field in first_user, f"Field '{field}' is missing"
    
    # Проверка вложенных структур
    assert isinstance(first_user['address'], dict), "Address should be an object"
    assert isinstance(first_user['company'], dict), "Company should be an object"
    
    print(f"✅ Found {len(users)} users")

def test_get_user_by_id(base_url):
    """Тест на получение пользователя по ID"""
    user_id = 1
    response = requests.get(f"{base_url}/users/{user_id}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    user = response.json()
    assert user['id'] == user_id, f"Expected id {user_id}, got {user['id']}"
    assert user['name'] == "Leanne Graham", "User name mismatch"
    assert user['email'] == "Sincere@april.biz", "User email mismatch"
    
    print(f"✅ Retrieved user: {user['name']}")

def test_get_user_posts(base_url):
    """Тест на получение постов пользователя"""
    user_id = 1
    response = requests.get(f"{base_url}/users/{user_id}/posts")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    posts = response.json()
    assert isinstance(posts, list), "Posts should be a list"
    assert len(posts) > 0, "User should have posts"
    
    # Проверка, что все посты принадлежат пользователю
    for post in posts:
        assert post['userId'] == user_id, f"Post {post['id']} belongs to different user"
    
    print(f"✅ User {user_id} has {len(posts)} posts")

def test_get_user_albums(base_url):
    """Тест на получение альбомов пользователя"""
    user_id = 1
    response = requests.get(f"{base_url}/users/{user_id}/albums")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    albums = response.json()
    assert isinstance(albums, list), "Albums should be a list"
    assert len(albums) > 0, "User should have albums"
    
    # Проверка структуры альбома
    first_album = albums[0]
    required_fields = ['userId', 'id', 'title']
    for field in required_fields:
        assert field in first_album, f"Field '{field}' is missing"
    
    assert first_album['userId'] == user_id, "Album belongs to different user"
    
    print(f"✅ User {user_id} has {len(albums)} albums")

def test_user_not_found(base_url):
    """Тест на обработку несуществующего пользователя"""
    response = requests.get(f"{base_url}/users/999")
    
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    print("✅ Correctly handled non-existent user")