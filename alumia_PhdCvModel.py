import torch
from torchvision import transforms
from utils.datasets import letterbox
from utils.general import non_max_suppression_kpt
from utils.plots import output_to_keypoint, plot_skeleton_kpts
import cv2
import numpy as np

BASE_PATH = 'BASE_PATH_HERE' 

class PhdCvModel():

    def __init__(self):

        self.roi_error_margin = 20

        #LOAD MODEL
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model = torch.load(BASE_PATH + 'experimental_system/models/yolov7-w6-pose.pt', map_location=self.device)['model']

        #Put in inference mode
        self.model.float().eval()
        if torch.cuda.is_available():
            # half() turns predictions into float16 tensors
            # which significantly lowers inference time
            self.model.half().to(self.device)

        test_image = cv2.imread(BASE_PATH + 'experimental_system/utils/models_test_image.jpg')
        self.infer(test_image)

    def output_to_keypoints(self, model_output):

        work_output = non_max_suppression_kpt(model_output, 
                                     0.25, # Confidence Threshold
                                     0.65, # IoU Threshold
                                     nc=self.model.yaml['nc'], # Number of Classes
                                     nkpt=self.model.yaml['nkpt'], # Number of Keypoints
                                     kpt_label=True)
  
  
        with torch.no_grad():
            final_output = output_to_keypoint(work_output)

        if final_output.shape[0] != 0: # model detected a human

            just_kp = final_output[0, 7:].T
            just_kp[0::3] = (just_kp[0::3]/959)*1919
            just_kp[1::3] = (just_kp[1::3]/575)*1079

            just_box = final_output[0, 2:7].T
            just_box[0] = just_box[0]/959
            just_box[1] = just_box[1]/575

            just_box[2] = (1919*just_box[2])/959
            just_box[3] = (1079*just_box[3])/575

            bbox_x1 = int(just_box[0]*1919-just_box[2]/2)
            bbox_x2 = int(just_box[0]*1919+just_box[2]/2)
            bbox_y1 = int(just_box[1]*1079-just_box[3]/2)
            bbox_y2 = int(just_box[1]*1079+just_box[3]/2)
            
            '''
            #ADD THE MARGIN
            if bbox_x1 >= self.roi_error_margin:
                bbox_x1 = bbox_x1 - self.roi_error_margin
            else:
                bbox_x1 = 0
            
            if bbox_y1 >= self.roi_error_margin:
                bbox_y1 = bbox_y1 - self.roi_error_margin
            else:
                bbox_y1 = 0
            
            if 1919 - bbox_x2 >= self.roi_error_margin:
                bbox_x2 = bbox_x2 + self.roi_error_margin
            else:
                bbox_x2 = 1919
            
            if 1079 - bbox_y2 >= self.roi_error_margin:
                bbox_y2 = bbox_y2 + self.roi_error_margin
            else:
                bbox_y2 = 1079
            '''
        else: # no human detected

            bbox_x1 = 0
            bbox_y1 = 0
            bbox_x2 = 1919
            bbox_y2 = 1079

            just_kp = np.zeros((51,))

        bbox_points = [bbox_x1/1919, bbox_x2/1919, bbox_y1/1079, bbox_y2/1079]
        just_kp = np.reshape(just_kp, (-1, 3))

        return just_kp, bbox_points


    def infer(self, input_frame):        
        
        # Resize and pad image
        image = letterbox(input_frame, 960, stride=64, auto=True)[0] # shape: (576, 960, 3)
        # Apply transforms
        image = transforms.ToTensor()(image) # torch.Size([3, 576, 960])
        if torch.cuda.is_available():
            image = image.half().to(self.device)
        # Turn image into batch
        image = image.unsqueeze(0) # torch.Size([1, 3, 576, 960])

        with torch.no_grad():
            model_output, _ = self.model(image)

        pose_est_output, roi_output = self.output_to_keypoints(model_output)

        return pose_est_output, roi_output