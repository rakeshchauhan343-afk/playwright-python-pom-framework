pipeline {
    agent any

    stages {
<<<<<<< HEAD
        stage('Install') {
            steps {
                sh 'python -m pip install -r requirements.txt'
                sh 'python -m playwright install chromium'
            }
        }
        stage('Test') {
            steps {
                sh 'python -m pytest -n auto --html=reports/html/report.html --self-contained-html --junitxml=reports/junit.xml'
=======

        stage('Install Dependencies') {
            steps {
                bat 'python -m pip install --upgrade pip'
                bat 'pip install -r requirements.txt'
            }
        }

        stage('Install Playwright') {
            steps {
                bat 'python -m playwright install'
            }
        }

        stage('Create Environment') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'orangehrm-credentials',
                        usernameVariable: 'ORANGEHRM_USER',
                        passwordVariable: 'ORANGEHRM_PASS'
                    )
                ]) {
                    powershell '''
                        @"
ORANGEHRM_URL=https://opensource-demo.orangehrmlive.com/web/index.php/auth/login
ORANGEHRM_USERNAME=$env:ORANGEHRM_USER
ORANGEHRM_PASSWORD=$env:ORANGEHRM_PASS
"@ | Set-Content .env
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                bat 'pytest'
>>>>>>> b1d7f85b35e6b497e06ac64b764f537e910ce603
            }
        }
    }

    post {
        always {
<<<<<<< HEAD
            archiveArtifacts artifacts: 'reports/**,screenshots/**,traces/**,videos/**', allowEmptyArchive: true
            junit testResults: 'reports/junit.xml', allowEmptyResults: true
=======
            bat 'if exist .env del /f /q .env'
            echo 'Test execution completed'
>>>>>>> b1d7f85b35e6b497e06ac64b764f537e910ce603
        }
    }
}
