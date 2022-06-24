import cv2  # opencv读取的格式是BGR
import time
import RPi.GPIO as GPIO
import numpy as np
GPIO.setmode(GPIO.BOARD)                      #设置GPIO的编码类型为board物理引脚

GPIO.setup(12, GPIO.OUT)                      #设置12号引脚为输出模式  控制舵机
p = GPIO.PWM(12, 50)                          # 50为频率
p.start(20)                                   #升起笔

GPIO.setup(16, GPIO.OUT)                       #电机1转向
GPIO.setup(18, GPIO.OUT)                       #电机1驱动
GPIO.setup(11, GPIO.OUT)                       #电机2转向      2019-04-08-raspbian-stretch-full
GPIO.setup(13, GPIO.OUT)                       #电机2驱动

GPIO.setup(15, GPIO.OUT)                       #ENA
GPIO.output(15,GPIO.LOW)

def move (x):       #同步移动
    while x>0:
        GPIO.output(13, GPIO.HIGH)
        GPIO.output(18, GPIO.HIGH)
        time.sleep(0.006)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(18, GPIO.LOW)
        time.sleep(0.006)
        x-=1
        
        
img = cv2.imread(r'/home/pi/Desktop/light.jpg')     # 从指定路径拿到图像
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 将图像转化为灰度图   0 ~ 255

test=10          #取二值时的阀值
TestMark1=0     #最多的轮廓数目
TestMark3=10    #最多时的阀值
while test<250 :  #这个while用来找到轮廓最多状态
    TestMark2=0   #轮廓数目
    test += 1
    ret, thresh = cv2.threshold(gray, test, 255, cv2.THRESH_BINARY)  # 0 100 255
    # 当大于127取 255     当小于127取0       即取二值  要么255 要么0
    binary, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # 检测轮廓
    for h in contours:
        TestMark2 += 1
    if TestMark2 > TestMark1:
        print("轮廓数目为",TestMark2)
        TestMark1 = TestMark2
        TestMark3 = test
print("轮廓数目最多时的阀值为",TestMark3)



            
            
ret, thresh = cv2.threshold(gray,TestMark3, 255, cv2.THRESH_BINARY)
    # 当大于127取 255     当小于127取0       即取二值  要么255 要么0
binary, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # 检测轮廓
        
    
canvas1 = img.copy()  # 取一个画布
canvas1[:, :, 0] = 0  # [行数,列数,0]     0表示 B通道
canvas1[:, :, 1] = 0  # [行数,列数,1]     1表示 G通道              #将画布清空
canvas1[:, :, 2] = 0  # [行数,列数,1]     1表示 R通道
res1 = cv2.drawContours(canvas1, contours, -1, (255, 0, 0), 1)
rest = np.hstack((res1,img))         #np.hstack((v1,v2))  将v1和v2拼起来
cv2.imshow('以下为基础轮廓与原图像的对比,请按任意键开始！',rest) 
cv2.waitKey(0)                              
cv2.destroyAllWindows()

x0 = -0.0
y0 = -0.0
for c in contours:  # 遍历每一个轮廓
    #当轮廓面积小于10  周长小于20  直接滤掉   受机械结构影响  太小的轮廓也画不出来
    if (cv2.contourArea(c)<10) or (cv2.arcLength(c,True)<20) or (cv2.arcLength(c,0)<20):
        continue
    
    #canvas1 = img.copy()  # 取一个画布
    #canvas1[:, :, 0] = 0  # [行数,列数,0]     0表示 B通道
    #canvas1[:, :, 1] = 0  # [行数,列数,1]     1表示 G通道              #将画布清空
    #canvas1[:, :, 2] = 0  # [行数,列数,1]     1表示 R通道
    #res = cv2.drawContours(canvas1, [c], -1, (0, 0, 255), 1)  # 使用红色在画布上画轮廓
    #cv2.imshow('66',res)
    #cv2.waitKey(10)
    #cv2.destroyAllWindows()
    #显示一下这个轮廓
    

    for a in c:#移动到下一个轮廓起点
        p.ChangeDutyCycle(20)  # 升起笔
        time.sleep(0.1)
        x = float(a[0][0])
        y = float(a[0][1])
        while int(x - x0) > 0:
            x0 += 1
            GPIO.output(16, GPIO.HIGH)
            GPIO.output(11, GPIO.LOW)           #  x正向
            move(2)

        while int(x - x0) < 0:                                                        #先移动x
            x0 -= 1
            GPIO.output(16, GPIO.LOW)
            GPIO.output(11, GPIO.HIGH)           # x负向
            move(2)

        while int(y - y0) > 0:
            y0 += 1
            GPIO.output(16, GPIO.HIGH)
            GPIO.output(11, GPIO.HIGH)           # Y正向
            move (1)

        while int(y - y0) < 0:                                                         #再移动y
            y0 -= 1
            GPIO.output(16, GPIO.LOW)
            GPIO.output(11, GPIO.LOW)           # Y负向
            move (1)
        break

    x1=x
    y1=y         #轮廓起始点


