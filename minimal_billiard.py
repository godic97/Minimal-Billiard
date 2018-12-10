from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import numpy as np
import random
from PIL import Image

wnd_width = 800
wnd_height = 600

Ld = [1, 1, 1, 0]
Ls = [1, 1, 1, 0]
La = [0.5, 0.5, 0.5, 0]

Md = [1, 1, 0, 1]
Ms = [1, 1, 1, 1]
Ma = [0.5, 0.5, 0.5, 0]
shininess = [80]

isLightOn = True
isRotateCamera = True
rotateSpeed = math.pi/1000

isBallMove = False
ballSpeed = 0
ballSpeed_min = 0.5
ballAngle = 0
ballFriction = 0.001

ballPosX = 0
ballPosY = 1
ballPosZ = 0

cameraDist = 40
cameraAngleX = math.pi / 6
cameraAngleY = math.pi / 6


cameraPosX = 15
cameraPosY = 10
cameraPosZ = 25

wallColor = [0.5, 0.7, 0.8]
floorColor = [0.3, 0.3, 0.7]
tableColor = [0.1, 0.1, 0.1]
ballColor = [1.0, 0.1, 0.1]

poolWall = [
    [[-10, 1, -20], [10, 1, -20]],
    [[10, 1, -20], [10, 1, 20]],
    [[10, 1, 20], [-10, 1, 20]],
    [[-10, 1, 20], [-10, 1, -20]]]

def loadImage(filename):
    img = Image.open(filename)
    data = np.array(list(img.getdata()), np.uint16)
    return img.size[0], img.size[1], data

wallImgX, wallImgY, wallImg = loadImage("wall.jpg")
floorImgX, floorImgY, floorImg = loadImage("floor.jpg")

def getNormalV(p1, p2, p3):
    u = np.array([p2[i] - p1[i] for i in range(0, 3)])
    v = np.array([p3[i] - p1[i] for i in range(0, 3)])
    normal = np.cross(u, v)
    normal = normal / np.linalg.norm(normal)
    return normal



def loadMesh(filename):
    with open(filename, "rt") as mesh:
        nV = int(next(mesh))
        vertices = [[0, 0, 0] for idx in range(nV)]
        for i in range(0, nV):
            vertices[i][0], vertices[i][1], vertices[i][2] = [float(x) for x in next(mesh).split()]
        nF = int(next(mesh))
        faces = [[0, 0, 0, 0] for idx in range(nF)]
        for i in range(0, nF):
            faces[i][0], faces[i][1], faces[i][2], faces[i][3] = [int(x) for x in next(mesh).split()]
    return vertices, faces

def drawWall():
    glColor3fv([1,1,1])
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, wallImgX, wallImgY, 0, GL_RGB, GL_UNSIGNED_BYTE, wallImg)

    glBegin(GL_QUADS)
    glTexCoord2fv([0, 1])
    glVertex3fv([-50, 50, 50])
    glTexCoord2fv([1, 1])
    glVertex3fv([-50, 50, -50])
    glTexCoord2fv([1, 0])
    glVertex3fv([-50, -50,-50])
    glTexCoord2fv([0, 0])
    glVertex3fv([-50, -50, 50])

    glTexCoord2fv([0, 1])
    glVertex3fv([50, 50, 50])
    glTexCoord2fv([1, 1])
    glVertex3fv([50, 50, -50])
    glTexCoord2fv([1, 0])
    glVertex3fv([50, -50,-50])
    glTexCoord2fv([0, 0])
    glVertex3fv([50, -50, 50])

    glTexCoord2fv([0, 1])
    glVertex3fv([-50, -50, -50])
    glTexCoord2fv([1, 1])
    glVertex3fv([50, -50, -50])
    glTexCoord2fv([1, 0])
    glVertex3fv([50, 50, -50])
    glTexCoord2fv([0, 0])
    glVertex3fv([-50, 50, -50])

    glTexCoord2fv([0, 1])
    glVertex3fv([-50, -50, 50])
    glTexCoord2fv([1, 1])
    glVertex3fv([50, -50, 50])
    glTexCoord2fv([1, 0])
    glVertex3fv([50, 50, 50])
    glTexCoord2fv([0, 0])
    glVertex3fv([-50, 50, 50])

    glEnd()

def drawFloor():
    glColor3fv([1,1,1])
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, floorImgX, floorImgY, 0, GL_RGB, GL_UNSIGNED_BYTE, floorImg)
    glBegin(GL_QUADS)
    glTexCoord2fv([0, 1])
    glVertex3fv([-60, -5, -60])
    glTexCoord2fv([1, 1])
    glVertex3fv([60, -5, -60])
    glTexCoord2fv([1, 0])
    glVertex3fv([60, -5, 60])
    glTexCoord2fv([0, 0])
    glVertex3fv([-60, -5, 60])

    glEnd()

def drawBilliardRoom():
    drawPoolTable()
    drawFloor()
    drawWall()

poolTableV, poolTableF = loadMesh("PoolTable.txt")

