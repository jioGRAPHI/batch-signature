try:
	import tkinter as tk
	from tkinter import ttk
except ImportError:
	import Tkinter as tk
	import ttk

import sys
import os
import fitz

from tkinter import *
from tkinter import font as tkfont
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image
from io import BytesIO

class BatchSigSystem(tk.Tk):

	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)

		container = tk.Frame(self)
		container.pack(side="top", fill="both", expand=True)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)

		self.title_font = tkfont.Font(family='Times New Roman', size=14, weight="bold")
		self.label_font = tkfont.Font(family='Helvetica', size=10)

		frame = MainPage(parent=container, controller=self)
		frame.grid(row=0, column=0, sticky="nsew")
		frame.tkraise()

class MainPage(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller
		self.folder_selected = ""
		self.pdf_selected = ()
		self.sig_selected = ()

		self.title_font = tkfont.Font(family='Courier', size=16, weight="bold")
		self.label_font = tkfont.Font(family='Helvetica', size=8)

		self.disp_pdf = tk.Text(self, height = 15, width = 35, wrap="word", font=("Microsoft JhengHei", 10))
		self.disp_pdf.place(x=90, y=60)
		self.disp_pdf.config(state = "disabled")

		self.disp_sig = tk.Text(self, height = 15, width = 35, wrap="word", font=("Microsoft JhengHei", 10))
		self.disp_sig.place(x=450, y=60)
		self.disp_sig.config(state = "disabled")

		self.pdf_bttn = tk.Button(self, text="Select PDFs", command=lambda: self.pick_pdfs(), height = 2, width = 25, bd = 0, bg = "#043c39", fg = "#ffffff", activebackground = "#cf0007")
		self.pdf_bttn.place(x=150, y=350)

		self.sig_bttn = tk.Button(self, text="Select Signature", command=lambda: self.pick_signature(), height = 2, width = 25, bd = 0, bg = "#043c39", fg = "#ffffff", activebackground = "#cf0007")
		self.sig_bttn.place(x=500, y=350)

		self.disp_dir = tk.Text(self, height = 2, width = 60, wrap="word", font=("Microsoft JhengHei", 10))
		self.disp_dir.place(x=100, y=450)
		self.disp_dir.config(state = "disabled")

		self.directory_bttn = tk.Button(self, text="Save PDFs To", command=lambda: self.pick_directories(), height = 2, width = 13, bd = 1, bg = "#043c39", fg = "#ffffff", activebackground = "#cf0007")
		self.directory_bttn.place(x=610, y=450)

		self.continue_bttn = tk.Button(self, text="Continue", command=lambda: self.save_pdf(), height = 2, width = 25, bd = 0, bg = "#279c57", fg = "#ffffff", activebackground = "#cf0007")
		self.continue_bttn.place(x=310, y=520)

	def pick_directories(self):
		self.disp_dir.config(state = "normal")
		self.disp_dir.delete('1.0', 'end')
		self.folder_selected = filedialog.askdirectory()
		self.disp_dir.insert('1.0', self.folder_selected)
		self.disp_dir.config(state = "disabled")

	def pick_pdfs(self):
		self.disp_pdf.config(state = "normal")
		self.disp_pdf.delete('1.0', 'end')
		self.pdf_selected = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
		for i in self.pdf_selected:
			self.disp_pdf.insert('1.0', os.path.basename(i) + '\n')
		self.disp_pdf.config(state = "disabled")

	def pick_signature(self):
		self.disp_sig.config(state = "normal")
		self.disp_sig.delete('1.0', 'end')
		self.sig_selected = filedialog.askopenfilenames(filetypes=[("PNG files", "*.png")])
		for i in self.sig_selected:
			self.disp_sig.insert('1.0', os.path.basename(i) + '\n')
		self.disp_sig.config(state = "disabled")

	def convertToPNG(self, im):
		with BytesIO() as f:
			im.save(f, format='PNG')
			return f.getvalue()

	def insert_signatures(self):
		pdf_list = []
		for i in self.pdf_selected:
			pdf_list.append(i)
		
		signature_file = self.sig_selected[0]

		image = Image.open(signature_file)
		image = image.point(lambda p: p > 191 and 255) 
		image = image.convert('RGBA')

		newImage = []
		for item in image.getdata():
			if item[:3] == (255, 255, 255):
				newImage.append((255, 255, 255, 0))
			else:
				newImage.append(item)

		image.putdata(newImage)

		ima_png = self.convertToPNG(image)

		for pdfs in pdf_list:
			image_rectangle_1 = fitz.Rect(370, 660, 470, 720)
			image_rectangle_2 = fitz.Rect(370, 760, 470, 810)
			
			file_handle = fitz.open(pdfs)
			target_page = file_handle[0]

			target_page.insertImage(image_rectangle_1, stream=ima_png)
			target_page.insertImage(image_rectangle_2, stream=ima_png)

			file_handle.save(self.folder_selected + "/signed " + os.path.basename(pdfs))
		
		messagebox.showinfo("Success", "PDFs successfully signed")

	def save_pdf(self):
		if self.folder_selected == "":
			messagebox.showwarning("Warning", "Please select a location to save PDFs")
		else:
			if len(self.pdf_selected) == 0:
				messagebox.showwarning("Warning", "No PDF selected")
			else:
				if len(self.pdf_selected) == 0:
					messagebox.showwarning("Warning", "No signature file selected")
				else:
					self.insert_signatures()

if __name__ == "__main__":

	app = BatchSigSystem()
	app.title("Batch PDF Signature")
	app.geometry("800x600")
	app.resizable(width=False, height=False)
	app.mainloop()