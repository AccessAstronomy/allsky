import asi
rtn, info = asi.ASIGetCameraProperty(0)
out = asi.ASIOpenCamera(info.CameraID)
out = asi.ASIInitCamera(info.CameraID)
out = asi.ASISetROIFormat(info.CameraID, info.MaxWidth, info.MaxHeight, 1, asi.ASI_IMG_RAW16)

rtn, num_controls = asi.ASIGetNumOfControls(info.CameraID)
for control_index in range(num_controls):
