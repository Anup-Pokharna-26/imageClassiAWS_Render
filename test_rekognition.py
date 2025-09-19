import boto3

# Rekognition client
rekognition = boto3.client("rekognition", region_name="us-east-1")

with open("burger.jpg", "rb") as img:  # replace with your food image
    response = rekognition.detect_labels(
        Image={"Bytes": img.read()},
        MaxLabels=5,
        MinConfidence=70
    )

print("Detected labels:")
for label in response["Labels"]:
    print(f"{label['Name']} ({label['Confidence']:.2f}%)")
