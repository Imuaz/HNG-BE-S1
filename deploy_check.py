#!/usr/bin/env python3
"""
Deployment Verification Script
=============================
This script verifies that all critical components are working correctly
for deployment.
"""

import sys
import os
from pathlib import Path

def check_imports():
    """Check if all required modules can be imported."""
    print("🔍 Checking imports...")
    
    try:
        from app.main import app
        print("✅ FastAPI app imported successfully")
        
        from app.database import engine, get_db
        print("✅ Database components imported successfully")
        
        from app.schemas import StringCreate, StringResponse, StringListResponse, NaturalLanguageResponse
        print("✅ Pydantic schemas imported successfully")
        
        from app.crud import create_string, get_string_by_value, get_all_strings, delete_string
        print("✅ CRUD functions imported successfully")
        
        from app.analyzer import analyze_string
        print("✅ String analyzer imported successfully")
        
        from app.nlp_parser import parse_natural_language_query
        print("✅ Natural language parser imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def check_routes():
    """Check if all critical routes are registered."""
    print("\n🔍 Checking route registration...")
    
    try:
        from app.main import app
        
        critical_routes = [
            ('POST', '/strings'),
            ('GET', '/strings/filter-by-natural-language'),
            ('GET', '/strings/{string_value}'),
            ('GET', '/strings'),
            ('DELETE', '/strings/{string_value}')
        ]
        
        registered_routes = []
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                registered_routes.append((list(route.methods), route.path))
        
        all_found = True
        for method, path in critical_routes:
            found = False
            for methods, route_path in registered_routes:
                if route_path == path and method in methods:
                    found = True
                    break
            
            status = "✅" if found else "❌"
            print(f"{status} {method:6} {path}")
            if not found:
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"❌ Route check error: {e}")
        return False

def check_string_analysis():
    """Check if string analysis functions work correctly."""
    print("\n🔍 Checking string analysis...")
    
    try:
        from app.analyzer import analyze_string
        
        test_cases = [
            ("hello world", {"length": 11, "is_palindrome": False, "word_count": 2}),
            ("racecar", {"length": 7, "is_palindrome": True, "word_count": 1}),
            ("Racecar", {"length": 7, "is_palindrome": True, "word_count": 1}),
            ("", {"length": 0, "is_palindrome": True, "word_count": 0})
        ]
        
        all_correct = True
        for test_string, expected in test_cases:
            result = analyze_string(test_string)
            
            correct = True
            for key, expected_value in expected.items():
                if result[key] != expected_value:
                    correct = False
                    break
            
            status = "✅" if correct else "❌"
            print(f"{status} '{test_string}' -> {result}")
            if not correct:
                all_correct = False
        
        return all_correct
        
    except Exception as e:
        print(f"❌ String analysis error: {e}")
        return False

def check_nlp_parser():
    """Check if natural language parser works correctly."""
    print("\n🔍 Checking natural language parser...")
    
    try:
        from app.nlp_parser import parse_natural_language_query
        
        test_queries = [
            ("all single word palindromic strings", {"is_palindrome": True, "word_count": 1}),
            ("strings longer than 10 characters", {"min_length": 11}),
            ("strings containing the letter z", {"contains_character": "z"})
        ]
        
        all_correct = True
        for query, expected in test_queries:
            try:
                result = parse_natural_language_query(query)
                correct = all(result.get(k) == v for k, v in expected.items())
                status = "✅" if correct else "❌"
                print(f"{status} '{query}' -> {result}")
                if not correct:
                    all_correct = False
            except Exception as e:
                print(f"❌ '{query}' -> Error: {e}")
                all_correct = False
        
        return all_correct
        
    except Exception as e:
        print(f"❌ NLP parser error: {e}")
        return False

def check_deployment_files():
    """Check if all deployment files exist and are correct."""
    print("\n🔍 Checking deployment files...")
    
    required_files = [
        "Procfile",
        "requirements.txt", 
        "runtime.txt",
        "app/main.py",
        "app/database.py",
        "app/models.py",
        "app/schemas.py",
        "app/analyzer.py",
        "app/crud.py",
        "app/nlp_parser.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING!")
            all_exist = False
    
    return all_exist

def main():
    """Run all deployment checks."""
    print("🚀 DEPLOYMENT VERIFICATION")
    print("=" * 50)
    
    checks = [
        ("Import Check", check_imports),
        ("Route Registration", check_routes),
        ("String Analysis", check_string_analysis),
        ("NLP Parser", check_nlp_parser),
        ("Deployment Files", check_deployment_files)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} failed with error: {e}")
            results.append((check_name, False))
    
    print("\n" + "=" * 50)
    print("📊 DEPLOYMENT VERIFICATION RESULTS")
    print("=" * 50)
    
    all_passed = True
    for check_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL CHECKS PASSED - READY FOR DEPLOYMENT!")
        return 0
    else:
        print("⚠️  SOME CHECKS FAILED - FIX ISSUES BEFORE DEPLOYMENT")
        return 1

if __name__ == "__main__":
    sys.exit(main())




