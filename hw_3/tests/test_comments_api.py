import pytest
import requests

def test_get_comments_for_post(base_url):
    """Тест на получение комментариев для поста"""
    post_id = 1
    response = requests.get(f"{base_url}/posts/{post_id}/comments")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    comments = response.json()
    assert isinstance(comments, list), "Comments should be a list"
    assert len(comments) > 0, "Comments list should not be empty"
    
    # Проверка структуры комментария
    first_comment = comments[0]
    required_fields = ['postId', 'id', 'name', 'email', 'body']
    for field in required_fields:
        assert field in first_comment, f"Field '{field}' is missing"
    
    # Проверка, что все комментарии принадлежат посту
    for comment in comments:
        assert comment['postId'] == post_id, f"Comment {comment['id']} belongs to different post"
    
    print(f"✅ Found {len(comments)} comments for post {post_id}")

def test_get_all_comments(base_url):
    """Тест на получение всех комментариев"""
    response = requests.get(f"{base_url}/comments")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    comments = response.json()
    assert isinstance(comments, list), "Comments should be a list"
    assert len(comments) > 0, "Comments list should not be empty"
    
    # Проверка структуры первых 3 комментариев
    for comment in comments[:3]:
        required_fields = ['postId', 'id', 'name', 'email', 'body']
        for field in required_fields:
            assert field in comment, f"Field '{field}' is missing"
    
    print(f"✅ Retrieved {len(comments)} total comments")

@pytest.mark.parametrize("post_id,expected_min", [
    (1, 5),
    (2, 5),
    (3, 5)
])
def test_comments_count_for_post(base_url, post_id, expected_min):
    """Тест на проверку количества комментариев у поста"""
    response = requests.get(f"{base_url}/posts/{post_id}/comments")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    comments = response.json()
    assert len(comments) >= expected_min, f"Expected at least {expected_min} comments, got {len(comments)}"
    
    print(f"✅ Post {post_id} has {len(comments)} comments")

def test_comment_structure(base_url):
    """Тест на проверку структуры комментария"""
    response = requests.get(f"{base_url}/comments/1")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    comment = response.json()
    
    # Проверка полей и типов данных
    assert isinstance(comment['postId'], int), "postId should be integer"
    assert isinstance(comment['id'], int), "id should be integer"
    assert isinstance(comment['name'], str), "name should be string"
    assert isinstance(comment['email'], str), "email should be string"
    assert isinstance(comment['body'], str), "body should be string"
    assert '@' in comment['email'], "Email should contain @"
    
    print(f"✅ Comment structure is valid: {comment['name']}")