#以下为绘制轮廓
    for b in c:                            # 遍历轮廓上每一个点 b为一个点
        #print('x0=', x0, 'y0=', y0)
        p.ChangeDutyCycle(5)  # 放下笔
        time.sleep(0.1)     #等一下  防止笔上来时移动
        x = float(b[0][0])
        y = float(b[0][1])
        #print('x=', x, 'y=', y)
        if x - x0 == 0:                                       #x方向无变化
            while int(y - y0) > 0:
                y0 += 1
                GPIO.output(16, GPIO.HIGH)
                GPIO.output(11, GPIO.HIGH)    # Y正向
                move(1)
            while int(y - y0) < 0:
                y0 -= 1
                GPIO.output(16, GPIO.LOW)
                GPIO.output(11, GPIO.LOW)     # Y负向
                move(1)

        elif y - y0 == 0:                                     #y方向无变化
            while int(x - x0) > 0:
                x0 += 1
                GPIO.output(16, GPIO.HIGH)
                GPIO.output(11, GPIO.LOW)  # x正向
                move(2)
            while int(x - x0) < 0:
                x0 -= 1
                GPIO.output(16, GPIO.LOW)
                GPIO.output(11, GPIO.HIGH)  # x负向
                move(2)
        
        else:
            scale =-0.000
            scale =((y - y0) / (x - x0))  # 比例
            print(scale)
            if scale<0:
                scale = -scale               
            while int(x - x0) > 0:
                x0 += 1
                GPIO.output(16, GPIO.HIGH)
                GPIO.output(11, GPIO.LOW)         # x正向一步
                move(2)
                if (y - y0)>0:
                    y0 += scale
                    GPIO.output(16, GPIO.HIGH)
                    GPIO.output(11, GPIO.HIGH)  # Y正向
                    move(scale)
                elif (y - y0)<0:
                    y0 -= scale
                    GPIO.output(16, GPIO.LOW)
                    GPIO.output(11, GPIO.LOW)  # Y负向
                    move(scale)

            while int(x - x0) < 0:
                x0 -= 1
                GPIO.output(16, GPIO.LOW)
                GPIO.output(11, GPIO.HIGH)      # x负向一步
                move(2)
                if (y - y0)> 0:
                    y0 += scale
                    GPIO.output(16, GPIO.HIGH)
                    GPIO.output(11, GPIO.HIGH)  # Y正向
                    move(scale)
                elif (y - y0) < 0:
                    y0 -= scale
                    GPIO.output(16, GPIO.LOW)
                    GPIO.output(11, GPIO.LOW)  # Y负向
                    move(scale)
            
        
        
        
        
    x=x1
    y=y1    #以下为回到轮廓起始点
            
    if x - x0 == 0:                                       #x方向无变化
        while int(y - y0) > 0:
            y0 += 1
            GPIO.output(16, GPIO.HIGH)
            GPIO.output(11, GPIO.HIGH)    # Y正向
            move(1)
        while int(y - y0) < 0:
            y0 -= 1
            GPIO.output(16, GPIO.LOW)
            GPIO.output(11, GPIO.LOW)     # Y负向
            move(1)

    elif y - y0 == 0:                                     #y方向无变化
        while int(x - x0) > 0:
            x0 += 1
            GPIO.output(16, GPIO.HIGH)
            GPIO.output(11, GPIO.LOW)  # x正向
            move(2)
        while int(x - x0) < 0:
            x0 -= 1
            GPIO.output(16, GPIO.LOW)
            GPIO.output(11, GPIO.HIGH)  # x负向
            move(2)
        
    else:
        scale =-0.000
        scale =((y - y0) / (x - x0))  # 比例
        print(scale)
        if scale<0:
            scale = -scale               
        while int(x - x0) > 0:
            x0 += 1
            GPIO.output(16, GPIO.HIGH)
            GPIO.output(11, GPIO.LOW)         # x正向一步
            move(2)
            if (y - y0)>0:
                y0 += scale
                GPIO.output(16, GPIO.HIGH)
                GPIO.output(11, GPIO.HIGH)  # Y正向
                move(scale)
            elif (y - y0)<0:
                y0 -= scale
                GPIO.output(16, GPIO.LOW)
                GPIO.output(11, GPIO.LOW)  # Y负向
                move(scale)

        while int(x - x0) < 0:
            x0 -= 1
            GPIO.output(16, GPIO.LOW)
            GPIO.output(11, GPIO.HIGH)      # x负向一步
            move(2)
            if (y - y0)> 0:
                y0 += scale
                GPIO.output(16, GPIO.HIGH)
                GPIO.output(11, GPIO.HIGH)  # Y正向
                move(scale)
            elif (y - y0) < 0:
                y0 -= scale
                GPIO.output(16, GPIO.LOW)
                GPIO.output(11, GPIO.LOW)  # Y负向
                move(scale)
                


