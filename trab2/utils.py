import cv2
import numpy as np

def apply_freq_filter(img, r1, r2 = None, high=False,
                       reject=False, t=60):
    
    fourier = cv2.dft(np.float32(img),
                      flags=cv2.DFT_COMPLEX_OUTPUT)
 
    fourier_shift = np.fft.fftshift(fourier)
    magnitude = 20*np.log(cv2.magnitude(fourier_shift[:,:,0],
                                        fourier_shift[:,:,1]))
    magnitude = cv2.normalize(magnitude, None, 0, 255,
                              cv2.NORM_MINMAX, cv2.CV_8UC1)

    mask = np.zeros_like(img)
    cy = mask.shape[0] // 2
    cx = mask.shape[1] // 2
    cv2.circle(mask, (cx,cy), r1, (255,255,255), -1)[0] 
    if r2 is not None:        
        cv2.circle(mask, (cx,cy), r2, (255,255,255), -1)[0]
        cv2.circle(mask, (cx,cy), r1, (0,0,0), -1)[0]
           
    if high:
        mask = np.where(mask == 0, 255, 0)
    if reject:
        mask = np.where(mask == 255, 0, 255)

    f_complex = fourier_shift[:,:,0]*1j + fourier_shift[:,:,1]
    f_filtered = mask * f_complex
    
    f_filtered_shifted = np.fft.fftshift(f_filtered)
    inv_img = np.fft.ifft2(f_filtered_shifted) # inverse F.T.
    filtered_img = np.abs(inv_img)
    filtered_img -= filtered_img.min()
    filtered_img = filtered_img*255 / filtered_img.max()
    filtered_img = filtered_img.astype(np.uint8)

    f_orig_shifted = np.fft.fftshift(np.where(magnitude < t, 0,
                                              f_complex))
    inv_orig_img = np.fft.ifft2(f_orig_shifted) # inverse F.T.
    back_img = np.abs(inv_orig_img)
    back_img -= back_img.min()
    back_img = back_img*255 / back_img.max()
    back_img = back_img.astype(np.uint8)

    return filtered_img, magnitude, \
            (magnitude * (mask/255)).astype(np.uint8), back_img