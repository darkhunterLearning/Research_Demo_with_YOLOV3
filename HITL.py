import os
import glob
from PIL import Image, ImageDraw
from dicttoxml import dicttoxml
from yolo_model import *

my_model = YoloModel()
my_model.load_model()

list_filenames = glob.glob('D:/Datasets/har/HITL/HITL_2/images/*.jpg')
idx = -1

for idx in range(len(list_filenames)):
	filepath = list_filenames[idx]
	filename = os.path.basename(filepath)
	image = Image.open(filepath)
	list_results = my_model.predict(image)
	xml_filepath = filepath.replace('images', 'anns').replace('jpg', 'xml')
	with open(xml_filepath, 'w') as fp:
		fp.write('<annotation>')
		fp.write(f'<filename>{filename}</filename>')
		fp.write(f'<size><width>{image.width}</width><height>{image.height}</height></size>')
		for result in list_results:
			fp.write(f'<object><name>Unlabel</name>')
			fp.write(f'<bndbox><xmin>{result[0]}</xmin><ymin>{result[1]}</ymin><xmax>{result[2]}</xmax><ymax>{result[3]}</ymax></bndbox>')
			fp.write('</object>')
		fp.write('</annotation>')