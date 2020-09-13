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
        stage('Lint RPi Code') {
            steps {
                sh '''
                . venv/bin/activate
                pylint src/*.py
                '''
            }
        }
    }
}
