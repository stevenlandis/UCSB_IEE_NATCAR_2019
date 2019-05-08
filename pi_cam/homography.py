from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import tkinter as tk

REAL_POINTS = [-5,9,-5,20,5,20,5,9]

# homography constants
# H = [0.07746203773260954, 0.0026592742006694894, -20.79510858690768, -5.857577974861805e-05, -0.03356021614233259, 33.599693587262415, -0.00062404541481389, 0.0048092072848485955]

def main():
    # get 4 points
    root = tk.Tk()
    points = GetPoints(root).run()
    # print(points)
    if len(points) != 4:
        return
    H = solveHomography(points)
    print([transform(p) for p in points])

# def transform(p):
#     x,y = p
#     return (
#         (H[0]*x+H[1]*y+H[2])/(H[6]*x+H[7]*y+1),
#         (H[3]*x+H[4]*y+H[5])/(H[6]*x+H[7]*y+1))

# img = Image.open('homography.png')

class GetPoints:
    def __init__(self):
        root = tk.Tk()
        img = Image.open('homography.png')
        self.w, self.h = img.size

        self.viewW = 500
        self.viewH = 500

        self.img = ImageTk.PhotoImage(
            Image.open('homography.png').resize((self.viewW, self.viewH), Image.ANTIALIAS))

        self.root = root;
        root.title('Homography Calibration')

        self.label = tk.Label(root, text='Click 4 calibration points')
        self.label.pack()

        self.panel = tk.Label(root, image=self.img)
        self.panel.bind('<Button-1>', self.onPanelClick)
        self.panel.pack()

        self.points = []

    def run(self):
        # let the window run until 4 points are chosen
        self.root.mainloop()

        # process the points
        self.points.sort(key=lambda a: a[0])

        return list(sum(self.points, ()))

    def onPanelClick(self, evt):
        x = evt.x / self.viewW * self.w
        y = evt.y / self.viewH * self.h
        print('clicked at {},{}'.format(x,y))
        self.points.append((x,y))
        if len(self.points) == 4:
            # sort the points by x because the closer points are wider and the farther points are narrower
            self.root.destroy()

def ToReducedRowEchelonForm(M):
    #print("Got to reducing matrix")
    if not M: return
    lead = 0
    rowCount = len(M)
    columnCount = len(M[0])
    for r in range(rowCount):
        if lead >= columnCount:
            return
        i = r
        while M[i][lead] == 0:
            i += 1
            if i == rowCount:
                i = r
                lead += 1
                if columnCount == lead:
                    return
        M[i],M[r] = M[r],M[i]
        lv = M[r][lead]
        M[r] = [ mrx / float(lv) for mrx in M[r]]
        for i in range(rowCount):
            if i != r:
                lv = M[i][lead]
                M[i] = [ iv - lv*rv for rv,iv in zip(M[r],M[i])]
        lead += 1

def solveHomography(imgPts, realPts):
    x1,y1,x2,y2,x3,y3,x4,y4 = imgPts
    X1,Y1,X2,Y2,X3,Y3,X4,Y4 = realPts

    Ab = [
        [x1, y1, 1, 0, 0, 0, -x1*X1, -y1*X1,X1],
        [x2, y2, 1, 0, 0, 0, -x2*X2, -y2*X2,X2],
        [x3, y3, 1, 0, 0, 0, -x3*X3, -y3*X3,X3],
        [x4, y4, 1, 0, 0, 0, -x4*X4, -y4*X4,X4],
        [0, 0, 0, x1, y1, 1, -x1*Y1, -y1*Y1,Y1],
        [0, 0, 0, x2, y2, 1, -x2*Y2, -y2*Y2,Y2],
        [0, 0, 0, x3, y3, 1, -x3*Y3, -y3*Y3,Y3],
        [0, 0, 0, x4, y4, 1, -x4*Y4, -y4*Y4,Y4]]

    ToReducedRowEchelonForm(Ab)

    return [x[8] for x in Ab]
    print('Homography Constants:')
    print(s)
    with open('H.py', 'w') as f:
        f.write('H = {}'.format(s))

# main()