#进行图像补充
if TestMark3 >200:
    add = (TestMark3/2)
elif TestMark3<20:
    add = (TestMark3*4)
elif TestMark3 <100:
    add = (TestMark3*2)
mark1 =1
    # 当大于127取 255     当小于127取0       即取二值  要么255 要么0
while(mark1):
    ret, thresh = cv2.threshold(gray,add, 255, cv2.THRESH_BINARY)
    binary, contours2, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # 检测轮廓
    canvas2 = img.copy()  # 取一个画布
    canvas2[:, :, 0] = 0  # [行数,列数,0]     0表示 B通道
    canvas2[:, :, 1] = 0  # [行数,列数,1]     1表示 G通道              #将画布清空
    canvas2[:, :, 2] = 0  # [行数,列数,1]     1表示 R通道
    res2 = cv2.drawContours(canvas2, contours2, -1, (0, 0, 255), 1)
    rest2 = np.hstack((res2,rest))         #np.hstack((v1,v2))  将v1和v2拼起来
    cv2.imshow('最左边为补充轮廓，请按任意键继续！',rest2)  
    cv2.waitKey(0)                              
    cv2.destroyAllWindows()
    key1 = input("请问对补充轮廓是否满意？（是请输入1 否请输入0)")
    if key1 == "1":
        mark1 = 0
    elif key1 == "0":
        print("基础轮廓灰度二分值为:",TestMark3)
        key2 = input("请输入补充轮廓的灰度二分值(0~255):")
        add = int(key2)
    
               


