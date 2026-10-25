pipeline {
    agent any

    environment {
        IMAGE_NAME     = "flask-devops-app"
        CONTAINER_NAME = "flask-app"
        APP_PORT       = "5000"
        HOST_PORT      = "5000"
    }

    stages {

        // ------------------------------------------------------------------
        // Stage 1 – Checkout
        // ------------------------------------------------------------------
        stage('Checkout') {
            steps {
                echo "========== Stage: Checkout =========="
                checkout scm
                echo "Source code checked out successfully."
            }
        }

        // ------------------------------------------------------------------
        // Stage 2 – Install Dependencies
        // ------------------------------------------------------------------
        stage('Install Dependencies') {
            steps {
                echo "========== Stage: Install Dependencies =========="
                sh '''
                    python3 -m pip install -r requirements.txt --break-system-packages -q
                    echo "Dependencies installed."
                    python3 -m pip show flask pytest
                '''
            }
        }

        // ------------------------------------------------------------------
        // Stage 3 – Run Tests
        // ------------------------------------------------------------------
        stage('Run Tests') {
            steps {
                echo "========== Stage: Run Tests =========="
                sh 'python3 -m pytest test_app.py -v --tb=short'
            }
        }

        // ------------------------------------------------------------------
        // Stage 4 – Build Docker Image
        // ------------------------------------------------------------------
        stage('Build Docker Image') {
            steps {
                echo "========== Stage: Build Docker Image =========="
                sh '''
                    docker build -t ${IMAGE_NAME}:latest .
                    echo "Docker image built: ${IMAGE_NAME}:latest"
                '''
            }
        }

        // ------------------------------------------------------------------
        // Stage 5 – Deploy Container
        // ------------------------------------------------------------------
        stage('Deploy Container') {
            steps {
                echo "========== Stage: Deploy Container =========="
                sh '''
                    docker stop ${CONTAINER_NAME} 2>/dev/null || true
                    docker rm   ${CONTAINER_NAME} 2>/dev/null || true

                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p ${HOST_PORT}:${APP_PORT} \
                        --restart unless-stopped \
                        ${IMAGE_NAME}:latest

                    echo "Container '${CONTAINER_NAME}' started on port ${HOST_PORT}."
                '''
            }
        }

        // ------------------------------------------------------------------
        // Stage 6 – Verify Deployment
        // ------------------------------------------------------------------
        stage('Verify Deployment') {
            steps {
                echo "========== Stage: Verify Deployment =========="
                sh '''
                    sleep 5

                    HTTP_CODE=$(curl -s -o /tmp/health_response.txt -w "%{http_code}" \
                        http://host.docker.internal:${HOST_PORT}/health)

                    echo "Health endpoint response:"
                    cat /tmp/health_response.txt
                    echo ""

                    if [ "$HTTP_CODE" = "200" ]; then
                        echo "Deployment verified successfully (HTTP 200)."
                    else
                        echo "Health check failed (HTTP ${HTTP_CODE})."
                        exit 1
                    fi
                '''
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully! Flask app is live on port ${HOST_PORT}."
        }
        failure {
            echo "Pipeline failed. Check the stage logs above for details."
        }
    }
}
