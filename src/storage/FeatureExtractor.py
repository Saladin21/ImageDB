import cv2
import numpy as np
import timm
import torchvision.transforms as transforms
import torch
import datetime
import os
from ultralytics import YOLO
from transformers import AutoTokenizer, CLIPModel, AutoProcessor
from PIL import Image

class FeatureExtractor():
    def __init__(self, id, name, supported_pred, feature_dim):
        self.id = id
        self.name = name
        self.supported_pred = supported_pred
        self.feature_dim = feature_dim
    # abstract method
    def extract(self, input, pred):
        #input: visually_similar : path, semantically_similar: text, contains : text 
        if pred not in self.supported_pred:
            raise AssertionError("Operation not supported")
    def extractImage(self, input):
        #input path image, for creating index
        return self.extract(input)
    def __call__(self, input, pred):
        return self.extract(input, pred)

    
class SIFTFeatureExtractor(FeatureExtractor):
    def __init__(self, vector_size=32):
        super().__init__(0, name='SIFT', supported_pred=['visually_similar'], feature_dim=4096)
        self.sift = cv2.SIFT_create()
        self.vector_size = vector_size

    def extract(self, input, pred='visually_similar'):
                # Dinding image keypoints
        im = cv2.imread(input, cv2.IMREAD_COLOR)
        kps = self.sift.detect(im)
        # Getting first 32 of them. 
        # Number of keypoints is varies depend on image size and color pallet
        # Sorting them based on keypoint response value(bigger is better)
        kps = sorted(kps, key=lambda x: -x.response)[:self.vector_size]
        # computing descriptors vector
        kps, dsc = self.sift.compute(im, kps)
        # Flatten all of them in one big vector - our feature vector
        dsc = dsc.flatten()
        # Making descriptor of same size
        # Descriptor vector size is 64
        needed_size = (self.vector_size * 64)
        if dsc.size < needed_size:
            # if we have less the 32 descriptors then just adding zeros at the
            # end of our feature vector
            dsc = np.concatenate([dsc, np.zeros(needed_size - dsc.size)])
        return dsc
    
class KAZEFeatureExtractor(FeatureExtractor):
    def __init__(self, vector_size=32):
        super().__init__(1, name='KAZE', supported_pred=['visually_similar'], feature_dim=2048)
        self.kaze = cv2.KAZE_create()
        self.vector_size = vector_size

    def extract(self, input, pred='visually_similar'):
                # Dinding image keypoints
        im = cv2.imread(input, cv2.IMREAD_COLOR)
        kps = self.kaze.detect(im)
        # Getting first 32 of them. 
        # Number of keypoints is varies depend on image size and color pallet
        # Sorting them based on keypoint response value(bigger is better)
        kps = sorted(kps, key=lambda x: -x.response)[:self.vector_size]
        # computing descriptors vector
        kps, dsc = self.kaze.compute(im, kps)
        # Flatten all of them in one big vector - our feature vector
        dsc = dsc.flatten()
        # Making descriptor of same size
        # Descriptor vector size is 64
        needed_size = (self.vector_size * 64)
        if dsc.size < needed_size:
            # if we have less the 32 descriptors then just adding zeros at the
            # end of our feature vector
            dsc = np.concatenate([dsc, np.zeros(needed_size - dsc.size)])
        return dsc

class EfficientNetB2FeatureExtractor(FeatureExtractor):
    def __init__(self):
        super().__init__(2, name='EFFICIENTNETB2', supported_pred=['visually_similar'], feature_dim=68992)
        self.model = timm.create_model('tf_efficientnet_b2', pretrained=True)

    def extract(self, input, pred='visually_similar'):
        image = cv2.imread(input, cv2.IMREAD_COLOR)
        image = cv2.resize(image, (224,224))
        image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)

        # Define a transform to convert the image to tensor
        transform = transforms.ToTensor()

        # Convert the image to PyTorch tensor
        tensor = transform(image)
        tensor = torch.unsqueeze(tensor, 0)
        feature = self.model.forward_features(tensor)

        return feature.detach().cpu().numpy()[0].flatten()
    
