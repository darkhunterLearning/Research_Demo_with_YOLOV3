import os
import cv2
from utils.utils import get_yolo_boxes, makedirs
from utils.bbox import draw_boxes
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image 

class YoloModel:
	def __init__(self):
		self.net_h = 416 
		self.net_w = 416
		self.anchors = [17,40, 23,53, 23,39, 26,73, 31,58, 34,151, 35,88, 48,91, 53,189]
		self.label = ["Non-Positive", "Positive"]
		self.model = None
		self.obj_thresh = 0.4
		self.nms_thresh = 0.45

	def load_model(self):
		self.model = load_model('classroom_2.h5')

	def predict(self, image):
		numpy_image=np.array(image) 
		preprocess_image=cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR) 
		no_class_img=cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
		pos_img=cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR) 
		non_pos_img=cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR) 

		boxes = get_yolo_boxes(self.model, [preprocess_image], self.net_h, self.net_w, 
							self.anchors, self.obj_thresh, self.nms_thresh)[0]

		#Get image with 2 class 
		img = draw_boxes(preprocess_image, boxes, self.label, self.obj_thresh)

		list_pos_boxes = []
		list_non_boxes = []
		num_pos = 0
		num_non_pos = 0

		for box in boxes:
			if box.score != -1:
				if box.get_label() == 0:
					list_non_boxes.append((box.xmin, box.ymin, box.xmax, box.ymax, box.get_score()))
					num_non_pos += 1
				else:
					list_pos_boxes.append((box.xmin, box.ymin, box.xmax, box.ymax, box.get_score()))
					num_pos += 1

		for i in range(len(list_pos_boxes)):
			label_str = ''
			label = -1

			if list_pos_boxes[i][4] > self.obj_thresh:
				if label_str != '': label_str += ', '
				label_str += ('Positive' + ' ' + str(round(list_pos_boxes[i][4]*100, 2)) + '%')


			text_size = cv2.getTextSize(label_str, cv2.FONT_HERSHEY_SIMPLEX, 1.1e-3*pos_img.shape[0], 5)
			width, height = text_size[0][0], text_size[0][1]
			region = np.array([[list_pos_boxes[i][0]-3,        list_pos_boxes[i][1]], 
								[list_pos_boxes[i][0]-3,        list_pos_boxes[i][1]-height-26], 
								[list_pos_boxes[i][0]+width+13, list_pos_boxes[i][1]-height-26], 
								[list_pos_boxes[i][0]+width+13, list_pos_boxes[i][1]]], dtype='int32')  
			
			cv2.rectangle(img=pos_img, pt1=(list_pos_boxes[i][0], list_pos_boxes[i][1]), pt2=(list_pos_boxes[i][2], list_pos_boxes[i][3]), color=(0, 255, 0), thickness=3)
			cv2.fillPoly(img=pos_img, pts=[region], color=[0, 255, 0])
			cv2.putText(img=pos_img, 
						text=label_str, 
						org=(list_pos_boxes[i][0]+13, list_pos_boxes[i][1] - 13), 
			 			fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
						fontScale=1e-3 * pos_img.shape[0], 
						color=(0,0,0), 
						thickness=2)

			for i in range(len(list_non_boxes)):
				label_str = ''
				label = -1
			
				if list_non_boxes[i][4] > self.obj_thresh:
					if label_str != '': label_str += ', '
					label_str += ('Non-Positive' + ' ' + str(round(list_non_boxes[i][4]*100, 2)) + '%')

				text_size = cv2.getTextSize(label_str, cv2.FONT_HERSHEY_SIMPLEX, 1.1e-3*non_pos_img.shape[0], 5)
				width, height = text_size[0][0], text_size[0][1]

				region = np.array([[list_non_boxes[i][0]-3,        list_non_boxes[i][1]], 
									[list_non_boxes[i][0]-3,        list_non_boxes[i][1]-height-26], 
									[list_non_boxes[i][0]+width+13, list_non_boxes[i][1]-height-26], 
									[list_non_boxes[i][0]+width+13, list_non_boxes[i][1]]], dtype='int32')  

				cv2.rectangle(img=non_pos_img, pt1=(list_non_boxes[i][0], list_non_boxes[i][1]), pt2=(list_non_boxes[i][2], list_non_boxes[i][3]), color=(255, 0, 0), thickness=3)
				cv2.fillPoly(img=non_pos_img, pts=[region], color=(255, 0, 0))
				cv2.putText(img=non_pos_img, 
							text=label_str, 
							org=(list_non_boxes[i][0]+13, list_non_boxes[i][1] - 13), 
							fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
							fontScale=1e-3*non_pos_img.shape[0], 
							color=(0,0,0), 
							thickness=2)

		#Back to RGB
		img=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		no_class_img=cv2.cvtColor(no_class_img, cv2.COLOR_BGR2RGB)
		pos_img=cv2.cvtColor(pos_img, cv2.COLOR_BGR2RGB)
		non_pos_img=cv2.cvtColor(non_pos_img, cv2.COLOR_BGR2RGB)

		return img, no_class_img, pos_img, non_pos_img, num_non_pos, num_pos