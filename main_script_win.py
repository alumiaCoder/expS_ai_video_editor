import alumia_TCP
import time

import alumia_VideoTools
import alumia_state_manager

STREAM_PATH = 'http://193.168.1.2:8000/stream.mjpeg'
PROCESS_SLEEP_TIME = 0.01
ROOT_SHARED = "E://"
NUMBER_OF_CLIENTS = 4

if __name__ == '__main__':

    #-------INIT TCP SERVER------#
    tcp_server = alumia_TCP.TCPServer(server_ip="193.168.1.3", server_port=12840, code="win")
    #-------------//-------------#

    #populate network
    while len(tcp_server.tcp_inputs) != NUMBER_OF_CLIENTS:
        print("Some connections to server are still missing...")
        tcp_server.get_select()
        for s in tcp_server.readable:
            if s is tcp_server.server:
                tcp_server.accept_conn(s)
            else:
                tcp_server.add_to_outputs(s)        
        time.sleep(1)

    print("All connections established!")
    time.sleep(1)

    #-------INIT SCREEN PROJECTION------#
    video_projector = alumia_VideoTools.VideoProjector()
    video_projector.start()
    #------------------//-----------------#
    
    #-------INIT SCREEN PROJECTION------#
    video_tracker = alumia_VideoTools.VideoFrameTracker()
    video_tracker.start()
    #------------------//-----------------#

    #-------INIT STATE CONTROL------#
    state_control = alumia_state_manager.StateManager(root=ROOT_SHARED)
    #----------------//-----------------#
    
    while tcp_server.tcp_inputs:
        tcp_server.get_select()

        for s in tcp_server.readable:

            if s is tcp_server.server:
                tcp_server.accept_conn(s)
            else:

                data = tcp_server.server_recv(connection=s)

                if data:
                    tcp_server.add_to_outputs(s)

                    if data[2] == "9":             
                        
                        if data[0] == "agc":
                        
                            tcp_server.server_send("193.168.1.2", data)

                        elif data[0] == "gain":
                        
                            tcp_server.server_send("193.168.1.2", data)

                        elif data[0] == "awb":
                        
                            tcp_server.server_send("193.168.1.2", data)

                    elif data[2] == "mon": # monitor is asking for an action
                        if "msp" in data[0]:
                            tcp_server.server_send("193.168.1.3", data[0]+"_"+data[1])

                        elif data[0] == "rec": # new recording

                            #send info to ras script to record video
                            tcp_server.server_send("193.168.1.2", "rec_0")

                        elif data[0] == "stop": # stop recording
                            # inform rasp we want to stop
                            tcp_server.server_send("193.168.1.2", "stop_0")
                        
                        elif data[0] == "str": # start/stop stream
                            # inform rasp
                            tcp_server.server_send("193.168.1.2", "str_0")

                        elif data[0] == "fld": # confirmed all changes in folder

                            params = data[1].split("&")
                            state_control.change_work_folder(params[0], params[1])
                            state_control.last_main_number = params[2]
                            state_control.last_snippet_number = params[3]
                        
                        elif data[0] == "fps":
                            
                            tcp_server.server_send("193.168.1.2", "fps_"+data[1])

                        elif data[0] == "exp":

                            tcp_server.server_send("193.168.1.2", "exp_"+data[1])

                        elif data[0] == "blk":

                            if data[1] == "0":

                                tcp_server.server_send("193.168.1.4", "blk_"+str(state_control.current_blk))
                            else:
                                if data[1] == "1":
                                    if state_control.current_blk < 10:
                                        state_control.current_blk += 1
                                        to_queue_dict = {"fps": -1, "black_frame_ratio": state_control.current_blk, "video_path": -1, "editing_func": -1}
                                        video_projector.set_input_queue(to_queue_dict)
                                        tcp_server.server_send("193.168.1.4", "blk_"+str(state_control.current_blk))
                                elif data[1] == "-1":        
                                    if state_control.current_blk > 1:
                                        state_control.current_blk -= 1
                                        to_queue_dict = {"fps": -1, "black_frame_ratio": state_control.current_blk, "video_path": -1, "editing_func": -1}
                                        video_projector.set_input_queue(to_queue_dict)
                                        tcp_server.server_send("193.168.1.4", "blk_"+str(state_control.current_blk))

                        elif data[0] == "edt":

                            if data[1] == "0":

                                tcp_server.server_send("193.168.1.4", "edt_"+str(state_control.current_edt))
                            else:
                                if data[1] == "1":
                                    if state_control.current_edt < 6:
                                        state_control.current_edt += 1
                                        video_projector.editing_tools.curr_edit_func = state_control.current_edt

                                        to_queue_dict = {"fps": -1, "black_frame_ratio": -1, "video_path": -1, "editing_func": state_control.current_edt}
                                        video_projector.set_input_queue(to_queue_dict)
                                        tcp_server.server_send("193.168.1.4", "edt_"+str(state_control.current_edt))
                                elif data[1] == "-1":        
                                    if state_control.current_edt > 1:
                                        state_control.current_edt -= 1
                                        video_projector.editing_tools.curr_edit_func = state_control.current_edt

                                        to_queue_dict = {"fps": -1, "black_frame_ratio": -1, "video_path": -1, "editing_func": state_control.current_edt}
                                        video_projector.set_input_queue(to_queue_dict)
                                        tcp_server.server_send("193.168.1.4", "edt_"+str(state_control.current_edt))

                        elif data[0] == "bperf":# we want to begin the performance
                            tcp_server.server_send("193.168.1.2", "bperf_0")

                        elif data[0] == "eperf":# we want to stop the performance
                            tcp_server.server_send("193.168.1.2", "eperf_0")

                        elif data[0] == "play":# we want to play a video
                            
                            params = data[1].split("&")

                            video_path = state_control.total_path + params[0] + "_" + params[1] +".avi"

                            to_queue_dict = {"fps": -1, "black_frame_ratio": -1, "video_path": video_path, "editing_func": -1}

                            video_projector.set_input_queue(to_queue_dict)
                            # after loading the video on the projector, we should hold the first frame until we get max confirmation

                            tcp_server.server_send("193.168.1.3", "play_" + data[1])
                            # there should be a reply from max

                    elif data[2] == "ras": # ras is confirming something
                        if data[0] == "rec": # we started recording
                            
                            params = data[1].split("&")
                            #win should start processing
                            video_path = state_control.total_path + params[0] + "_" + params[1] + ".avi"
                            state_control.last_snippet_number = params[1]

                            input_info = ["snippet", video_path, state_control.current_fps]
                            video_tracker.set_input_queue(input_info)

                            #inform max we want to start recording that file
                            tcp_server.server_send("193.168.1.3", "rec_" + data[1])
                                # in max update internal state

                            #inform monitor to show video is recording
                            tcp_server.server_send("193.168.1.4", "vid_1")

                        elif data[0] == "stop": # we stopped recording
                            #win should stop processing
                            video_tracker.set_input_queue(["track", "", ""])
            
                            #inform max we want to stop recording
                            tcp_server.server_send("193.168.1.3", "stop_" + data[1])

                            #inform monitor video stopped recording
                            tcp_server.server_send("193.168.1.4", "vid_0")
                        
                        elif data[0] == "str": # stream started/stopped
                            if data[1] == "0":# stopped
                                # win stops stream projection
                                video_projector.set_stop_queue("end")
                                state_control.stream_state = False

                                #inform monitor we stopped streaming
                                tcp_server.server_send("193.168.1.4", "str_0")
                            
                            else:# started
                                #win starts projection
                                video_path = STREAM_PATH
                                to_queue_dict = {"fps": -1, "black_frame_ratio": -1, "video_path": video_path, "editing_func": -1}

                                video_projector.set_input_queue(to_queue_dict)
                                state_control.stream_state = True

                                #inform monitor started stream
                                tcp_server.server_send("193.168.1.4", "str_1")

                        elif data[0] == "fld": #rasp confirms folder change
                            # ask monitor to save that folder
                            tcp_server.server_send("193.168.1.4", "fld_"+data[1])

                        elif data[0] == "fps":
                            
                            tcp_server.server_send("193.168.1.4", "fps_"+data[1])
                            state_control.current_fps = int(data[1])

                        elif data[0] == "exp":

                            tcp_server.server_send("193.168.1.4", "exp_"+data[1])

                        elif data[0] == "bperf":
                            state_control.last_main_number = data[1]

                            video_path = state_control.total_path + data[1] + ".mjpeg"

                            video_tracker.set_input_queue(["track", video_path])

                            tcp_server.server_send("193.168.1.3", "bperf_"+ data[1]) # to max we should inform about the video number
                            tcp_server.server_send("193.168.1.4", "bperf_0")

                        elif data[0] == "eperf":

                            video_tracker.set_input_queue(["stop", ""])

                            tcp_server.server_send("193.168.1.3", "eperf_0")
                            tcp_server.server_send("193.168.1.4", "eperf_0")

                    elif data[2] == "max": # max wants to confirm something
                        if data[0] == "rec": # confirm audio is being recorded
                            # inform monitor audio is being recorded
                            tcp_server.server_send("193.168.1.4", "aud_1")

                        elif data[0] == "stop":# confirm audio stoped recording
                            # informs monitor audio stoped recording
                            tcp_server.server_send("193.168.1.4", "aud_0")
                        
                        elif data[0] == "fld":# change work folder

                            # inform rasp of this change
                            tcp_server.server_send("193.168.1.2", "fld_"+ data[1])
                        
                        elif data [0] == "play":# reply with the audio's duration
                            
                            print(float(data[1]))
                            to_queue_dict = {"duration": float(data[1])}

                            video_projector.set_input_queue(to_queue_dict)

                        elif "msp" in data[0]:
                            
                            tcp_server.server_send("193.168.1.4", data[0] + "_" + data[1])

                        elif data[0] == "isogain":

                            tcp_server.server_send("193.168.1.2", data[0] + "_" + data[1])

                        elif data[0] == "agc":

                            tcp_server.server_send("193.168.1.2", data[0] + "_" + data[1])

                        elif data[0] == "awb":

                            tcp_server.server_send("193.168.1.2", data[0] + "_" + data[1])

                        elif data[0] == "end": # close everything
                            if video_tracker.video_processor.process_state == False and video_projector.play_state == False and state_control.stream_state == False:
                                # informs monitor and rasp to close
                                tcp_server.server_send("193.168.1.2", "end_0")
                                tcp_server.server_send("193.168.1.4", "end_0")
                                #close local
                                tcp_server.server_close()
                                video_projector.join()
                                exit()

        time.sleep(PROCESS_SLEEP_TIME)
