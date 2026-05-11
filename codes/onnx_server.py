import math
import socket
import pickle  
import numpy as np
import onnxruntime as ort
import timeit
import cv2

global error, cont, sec
cont = 0
sec = 0
error = 0
HEADERSIZE =10
print(5)
n = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
n.bind(("localhost",1808))
n.listen(10)
print("waiting")
clientsocket, address = n.accept()

onnx_model_path = "PipeSeg_tiny (2).onnx"
sess = ort.InferenceSession(onnx_model_path)
inp, out = sess.get_inputs()[0], sess.get_outputs()[0]
print('data_sent')
video = cv2.VideoCapture(0)
if (video.isOpened() == False):
	print("Error reading video file")

while(True):
	ret, frame = video.read()
	cont += 1
	if ret == True:

		#print(c)
		
		# if c > 100:
		# 	break
		tic = timeit.default_timer() #time start
		frame = cv2.resize(frame, (320, 240))
		frame = frame[:,:,::-1]/255.0
		img = frame.reshape(1, 240, 320, 3).astype(np.float32)
		
		pred = sess.run([out.name], {inp.name: img})[0].reshape(240, 320)
		toc = timeit.default_timer()
		#print(toc-tic)
		duration = toc-tic
		
		sec += duration
		if sec >= 1:
			print(cont)
			cont = 0
			sec = 0
		pred = np.where(pred>0.5, 0.0, 1.0)*255.0
		pred = np.dstack([pred, pred, pred]).astype(np.uint8)
		#print(pred.shape)
		final = np.hstack([frame[:,:,::-1]*255, pred]).astype(np.uint8)
		#cv2.imshow('final', final)
		op =  cv2.resize(pred,(640,480))#, fx=0, fy=0, interpolation=cv2.INTER_NEAREST) 
		#print(np.unique(op))
		pred_gray = cv2.cvtColor(op,cv2.COLOR_BGR2GRAY)
		
		ret, thers1 = cv2.threshold(pred_gray, 128, 255, cv2.THRESH_BINARY)
		#thers1 = np.array(thers1)
		cnts, her = cv2.findContours(thers1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		conts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]
		if len(conts) >0:
			cnt = conts[0]
			area = cv2.contourArea(cnt)
			if area>1500 and area<150000:
				rect = cv2.minAreaRect(cnt)
				#elips = cv2.fitEllipse(cnt)
				#print('elipse_angle',elips[2])
				box = cv2.boxPoints(rect)
				centre = rect[0]
				rect_angle = rect[2]
				box = np.int0(box)
				[vx, vy, x, y] = cv2.fitLine(cnt, cv2.DIST_L2, 0,0.01,0.01)
				rows,cols =op.shape[:2]
				left = int((-x*vy/vx)+y)
				right = int(((cols-x)*vy/vx)+y)
				if left>right:
					angle = -rect_angle
				elif right>left:
					angle = 90-rect_angle
				if angle <=-90 or angle >= 90:
					angle =0
					
					
				print(angle)	
				data = {1:[centre[0],centre[1],angle]}
				p = pickle.dumps(data)
				msg = p
				clientsocket.send(msg)
		resultin.write(final)
		if cv2.waitKey(1) & 0xFF == ord('s'):
			break	
		
				
                
    



