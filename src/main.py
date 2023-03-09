from flask import Flask, request
from PIL import Image
import numpy as np
import cv2
import torch
from utils.feature_extractor import featureExtractor
from utils.data_loader import TestDataset 
from torch.utils.data import Dataset, DataLoader

app = Flask(__name__)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
trained_model = torch.load('./trained_model/trained_model')
trained_model = trained_model['model_state']


def is_image_blurry(trained_model, img, threshold=0.5):
    feature_extractor = featureExtractor()
    accumulator = []

    # Resize the image by the downsampling factor
    feature_extractor.resize_image(img, np.shape(img)[0], np.shape(img)[1])

    # compute the image ROI using local entropy filter
    feature_extractor.compute_roi()

    # extract the blur features using DCT transform coefficients
    extracted_features = feature_extractor.extract_feature()
    extracted_features = np.array(extracted_features)

    if(len(extracted_features) == 0):
        return True
    test_data_loader = DataLoader(TestDataset(extracted_features), batch_size=1, shuffle=False)

    # trained_model.test()
    for batch_num, input_data in enumerate(test_data_loader):
        x = input_data
        x = x.to(device).float()

        output = trained_model(x)
        _, predicted_label = torch.max(output, 1)
        accumulator.append(predicted_label.item())

    prediction= np.mean(accumulator) < threshold
    return(prediction)


@app.route('/check_image', methods=["POST"])
def process_image():
    app.logger.debug('process_image() start!')
    file = request.files['image']
    app.logger.debug('Image (%s)',request.files['image'])
    img = Image.open(file.stream)
    img1 = np. array(img) 
    img1 = cv2.cvtColor(img1 , cv2.COLOR_BGR2GRAY)
    app.logger.debug('Image begin teste!')
    if not is_image_blurry(trained_model, img1,threshold=0.5):
        app.logger.debug('TesteOK!')
        return "OK"
    else:
        app.logger.debug('TesteNOK!')
        return "NOK"
    
@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=88,debug=True)
   # serve(app, host='0.0.0.0', port=87)


