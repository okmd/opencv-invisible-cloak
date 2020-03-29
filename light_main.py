import cv2
import numpy as np

def mask_3d(mask, shape):
    # takes 2d mask and convert to 3d channel mask
    # return image with 3 channel and back[0] and wihte[255]
    mask = mask.astype(np.bool)
    return np.ones(shape) * np.dstack([mask, mask, mask])*255

def mycloak(background, image, debug=False):
    # use HSV color space instead of RGB
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    image_mask_lower_color = cv2.inRange(image_hsv,(0,150,0),(10,255,255)) # 2d numpy array binary array[0-255] [balck-white]
    # if image of color is in this range then 255 otherwise 0
    image_mask_upper_color = cv2.inRange(image_hsv,(170,80,0),(180,255,255))
    mask_full = image_mask_lower_color + image_mask_upper_color
    mask_full = cv2.morphologyEx(mask_full, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))
    # mask_full = cv2.morphologyEx(mask_full, cv2.MORPH_CLOSE, np.ones((3,3),np.uint8))
    mask_full = cv2.dilate(mask_full, np.ones((3,3),np.uint8))
    mask_full_inv = cv2.bitwise_not(mask_full)
    image_with_black_roi = cv2.bitwise_and(image, image, mask=mask_full_inv)
    background_at_roi = cv2.bitwise_and(background, background, mask=mask_full)
    final_image = cv2.addWeighted(image_with_black_roi, 1, background_at_roi, 1, 0) # overlay image with
    if debug: # show all intermediate results
        temp_img_lc = cv2.resize(mask_3d(image_mask_lower_color, image.shape), (200,200), fx=.5, fy=.5)
        temp_img_uc = cv2.resize(mask_3d(image_mask_lower_color, image.shape), (200,200), fx=.5, fy=.5)
        temp_img_f = cv2.resize(mask_3d(mask_full, image.shape), (200,200), fx=.5, fy=.5)
        temp_img_f_inv = cv2.resize(mask_3d(mask_full_inv, image.shape), (200,200), fx=.5, fy=.5)
        cv2.imshow("Masks|Lower|Upper|Full|Inverse", np.hstack([temp_img_lc, temp_img_uc, temp_img_f, temp_img_f_inv]))
        image_with_b_roi = cv2.resize(image_with_black_roi, (200,200), fx=.5, fy=.5)
        bg_at_roi = cv2.resize(background_at_roi, (200,200), fx=.5, fy=.5)
        cv2.imshow("ROIs|Image[ROI]|Background[ROI]", np.hstack([image_with_b_roi, bg_at_roi]))
     
    cv2.imshow("Magical Cloak", final_image)

### MAIN ##
capture = cv2.VideoCapture(0) # use 0 for default camera and 1 for external camera.
# You can also give source url of a video file.

## Capture backgorund ##
count = 10
while count:
    count -= 1
    status, background = capture.read()
    if not status:
        capture.release()
        print("Unable to read background.")
        break
# cv2.imshow("bg", background)
background = np.ones(background.shape,np.uint8)*255
## Runing the Live stream ##
while 1:
    status, frame = capture.read()
    if not status:
        capture.release()
        print("Unable to read frame.")
        break
    mycloak(background, frame, debug=False)
    if cv2.waitKey(2) == ord('q'):
        capture.release()
        break

cv2.destroyAllWindows()

"""
How to use this script?
    1. Run the script and do not change camera position.
    2. Wait for a minute and record the background without person.
    3. Now come to frame[person].
    4. Use any red colored or similar colored cloth/thing to hide yourself.
"""