import ydlidar
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import numpy as np

RMAX = 0.3  # 30 cm maximum range

fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))
fig.canvas.manager.set_window_title('YDLidar LIDAR Monitor (30cm range)')
lidar_polar = ax
lidar_polar.autoscale_view(True,True,True)
lidar_polar.set_rmax(RMAX)
lidar_polar.grid(True)

ports = ydlidar.lidarPortList()
port = "/dev/ttyUSB0"
for key, value in ports.items():
    port = value
    print(f"Detected port: {port}")

laser = ydlidar.CYdLidar()
laser.setlidaropt(ydlidar.LidarPropSerialPort, port)
laser.setlidaropt(ydlidar.LidarPropSerialBaudrate, 128000)  # X4 Pro uses 128000 baud rate
laser.setlidaropt(ydlidar.LidarPropLidarType, ydlidar.TYPE_TRIANGLE)
laser.setlidaropt(ydlidar.LidarPropDeviceType, ydlidar.YDLIDAR_TYPE_SERIAL)
laser.setlidaropt(ydlidar.LidarPropScanFrequency, 12.0)
laser.setlidaropt(ydlidar.LidarPropSampleRate, 8)
laser.setlidaropt(ydlidar.LidarPropSingleChannel, True)
laser.setlidaropt(ydlidar.LidarPropMaxAngle, 180.0)
laser.setlidaropt(ydlidar.LidarPropMinAngle, -180.0)
laser.setlidaropt(ydlidar.LidarPropMaxRange, RMAX)
laser.setlidaropt(ydlidar.LidarPropMinRange, 0.1)
laser.setlidaropt(ydlidar.LidarPropIntenstiy, False)
scan = ydlidar.LaserScan()

def animate(num):
    r = laser.doProcessSimple(scan)
    if r:
        angle = []
        ran = []
        for point in scan.points:
            if 0 < point.range <= RMAX:  # Only include points within 30 cm
                angle.append(point.angle)
                ran.append(point.range)
        lidar_polar.clear()
        lidar_polar.scatter(angle, ran, s=5)
        lidar_polar.set_theta_zero_location('N')
        lidar_polar.set_theta_direction(-1)
    else:
        print("Failed to get Lidar Data")

ret = laser.initialize()
if ret:
    print("Lidar initialized successfully")
    
    for attempt in range(5):
        ret = laser.turnOn()
        if ret:
            print("Lidar turned on successfully")
            ani = animation.FuncAnimation(fig, animate, interval=50)
            plt.show()
            break
        else:
            print(f"Failed to turn on the Lidar (Attempt {attempt + 1}/5)")
            time.sleep(1)
    else:
        print("Failed to turn on the Lidar after 5 attempts")
else:
    print("Failed to initialize the Lidar")

laser.turnOff()
laser.disconnecting()
plt.close()