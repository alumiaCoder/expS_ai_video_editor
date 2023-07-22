import cv2
import numpy as np

class ImageProcessingTools:
    '''A set of processing tools, mostly based on OpenCV, to pre and post-process frames.
    - These are tools mostly used for object detection and pose estimation models'''

    def crop_frame(self, input_frame, crop_points):
        '''Crops an image according to the crop_points values.
        - Crop points is a list values normalized to 1 for each point. (x_min, x_max, y_min, y_max)'''

        original_width = input_frame.shape[1]
        original_height = input_frame.shape[0]
        
        x_min = int(original_width*crop_points[0])
        x_max = int(original_width*crop_points[1])
        
        y_min = int(original_height*crop_points[2])
        y_max = int(original_height*crop_points[3])


        cropped_image = input_frame[y_min:y_max, x_min:x_max]   

        return cropped_image


    def pad_frame(self, input_frame, new_dimensions):
        '''Pads an image to a given dimension.
        - new_dimension is a tupple with the new x and y dimensions = (new_width, new_height)
        - This function should come after a resize, since the image has to be smaller or equal to the new pad dimensions'''

        original_width = input_frame.shape[1]
        original_height = input_frame.shape[0]

        resize_dim = (original_width, original_height)

        x_pad = abs(new_dimensions[0]-resize_dim[0])
        y_pad = abs(new_dimensions[1]-resize_dim[1])

        if x_pad%2 == 1:
            x_pad_1 = int(x_pad/2)
            x_pad_2 = x_pad_1 + 1 
        else:
            x_pad_1 = int(x_pad/2)
            x_pad_2 = x_pad_1

        if y_pad%2 == 1:
            y_pad_1 = int(y_pad/2)
            y_pad_2 = y_pad_1 + 1 
        else:
            y_pad_1 = int(y_pad/2)
            y_pad_2 = y_pad_1

        padded_image = cv2.copyMakeBorder(input_frame,y_pad_1,y_pad_2,x_pad_1,x_pad_2,cv2.BORDER_CONSTANT,value=[0,0,0])

        return padded_image, [x_pad_1, x_pad_2, y_pad_1, y_pad_2]

    def cast_frame(self, input_frame, cast_type):
        '''Casts a numpy array using the numpy package funtion "astype"'''

        casted_frame = input_frame.astype(cast_type)

        return casted_frame

    def expand_dim(self, input_frame):
        '''Expands the dimension of a numpy array by one, on axis = 0'''

        expanded_frame = np.expand_dims(input_frame, axis=0)
        return expanded_frame

    def resize_frame(self, input_frame, new_dimensions, resize_speed):
        '''Resizes the image to new new_dimensions without changing the aspect ratio.
        - new_dimensions is a tupple (new_x, new_y) with the number of pixels. X is width
        - resize_speed changes the type of algorithm used for resizing, taking the values "fast, "medium", "slow"
        - Pads, if necessary, with black''' 
        
        #CALCULATE NECESSARY VARIABLES
        original_width = input_frame.shape[1]
        original_height = input_frame.shape[0]

        original_aspect_ratio = original_width/original_height
        new_aspect_ratio = new_dimensions[0]/new_dimensions[1]
        

        if new_aspect_ratio/original_aspect_ratio < 1: #meaning height is now proportionally bigger than before
            
            division_ratio = original_width/new_dimensions[0]
            new_width = new_dimensions[0]
            new_height = int(original_height/division_ratio)

            resize_dim = (new_width, new_height)

        elif new_aspect_ratio/original_aspect_ratio > 1:

            division_ratio = original_height/new_dimensions[1]
            new_height = new_dimensions[1]
            new_width = int(original_width/division_ratio)

            resize_dim = (new_width, new_height)

        else:#it doesnt matter if we pick width or height

            division_ratio = original_width/new_dimensions[0]
            new_width = new_dimensions[0]
            new_height = int(original_height/division_ratio)

            resize_dim = (new_width, new_height)

        #CHECK THE INTERPOLATION TYPE
        if resize_speed == "fast":

            if (division_ratio >= 1):
                cv2_interpolation = cv2.INTER_NEAREST 
            else:
                cv2_interpolation = cv2.INTER_NEAREST 

        elif resize_speed == "average":

            if (division_ratio >= 1):
                cv2_interpolation = cv2.INTER_AREA
            else:
                cv2_interpolation = cv2.INTER_LINEAR  

        elif resize_speed == "slow":

            if (division_ratio >= 1):
                cv2_interpolation = cv2.INTER_AREA 
            else:
                cv2_interpolation = cv2.INTER_CUBIC
        
        #PERFORM RESIZE
        temp_resized_image = cv2.resize(input_frame, resize_dim, interpolation=cv2_interpolation)       

        #PERFORM PADDING
        resized_pad_image, pad_ammounts = self.pad_frame(temp_resized_image, new_dimensions)

        return resized_pad_image, pad_ammounts