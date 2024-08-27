# -*- coding: utf-8 -*-
"""
Simple script to collect data from the cameras on TOMAS

Riccardo Ragona 20190823

"""

import cv2
import time
import numpy as np
#import matplotlib.pyplot as plt 

from os import remove
from sys import exit


import threading
    

'''
Auxiliary frams waiting for the fourth camera
''' 
trump_time=False

fake_frame_b=np.zeros(shape=[480, 640, 3], dtype=np.uint8)
#fake_frame_b=np.zeros(shape=[600, 800, 3], dtype=np.uint8)
#fake_frame_t=cv2.imread('fake_frame_t.jpg',1)
#fake_frame_t=cv2.resize(fake_frame_t,(600,800))

#fake_frame=[fake_frame_b,fake_frame_t]

"""
List of key values to set properties of the cameras

#       key value
cam.set(3 , 640  ) # width        
cam.set(4 , 480  ) # height       
cam.set(10, 120  ) # brightness     min: 0   , max: 255 , increment:1  
cam.set(11, 50   ) # contrast       min: 0   , max: 255 , increment:1     
cam.set(12, 70   ) # saturation     min: 0   , max: 255 , increment:1
cam.set(13, 13   ) # hue         
cam.set(14, 50   ) # gain           min: 0   , max: 127 , increment:1
cam.set(15, -3   ) # exposure       min: -7  , max: -1  , increment:1
cam.set(17, 5000 ) # white_balance  min: 4000, max: 7000, increment:1
cam.set(28, 0    ) # focus          min: 0   , max: 255 , increment:5
"""
#%%
### Initializing the cameras
print('Initializing cameras...')
cam0 = cv2.VideoCapture(0,cv2.CAP_DSHOW) 
print('Cam0: ok') if cam0.isOpened() else exit()
cam1 = cv2.VideoCapture(1)
print('Cam1: ok') if cam1.isOpened() else exit()
cam2 = cv2.VideoCapture(2) 
print('Cam2: ok') if cam2.isOpened() else exit()
cam3 = cv2.VideoCapture(0)
print('Cam3: ok') if cam3.isOpened() else exit()

# ### Check if cameras are active
print("Cameras ready!") if (cam0.isOpened() & cam1.isOpened() & cam2.isOpened() & cam3.isOpened()) else print("Cameras not ready!")
#exit()

#%%
cameras=[cam0,cam1,cam2,cam3]

## Settings for cam0
cam0.set(28,75) # focus   min: 0, max: 255, increment: 5
cam0.set(11,128)
# cam0.set(3,800)
# cam0.set(4,600)
cam0.set(10,40) # bri 120
cam0.set(15,-7) # exp -6
cam0.set(14,80) # gain
# ## settings for cam1
cam1.set(10,10)
cam1.set(14,10)
cam1.set(15,-7) 
cam1.set(28,25) # focus   min: 0, max: 255, increment: 5
# exp -6# cam1.set(3,800)
# cam1.set(4,600)
# # settings for cam2
# cam2.set(3,800)
# cam2.set(4,600)
# # settings for cam3
# cam3.set(28,0)
# cam3.set(3,800)
# cam3.set(4,600)

for c in cameras:
      c.set(3,640)
      c.set(4,480)


#for c in cameras:
#    print(int(c.get(3)),' ', int(c.get(4)))


save_probe_img=False
shotnumber=''

def polling():
    while True:
        time.sleep(0.5)
        try:
            with open('C:/Users/TOMAS/Python-scripts/Camera/shotnumber.txt') as f:
                shotnumber=f.read()
                
            save_probe_img=True
            print('Saving image for probe location, shot #{}'.format(shotnumber))
            remove('shotnumber.txt')
            
        except Exception as e:
            pass

