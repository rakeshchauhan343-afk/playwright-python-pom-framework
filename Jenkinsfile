pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Code is already checked out by Jenkins'
            }
        }

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

        stage('Run Tests') {
            steps {
                bat 'pytest'
            }
        }
    }

    post {
        always {
            echo 'Test execution completed'
        }
    }
}