for k in contours2:
    if (cv2.contourArea(k) < 10) or (cv2.arcLength(k, True) < 20) or (cv2.arcLength(k, 0) < 20):
        continue
    mark2=0
    mark3=1
    for c in contours:  # 遍历每一个轮
        if (cv2.contourArea(c) < 10) or (cv2.arcLength(c, True) < 20) or (cv2.arcLength(c, 0) < 20):
            continue
        a1 = np.reshape(k, (-1, 2))       #将三维数组转化为二维
        a2 = np.reshape(c, (-1, 2))
        sum1 = a1.shape[0]           #输出行数   即该轮廓中点的个数
        #print(a1.shape[1])          #输出列数

        a1_rows = a1.view([('', a1.dtype)] * a1.shape[1])
        a2_rows = a2.view([('', a2.dtype)] * a2.shape[1])                             #a3=a1-a2 为a1中有而a2中没有的点
        a3 = np.setdiff1d(a1_rows, a2_rows).view(a1.dtype).reshape(-1, a1.shape[1])

        sum2 = sum1 - a3.shape[0]  # 输出行数  基础轮廓与补充轮廓  在该轮廓上相同点的个数     #相同点的个数
        percentage = (sum2/sum1)*100      #相似度
        if (percentage>2) and (percentage<5):   #相似度大于5%就不再补充
            mark2 = 1
        if percentage > 1:               #相似度一直小于1%  说明为全新轮廓需要补充
            mark3 = 0

    if mark3==1 or mark2 == 1:
        for a in k:                                   # 移动到轮廓起点
            p.ChangeDutyCycle(20)  # 升起笔
            time.sleep(0.1)
            x = float(a[0][0])
            y = float(a[0][1])
            while int(x - x0) > 0:
                x0 += 1
                GPIO.output(16, GPIO.HIGH)
                GPIO.output(11, GPIO.LOW)  # x正向
                move(2)

            while int(x - x0) < 0:  # 先移动x
                x0 -= 1
                GPIO.output(16, GPIO.LOW)
                GPIO.output(11, GPIO.HIGH)  # x负向
                move(2)

            while int(y - y0) > 0:
                y0 += 1
                GPIO.output(16, GPIO.HIGH)
                GPIO.output(11, GPIO.HIGH)  # Y正向
                move(1)

            while int(y - y0) < 0:  # 再移动y
                y0 -= 1
                GPIO.output(16, GPIO.LOW)
                GPIO.output(11, GPIO.LOW)  # Y负向
                move(1)
            break

        x1 = x
        y1 = y  # 轮廓起始点

        # 以下为绘制轮廓
        for b in k:  # 遍历轮廓上每一个点 b为一个点
            # print('x0=', x0, 'y0=', y0)
            p.ChangeDutyCycle(5)  # 放下笔
            time.sleep(0.1)
            x = float(b[0][0])
            y = float(b[0][1])
            # print('x=', x, 'y=', y)
            if x - x0 == 0:  # x方向无变化
                while int(y - y0) > 0:
                    y0 += 1
                    GPIO.output(16, GPIO.HIGH)
                    GPIO.output(11, GPIO.HIGH)  # Y正向
                    move(1)
                while int(y - y0) < 0:
                    y0 -= 1
                    GPIO.output(16, GPIO.LOW)
                    GPIO.output(11, GPIO.LOW)  # Y负向
                    move(1)

            elif y - y0 == 0:  # y方向无变化
                while int(x - x0) > 0:
                    x0 += 1
                    GPIO.output(16, GPIO.HIGH)
                    GPIO.output(11, GPIO.LOW)  # x正向
                    move(2)
                while int(x - x0) < 0:
                    x0 -= 1
                    GPIO.output(16, GPIO.LOW)
                    GPIO.output(11, GPIO.HIGH)  # x负向
                    move(2)

            else:
                scale = -0.000
                scale = ((y - y0) / (x - x0))  # 比例
                print(scale)
                if scale < 0:
                    scale = -scale
                while int(x - x0) > 0:
                    x0 += 1
                    GPIO.output(16, GPIO.HIGH)
                    GPIO.output(11, GPIO.LOW)  # x正向一步
                    move(2)
                    if (y - y0) > 0:
                        y0 += scale
                        GPIO.output(16, GPIO.HIGH)
                        GPIO.output(11, GPIO.HIGH)  # Y正向
                        move(scale)
                    elif (y - y0) < 0:
                        y0 -= scale
                        GPIO.output(16, GPIO.LOW)
                        GPIO.output(11, GPIO.LOW)  # Y负向
                        move(scale)

                while int(x - x0) < 0:
                    x0 -= 1
                    GPIO.output(16, GPIO.LOW)
                    GPIO.output(11, GPIO.HIGH)  # x负向一步
                    move(2)
                    if (y - y0) > 0:
                        y0 += scale
                        GPIO.output(16, GPIO.HIGH)
                        GPIO.output(11, GPIO.HIGH)  # Y正向
                        move(scale)
                    elif (y - y0) < 0:
                        y0 -= scale
                        GPIO.output(16, GPIO.LOW)
                        GPIO.output(11, GPIO.LOW)  # Y负向
                        move(scale)

        x = x1
        y = y1  # 以下为回到轮廓起始点

        if x - x0 == 0:  # x方向无变化
            while int(y - y0) > 0:
                y0 += 1
                GPIO.output(16, GPIO.HIGH)
                GPIO.output(11, GPIO.HIGH)  # Y正向
                move(1)
            while int(y - y0) < 0:
                y0 -= 1
                GPIO.output(16, GPIO.LOW)
                GPIO.output(11, GPIO.LOW)  # Y负向
                move(1)

        elif y - y0 == 0:  # y方向无变化
            while int(x - x0) > 0:
                x0 += 1
                GPIO.output(16, GPIO.HIGH)
                GPIO.output(11, GPIO.LOW)  # x正向
                move(2)
            while int(x - x0) < 0:
                x0 -= 1
                GPIO.output(16, GPIO.LOW)
                GPIO.output(11, GPIO.HIGH)  # x负向
                move(2)

        else:
            scale = -0.000
            scale = ((y - y0) / (x - x0))  # 比例
            print(scale)
            if scale < 0:
                scale = -scale
            while int(x - x0) > 0:
                x0 += 1
                GPIO.output(16, GPIO.HIGH)
                GPIO.output(11, GPIO.LOW)  # x正向一步
                move(2)
                if (y - y0) > 0:
                    y0 += scale
                    GPIO.output(16, GPIO.HIGH)
                    GPIO.output(11, GPIO.HIGH)  # Y正向
                    move(scale)
                elif (y - y0) < 0:
                    y0 -= scale
                    GPIO.output(16, GPIO.LOW)
                    GPIO.output(11, GPIO.LOW)  # Y负向
                    move(scale)

            while int(x - x0) < 0:
                x0 -= 1
                GPIO.output(16, GPIO.LOW)
                GPIO.output(11, GPIO.HIGH)  # x负向一步
                move(2)
                if (y - y0) > 0:
                    y0 += scale
                    GPIO.output(16, GPIO.HIGH)
                    GPIO.output(11, GPIO.HIGH)  # Y正向
                    move(scale)
                elif (y - y0) < 0:
                    y0 -= scale
                    GPIO.output(16, GPIO.LOW)
                    GPIO.output(11, GPIO.LOW)  # Y负向
                    move(scale)





