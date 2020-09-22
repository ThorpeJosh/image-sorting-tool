pipeline {
    options {
        timeout(time: 10, unit: 'MINUTES')
        } 
    agent any

    stages {
        stage('Python Environment') {
            steps {
                sh '''
                virtualenv venv -p python3
                . venv/bin/activate
                pip install .[dev]
                '''
            }
        }
        stage('Linter') {
            steps {
                sh '''
                . venv/bin/activate
                pylint image_sorting_tool/*.py
                pylint image_sorting_tool/tests/*.py
                '''
            }
        }
        stage('Unit Tests') {
            steps {
                sh '''
                . venv/bin/activate
                tox
                '''
            }
        }
    }
}
