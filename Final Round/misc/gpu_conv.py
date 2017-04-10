"""
Demonstrates how to use the PyCUDA interface to CUFFT to compute 2D FFTs.
"""
import ctypes
ctypes.CDLL('libgomp.so.1', mode=ctypes.RTLD_GLOBAL)

import time
import pycuda.autoinit
import pycuda.gpuarray as gpuarray
import numpy as np
import scipy.misc

import skcuda.fft as cu_fft
import skcuda.linalg as culinalg

from best_solution_in_the_wuuuuuuurld import gkern2

culinalg.init()

R = 10
face = scipy.misc.face(gray=True)
image = np.asarray(face, np.float32)
kernel = np.zeros(image.shape, dtype=np.float32)
gaus = gkern2(2 * R + 1, 2.5)
kernel[0:gaus.shape[0], 0:gaus.shape[1]] = gaus
kernel = np.roll(kernel, axis=0, shift=-R)
kernel = np.roll(kernel, axis=1, shift=-R)
kernel = np.asarray(kernel, np.float32)

start = time.time()
xf = np.fft.fft2(image) * np.fft.fft2(kernel)
conv_cpu = np.real(np.fft.ifft2(xf))
cpu_time = time.time() - start
print('CPU FFT in ', cpu_time)

shape = image.shape
image_gpu = gpuarray.to_gpu(image)
xf_gpu = gpuarray.empty(shape, np.complex64)
image_plan_forward = cu_fft.Plan(shape, np.float32, np.complex64)

kernel_gpu = gpuarray.to_gpu(kernel)
kf_gpu = gpuarray.empty(shape, np.complex64)
kernel_plan_forward = cu_fft.Plan(shape, np.float32, np.complex64)

plan_inverse = cu_fft.Plan(shape, np.complex64, np.float32)


start = time.time()
cu_fft.fft(image_gpu, xf_gpu, image_plan_forward)
cu_fft.fft(kernel_gpu, kf_gpu, kernel_plan_forward)
cf_gpu = culinalg.multiply(xf_gpu, kf_gpu)
cu_fft.ifft(cf_gpu, image_gpu, plan_inverse, True)
gpu_time = time.time() - start

conv_gpu = image_gpu.get()
print('GPU FFT in ', gpu_time)
tol = 1e-4
print('Success status: ', np.allclose(conv_cpu, conv_gpu, atol=tol), "; atol=", tol)
