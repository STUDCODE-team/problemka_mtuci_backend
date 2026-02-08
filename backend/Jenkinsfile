pipeline {
  agent any

  triggers {
    githubPush()
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Deploy (dev)') {
      // when {
      //   branch 'dev'
      // }
      steps {
        dir('backend') {
          withCredentials([file(credentialsId: 'env-dev', variable: 'ENV_FILE')]) {
            sh 'chmod +x scripts/deploy-server.sh'
            sh './scripts/deploy-server.sh'
          }
        }
      }
    }
  }
}
