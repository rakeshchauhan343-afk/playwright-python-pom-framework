pipeline {
    agent any

    stages {

        stage('Install Dependencies') {
            steps {
                bat 'python -m pip install --upgrade pip'
                bat 'python -m pip install -r requirements.txt'
            }
        }

        stage('Install Playwright') {
            steps {
                bat 'python -m playwright install chromium'
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
                bat 'python -m pytest -v --html=reports/html/report.html --self-contained-html --junitxml=reports/junit.xml'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**,screenshots/**,traces/**,videos/**',
                             allowEmptyArchive: true

            junit testResults: 'reports/junit.xml',
                  allowEmptyResults: true

            bat 'if exist .env del /f /q .env'

            echo 'Test execution completed'
        }
    }
}
