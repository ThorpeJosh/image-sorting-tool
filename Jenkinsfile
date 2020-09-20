pipeline {
    options {
        timeout(time: 1, unit: 'MINUTES')
        } 
    agent any

    stages {
        stage('Python Environment') {
            steps {
                sh '''
                virtualenv venv -p python3
                . venv/bin/activate
                pip install -r requirements.txt
                '''
            }
        }
        stage('Linter') {
            steps {
                sh '''
                . venv/bin/activate
                pylint image_sorting_tool/*.py
                '''
            }
        }
        stage('Unit Tests') {
            steps {
                sh '''
                . venv/bin/activate
                pytest
                '''
            }
        }
    }
}