class EfficientNetB5FeatureExtractor(FeatureExtractor):
    def __init__(self):
        super().__init__(5, name='EFFICIENTNETB5', supported_pred=['visually_similar'], feature_dim=100352)
        self.model = timm.create_model('tf_efficientnet_b5', pretrained=True)

    def extract(self, input, pred='visually_similar'):
        image = cv2.imread(input, cv2.IMREAD_COLOR)
        image = cv2.resize(image, (224,224))
        image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)

        # Define a transform to convert the image to tensor
        transform = transforms.ToTensor()

        # Convert the image to PyTorch tensor
        tensor = transform(image)
        tensor = torch.unsqueeze(tensor, 0)
        feature = self.model.forward_features(tensor)

        return feature.detach().cpu().numpy()[0].flatten()
    

class ClipFeatureExtractor(FeatureExtractor):
    def __init__(self):
        super().__init__(3, name='CLIP', supported_pred=['VISUALLY_SIMILAR', 'SEMANTICALLY_SIMILAR'], feature_dim=512)

        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.tokenizer = AutoTokenizer.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = AutoProcessor.from_pretrained("openai/clip-vit-base-patch32")
    def extractImage(self, input):
        image = Image.open(input)
        inputs = self.processor(images=image, return_tensors="pt")
        image_features = self.model.get_image_features(**inputs)
        return image_features.detach().cpu().numpy()[0].flatten()
    def extract(self, input, pred):
        if pred == 'VISUALLY_SIMILAR':
            return self.extractImage(input[0])
        elif pred =='SEMANTICALLY_SIMILAR':
            inputs = self.tokenizer(input[0], padding=True, return_tensors="pt")
            text_features = self.model.get_text_features(**inputs)
            return text_features.detach().cpu().numpy()[0].flatten()
        
class YOLOv8FeatureExtractor(FeatureExtractor):
    def __init__(self):
        super().__init__(4, name='YOLOV8', supported_pred=['CONTAINS'], feature_dim=80)
        self.model = YOLO('yolov8n.pt')
    def extractImage(self, input):
        res = self.model(input, verbose=False)
        vec = np.zeros(len(self.model.names),dtype="float32")
        for i in res[0].boxes.cls:
            vec[int(i)] = 1
        return vec
    def extract(self, input, pred):
        if pred == 'CONTAINS':
            res = np.zeros(len(self.model.names),dtype="float32")
            for k,v in self.model.names.items():
                if v == input[0]:
                    res[k] = 1
                    return res
            #assert input not supported

class YOLOv8LeftFeatureExtractor(FeatureExtractor):
    def __init__(self):
        super().__init__(6, name='YOLOV8LEFT', supported_pred=['LEFT'], feature_dim=6400)
        self.model = YOLO('yolov8n.pt')
    def extractImage(self, input):
        res = self.model(input, verbose=False)
        cls = [int(o.item()) for o in res[0].boxes.cls]
        vec = np.array([[0 for i in range(len(res[0].names))] for i in range(len(res[0].names))], dtype="float32")
        for i in range (len(cls)):
            for j in range(i+1, len(cls)):

                if res[0].boxes.xyxy[i][2] < res[0].boxes.xyxy[j][0]:
                    vec[cls[i]][cls[j]] = 1
                elif res[0].boxes.xyxy[j][2] < res[0].boxes.xyxy[i][0]:
                    vec[cls[j]][cls[i]] = 1
        return vec.flatten()
    def extract(self, input, pred):
        if pred == 'LEFT':
            vec = np.array([[0 for i in range(len(self.model.names))] for i in range(len(self.model.names))], dtype="float32")
            for k,v in self.model.names.items():
                if v == input[0]:
                    l = k
                if v == input[1]:
                    r = k
            vec[l][r] = 1
            return vec.flatten()

