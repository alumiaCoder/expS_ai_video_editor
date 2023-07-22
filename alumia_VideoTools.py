#class that takes care of video projetion for windows machine
import cv2
from multiprocessing import Queue
from threading import Thread, Event
import time
import os
import numpy as np

import alumia_PhdCvModel
import alumia_BodyMotionTools

FRAME_RATE = 30
PROCESS_SLEEP_TIME = 0.001
BASE_PATH = 'BASE_PATH_HERE'

class EditingClass():

    def __init__(self):

        self.largest_box = np.array([0.,1.,0.,1.])
        self.speaker_position = np.array([0.,1.,0.,1.])
        self.box_with_speaker = np.array([0.,1.,0.,1.])
        self.max_hands_position = np.array([0.,1.,0.,1.])
        self.last_frame = -1
        self.curr_edit_func = 1

    def reset_class(self, box_points, key_points, total_frames):

        self.largest_box = np.array([0.,1.,0.,1.])
        self.box_points = box_points
        self.key_points = key_points
        self.total_frames = total_frames

        self.current_frame_idx = 0

        if self.curr_edit_func == 2:

            self.prepare_edit_2()

        elif self.curr_edit_func == 3:

            self.prepare_edit_3()

        elif self.curr_edit_func == 4:

            self.prepare_edit_4()
        
        elif self.curr_edit_func == 5:

            self.prepare_edit_5()


    def prepare_edit_2(self):
        
        self.set_largest_box()
    
    def prepare_edit_3(self):

        self.set_largest_box()
        self.set_box_with_speaker()

    def prepare_edit_4(self):
        self.set_max_hands_position()

    def prepare_edit_5(self):
        self.last_frame = -1

    def edit_frame(self, input_frame):

        if self.curr_edit_func == 1:

            return input_frame
        
        elif self.curr_edit_func == 2:

            return self.edit_func_2(input_frame)

        elif self.curr_edit_func == 3:

            return self.edit_func_3(input_frame)

        elif self.curr_edit_func == 4:

            return self.edit_func_4(input_frame)

        elif self.curr_edit_func == 5:

            return self.edit_func_5(input_frame)
    
        elif self.curr_edit_func == 6:

            return self.edit_func_6(input_frame)

    def edit_func_2(self, input_frame):

        black_frame = np.zeros_like(input_frame)

        original_width = input_frame.shape[1]
        original_height = input_frame.shape[0]
        
        x_min = int(original_width*self.largest_box[0])
        x_max = int(original_width*self.largest_box[1])
        
        y_min = int(original_height*self.largest_box[2])
        y_max = int(original_height*self.largest_box[3])

        black_frame[y_min:y_max, x_min:x_max] = input_frame[y_min:y_max, x_min:x_max]

        return black_frame

    def edit_func_3(self, input_frame):
        
        black_frame = np.zeros_like(input_frame)

        original_width = input_frame.shape[1]
        original_height = input_frame.shape[0]
        
        x_min = int(original_width*self.box_with_speaker[0])
        x_max = int(original_width*self.box_with_speaker[1])
        
        y_min = int(original_height*self.box_with_speaker[2])
        y_max = int(original_height*self.box_with_speaker[3])

        black_frame[y_min:y_max, x_min:x_max] = input_frame[y_min:y_max, x_min:x_max]

        return black_frame

    def edit_func_4(self, input_frame):
        
        black_frame = np.zeros_like(input_frame)

        original_width = input_frame.shape[1]
        original_height = input_frame.shape[0]
        
        x_min = int(original_width*self.max_hands_position[0])
        x_max = int(original_width*self.max_hands_position[1])
        
        y_min = int(original_height*self.max_hands_position[2])
        y_max = int(original_height*self.max_hands_position[3])

        black_frame[y_min:y_max, x_min:x_max] = input_frame[y_min:y_max, x_min:x_max]

        return black_frame

    def edit_func_5(self, input_frame):

        if type(self.last_frame) == int:

            return_frame = cv2.absdiff(input_frame, input_frame)
        else:

            return_frame = cv2.absdiff(input_frame, self.last_frame)

        self.last_frame = input_frame[:]
        
        return return_frame

    def edit_func_6(self, input_frame):

        for i in range(17):
            cv2.circle(input_frame, (int(self.key_points[self.current_frame_idx][i][0]), int(self.key_points[self.current_frame_idx][i][1])), 10, (int(150), int(60), int(99)), -1)

        self.current_frame_idx += 1

        return input_frame
    
    def set_max_hands_position(self):

        left_hand_idx = 9
        right_hand_idx = 10

        # XX ---------------------------
        left_hand_x_max = np.amax(self.key_points[:self.total_frames, left_hand_idx, 0], 
                                    initial=0)
        
        right_hand_x_max = np.amax(self.key_points[:self.total_frames, right_hand_idx, 0], 
                                    initial=0)
        
        left_hand_x_min = np.amin(self.key_points[:self.total_frames, left_hand_idx, 0], 
                                    initial=1919,
                                    where=((self.key_points[:self.total_frames, left_hand_idx, 0]!=0)))
        
        
        right_hand_x_min = np.amin(self.key_points[:self.total_frames, right_hand_idx, 0], 
                                    initial=1919,
                                    where=((self.key_points[:self.total_frames, right_hand_idx, 0]!=0)))
        
        # YY ------------------------
        left_hand_y_max = np.amax(self.key_points[:self.total_frames, left_hand_idx, 1], 
                                    initial=0)
        
        right_hand_y_max = np.amax(self.key_points[:self.total_frames, right_hand_idx, 1], 
                                    initial=0)
        
        left_hand_y_min = np.amin(self.key_points[:self.total_frames, left_hand_idx, 1], 
                                    initial=1079,
                                    where=((self.key_points[:self.total_frames, left_hand_idx, 1]!=0)))
        
        right_hand_y_min = np.amin(self.key_points[:self.total_frames, right_hand_idx, 1], 
                                    initial=1079,
                                    where=((self.key_points[:self.total_frames, right_hand_idx, 1]!=0)))

        self.max_hands_position[0] = min(left_hand_x_min, right_hand_x_min)/1919
        self.max_hands_position[1] = max(left_hand_x_max, right_hand_x_max)/1919

        self.max_hands_position[2] = min(left_hand_y_min, right_hand_y_min)/1079
        self.max_hands_position[3] = max(left_hand_y_max, right_hand_y_max)/1079

    def set_largest_box(self):
        
        self.largest_box[0] = np.amin(self.box_points[:self.total_frames, 0], 
                                    initial=2, 
                                    where=((self.box_points[:self.total_frames, 0]!=0) & (self.box_points[:self.total_frames, 0]!=1)))
        
        self.largest_box[1] = np.amax(self.box_points[:self.total_frames, 1], 
                                    initial=-1, 
                                    where=((self.box_points[:self.total_frames, 1]!=1) & (self.box_points[:self.total_frames, 1]!=0)))
        
        self.largest_box[2] = np.amin(self.box_points[:self.total_frames, 2], 
                                    initial=2, 
                                    where=((self.box_points[:self.total_frames, 2]!=0) & (self.box_points[:self.total_frames, 2]!=1)))
        
        self.largest_box[3] = np.amax(self.box_points[:self.total_frames, 3], 
                                    initial=-1, 
                                    where=((self.box_points[:self.total_frames, 3]!=1) & (self.box_points[:self.total_frames, 3]!=0)))

        for idx, point in enumerate(self.largest_box):
            if point == 2:
                self.largest_box[idx] = 0
            elif point == -1:
                self.largest_box[idx] = 1
    
    def set_box_with_speaker(self):
        
        if self.largest_box[0] < self.speaker_position[0]:
            self.box_with_speaker[0] = self.largest_box[0]
        else:
            self.box_with_speaker[0] = self.speaker_position[0]

        if self.largest_box[1] > self.speaker_position[1]:
            self.box_with_speaker[1] = self.largest_box[1]
        else:
            self.box_with_speaker[1] = self.speaker_position[1]

        if self.largest_box[2] < self.speaker_position[2]:
            self.box_with_speaker[2] = self.largest_box[2]
        else:
            self.box_with_speaker[2] = self.speaker_position[2]
        
        if self.largest_box[3] > self.speaker_position[3]:
            self.box_with_speaker[3] = self.largest_box[3]
        else:
            self.box_with_speaker[3] = self.speaker_position[3]
    
    def set_speaker_position(self, speaker_pixel_position):

        self.speaker_position[0] = speaker_pixel_position[0]/1919
        self.speaker_position[1] = speaker_pixel_position[1]/1919

        self.speaker_position[2] = speaker_pixel_position[2]/1079
        self.speaker_position[3] = speaker_pixel_position[3]/1079


