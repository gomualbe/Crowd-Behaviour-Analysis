from PyQt6.QtWidgets import QWidget
from ui.threads.processing_thread import ProcessingThread
from ui.camera_stream.camera import Camera

class Analysis(QWidget):
    def __init__(self, width, height, main_window, switch):
        super().__init__()
        self.width = width
        self.height = height
        self.main_window = main_window
        self.switch = switch
        self.camera = None

        # Separate thread for frame processing.
        # switch checked == flow-map mode, so the counting flag is its inverse.
        self.processing_thread = ProcessingThread(not switch.isChecked())
        self.processing_thread.people_count_signal.connect(self.main_window.update_people_count)

        # Connect the switch only once, to a single handler that always targets
        # the currently selected camera (connecting per-camera stacked signals).
        self.switch.toggled.connect(self.on_switch_toggled)

    def on_switch_toggled(self, checked):
        # checked -> flow-map mode (draw flow); unchecked -> counting (draw grid)
        self.processing_thread.set_flag(not checked)
        if self.camera is not None:
            self.camera.toggle_density_flag(checked)

    def setup_camera(self, camera: Camera):
        print(f'Using camera instance: {camera}')
        self.camera = camera

        # Keep the newly selected camera in sync with the current switch state.
        self.camera.toggle_density_flag(self.switch.isChecked())

        frame_video = self.camera.get_video_frame(analysis=True)
        self.main_window.set_camera_frame(frame_video)

        # Ensure the processing thread uses the updated camera.
        self.processing_thread.set_camera(self.camera)

        if not self.processing_thread.isRunning():
            self.processing_thread.start()  # Starts thread
        else:
            self.processing_thread.update_camera(self.camera)