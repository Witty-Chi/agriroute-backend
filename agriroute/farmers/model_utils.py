import torch
import os
import torch.nn as nn
from torchvision import transforms
from PIL import Image
#from plant_disease_model import SimpleCNN

class SimpleCNN(nn.Module):
    def __init__(self, num_classes=5):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(16 * 112 * 112, num_classes)

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = x.view(-1, 16 * 112 * 112)
        return self.fc1(x)

# Load the model
model = SimpleCNN(num_classes=5)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "plant_disease_model.pth") # plant-disease-model-complete

model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
model.eval()

# Class labels
class_labels = ['Late Blight', 'Mosaic Virus', 'Rust', 'Healthy', 'Leaf Spot']


# Add corresponding cause & treatment info
disease_info = {
    "Late Blight": {
        "cause": "Caused by Phytophthora infestans in cool, wet weather.",
        "treatment": "Use copper fungicides and destroy infected plants."
    },
    "Mosaic Virus": {
        "cause": "Viral infection spread by aphids or infected tools.",
        "treatment": "Remove infected plants and control insect vectors."
    },
    "Rust": {
        "cause": "Fungal spores that thrive in moist conditions.",
        "treatment": "Apply sulfur-based fungicides and prune infected leaves."
    },
    "Healthy": {
        "cause": "No disease detected.",
        "treatment": "Maintain regular care and monitoring."
    },
    "Leaf Spot": {
        "cause": "Caused by bacteria or fungi due to water splash.",
        "treatment": "Avoid overhead watering, apply appropriate fungicides."
    },
}

# Prediction function
def predict_disease(image_file):
    image = Image.open(image_file).convert("RGB")
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor()
    ])
    input_tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        output = model(input_tensor)
        probabilities = torch.softmax(output, dim=1)[0]
        top3 = torch.topk(probabilities, 3)
        return [
            {
                "name": class_labels[i],
                "confidence": round(probabilities[i].item() * 100, 2),
                "cause": disease_info[class_labels[i]]["cause"],
                "treatment": disease_info[class_labels[i]]["treatment"]
            }
            for i in top3.indices
        ]