class VideoProjector(Thread):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.mouse_box = np.array([-1,-1,-1,-1])
        self.drawing = False
        self.mouse_box_show_counter = 0
        self.inputQueue = Queue(maxsize=1)
        self.stopQueue = Queue(maxsize=1)
        self.play_state = False
        self.editing_tools = EditingClass()

    def run(self):
        thread = Thread(target=self.video_projector, args=(self.inputQueue,self.stopQueue))
        thread.daemon = True
        thread.start()

    def set_input_queue(self, input_info):

        self.inputQueue.put(input_info)

    def set_stop_queue(self, value):

        self.stopQueue.put(value)

    def draw_rectangle(self, event, x, y, flags, param):
        
        if event == cv2.EVENT_LBUTTONDOWN:
            self.mouse_box = np.array([-1,-1,-1,-1])
            self.drawing = True
            self.mouse_box[0] = x
            self.mouse_box[2] = y
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.mouse_box[1] = x
            self.mouse_box[3] = y
            self.mouse_box_show_counter = 0

    def video_projector(self, inputQueue, stopQueue):
        
        frame_calc_rate_play = 1/FRAME_RATE
        background_img = cv2.imread(BASE_PATH + "experimental_system/utils/black_1080.jpg")
        cv2.namedWindow('projector', cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("projector", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.moveWindow("projector", 0, 0)
        cv2.imshow("projector", background_img)
        cv2.setMouseCallback("projector", self.draw_rectangle)
        cv2.waitKey(1)

        black_ratio = -2
        play_fps = 30

        while True:

            cv2.imshow("projector", background_img)
            self.play_state = False
            if not inputQueue.empty():
                from_queue_dict = inputQueue.get()
                dont_exit = False
                its_stream = False

                if from_queue_dict["black_frame_ratio"] != -1:
                
                    black_ratio = from_queue_dict["black_frame_ratio"]

                if from_queue_dict["fps"] != -1:
                    play_fps = from_queue_dict["fps"]
                    frame_calc_rate_play = 1/play_fps
                
                if from_queue_dict["editing_func"] != -1:
                
                    self.editing_tools.curr_edit_func = from_queue_dict["editing_func"]
                
                if from_queue_dict["video_path"] != -1:

                    video_path = from_queue_dict["video_path"]

                    #open the correct numpy array
                    if from_queue_dict["fps"] == -1 and "stream" not in video_path:
                        fps_numpy_path = video_path.rsplit('.', 1)[0] + "_fps.npy"
                        box_numpy_path = video_path.rsplit('.', 1)[0] + "_bp.npy"
                        keypoints_numpy_path = video_path.rsplit('.', 1)[0] + "_kp.npy"

                        fps_recall = np.load(fps_numpy_path)
                        boxpoints = np.load(box_numpy_path)
                        keypoints = np.load(keypoints_numpy_path)

                        frame_calc_rate_play = 1/fps_recall[0]
                        total_video_frames = fps_recall[1]
                        
                        self.editing_tools.reset_class(boxpoints, keypoints, total_video_frames)
                        
                    elif "stream" in video_path:
                        its_stream = True

                    cap = cv2.VideoCapture(video_path)
                    start_time = time.perf_counter()
                    n_frames = 1
                    stream_fps = 30

                    dont_exit = True
                    self.play_state = True
                    frame_idx = -1

                    adjustment = 0

                while dont_exit:
                    time_show_start = time.perf_counter()

                    ret, image = cap.read()
                    if ret:

                        if frame_idx == -1 and its_stream == False:
                            got_duration = False
                            audio_duration = -1
                            while not got_duration:
                                if not inputQueue.empty():
                                    audio_duration = inputQueue.get()
                                    audio_duration = audio_duration["duration"]
                                    got_duration = True

                        frame_idx += 1
                    
                    if not stopQueue.empty():
                        rcv_message = stopQueue.get()
                    else:
                        rcv_message = ''

                    if not ret or rcv_message == 'end':
                        
                        cv2.imshow("projector", background_img)
                        cv2.waitKey(1)
                        dont_exit = False
                        continue  
                    
                    if -1 not in self.mouse_box and self.mouse_box_show_counter < play_fps*3:

                        if self.mouse_box_show_counter == 0:
                            self.editing_tools.set_speaker_position(self.mouse_box)

                        cv2.rectangle(image, 
                                    (self.mouse_box[0], self.mouse_box[2]),
                                    (self.mouse_box[1], self.mouse_box[3]),
                                    (255, 255, 255),
                                    4)
                        
                        cv2.putText(image, 
                                    'OK', 
                                    (self.mouse_box[0], self.mouse_box[2] + 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 
                                    0.9, 
                                    (36,255,12), 
                                    2)
                        
                        self.mouse_box_show_counter += 1

                    if not inputQueue.empty():
                        from_queue_dict = inputQueue.get()

                    if from_queue_dict["black_frame_ratio"] != -1:
                    
                        black_ratio = from_queue_dict["black_frame_ratio"]

                    if from_queue_dict["fps"] != -1:

                        play_fps = from_queue_dict["fps"]
                        frame_calc_rate_play = 1/play_fps

                    if its_stream == False:
                        image = self.editing_tools.edit_frame(image)
                    
                    cv2.imshow('projector', image)
                    cv2.waitKey(1)

                    if time.perf_counter()-start_time >= 1:
                        start_time = time.perf_counter()
                        print(n_frames)
                        stream_fps = n_frames
                        n_frames = 1
                    else:
                        n_frames += 1
                    
                    if its_stream == False: #whe it is not stream, we should consider fps
                        time_elapsed = time.perf_counter()-time_show_start

                        if black_ratio > 1: 
                            condition = time_elapsed < frame_calc_rate_play*(1-1/black_ratio)
                            while condition:

                                time_elapsed = time.perf_counter()-time_show_start
                                condition = time_elapsed < frame_calc_rate_play*(1-1/black_ratio)

                            cv2.imshow("projector", background_img)
                            cv2.waitKey(1)
                        
                        time_elapsed = time.perf_counter()-time_show_start

                        while time_elapsed < audio_duration/total_video_frames - adjustment:
                            time_elapsed = time.perf_counter()-time_show_start

                        adjustment = time_elapsed - audio_duration/total_video_frames

                    else: #read/writting process takes care of fps on stream case
                        
                        if black_ratio > 1:
                            time_elapsed = time.perf_counter()-time_show_start
                            condition = time_elapsed < (1/stream_fps)*(1-1/black_ratio)
                            while condition:

                                time_elapsed = time.perf_counter()-time_show_start
                                condition = time_elapsed < (1/stream_fps)*(1-1/black_ratio)

                            cv2.imshow("projector", background_img)
                            cv2.waitKey(1)

            cv2.waitKey(1)
            time.sleep(PROCESS_SLEEP_TIME)

class VideoProcessor(Thread):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.inputQueue = Queue(maxsize=0)
        self.snippet_event = Event()
        
        self.process_state = False
        self.model = alumia_PhdCvModel.PhdCvModel()
        self.motion_infer = alumia_BodyMotionTools.BodyMotionTools()

    def run(self):
        thread = Thread(target=self.video_processor, args=())
        thread.daemon = True
        thread.start()

    def set_input_queue(self, input_info):

        self.inputQueue.put(input_info)

    def video_processor(self):

        print("Model loaded!")

        while True:
            self.process_state = False
            self.snippet_event.wait()

            self.process_state = True
            input_info = self.inputQueue.get()

            video_path = input_info[0]

            frame_calc_rate_process = 1/int(input_info[1])

            fps_numpy_path = video_path.rsplit('.', 1)[0] + "_fps.npy"
            key_points_numpy_path = video_path.rsplit('.', 1)[0] + "_kp.npy"
            box_points_numpy_path = video_path.rsplit('.', 1)[0] + "_bp.npy"

            video_out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'MJPG'), float(input_info[1]), (1920,1080))
            
            frame_idx = 0
            n_frames=1

            self.motion_infer.prepare_for_new_video(key_points_numpy_path, box_points_numpy_path)

            dont_exit = True
            print("Started video processing") 
            start_time = time.time()
            while dont_exit:
                
                if not self.inputQueue.empty():
                    
                    frame = self.inputQueue.get()

                    if frame[0] != "frame":

                        print("Stopped video processing")                                    
                        dont_exit = False
                        continue

                    video_out.write(frame[1])

                    keypoints_infer, box_infer = self.model.infer(frame[1])
                    self.motion_infer.consider_frame(keypoints_infer, box_infer)

                    frame_idx += 1
                    
                    if time.time()-start_time >= 1:
                        start_time = time.time()
                        print(n_frames)
                        n_frames = 1
                    else:
                        n_frames += 1

            video_out.release()
            
            np.save(fps_numpy_path, np.array([input_info[1], frame_idx+1]))
            avg_accur = self.motion_infer.process_keypoints()
            print("snippet avg accur =", avg_accur)

class VideoFrameTracker(Thread):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.inputQueue = Queue(maxsize=1)
        #-------INIT VIDEO PROCESSOR--------#
        self.video_processor = VideoProcessor()
        self.video_processor.start()
        #------------------//---------------#
        
    def run(self):
        thread = Thread(target=self.video_tracker, args=())
        thread.daemon = True
        thread.start()

    def set_input_queue(self, input_info):

        self.inputQueue.put(input_info)

    def video_tracker(self):

        while True:

            if not self.inputQueue.empty():
                input_queue_output = self.inputQueue.get()

                if input_queue_output[0] == "track":

                    video_path = input_queue_output[1]

                    found_video = False
                    while found_video == False:
                        found_video = os.path.isfile(video_path)

                    cap = cv2.VideoCapture(video_path)

                    dont_exit = True
                    stop_tracking = False
                    snippet_mode = False
                    
                    frame_idx = 0

                    while dont_exit:
                        # if there is a new frame, there is a new timestamp
                        ret = cap.grab()
                        

                        if not ret:
                            evaluating = True
                            while evaluating:
                                if not self.inputQueue.empty():

                                    input_queue_output = self.inputQueue.get()

                                    if input_queue_output[0] == "track" and snippet_mode == True:

                                        snippet_mode = False
                                        self.video_processor.set_input_queue(["end", ""])
                                        self.video_processor.snippet_event.clear()

                                    elif input_queue_output[0] == "snippet" and snippet_mode == False:

                                        snippet_mode = True
                                        self.video_processor.set_input_queue(input_queue_output[1:])
                                        self.video_processor.snippet_event.set()

                                    elif input_queue_output[0] == "stop" and snippet_mode == False:

                                        evaluating = False
                                        stop_tracking = True
                                        cap.release()

                                elif cap.grab(): # check if frame is available to read

                                    frame_idx += 1
                                    evaluating = False

                                    if snippet_mode == True:

                                        ret_1, input_frame = cap.retrieve(ret)
                                        self.video_processor.set_input_queue(["frame", input_frame])

                                else: # little trick to handle faster reading time than video writting time
                                    #1 same as CV_CAP_PROP_POS_FRAMES -> 0 based index of the next frame to decode
                                    cap.set(1, frame_idx)
                                    time.sleep(PROCESS_SLEEP_TIME) #to reduce number of loops
                            
                            if stop_tracking == True:
                                break

                        else:

                            frame_idx += 1

                            if not self.inputQueue.empty():
                                input_queue_output = self.inputQueue.get()
                                if input_queue_output[0] == "snippet" and snippet_mode == False:
                                    ret_1, input_frame = cap.retrieve(ret)

                                    snippet_mode = True

                                    self.video_processor.set_input_queue(input_queue_output[1:])
                                    self.video_processor.snippet_event.set()
                                    self.video_processor.set_input_queue(["frame", input_frame])

                                elif input_queue_output[0] == "track" and snippet_mode == True:
                                    ret_1, input_frame = cap.retrieve(ret)
                                    
                                    snippet_mode = False

                                    self.video_processor.set_input_queue(["frame", input_frame])
                                    self.video_processor.set_input_queue(["end", ""])
                                    self.video_processor.snippet_event.clear()

                            else:
                                if snippet_mode == True:

                                    ret_1, input_frame = cap.retrieve(ret)
                                    self.video_processor.set_input_queue(["frame", input_frame])
                        
            time.sleep(PROCESS_SLEEP_TIME)