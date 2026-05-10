pipeline {
  agent any

  options {
    buildDiscarder(logRotator(numToKeepStr: '5'))
  }

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
        withCredentials([
          file(credentialsId: 'env-dev', variable: 'ENV_FILE'),
          string(credentialsId: 'glitchtip-secret-key', variable: 'GLITCHTIP_SECRET_KEY'),
          string(credentialsId: 'glitchtip-db-password', variable: 'GLITCHTIP_DB_PASSWORD'),
        ]) {
          sh 'chmod +x scripts/deploy-server.sh'
          sh './scripts/deploy-server.sh'
        }
      }
    }
  }
}
