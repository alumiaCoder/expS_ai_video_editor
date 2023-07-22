class StateManager():

    def __init__(self, root, sub_folder="/video/", init_fps=30, stream_state=False):
        # folders
        self.root = root #needed to know what to send to rasp
        self.date_folder = ""
        self.perf_folder = ""
        self.sub_folder = sub_folder
        self.total_path = ""

        # state var.
        self.current_fps = init_fps
        self.stream_state = stream_state
        self.last_main_number = -1
        self.last_snippet_number = -1
        self.current_blk = 1
        self.current_edt = 1


    def change_work_folder(self, date_folder, perf_folder):

        partial_path = self.root + date_folder + "/" + perf_folder

        self.date_folder = date_folder
        self.perf_folder = perf_folder

        full_path = partial_path + self.sub_folder

        self.total_path = full_path

