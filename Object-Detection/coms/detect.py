# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A demo that runs object detection on camera frames using OpenCV.

TEST_DATA=../all_models

Run face detection model:
python3 detect.py \
  --model ${TEST_DATA}/mobilenet_ssd_v2_face_quant_postprocess_edgetpu.tflite

Run coco model:
python3 detect.py \
  --model ${TEST_DATA}/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite \
  --labels ${TEST_DATA}/coco_labels.txt

"""
import argparse
import cv2
import os
import sys

from pycoral.adapters.common import input_size
from pycoral.adapters.detect import get_objects
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter
from pycoral.utils.edgetpu import run_inference

from flask import Flask, render_template, Response
import threading
# from camera import Camera

import time
import board
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit

kit = MotorKit(i2c=board.I2C())
app = Flask(__name__)

outputFrame = None
lock = threading.Lock()

@app.route('/')
def index():
    return render_template('./index.html')

@app.route('/video_feed')
def video_feed():
    return Response(main(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def main():
    default_model_dir = './'
    default_model = '/home/pi/DDS/Object-Detection/coms/output_tflite_graph_edgetpu_v2.tflite'
    default_labels = '/home/pi/DDS/Object-Detection/coms/drone_labels.txt'
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', help='.tflite model path',
                        default=os.path.join(default_model_dir,default_model))
    parser.add_argument('--labels', help='label file path',
                        default=os.path.join(default_model_dir, default_labels))
    parser.add_argument('--top_k', type=int, default=3,
                        help='number of categories with highest score to display')
    parser.add_argument('--camera_idx', type=int, help='Index of which video source to use. ', default = 0)
    parser.add_argument('--threshold', type=float, default=0.1,
                        help='classifier score threshold')
    args = parser.parse_args()

    print('Loading {} with {} labels.'.format(args.model, args.labels))
    interpreter = make_interpreter(args.model)
    interpreter.allocate_tensors()
    labels = read_label_file(args.labels)
    inference_size = input_size(interpreter)

    cap = cv2.VideoCapture(args.camera_idx)

    frame_rate_calc = 1
    freq = cv2.getTickFrequency()
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        t1 = cv2.getTickCount()
        
        cv2_im = frame

        height, width, _ = frame.shape
        center_bar = ((2*width//3) - width//3)//2 + width//3
        cv2.line(cv2_im, (center_bar,0), (center_bar,height), (255,0,0), 5)

        cv2_im_rgb = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
        cv2_im_rgb = cv2.resize(cv2_im_rgb, inference_size)
        run_inference(interpreter, cv2_im_rgb.tobytes())
        objs = get_objects(interpreter, args.threshold)[:args.top_k]
        cv2_im = append_objs_to_img(cv2_im, inference_size, objs, labels)
        
        cv2.putText(frame, f'FPS: {int(frame_rate_calc)}', (30,50), cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)
        #cv2.imshow('frame', cv2_im)
        
        t2 = cv2.getTickCount()
        time1 = (t2-t1)/freq
        frame_rate_calc = 1/time1
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        (flag, encodedImage) = cv2.imencode(".jpg", cv2_im)
        if not flag:
            continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

    cap.release()
    cv2.destroyAllWindows()
    kit.stepper1.release()

def append_objs_to_img(cv2_im, inference_size, objs, labels):
    height, width, channels = cv2_im.shape
    scale_x, scale_y = width / inference_size[0], height / inference_size[1]
    max_score = 0
    if objs:
        max_score = max([o.score for o in objs])
    for obj in objs:
        if obj.score > .40:
            bbox = obj.bbox.scale(scale_x, scale_y)
            x0, y0 = int(bbox.xmin), int(bbox.ymin)
            x1, y1 = int(bbox.xmax), int(bbox.ymax)
            center = (x1 - x0) // 2 + x0 
            right_bar = width //3
            left_bar = 2 * (width // 3)
            center_bar = (right_bar - left_bar) // 2 + left_bar

            percent = int(100 * obj.score)
            label = '{}% {}'.format(percent, labels.get(obj.id, obj.id))
            

            if center < center_bar-20 and max_score >= obj.score:
                kit.stepper1.onestep(direction=stepper.FORWARD, style=stepper.SINGLE)

            if center > center_bar+20 and max_score >= obj.score:
                kit.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)

            cv2_im = cv2.rectangle(cv2_im, (x0, y0), (x1, y1), (0, 255, 0), 2)
            cv2_im = cv2.putText(cv2_im, label, (x0, y0+30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)

        if obj.score > .75:
            cv2.putText(cv2_im, f'SHEEESH', (120,120), cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)

    return cv2_im

if __name__ == '__main__':
    try:
        # main()
        app.run(host='192.168.1.24', debug=True)
    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        kit.stepper1.release()
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
