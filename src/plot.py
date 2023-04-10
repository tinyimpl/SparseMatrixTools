#!/usr/bin/env python3
import scipy.io as sio
from matplotlib.pyplot import figure, show

def matrix_market_reader(mtx_path):
	mtx = sio.mmread(mtx_path)	
	return mtx

def matlab_reader(mtx_path):
	mtx = sio.loadmat(mtx_path)
	return mtx

def idl_reader(mtx_path):
	mtx = sio.readsav(mtx_path)
	return mtx

def plot_mtx(mtx):
	fig = figure()
	ax1 = fig.add_subplot()
	ax1.spy(mtx, markersize = 1)
	show()

if __name__ == '__main__':
	mtx_path = input("mtx: ")
	mtx = matrix_market_reader(mtx_path)
	plot_mtx(mtx)

