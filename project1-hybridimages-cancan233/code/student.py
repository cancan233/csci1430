# Project Image Filtering and Hybrid Images Stencil Code
# Based on previous and current work
# by James Hays for CSCI 1430 @ Brown and
# CS 4495/6476 @ Georgia Tech
import numpy as np
from numpy import pi, exp, sqrt
from skimage import io, img_as_ubyte, img_as_float32
from skimage.transform import rescale
from scipy import fftpack
from scipy import signal

# def my_imfilter(image, kernel):
#     """
#     Your function should meet the requirements laid out on the project webpage.
#     Apply a filter (using kernel) to an image. Return the filtered image. To
#     achieve acceptable runtimes, you MUST use numpy multiplication and summation
#     when applying the kernel.
#     Inputs
#     - image: numpy nd-array of dim (m,n) or (m, n, c)
#     - kernel: numpy nd-array of dim (k, l)
#     Returns
#     - filtered_image: numpy nd-array of dim of equal 2D size (m,n) or 3D size (m, n, c)
#     Errors if:
#     - filter/kernel has any even dimension -> raise an Exception with a suitable error message.
#     """
#     filtered_image = np.zeros(image.shape)

#     ##################
#     # Your code here #
#     (k, l) = kernel.shape
#     if (k * l) % 2 == 0:
#         raise Exception("Output with even filters are not defined!")

#     Grayscale = False
#     if len(image.shape) == 2:
#         Grayscale = True
#         image = np.reshape(image, (image.shape[0], image.shape[1], 1))
#     (m, n, _) = image.shape

#     # zero padded
#     # padded_image = np.pad(
#     # image, ((k // 2, k // 2), (l // 2, l // 2), (0, 0)), "constant"
#     # )

#     # reflected padded
#     padded_image = np.pad(
#         image, ((k // 2, k // 2), (l // 2, l // 2), (0, 0)), "reflect"
#     )
#     # because we want to calculate convolution, we need to flip the kernel
#     flipped_kernel = np.flip(kernel)
#     output = np.zeros(image.shape)

#     for i in range(m):
#         for j in range(n):
#             output[i, j] = np.tensordot(
#                 flipped_kernel,
#                 padded_image[i : i + k, j : j + l],
#                 axes=[(0, 1), (0, 1)],
#             )

#     if Grayscale:
#         output = np.reshape(output, (m, n))
#     filtered_image = output
#     # print('my_imfilter function in student.py needs to be implemented')
#     ##################
#     return filtered_image