trd=threading.Thread(target=polling,daemon=True)
trd.start()
## Acquisition loop
while(True):
        
    ret,frame_cam0 = cam0.read()
    if ret:
        #cv2.imshow("Camera 0",frame_cam0)
        pass
    else:
        print("Something wrong with cam0!")
        break
    
    ret,frame_cam1 = cam1.read()
    if ret:
        #cv2.imshow("Camera 1",frame_cam1)
        pass
    else:
        print("Something wrong with cam1!")
        break
    
    ret,frame_cam2 = cam0.read()
    if ret:
        #cv2.imshow("Camera 2",frame_cam2)
        pass
    else:
        print("Something wrong with cam2!")
        break
    
    ret,frame_cam3 = cam3.read()
    if ret:
        #cv2.imshow("Camera 3",frame_cam3)
        pass
    else:
        print("Something wrong with cam3!")
        break
    
    frame_cam3_resized=frame_cam3[300:-1,300:800,:]
    
#     #if not frame_cam3.shape==frame_cam2.shape:
#     #    frame_cam3=cv2.resize(frame_cam3,(frame_cam2.shape[1],frame_cam2.shape[0]))
    
#     # frame_cam0=cv2.resize(frame_cam0,(640,480))
#     # frame_cam1=cv2.resize(frame_cam1,(640,480))
#     # frame_cam2=cv2.resize(frame_cam2,(640,480))
#     # frame_cam3=cv2.resize(frame_cam3,(640,480))
        
    frame_cam3_resized2=cv2.resize(frame_cam3_resized,(frame_cam2.shape[1],frame_cam2.shape[0]))
    
    ### Create a 2x2 mosaic to display all cameras in a single window
    hfrm1=np.concatenate((frame_cam0,frame_cam1),axis=1)
    if not trump_time:
        hfrm2=np.concatenate((frame_cam2,frame_cam3_resized2),axis=1)
    else:
        hfrm2=np.concatenate((frame_cam2,fake_frame[int(trump_time)]),axis=1)
    big_frame=np.concatenate((hfrm1,hfrm2),axis=0)
    
    red_frame=cv2.resize(big_frame,(1024,768))
    
    ### Display the cameras mosaic
    cv2.imshow('The big picture!',red_frame)
    
    if save_probe_img==True:
        timestr = time.strftime("%Y%m%d-%H%M%S")
        cv2.imwrite(timestr+'_probe_'+shotnumber+'.jpg',frame_cam3)
        save_probe_img=False
    
    #cv2.imshow('Display',red_frame)
    ### Catch keybord intterupts
    key=cv2.waitKey(1)
    
    if key==27:
        break # press ESC to quit
    
    elif key==32: # press SPACE to save the big picture
        timestr = time.strftime("%Y%m%d-%H%M%S")
        cv2.imwrite(timestr +'_cam.jpg',big_frame)
    
    elif key==116: # press t to activate deactivate Trump
        trump_time=not trump_time
#   
#    elif key==48: # press 0 to save cam0
#        timestr = time.strftime("%Y%m%d-%H%M%S")
#        cv2.imwrite(timestr +'_cam0.jpg',frame_cam0)
#    elif key==49:  # press 1 to save cam1
#        timestr = time.strftime("%Y%m%d-%H%M%S")
#        cv2.imwrite(timestr +'_cam1.jpg',frame_cam1)
#    elif key==50:  # press 2 to save cam2
#        timestr = time.strftime("%Y%m%d-%H%M%S")
#        cv2.imwrite(timestr +'_cam2.jpg',frame_cam2)
#    elif key==57:  # press 9 to save all
#        timestr = time.strftime("%Y%m%d-%H%M%S")
#        cv2.imwrite(timestr +'_cam0.jpg',frame_cam0)
#        cv2.imwrite(timestr +'_cam1.jpg',frame_cam1)
#        cv2.imwrite(timestr +'_cam2.jpg',frame_cam2)
            
        
    
### Close all windows        
cv2.destroyAllWindows()

# ### Free the cameras
# #%%
cam0.release()
cam1.release()
cam2.release()
cam3.release()

