pipeline {
    agent any

    environment {
        IMAGE_NAME    = "flask-devops-app"
        CONTAINER_NAME = "flask-app"
        APP_PORT      = "5000"
        HOST_PORT     = "5000"
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
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    echo "Dependencies installed."
                '''
            }
        }

        // ------------------------------------------------------------------
        // Stage 3 – Run Tests
        // ------------------------------------------------------------------
        stage('Run Tests') {
            steps {
                echo "========== Stage: Run Tests =========="
                sh '''
                    . venv/bin/activate
                    pytest test_app.py -v --tb=short
                '''
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
                    # Stop and remove any existing container (idempotent)
                    docker stop ${CONTAINER_NAME} 2>/dev/null || true
                    docker rm   ${CONTAINER_NAME} 2>/dev/null || true

                    # Run the new container
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
                    # Give the container a moment to start
                    sleep 5

                    # Curl the health endpoint from inside the Jenkins container.
                    # The Flask container is on the Docker host network, so we
                    # use host.docker.internal (resolves to the Docker host).
                    HTTP_CODE=$(curl -s -o /tmp/health_response.txt -w "%{http_code}" \
                        http://host.docker.internal:${HOST_PORT}/health)

                    echo "Health endpoint response:"
                    cat /tmp/health_response.txt
                    echo ""

                    if [ "$HTTP_CODE" = "200" ]; then
                        echo "✅ Deployment verified successfully (HTTP 200)."
                    else
                        echo "❌ Health check failed (HTTP ${HTTP_CODE})."
                        exit 1
                    fi
                '''
            }
        }
    }

    // ------------------------------------------------------------------
    // Post-build notifications
    // ------------------------------------------------------------------
    post {
        success {
            echo "✅ Pipeline completed successfully! Flask app is live on port ${HOST_PORT}."
        }
        failure {
            echo "❌ Pipeline failed. Check the stage logs above for details."
        }
        always {
            // Clean up the Python virtual environment to keep the workspace tidy
            sh 'rm -rf venv || true'
        }
    }
}
