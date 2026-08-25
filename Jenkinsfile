pipeline {
    agent any

    stages {
        stage('Install') {
            steps {
                sh 'python -m pip install -r requirements.txt'
                sh 'python -m playwright install chromium'
            }
        }
        stage('Test') {
            steps {
                sh 'python -m pytest -n auto --html=reports/html/report.html --self-contained-html --junitxml=reports/junit.xml'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**,screenshots/**,traces/**,videos/**', allowEmptyArchive: true
            junit testResults: 'reports/junit.xml', allowEmptyResults: true
        }
    }
}
