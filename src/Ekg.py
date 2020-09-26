import numpy as np
import cv2


def gen_ekg(img, pos, tail_length=50):
    s = np.shape(img)
    grad = np.zeros(s)
    for i in range(0, s[0]):
        for j in range(0, s[1]):
            if j < pos:
                grad[i, j] = ((j-(pos-tail_length))/(pos-(pos-tail_length)))*255
    grad = np.clip(grad/255, 0, 1)
    return grad * img


img = 255 - cv2.imread("/home/matthias/Documents/EKG1.png", 0)
s = np.shape(img)
tail_length = 130
for i in range(0, s[1]+tail_length):
    ekg = gen_ekg(img, pos=i, tail_length=tail_length).astype(np.uint8)
    print(np.shape(ekg))
    ekg = cv2.cvtColor(ekg, cv2.COLOR_GRAY2BGR)
    ekg = ekg/255
    ekg[:, :, 0] *= 255 - 255
    ekg[:, :, 1] *= 255 - 232
    ekg[:, :, 2] *= 255 - 205
    ekg = 255 - ekg
    ekg = ekg.astype(np.uint8)
    # ekg[np.where((ekg == [0, 0, 0]).all(axis=2))] = [255,255,255]
    cv2.imshow('EKG', ekg)
    cv2.waitKey(1)