def drawPoolTable():
    glColor3fv(tableColor)
    glBegin(GL_QUADS)
    for i in range(len(poolTableF)):
        p1, p2, p3, p4 = poolTableF[i][0], poolTableF[i][1], poolTableF[i][2], poolTableF[i][3]
        normal = getNormalV(poolTableV[p1], poolTableV[p2], poolTableV[p3])
        glNormal3fv(normal)
        glVertex3fv(poolTableV[p1])
        glVertex3fv(poolTableV[p2])
        glVertex3fv(poolTableV[p3])
        glVertex3fv(poolTableV[p4])
    glEnd()

def drawBall():
    global ballPosX, ballPosY, ballPosZ
    glPushMatrix()
    glTranslatef(ballPosX, ballPosY, ballPosZ)
    glColor3fv(ballColor)
    glutSolidSphere(1, 10, 10)
    glPopMatrix()

def CalcDistBall2Wall(wall, ballX, ballY, ballZ):
    if(wall[0][1] != ballY) : return
    wall_dx = wall[0][0] - wall[1][0]
    wall_dz = wall[0][2] - wall[1][2]
    a = wall_dz
    b = wall_dx
    c = wall_dz * wall[0][0] - wall_dx * wall[0][2]
    dist = (a * ballX + b * ballZ + c) / math.sqrt(a*a + b*b)
    return dist

def CalcBallPos():
    global ballPosX, ballPosY, ballPosZ, ballSpeed, ballAngle, ballFriction, isBallMove, poolWall
    if(isBallMove):
        ballSpeed -= ballFriction
        if(ballSpeed <= 0):
            isBallMove = False
            return

        ballPosX += ballSpeed * math.cos(ballAngle)
        ballPosZ += ballSpeed * math.sin(ballAngle)

        for i in range(0, len(poolWall)):
            dist = CalcDistBall2Wall(poolWall[i], ballPosX, ballPosY, ballPosZ)
            if(dist >= -1.05) :
                if(i == 0 or i == 2):
                    ballAngle *= -1

                if(i == 1 or i == 3):
                    ballAngle += math.pi
                    ballAngle *= -1

def GLinit():
    glClearColor(0, 0, 0, 0)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, Ld)
    glLightfv(GL_LIGHT0, GL_AMBIENT, La)
    glLightfv(GL_LIGHT0, GL_SPECULAR, Ls)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, Md)
    glMaterialfv(GL_FRONT, GL_SPECULAR, Ms)
    glMaterialfv(GL_FRONT, GL_AMBIENT, Ma)
    glMaterialfv(GL_FRONT, GL_SHININESS, shininess)

    glEnable(GL_TEXTURE_2D)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)


def keyboardEvent(key, x, y):
    global isLightOn, isRotateCamera, cameraDist, isBallMove, ballAngle, ballSpeed, ballSpeed_min
    if (key == b'n' or key == b'N'):
        if(isLightOn == False):
            glEnable(GL_LIGHT0)
            isLightOn = True

    if(key == b'f' or key == b'F'):
        if (isLightOn):
            glDisable(GL_LIGHT0)
            isLightOn = False

    if(key == b'i' or key == b'I'):
        if(cameraDist >= 10):
            cameraDist -= 1

    if(key == b'o' or key == b'O'):
        if(cameraDist <= 50):
            cameraDist += 1

    if(key == b'r' or key == b'R'):
        if(isRotateCamera):
            isRotateCamera = False
        else:
            isRotateCamera = True

    if(key == b'h' or key == b'H'):
        if(isBallMove == False):
            ballAngle = random.random() * 2 * math.pi
            ballSpeed = ballSpeed_min
            isBallMove = True

def CalcCameraPos():
    global cameraDist, cameraAngleX, cameraAngleY

    x = cameraDist * math.cos(cameraAngleY) *math.cos(cameraAngleX)
    y = cameraDist * math.sin(cameraAngleY)
    z = cameraDist * math.cos(cameraAngleY) *math.sin(cameraAngleX)

    return x, y, z

def display():
    global cameraPosX, cameraPosY, cameraPosZ, cameraAngleX, rotateSpeed, ballSpeed
    if(isRotateCamera):
        cameraAngleX += rotateSpeed
        if(rotateSpeed >= math.pi):
            rotateSpeed = 0
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, wnd_width / wnd_height, 0.1, 1000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    cameraPosX, cameraPosY, cameraPosZ = CalcCameraPos()
    gluLookAt(cameraPosX, cameraPosY, cameraPosZ, 0, 0, 0, 0, 1, 0)

    glLightfv(GL_LIGHT0, GL_POSITION, [-30, +30, +30, 1])

    drawBilliardRoom()
    CalcBallPos()
    drawBall()
    glFlush()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_DEPTH | GLUT_RGBA)
    glutInitWindowSize(wnd_width, wnd_height)
    glutInitWindowPosition(10, 10)
    glutCreateWindow(b"Minimal Billiard")
    GLinit()


    glutDisplayFunc(display)
    glutIdleFunc(display)
    glutKeyboardFunc(keyboardEvent)

    glutMainLoop()

if __name__ == '__main__':
    main()