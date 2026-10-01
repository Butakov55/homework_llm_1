#!/usr/bin/env python3
"""
Скрипт для генерации автотестов с помощью Ollama
"""

import json
import requests
import os
import time
import sys

def wait_for_ollama():
    """Ожидание готовности Ollama"""
    url = "http://ollama:11434/api/generate"
    max_attempts = 30
    attempt = 0
    
    print("⏳ Waiting for Ollama to be ready...")
    
    while attempt < max_attempts:
        try:
            response = requests.post(url, json={
                "model": "codellama:7b-code",
                "prompt": "ping",
                "stream": False
            }, timeout=5)
            if response.status_code == 200:
                print("✅ Ollama is ready")
                return True
        except:
            pass
        
        attempt += 1
        print(f"⏳ Waiting... ({attempt}/{max_attempts})")
        time.sleep(2)
    
    return False

def generate_tests():
    """Генерация тестов с помощью Ollama"""
    print("\n" + "="*60)
    print("🚀 Starting test generation with Ollama...")
    print("="*60 + "\n")
    
    if not wait_for_ollama():
        print("❌ Ollama is not responding. Make sure it's running.")
        return False
    
    # Читаем промпт
    prompt_file = 'prompts/generate_tests.txt'
    if not os.path.exists(prompt_file):
        print(f"❌ Prompt file not found: {prompt_file}")
        return False
    
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt = f.read()
    
    print("\n📝 Sending prompt to Ollama...")
    print(f"📄 Prompt length: {len(prompt)} characters")
    
    # Отправляем запрос к Ollama
    try:
        response = requests.post('http://ollama:11434/api/generate', json={
            "model": "codellama:7b-code",
            "prompt": prompt,
            "stream": False,
            "temperature": 0.3,
            "top_p": 0.9,
            "max_tokens": 3000
        }, timeout=120)
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        result = response.json()
        generated_code = result.get('response', '')
        
        # Сохраняем сгенерированный код
        output_file = 'tests/generated_tests.py'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(generated_code)
        
        print(f"\n✅ Tests generated and saved to {output_file}")
        print("\n📋 Generated code preview:")
        print("="*60)
        preview = generated_code[:800] + "..." if len(generated_code) > 800 else generated_code
        print(preview)
        print("="*60)
        
        return True
        
    except requests.exceptions.Timeout:
        print("❌ Timeout waiting for Ollama response")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = generate_tests()
    sys.exit(0 if success else 1)