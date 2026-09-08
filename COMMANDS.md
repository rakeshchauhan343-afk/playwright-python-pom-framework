# Playwright Python POM - Important Commands

## 🔹 Virtual Environment

# Activate
.\.venv\Scripts\Activate.ps1

# Check Python
python --version

# Check active Python
python -c "import sys; print(sys.executable)"

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install


## 🔹 Run Tests

# Run all tests
python -m pytest -v

# Run all tests with browser
python -m pytest -v --headed

# Run Login test
python -m pytest tests/ui/test_login.py -v --headed

# Run Admin test
python -m pytest tests/ui/test_admin.py -v --headed


## 🔹 HTML Report

python -m pytest -v --html=reports/html/report.html --self-contained-html


## 🔹 Allure Report

# Run tests and generate Allure results
python -m pytest -v

# Check Allure version
allure --version

# Open Allure report
allure serve reports/allure-results

# Generate static Allure report
allure generate reports/allure-results -o reports/allure-report --clean

# Open generated report
allure open reports/allure-report


## 🔹 Clean Allure Results

Remove-Item -Recurse -Force reports/allure-results/*


## 🔹 Git - Check

git status

git branch

git remote -v


## 🔹 Git - Pull Latest Code

git pull origin main


## 🔹 Git - Add Changes

git add .


## 🔹 Git - Commit

git commit -m "Update Playwright automation framework"


## 🔹 Git - Push

git push origin main


## 🔹 Complete Daily Git Flow

git pull origin main
git status
git add .
git commit -m "Update Playwright automation framework"
git push origin main


## 🔹 First Time Git Push

git branch -M main
git remote -v
git push -u origin main


## 🔹 Debug

# Run specific test
python -m pytest tests/ui/test_login.py::test_user_can_log_in_to_orangehrm -v --headed

# Run Admin test
python -m pytest tests/ui/test_admin.py -v --headed


## 🔹 Useful Pytest Commands

# Collect tests without running
python -m pytest --collect-only

# Stop after first failure
python -m pytest -x

# Run failed tests from previous run
python -m pytest --lf

# Run tests matching keyword
python -m pytest -k "login" -v