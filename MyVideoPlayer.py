#!/usr/bin/env python3

import threading
import cv2
import numpy as np
import base64
import queue

# Sentinel value to indicate the end of processing
SENTINEL = None

# Flag to signal the main thread to close the window
close_window_flag = False

def extractFrames(fileName, outputBuffer, maxFramesToLoad=9999):
    # Initialize frame count 
    count = 0

    # Open video file
    vidcap = cv2.VideoCapture(fileName)

    # Read first image
    success, image = vidcap.read()
    
    print(f'Reading frame {count} {success}')
    while success and count < maxFramesToLoad:
        # Get a jpg encoded frame
        success, jpgImage = cv2.imencode('.jpg', image)

        # Encode the frame as base 64 to make debugging easier
        jpgAsText = base64.b64encode(jpgImage)

        # Add the frame to the buffer
        outputBuffer.put(image)
       
        success, image = vidcap.read()
        print(f'Reading frame {count} {success}')
        count += 1

    # Signal the end of processing by adding a sentinel value to the buffer
    outputBuffer.put(SENTINEL)

    print('Frame extraction complete')

def convertFramesToGrayscale(inputBuffer, outputBuffer):
    # Initialize the frame count
    count = 0

    # Go through each frame in the input buffer until the buffer is empty
    while True:
        # Get the next frame or sentinel value
        frame = inputBuffer.get()

        # Check if it's the sentinel value
        if frame is SENTINEL:
            break

        print(f'Converting frame {count}')

        # Convert the image to grayscale
        grayscaleFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Add the converted frame to the output buffer
        outputBuffer.put(grayscaleFrame)

        count += 1

    # Signal the end of processing by adding a sentinel value to the buffer
    outputBuffer.put(SENTINEL)

    print('Frame conversion complete')

def displayFrames(inputBuffer):
    # Initialize frame count
    count = 0

    # Go through each frame in the buffer until the buffer is empty
    while True:
        # Get the next frame or sentinel value
        frame = inputBuffer.get()

        # Check if it's the sentinel value
        if frame is SENTINEL:
            break

        print(f'Displaying frame {count}')        

        # Display the image in a window called "video" and wait 42ms
        # before displaying the next frame
        cv2.imshow('Video', frame)
        if cv2.waitKey(42) and 0xFF == ord("q"):
            global close_window_flag
            close_window_flag = True
            break

        count += 1

    print('Finished displaying all frames')
    cv2.destroyAllWindows()

# Filename of clip to load
filename = 'clip.mp4'

# Extra fluff to calculate the length of the mp4 file if you wanted to play the full thing
cap = cv2.VideoCapture(filename)
property_id = int(cv2.CAP_PROP_FRAME_COUNT) 
length = int(cv2.VideoCapture.get(cap, property_id))

# Shared queues (bounded to ten frames)
extractionQueue = queue.Queue(maxsize=10)
conversionQueue = queue.Queue(maxsize=10)

# Extract the frames (Can change the 72 to length to play full thing)
extractThread = threading.Thread(target=extractFrames, args=(filename, extractionQueue, 72))
extractThread.start()

# Convert the frames to grayscale
convertThread = threading.Thread(target=convertFramesToGrayscale, args=(extractionQueue, conversionQueue))
convertThread.start()

# Display the frames
displayThread = threading.Thread(target=displayFrames, args=(conversionQueue,))
displayThread.start()

# Wait for all threads to finish
extractThread.join()
convertThread.join()
displayThread.join()
