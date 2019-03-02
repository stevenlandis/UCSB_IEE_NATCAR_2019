from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import tkinter as tk

img = Image.open('homography.jpg')

class App:
	def __init__(self, master):

		self.img = ImageTk.PhotoImage(Image.open('homography.jpg').resize((500, 500), Image.ANTIALIAS))

		self.master = master;
		master.title('Homography Calibration')

		self.label = tk.Label(master, text='Pick the 4 calibration points')
		self.label.pack()

		self.button = tk.Button(master, text='Test button')
		self.button.pack()

		self.panel = tk.Label(master, image=self.img)
		self.panel.pack()

root = tk.Tk()
app = App(root)
root.mainloop()