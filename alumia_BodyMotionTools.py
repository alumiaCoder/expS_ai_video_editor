import numpy as np
from scipy import signal

class BodyMotionTools():
    def __init__(self, min_conf_value=0.3, window_length=7, polyorder=2):
        self.n_total_frames = -1
        self.total_boxpoints = np.zeros((30*60*60, 4))
        self.total_keypoints = np.zeros((30*60*60, 17, 3))
        self.frames_analysed = np.zeros(30*60*60)
        self.min_conf = min_conf_value
        self.window_length = window_length
        self.polyorder = polyorder
        self.keypoints_save_path = "N/A"
        self.boxpoints_save_path = "N/A"

    def prepare_for_new_video(self, keypoints_save_path, boxpoints_save_path):
        self.n_total_frames = -1
        self.total_boxpoints = np.zeros((30*60*60, 4))
        self.total_keypoints = np.zeros((30*60*60, 17, 3))
        self.frames_analysed = np.zeros(30*60*60)
        self.keypoints_save_path = keypoints_save_path
        self.boxpoints_save_path = boxpoints_save_path

    def consider_frame(self, frame_keypoints, box_infer):
        self.n_total_frames += 1
        self.frames_analysed[self.n_total_frames] = 1
        self.total_keypoints[self.n_total_frames] = frame_keypoints
        self.total_boxpoints[self.n_total_frames] = box_infer

    def process_keypoints(self):
        
        avr_conf = self.calculate_acc()
        self.frames_smooth()
        self.frames_smooth()

        np.save(self.keypoints_save_path,self.total_keypoints)
        np.save(self.boxpoints_save_path,self.total_boxpoints)

        return avr_conf

    def calculate_acc(self):
        keypoints = [0, 9, 10, 15, 16]
        conf_sum = 0  

        for idx in keypoints:
            conf_sum+= np.sum(self.total_keypoints[:,idx,2])
        
        avr_conf = conf_sum/(5*self.n_total_frames)

        return avr_conf

    def frames_smooth(self):
        
        if self.n_total_frames >= self.window_length:
            for key_frame_idx in range(17):
                self.total_keypoints[0:self.n_total_frames,key_frame_idx:key_frame_idx+1,0:1] = signal.savgol_filter(self.total_keypoints[0:self.n_total_frames,key_frame_idx:key_frame_idx+1,0:1], self.window_length, self.polyorder, axis=0)
                self.total_keypoints[0:self.n_total_frames,key_frame_idx:key_frame_idx+1,1:2] = signal.savgol_filter(self.total_keypoints[0:self.n_total_frames,key_frame_idx:key_frame_idx+1,1:2], self.window_length, self.polyorder, axis=0)
    
    def frames_interpol(self):

        for key_frame_idx in range(17):
            begin_idx = -1
            end_idx = -1
            looking = 0
            for frame_idx in range(self.n_total_frames):

                if(self.total_keypoints[frame_idx][key_frame_idx][2] < self.min_conf and looking == 0 and frame_idx != self.n_total_frames - 1):
                    begin_idx = frame_idx
                    looking = 1
                    continue
                    
                if(frame_idx == self.n_total_frames - 1 and looking == 1):#chegamos ao ultimo e temos de interpolar
                    if begin_idx == 0 or begin_idx == -1:
                        begin_idx = 0
                        end_idx = frame_idx + 1               
                        temp_array_0 = np.linspace(self.total_keypoints[begin_idx][key_frame_idx][0], self.total_keypoints[begin_idx][key_frame_idx][0], num=end_idx - begin_idx, endpoint=False)
                        temp_array_1 = np.linspace(self.total_keypoints[begin_idx][key_frame_idx][1], self.total_keypoints[begin_idx][key_frame_idx][1], num=end_idx - begin_idx, endpoint=False)

                        temp_array_0 = np.expand_dims(temp_array_0, axis=(2, 1))
                        temp_array_1 = np.expand_dims(temp_array_1, axis=(2, 1))

                        self.total_keypoints[begin_idx:end_idx, key_frame_idx:key_frame_idx+1, 0:1] = temp_array_0
                        self.total_keypoints[begin_idx:end_idx, key_frame_idx:key_frame_idx+1, 1:2] = temp_array_1
                    else:
                        end_idx = frame_idx + 1                
                        temp_array_0 = np.linspace(self.total_keypoints[begin_idx-1][key_frame_idx][0], self.total_keypoints[begin_idx-1][key_frame_idx][0], num=end_idx - begin_idx, endpoint=False)
                        temp_array_1 = np.linspace(self.total_keypoints[begin_idx-1][key_frame_idx][1], self.total_keypoints[begin_idx-1][key_frame_idx][1], num=end_idx - begin_idx, endpoint=False)

                        temp_array_0 = np.expand_dims(temp_array_0, axis=(2, 1))
                        temp_array_1 = np.expand_dims(temp_array_1, axis=(2, 1))

                        self.total_keypoints[begin_idx:end_idx, key_frame_idx:key_frame_idx+1, 0:1] = temp_array_0
                        self.total_keypoints[begin_idx:end_idx, key_frame_idx:key_frame_idx+1, 1:2] = temp_array_1

                elif(self.total_keypoints[frame_idx][key_frame_idx][2] > self.min_conf and looking == 1): #chegamos ao ponto onde encontramos um correcto depois de varios errados
                    if(begin_idx > 0):
                        end_idx = frame_idx                
                        temp_array_0 = np.linspace(self.total_keypoints[begin_idx-1][key_frame_idx][0], self.total_keypoints[end_idx][key_frame_idx][0], num=end_idx - begin_idx, endpoint=False)
                        temp_array_1 = np.linspace(self.total_keypoints[begin_idx-1][key_frame_idx][1], self.total_keypoints[end_idx][key_frame_idx][1], num=end_idx - begin_idx, endpoint=False)

                        temp_array_0 = np.expand_dims(temp_array_0, axis=(2, 1))
                        temp_array_1 = np.expand_dims(temp_array_1, axis=(2, 1))

                        self.total_keypoints[begin_idx:end_idx, key_frame_idx:key_frame_idx+1, 0:1] = temp_array_0
                        self.total_keypoints[begin_idx:end_idx, key_frame_idx:key_frame_idx+1, 1:2] = temp_array_1
                        
                        begin_idx = frame_idx
                        end_idx = begin_idx
                        looking = 0

                    else:
                        begin_idx = 0
                        end_idx = frame_idx                
                        temp_array_0 = np.linspace(self.total_keypoints[end_idx][key_frame_idx][0], self.total_keypoints[end_idx][key_frame_idx][0], num=end_idx - begin_idx, endpoint=False)
                        temp_array_1 = np.linspace(self.total_keypoints[end_idx][key_frame_idx][1], self.total_keypoints[end_idx][key_frame_idx][1], num=end_idx - begin_idx, endpoint=False)

                        temp_array_0 = np.expand_dims(temp_array_0, axis=(2, 1))
                        temp_array_1 = np.expand_dims(temp_array_1, axis=(2, 1))

                        self.total_keypoints[begin_idx:end_idx, key_frame_idx:key_frame_idx+1, 0:1] = temp_array_0
                        self.total_keypoints[begin_idx:end_idx, key_frame_idx:key_frame_idx+1, 1:2] = temp_array_1
                        
                        begin_idx = frame_idx
                        end_idx = begin_idx
                        looking = 0

                elif(self.total_keypoints[frame_idx][key_frame_idx][2] > self.min_conf and looking == 0): #viemos de estar correcto e agora esta correcto tambem
                    begin_idx = frame_idx