x=0
y=0    #以下为回到（0.0）点
p.ChangeDutyCycle(20)  # 升起笔
time.sleep(1)            
if x - x0 == 0:                                       #x方向无变化
    while int(y - y0) > 0:
        y0 += 1
        GPIO.output(16, GPIO.HIGH)
        GPIO.output(11, GPIO.HIGH)    # Y正向
        move(1)
    while int(y - y0) < 0:
        y0 -= 1
        GPIO.output(16, GPIO.LOW)
        GPIO.output(11, GPIO.LOW)     # Y负向
        move(1)

elif y - y0 == 0:                                     #y方向无变化
    while int(x - x0) > 0:
        x0 += 1
        GPIO.output(16, GPIO.HIGH)
        GPIO.output(11, GPIO.LOW)  # x正向
        move(2)
    while int(x - x0) < 0:
        x0 -= 1
        GPIO.output(16, GPIO.LOW)
        GPIO.output(11, GPIO.HIGH)  # x负向
        move(2)
        
else:
    scale =-0.000
    scale =((y - y0) / (x - x0))  # 比例
    print(scale)
    if scale<0:
        scale = -scale               
    while int(x - x0) > 0:
        x0 += 1
        GPIO.output(16, GPIO.HIGH)
        GPIO.output(11, GPIO.LOW)         # x正向一步
        move(2)
        if (y - y0)>0:
            y0 += scale
            GPIO.output(16, GPIO.HIGH)
            GPIO.output(11, GPIO.HIGH)  # Y正向
            move(scale)
        elif (y - y0)<0:
            y0 -= scale
            GPIO.output(16, GPIO.LOW)
            GPIO.output(11, GPIO.LOW)  # Y负向
            move(scale)

    while int(x - x0) < 0:
        x0 -= 1
        GPIO.output(16, GPIO.LOW)
        GPIO.output(11, GPIO.HIGH)      # x负向一步
        move(2)
        if (y - y0)> 0:
            y0 += scale
            GPIO.output(16, GPIO.HIGH)
            GPIO.output(11, GPIO.HIGH)  # Y正向
            move(scale)
        elif (y - y0) < 0:
            y0 -= scale
            GPIO.output(16, GPIO.LOW)
            GPIO.output(11, GPIO.LOW)  # Y负向
            move(scale)
                
    
                



cv2.destroyAllWindows()
p.stop()                         #停止 PWM
GPIO.output(16, GPIO.LOW)
GPIO.output(11, GPIO.LOW)  
GPIO.output(13, GPIO.LOW)  
GPIO.output(18, GPIO.LOW)  