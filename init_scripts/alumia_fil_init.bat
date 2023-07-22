nvidia-smi -lgc 1875
nvidia-smi -lmc 9000
cd <PATH_TO_CONDA_ENV>
runas /user:phd "PATH_TO_MAX_8_EXE"
timeout /t 10
"PATH_TO_MAX_PATCH"
start /b python <PATH_TO_WIN_MAIN_SCRIPT>
start /b python <PATH_TO_ALUMIA_FIL_SCRIPT>
 