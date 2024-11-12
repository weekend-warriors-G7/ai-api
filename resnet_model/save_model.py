import torch
import torchvision.models as models
from torchvision import transforms
from sentence_transformers import util
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"
model = models.efficientnet_b0(weights="EfficientNet_B0_Weights.IMAGENET1K_V1")
model.to(device)
model.eval()

model = torch.nn.Sequential(*list(model.children())[:-1])

print(model)

preprocess_transform = transforms.Compose([
    transforms.Resize(232),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

def image_encoder(image_path):
    # Load the image (replace with your own image path)
    img = Image.open(image_path)
    img.show()

    # Apply the preprocessing to the image
    input_tensor = preprocess_transform(img)

    # Add a batch dimension (since the model expects a batch of images)
    input_batch = input_tensor.unsqueeze(0)
    input_batch.to(device)
    
    with torch.no_grad():  # No need to track gradients for feature extraction
        features = model(input_batch)
    return features.view(features.size(0), -1).squeeze()

    
def image_simmilarity(img1, img2):
    cos_scores = util.pytorch_cos_sim(image_encoder(img1), image_encoder(img2))
    score = round(float(cos_scores[0][0])*100, 2)
    return score
    

# The output is a 4D tensor: (batch_size, channels, height, width)
# Since we've removed the fully connected layer, we should have (batch_size, channels, 1, 1)
# You can flatten the output to get the feature vector (1D vector)
#feature_vector = features.view(features.size(0), -1).squeeze()

if __name__ == "__main__":
    torch.save(model, r"./efficientnet_b0.ph")
    print(image_simmilarity("piele.png", "textila.png"))
