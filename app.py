from flask import Flask, jsonify

app = Flask(__name__)

APP_VERSION = "1.0.0"


@app.route("/")
def home():
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 80px;">
        <h1>🚀 Flask DevOps Demo</h1>
        <p>Automated Deployment using Jenkins &amp; Docker</p>
        <p><strong>Version:</strong> {APP_VERSION}</p>
        <p><em>Deployed via Jenkins CI/CD Pipeline</em></p>
      </body>
    </html>
    """


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "version": APP_VERSION}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
