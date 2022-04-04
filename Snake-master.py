import math
import random
import cvzone
import CV2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
#导入需要用到的包
cap = CV2.VideoCapture(2)
cap.set(3, 1280)
cap.set(4, 720)
#对摄像头进行调用，并设置界面大小
detector = HandDetector(detectionCon=0.8, maxHands=1)

#定义游戏类
class SnakeGameClass:
    def __init__(self, pathFood): #自定义一些参数，作用即为其字面意思
        self.points = []
        self.lengths = []
        self.currentLength = 0
        self.allowedLength = 150
        self.previousHead = 0, 0

        self.imgFood = CV2.imread(pathFood, CV2.IMREAD_UNCHANGED)
        self.hFood, self.wFood, _ = self.imgFood.shape
        self.foodPoint = 0, 0
        self.randomFoodLocation()

        self.score = 0
        self.gameOver = False

    def randomFoodLocation(self): #定义食物随机出现的位置，调用了随机类
        self.foodPoint = random.randint(100, 1000), random.randint(100, 600)

    def update(self, imgMain, currentHead):#进行更新

        if self.gameOver:
            cvzone.putTextRect(imgMain, "Game Over", [300, 400],
                               scale=7, thickness=5, offset=20)
            cvzone.putTextRect(imgMain, f'Your Score: {self.score}', [300, 550],
                               scale=7, thickness=5, offset=20)
        else:
            px, py = self.previousHead
            cx, cy = currentHead

            self.points.append([cx, cy])
            distance = math.hypot(cx - px, cy - py)
            self.lengths.append(distance)
            self.currentLength += distance
            self.previousHead = cx, cy

            # 长度缩减
            if self.currentLength > self.allowedLength:
                for i, length in enumerate(self.lengths):
                    self.currentLength -= length
                    self.lengths.pop(i)
                    self.points.pop(i)
                    if self.currentLength < self.allowedLength:
                        break

            # 检查是否吃到食物
            rx, ry = self.foodPoint
            if rx - self.wFood // 2 < cx < rx + self.wFood // 2 and \
                    ry - self.hFood // 2 < cy < ry + self.hFood // 2:
                self.randomFoodLocation()
                self.allowedLength += 50
                self.score += 1
                print(self.score)

            # 对蛇进行描述，吃到食物进行增加
            if self.points:
                for i, point in enumerate(self.points):
                    if i != 0:
                        CV2.line(imgMain, self.points[i - 1], self.points[i], (0, 0, 255), 20)
                CV2.circle(imgMain, self.points[-1], 20, (0, 255, 0), CV2.FILLED)


            imgMain = cvzone.overlayPNG(imgMain, self.imgFood,
                                        (rx - self.wFood // 2, ry - self.hFood // 2))

            cvzone.putTextRect(imgMain, f'Score: {self.score}', [50, 80],
                               scale=3, thickness=3, offset=10)

            # 检查是否碰撞
            pts = np.array(self.points[:-2], np.int32)
            pts = pts.reshape((-1, 1, 2))
            CV2.polylines(imgMain, [pts], False, (0, 255, 0), 3)
            minDist = CV2.pointPolygonTest(pts, (cx, cy), True)

            if -1 <= minDist <= 1:
                print("Hit")
                self.gameOver = True
                self.points = []
                self.lengths = []
                self.currentLength = 0
                self.allowedLength = 150
                self.previousHead = 0, 0
                self.randomFoodLocation()

        return imgMain


game = SnakeGameClass("Donut.png") # 食物图片可以自己随便换

while True:
    success, img = cap.read()
    img = CV2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)

    if hands:
        lmList = hands[0]['lmList']
        pointIndex = lmList[8][0:2]
        img = game.update(img, pointIndex)
    CV2.imshow("Image", img)
    key = CV2.waitKey(1)
    if key == ord('r'):
        game.gameOver = False