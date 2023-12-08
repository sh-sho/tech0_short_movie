import torch
import torchvision
from torchvision import transforms, datasets
from IPython.display import Image
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import os

import json
import requests
import faiss
import numpy as np

import pickle
import streamlit as st

# set env
os.environ["VISION_ENDPOINT"] = "https://vision-movie.cognitiveservices.azure.com/"
os.environ["VISION_API_KEY"] = "6b76e18bf1ea4948a3d7b302df8ea32c"


base_folder = '../short_movie/data/data_coco'
image_folder = base_folder + "val2014/val2014/"
ann_file = base_folder + "annotations/captions_val2014.json"

transform = transforms.Compose([transforms.ToTensor()])
val_dataset = torchvision.datasets.CocoDetection(
    root=image_folder,
    annFile=ann_file,
    transform=transform
)


# # check label
# _, label = val_dataset[1]
# for l in label:
#     print(l)
# image_file_name = "COCO_val2014_" + str(label[0]["image_id"]).zfill(12) + ".jpg"
# Image(image_folder + image_file_name)



# embed image
images = []
labels = []
vectors = []
num = 2  # the number of images
for i in range(num):
    _, label = val_dataset[i]
    labels.append(label)
    image_file_name = "COCO_val2014_" + str(label[0]["image_id"]).zfill(12) + ".jpg"
    images.append(image_folder + image_file_name)  # 画像ファイルのパス

endpoint = os.getenv("VISION_ENDPOINT") + "/computervision/retrieval:vectorizeImage?api-version=2023-02-01-preview&modelVersion=latest"
headers = {
    "Content-Type": "application/octet-stream",  # リクエストボディは画像のバイナリデータ
    "Ocp-Apim-Subscription-Key": os.getenv("VISION_API_KEY")
}

for idx, image in enumerate(images):
    with open(image, mode="rb") as f:
        image_bin = f.read()
    # Vectorize Image API を使って画像をベクトル化
    response = requests.post(endpoint, headers=headers, data=image_bin)
    # print(response.json())
    image_vec = np.array(response.json()["vector"], dtype="float32").reshape(1, -1)
    vectors.append(image_vec)


# # recycle metadata
# # dump metadata
# with open("images.pkl", "wb") as f:
#     pickle.dump(images, f)

# with open("labels.pkl", "wb") as f:
#     pickle.dump(labels, f)

# with open("vectors.pkl", "wb") as f:
#     pickle.dump(vectors, f)

# # load metadata
# with open("images.pkl", "rb") as f:
#     images = pickle.load(f)

# with open("labels.pkl", "rb") as f:
#     labels = pickle.load(f)

# with open("vectors.pkl", "rb") as f:
#     vectors = pickle.load(f)

# create index
dimension = 1024
index_flat_l2 = faiss.IndexFlatL2(dimension)

for vector in vectors:
    index_flat_l2.add(vector)


# search images
def search_faiss_by_text(query_text, n=3):
    endpoint = os.getenv("VISION_ENDPOINT") + "/computervision/retrieval:vectorizeText?api-version=2023-02-01-preview&modelVersion=latest"
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": os.getenv("VISION_API_KEY")
    }
    data = {
        "text": query_text
    }
    # Vectorize Text API を使ってクエリをベクトル化
    response = requests.post(endpoint, headers=headers, data=json.dumps(data))
    query_vector = np.array(response.json()["vector"], dtype="float32").reshape(1, -1)
    # Faiss 検索
    D, I = index_flat_l2.search(query_vector, n)
    return D, I

n = 6
D, I = search_faiss_by_text("dog", n)

# streamlit view
st.title("Short Movie :movie_camera:")
img = mpimg.imread(images[I[0][0]])
st.image(img)

# Image(images[I[0][0]])


