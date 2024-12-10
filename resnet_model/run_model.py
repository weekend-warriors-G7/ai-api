import torch
import time

from torchvision import transforms
from sentence_transformers import util
from PIL import Image
    
class ImageSimmilarity:
    def __init__(self, model_path = r"./resnet_model/efficientnet_b1.ph"):
        self.__model = torch.load(model_path, weights_only=False)
        self.__device = device = "cuda" if torch.cuda.is_available() else "cpu"
        self.__model.to(device)
        self.__model.eval()
        
        self.__preprocess_transform = transforms.Compose([
            transforms.Resize(232),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
    def read_image(self, image_path):
        loaded_image = Image.open(image_path)
        return loaded_image.convert('RGB')
        
    def image_encode(self, image):
        # Apply the preprocessing to the image
        input_tensor = self.__preprocess_transform(image)

        # Add a batch dimension (since the model expects a batch of images)
        input_batch = input_tensor.unsqueeze(0).to(self.__device)
        
        with torch.no_grad():  # No need to track gradients for feature extraction
            extracted_features = self.__model(input_batch)
        return extracted_features.view(extracted_features.size(0), -1).squeeze()
    
    #image_simmilarity returns a value between [-1, 1], the higher, the better
    def image_simmilarity(self, img1_path, img2_path):
        img1_extracted_features = self.image_encode(self.read_image(img1_path))
        img2_extracted_features = self.image_encode(self.read_image(img2_path))

        cos_scores = util.pytorch_cos_sim(img1_extracted_features, img2_extracted_features)
        score = round(float(cos_scores[0][0]), 10)
        return score
        

def get_similarity(first: str, second: str):
    sim_class = ImageSimmilarity()

    start_time = time.time()
    result = sim_class.image_simmilarity(first, second)
    end_time = time.time()
    return result, end_time - start_time