class YOLOv8AboveFeatureExtractor(FeatureExtractor):
    def __init__(self):
        super().__init__(7, name='YOLOV8ABOVE', supported_pred=['ABOVE'], feature_dim=6400)
        self.model = YOLO('yolov8n.pt')
    def extractImage(self, input):
        res = self.model(input, verbose=False)
        cls = [int(o.item()) for o in res[0].boxes.cls]
        vec = np.array([[0 for i in range(len(res[0].names))] for i in range(len(res[0].names))], dtype="float32")
        for i in range (len(cls)):
            for j in range(i+1, len(cls)):

                if res[0].boxes.xyxy[i][3] > res[0].boxes.xyxy[j][1]:
                    vec[cls[i]][cls[j]] = 1
                elif res[0].boxes.xyxy[j][3] > res[0].boxes.xyxy[i][1]:
                    vec[cls[j]][cls[i]] = 1
        return vec.flatten()
    def extract(self, input, pred):
        if pred == 'ABOVE':
            vec = np.array([[0 for i in range(len(self.model.names))] for i in range(len(self.model.names))], dtype="float32")
            for k,v in self.model.names.items():
                if v == input[0]:
                    l = k
                if v == input[1]:
                    r = k
            vec[l][r] = 1
            return vec.flatten()

class MetadataFeatureExtractor(FeatureExtractor):
    def __init__(self):
        super().__init__(5, name='META', supported_pred=['date', 'height', 'width', 'extension'], feature_dim=None)
    def extract(self, input, pred='METADATA'):
        # Dic={}

        # exeProcess = "hachoir-metadata"
        # process = subprocess.Popen([exeProcess,input],
        #                         stdout=subprocess.PIPE,
        #                         stderr=subprocess.STDOUT,
        #                         universal_newlines=True)
        # Dic={}

        # for tag in process.stdout:
        #         line = tag.strip().split(':')
        #         Dic[line[0].strip()] = line[-1].strip()

        im = cv2.imread(input)
        height, width, _ =im.shape

        result = {
            'name' : os.path.basename(input),
            'date' : datetime.datetime.fromtimestamp(os.path.getmtime(input)).date().isoformat(),
            'height' : height,
            'width' : width,
            'extension' : input.split('/')[-1].split(".")[-1]
        }
        
        return result

class FEFactory():
    def __init__(self) :
        self.registry = {
            "META" : {
                "class" : MetadataFeatureExtractor,
                "ops" : ["METADATA"]
            },
            "SIFT" : {
                "class" : SIFTFeatureExtractor,
                "ops" : ["VISUALLY_SIMILAR"]
            },
            "KAZE" : {
                "class" : KAZEFeatureExtractor,
                "ops" : ["VISUALLY_SIMILAR"]
            },
            "EFFICIENTNETB2" : {
                "class" : EfficientNetB2FeatureExtractor,
                "ops" : ["VISUALLY_SIMILAR"]
            },
            "EFFICIENTNETB5" : {
                "class" : EfficientNetB5FeatureExtractor,
                "ops" : ["VISUALLY_SIMILAR"]
            },
            "CLIP" : {
                "class" : ClipFeatureExtractor,
                "ops" : ["VISUALLY_SIMILAR", "SEMANTICALLY_SIMILAR"]
            },
            "YOLOV8" : {
                "class" : YOLOv8FeatureExtractor,
                "ops" : ["CONTAINS"]
            },
            "YOLOV8LEFT" : {
                "class" : YOLOv8LeftFeatureExtractor,
                "ops" : ["LEFT"]
            },
            "YOLOV8ABOVE" : {
                "class" : YOLOv8AboveFeatureExtractor,
                "ops" : ["ABOVE"]
            },

        }
        self.FE = {}
    def getFE(self, id) -> FeatureExtractor: 
        if self.FE.get(id) == None:
            self.FE[id] = self.registry[id]['class']()
        return self.FE[id] 
    def listFE(self):
        res = []
        for k, v in self.registry.items():
            if k != 'META':
                res.append({
                    "name" : k,
                    "ops" : v['ops']
                })
        return res