def my_imfilter(image, kernel):
    """
    Your function should meet the requirements laid out on the project webpage.
    Apply a filter (using kernel) to an image. Return the filtered image. To
    achieve acceptable runtimes, you MUST use numpy multiplication and summation
    when applying the kernel.
    Inputs
    - image: numpy nd-array of dim (m,n) or (m, n, c)
    - kernel: numpy nd-array of dim (k, l)
    Returns
    - filtered_image: numpy nd-array of dim of equal 2D size (m,n) or 3D size (m, n, c)
    Errors if:
    - filter/kernel has any even dimension -> raise an Exception with a suitable error message.
    """
    filtered_image = np.zeros(image.shape)

    ##################
    # Your code here #
    (k, l) = kernel.shape
    if (k * l) % 2 == 0:
        raise Exception("Output with even filters are not defined!")

    Grayscale = False
    if len(image.shape) == 2:
        Grayscale = True
        image = np.reshape(image, (image.shape[0], image.shape[1], 1))
    (m, n, c) = image.shape

    # because we want to calculate convolution, we need to flip the kernel
    flipped_kernel = np.flip(kernel)
    (k, l) = flipped_kernel.shape
    padded_image = np.pad(
        image, ((k // 2, k // 2), (l // 2, l // 2), (0, 0)), "reflect"
    )

    expanded_image = np.lib.stride_tricks.as_strided(
        padded_image,
        shape=(
            m,
            n,
            c,
            k,
            l,
        ),
        strides=(
            padded_image.strides[0],
            padded_image.strides[1],
            padded_image.strides[2],
            padded_image.strides[0],
            padded_image.strides[1],
        ),
        writeable=False,
    )

    output = np.einsum("xyzij, ij->xyz", expanded_image, flipped_kernel)

    if Grayscale:
        output = np.reshape(output, (m, n))
    filtered_image = output
    # print('my_imfilter function in student.py needs to be implemented')
    ##################
    return filtered_image


"""
EXTRA CREDIT placeholder function
"""


def my_imfilter_fft(image, kernel):
    """
    Your function should meet the requirements laid out in the extra credit section on
    the project webpage. Apply a filter (using kernel) to an image. Return the filtered image.
    Inputs
    - image: numpy nd-array of dim (m,n) or (m, n, c)
    - kernel: numpy nd-array of dim (k, l)
    Returns
    - filtered_image: numpy nd-array of dim of equal 2D size (m,n) or 3D size (m, n, c)
    Errors if:
    - filter/kernel has any even dimension -> raise an Exception with a suitable error message.
    """
    filtered_image = np.zeros(image.shape)

    ##################
    # Your code here #
    (k, l) = kernel.shape
    if (k * l) % 2 == 0:
        raise Exception("Output with even filters are not defined!")

    Grayscale = False
    if len(image.shape) == 2:
        Grayscale = True
        image = np.reshape(image, (image.shape[0], image.shape[1], 1))
    (m, n, c) = image.shape
    # because we want to calculate convolution, we need to flip the kernel
    flipped_kernel = np.flip(kernel)
    (k, l) = flipped_kernel.shape
    padded_image = np.pad(
        image, ((k // 2, k // 2), (l // 2, l // 2), (0, 0)), "constant"
    )

    fft_kernel = fftpack.fft2(flipped_kernel, shape=padded_image.shape[:2], axes=(0, 1))
    reshape_kernel = flipped_kernel.reshape(k, l, 1)
    ref_fft_kernel = signal.fftconvolve(image, reshape_kernel, mode='same')

    # print(ref_fft_kernel.shape)
    # print(ref_fft_kernel[0])

    fft_image = fftpack.fft2(padded_image, axes=(0, 1))
    fft_output = fft_kernel[:, :, np.newaxis] * fft_image
    # fft_output = fftpack.fftshift(fft_output)
    output = fftpack.ifft2(fft_output, axes=(0, 1)).real

    # output = np.clip(output[], 0, 1)
    # print(output.shape)
    # print(output[0])
    # exit()
    output = np.clip(output[k // 2 : -(k // 2), l // 2 : -(l // 2), :], 0, 1)
    if Grayscale:
        output = np.reshape(output, (m, n))
    filtered_image = output

    print(ref_fft_kernel.shape)
    print(filtered_image.shape)
    # print(filtered_image[:,:,0])
    print(ref_fft_kernel[0,:10,0] - filtered_image[0,:10,0])

    # print("my_imfilter_fft function in student.py is not implemented")
    ##################

    return filtered_image


def gen_hybrid_image(image1, image2, cutoff_frequency):
    """
    Inputs:
    - image1 -> The image from which to take the low frequencies.
    - image2 -> The image from which to take the high frequencies.
    - cutoff_frequency -> The standard deviation, in pixels, of the Gaussian
                          blur that will remove high frequencies.

    Task:
    - Use my_imfilter to create 'low_frequencies' and 'high_frequencies'.
    - Combine them to create 'hybrid_image'.
    """

    assert image1.shape[0] == image2.shape[0]
    assert image1.shape[1] == image2.shape[1]
    assert image1.shape[2] == image2.shape[2]

    # Steps:
    # (1) Remove the high frequencies from image1 by blurring it. The amount of
    #     blur that works best will vary with different image pairs
    # generate a 1x(2k+1) gaussian kernel with mean=0 and sigma = s, see https://stackoverflow.com/questions/17190649/how-to-obtain-a-gaussian-filter-in-python
    s, k = cutoff_frequency, cutoff_frequency * 2
    probs = np.asarray(
        [exp(-z * z / (2 * s * s)) / sqrt(2 * pi * s * s) for z in range(-k, k + 1)],
        dtype=np.float32,
    )
    kernel = np.outer(probs, probs)

    # Your code here:
    low_frequencies = my_imfilter(image1, kernel)  # Replace with your implementation

    # (2) Remove the low frequencies from image2. The easiest way to do this is to
    #     subtract a blurred version of image2 from the original version of image2.
    #     This will give you an image centered at zero with negative values.
    # Your code here #
    high_frequencies = image2 - my_imfilter(
        image2, kernel
    )  # Replace with your implementation

    # (3) Combine the high frequencies and low frequencies
    # Your code here #
    hybrid_image = low_frequencies + high_frequencies
    # Replace with your implementation

    # (4) At this point, you need to be aware that values larger than 1.0
    # or less than 0.0 may cause issues in the functions in Python for saving
    # images to disk. These are called in proj1_part2 after the call to
    # gen_hybrid_image().
    # One option is to clip (also called clamp) all values below 0.0 to 0.0,
    # and all values larger than 1.0 to 1.0.
    low_frequencies = np.clip(low_frequencies, 0, 1)
    high_frequencies = np.clip(high_frequencies, 0, 1)
    hybrid_image = np.clip(hybrid_image, 0, 1)

    return low_frequencies, high_frequencies, hybrid_image
