#!/usr/bin/env python3
"""
Setup validation script - Run this to check if everything is configured correctly.
"""
import sys
import os


def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print("✓ Python version:", f"{version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print("✗ Python 3.8+ required. Current:", f"{version.major}.{version.minor}.{version.micro}")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    required = [
        'selenium',
        'beautifulsoup4',
        'requests',
        'dotenv',
        'lxml',
        'webdriver_manager'
    ]

    all_installed = True
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package} installed")
        except ImportError:
            print(f"✗ {package} NOT installed")
            all_installed = False

    return all_installed


def check_env_file():
    """Check if .env file exists"""
    if os.path.exists('.env'):
        print("✓ .env file exists")

        # Check if required variables are set
        from dotenv import load_dotenv
        load_dotenv()

        required_vars = [
            'SENDER_EMAIL',
            'SENDER_PASSWORD',
            'MARKETPLACE_URL',
            'MESSAGE_BODY'
        ]

        all_set = True
        for var in required_vars:
            value = os.getenv(var)
            if value and value.strip():
                print(f"  ✓ {var} is set")
            else:
                print(f"  ✗ {var} is NOT set")
                all_set = False

        return all_set
    else:
        print("✗ .env file NOT found")
        print("  → Run: cp .env.example .env")
        return False


def check_chrome():
    """Check if Chrome/Chromium is available"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.quit()

        print("✓ Chrome/ChromeDriver working")
        return True
    except Exception as e:
        print(f"✗ Chrome/ChromeDriver issue: {e}")
        return False


def main():
    """Run all checks"""
    print("="*60)
    print("AUTOMATED MESSAGING BOT - SETUP VALIDATION")
    print("="*60)
    print()

    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment File", check_env_file),
        ("Chrome Browser", check_chrome),
    ]

    results = []

    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 60)
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Error during check: {e}")
            results.append((name, False))

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} - {name}")
        if not result:
            all_passed = False

    print("="*60)

    if all_passed:
        print("\n🎉 All checks passed! You're ready to run the bot.")
        print("\nNext steps:")
        print("  python main.py --interactive")
    else:
        print("\n⚠ Some checks failed. Please fix the issues above.")
        print("\nQuick fixes:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Create .env file: cp .env.example .env")
        print("  3. Edit .env with your settings")

    print()


if __name__ == '__main__':
    main()
