import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keras.models import load_model
import tensorflow as tf




def iou(y_true, y_pred):
    def f(y_true, y_pred):
        intersection = (y_true * y_pred).sum()
        union = y_true.sum() + y_pred.sum() - intersection

        x = (intersection + 1e-15) / (union + 1e-15)
        x = x.astype(np.float32)
        return x
    return tf.numpy_function(f, [y_true, y_pred], tf.float32)


smooth = 1e-15
def dice_coef(y_true, y_pred):
    y_true = tf.keras.layers.Flatten()(y_true)
    y_pred = tf.keras.layers.Flatten()(y_pred)

    intersection = tf.reduce_sum(y_true*y_pred)
    return (2. * intersection + smooth) / (tf.reduce_sum(y_true) + tf.reduce_sum(y_pred))


def dice_loss(y_true, y_pred):
    return 1.0 - dice_coef(y_true, y_pred)


def get_segmentation(image,w, h):
        saved_model_path = r"C:\Users\EkremSerdar\Downloads\saved_model_road"
        loaded_model = tf.saved_model.load(saved_model_path)
        model = loaded_model.signatures["serving_default"]
        image = cv2.resize(image, (256, 256))
        img = np.expand_dims(image, axis=0)
        img = img /255.
        img = img.astype(np.float32)
        prediction = model(tf.constant(img))['conv2d_18'].numpy()
        prediction = prediction[0, ...]
        prediction = (prediction * 255).astype(np.uint8)
        prediction = cv2.resize(prediction, (int(h/2), int(w/2)))
        threshold_value = 5
        _, binary_image = cv2.threshold(prediction, threshold_value, 255, cv2.THRESH_BINARY)
        kernel = np.ones((3, 3), np.uint8)
        reversed_dilated_image = cv2.erode(binary_image, kernel, iterations=1)
        grayscale_image = cv2.cvtColor(reversed_dilated_image, cv2.COLOR_GRAY2BGR)
        return reversed_dilated_image




# Add it as a layer rather than showing with the ui

def save_prediction(pred):
     cv2.imwrite(r"C:\Users\EkremSerdar\OneDrive\Masaüstü\segmented_image\segmented.png", pred)
     

# img = plt.imread("satellite_img.PNG")
# print(img.shape)
# img = img[:, :, :3]
# pred = get_segmentation(img, 256,256)
# plt.imshow(pred)
# print(pred.shape)
# plt.show()

# path = r"C:\Users\EkremSerdar\OneDrive\Masaüstü\road_segmented_images"
# cv2.imwrite("segmented.png", pred)
# print("image is saved")
# threshold_value = 4  # Example threshold value
# _, binary_image = cv2.threshold(pred, threshold_value, 255, cv2.THRESH_BINARY)
# mask = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
# print(img.shape, binary_image.shape, mask.shape)

# masked_image = cv2.bitwise_and(img, mask)



# # New Shit


# #print(pred.shape)

# plt.figure(figsize=(12, 6))
# plt.subplot(121)
# plt.imshow(binary_image)
# plt.title("Original Image")
# plt.subplot(122)
# plt.imshow(masked_image, cmap="gray")
# plt.title("Segmented Image")
# plt.show()







































# Works but can be better

# max_lines = 50

# kernel = np.ones((3, 3), np.uint8)
# dilated_image = cv2.dilate(binary_image, kernel, iterations=1)
# reversed_dilated_image = cv2.erode(binary_image, kernel, iterations=1)
# print(dilated_image.shape) # (256, 256)
# edges = cv2.Canny(reversed_dilated_image, threshold1=50, threshold2=100)
# lines = cv2.HoughLinesP(reversed_dilated_image, rho=1, theta=np.pi/180, threshold=80, minLineLength=10, maxLineGap=100)
# print(len(lines))
# if lines is not None and len(lines) > max_lines:
#     lines = lines[:max_lines]

# # Check the distance between lines
# distance_threshold = 20  # Adjust this value based on your needs
# filtered_lines = []

# for line in lines:
#     x1, y1, x2, y2 = line[0]
#     is_close = False

#     for filtered_line in filtered_lines:
#         # Calculate the distance between the current line and filtered lines
#         distance = np.sqrt((x1 - filtered_line[0]) ** 2 + (y1 - filtered_line[1]) ** 2)
        
#         if distance < distance_threshold:
#             is_close = True
#             break

#     if not is_close:
#         filtered_lines.append([x1, y1, x2, y2])

# result_img = img.copy()
# for line in filtered_lines:
#     x1, y1, x2, y2 = line
#     cv2.line(result_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

# print(f"filtered lines: {len(filtered_lines)}")

# plt.figure(figsize=(12, 6))
# plt.subplot(141)
# plt.imshow(img)
# plt.title("pred Image")
# plt.subplot(142)
# plt.imshow(binary_image)
# plt.title("binary_image")
# plt.subplot(143)
# plt.imshow(reversed_dilated_image, cmap="gray")
# plt.title("reversed_dilated_image ")
# plt.subplot(144)
# plt.imshow(result_img, cmap="gray")
# plt.title("result_img")
# plt.show()



