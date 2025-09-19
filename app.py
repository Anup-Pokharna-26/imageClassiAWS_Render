from flask import Flask, request, render_template, jsonify
import boto3

app = Flask(__name__)

# Initialize Rekognition client
rekognition = boto3.client("rekognition", region_name="ap-south-1",)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/classify", methods=["POST"])
def classify():
    file = request.files["image"]
    image_bytes = file.read()
    model_type = request.form.get("model", "default")

    if model_type == "custom":
        response = rekognition.detect_custom_labels(
            ProjectVersionArn="arn:aws:rekognition:ap-south-1:891335233860:project/indianfood/version/indianfood.2025-09-19T18.05.02/1758285303156",
            Image={"Bytes": image_bytes},
            MinConfidence=70
        )
        labels = [label["Name"] for label in response.get("CustomLabels", [])]
    else:
        response = rekognition.detect_labels(
            Image={"Bytes": image_bytes},
            MaxLabels=5,
            MinConfidence=70
        )
        labels = [label["Name"] for label in response["Labels"]]
    return jsonify({"labels": labels})

if __name__ == "__main__":
    app.run(debug=True)
