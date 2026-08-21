[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

function Test-CommandAvailable {
    param(
        [Parameter(Mandatory)]
        [string]$CommandName,
        [string]$InstallHint
    )

    if (-not (Get-Command $CommandName -ErrorAction SilentlyContinue)) {
        Write-Host "ERROR: '$CommandName' was not found." -ForegroundColor Red
        if ($InstallHint) {
            Write-Host $InstallHint -ForegroundColor Yellow
        }
        return $false
    }
    return $true
}

function Invoke-Pytest {
    param(
        [Parameter(Mandatory)]
        [string[]]$Arguments
    )

    if (-not (Test-CommandAvailable "python" "Install Python and ensure it is available on PATH.")) {
        return
    }

    & python -m pytest @Arguments
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Pytest finished with exit code $LASTEXITCODE." -ForegroundColor Red
    }
}

function Ensure-ReportDirectories {
    New-Item -ItemType Directory -Force -Path "reports/allure-results", "reports/allure-report", "reports/html" | Out-Null
}

function Invoke-AllureGenerate {
    if (-not (Test-CommandAvailable "allure" "Install the Allure Commandline tool and Java, then reopen PowerShell.")) {
        return
    }

    Ensure-ReportDirectories
    & allure generate reports/allure-results -o reports/allure-report --clean
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Allure report generation failed with exit code $LASTEXITCODE." -ForegroundColor Red
    }
}

function Invoke-AllureOpen {
    if (-not (Test-CommandAvailable "allure" "Install the Allure Commandline tool and Java, then reopen PowerShell.")) {
        return
    }

    if (-not (Test-Path "reports/allure-report")) {
        Write-Host "ERROR: reports/allure-report does not exist. Generate the report first." -ForegroundColor Red
        return
    }

    & allure open reports/allure-report
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Opening the Allure report failed with exit code $LASTEXITCODE." -ForegroundColor Red
    }
}

function Show-Menu {
    Write-Host ""
    Write-Host "Playwright Python POM Test Runner" -ForegroundColor Cyan
    Write-Host "=================================" -ForegroundColor Cyan
    Write-Host "1. Run All Tests"
    Write-Host "2. Run Headed Tests"
    Write-Host "3. Run OrangeHRM Login"
    Write-Host "4. Run OrangeHRM Login + Allure"
    Write-Host "5. Generate Allure Report"
    Write-Host "6. Open Allure Report"
    Write-Host "7. Generate HTML Report"
    Write-Host "8. Run Allure + HTML"
    Write-Host "9. Exit"
}

$continue = $true
while ($continue) {
    Show-Menu
    $choice = Read-Host "Select an option (1-9)"

    try {
        switch ($choice) {
            # Option 1: Run the complete pytest suite in verbose mode.
            "1" {
                Invoke-Pytest @("-v")
            }
            # Option 2: Run the complete pytest suite with a visible browser.
            "2" {
                Invoke-Pytest @("-v", "--headed")
            }
            # Option 3: Run only the OrangeHRM login test with a visible browser.
            "3" {
                Invoke-Pytest @("tests/ui/test_login.py", "-v", "--headed")
            }
            # Option 4: Run the OrangeHRM login test and write raw Allure results.
            "4" {
                Ensure-ReportDirectories
                Invoke-Pytest @("tests/ui/test_login.py", "-v", "--headed", "--alluredir=reports/allure-results")
            }
            # Option 5: Build the browsable Allure HTML report from raw results.
            "5" {
                Invoke-AllureGenerate
            }
            # Option 6: Start the local server for the generated Allure report.
            "6" {
                Invoke-AllureOpen
            }
            # Option 7: Run the OrangeHRM login test and create pytest HTML.
            "7" {
                Ensure-ReportDirectories
                Invoke-Pytest @("tests/ui/test_login.py", "-v", "--html=reports/html/report.html", "--self-contained-html")
            }
            # Option 8: Run the login test and create both Allure and pytest HTML outputs.
            "8" {
                Ensure-ReportDirectories
                Invoke-Pytest @("tests/ui/test_login.py", "-v", "--html=reports/html/report.html", "--self-contained-html", "--alluredir=reports/allure-results", "--clean-alluredir")
            }
            # Option 9: Leave the interactive runner.
            "9" {
                $continue = $false
                Write-Host "Exiting test runner." -ForegroundColor Cyan
            }
            default {
                Write-Host "Invalid option. Select a number from 1 to 9." -ForegroundColor Yellow
            }
        }
    }
    catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }

    if ($continue) {
        Read-Host "Press Enter to return to the menu"
    }
}
