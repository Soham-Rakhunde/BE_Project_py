# Generated with SMOP  0.41
from smop.libsmop import *
from scipy.signal import wiener
import utils
from PIL import Image
import PIL
import math
# C:\Users\soham\OneDrive\Desktop\341a4625-cec0-45df-9753-7f9e16f8832c_v4.0\code\JMiPOD_fast.m


@function
def JMiPOD_fast(C_STRUCT=None, Payload=None, *args, **kwargs):
    varargin = JMiPOD_fast.varargin
    nargin = JMiPOD_fast.nargin

    # -------------------------------------------------------------------------
    # J_MiPOD Embedding       |      February 2021       |      version 1.0
    # -------------------------------------------------------------------------
    # INPUT:
    #  - C_STRUCT    - Struct representing JPEG compressed image (or path to JPEG file)
    #  - Payload     - Embedding payload in bits per non-zeros AC DCT coefs (bpnzAC).
    # OUTPUT:
    #  - S_STRUCT    - Resulting stego jpeg STRUCT with embedded payload
    #  - pChange     - Embedding change probabilities.
    #  - ChangeRate  - Average number of changed pixels
    #  - Deflection  - Overall deflection.
    # -------------------------------------------------------------------------
    # Copyright (c) 2020
    # Remi Cogranne, UTT (Troyes University of Technology)
    # All Rights Reserved.
    # -------------------------------------------------------------------------
    # This code is provided by the author under Creative Common License
    # (CC BY-NC-SA 4.0) which, as explained on this webpage
    # https://creativecommons.org/licenses/by-nc-sa/4.0/
    # Allows modification, redistribution, provided that:
    # * You share your code under the same license ;
    # * That you give credits to the authors ;
    # * The code is used only for non-commercial purposes (which includes
    # education and research)
    # -------------------------------------------------------------------------
    #
    # The authors hereby grant the use of the present code without fee, and
    # without a written agreement under compliance with aforementioned
    # and provided and the present copyright notice appears in all copies.
    # The program is supplied "as is," without any accompanying services from
    # the UTT or the authors. The UTT does not warrant the operation of the
    # program will be uninterrupted or error-free. The end-user understands
    # that the program was developed for research purposes and is advised not
    # to rely exclusively on the program for any reason. In no event shall
    # the UTT or the authors be liable to any party for any consequential
    # damages. The authors also fordid any practical use of this code for
    # communication by hiding data into JPEG images.
    # -------------------------------------------------------------------------
    # Contact: remi.cogranne@utt.fr
    #          Septembre 2020
    # -------------------------------------------------------------------------
    # References to be mentioned to give appropriate credits to the authors:
    # R.Cogranne, Q.Giboulot & P.Bas "Efficient Steganography in JPEG Images by
    # Minimizing Performance of Optimal Detector" under review
    # ---------- #
    # R.Cogranne, Q.Giboulot & P.Bas "Steganography by Minimizing Statistical
    # Detectability: The cases of JPEG and Color Images", ACM IH&MMSec, 2020,
    # Denver, CO, USA, pp. 161--167 https://doi.org/10.1145/3369412.3395075.
    # ---------- #
    # This work has been developped for :
    # R.Cogranne, Q.Giboulot & P.Bas "ALASKA-2 : Challenging Academic Research
    # on Steganalysis with Realistic Images", IEEE WIFS, 2020, NYC, USA
    # ---------- #
    # Based on the prior work for spatial domain images :
    # V. Sedighi, R. Cogranne, and J. Fridrich. "Content-Adaptive Steganography by Minimizing Statistical Detectability."
    # IEEE Transactions on Information Forensics and Security, vol. 11, no. 2, 221--234, 2016
    # -------------------------------------------------------------------------
    # Let us wrap it up by acknowledging the great inspiration we owe to Prof.
    # Jessica Fridrich and to Vahid Sedighi with whom the spatial version of
    # this method had been developed.
    # Part of this code have been based on Matlab Implementation of MIPOD

    # Read the JPEG image if needed
    if ischar(C_STRUCT):
        C_STRUCT = Image.open(C_STRUCT)
    # 66

    # First let us decompress the image back into the spatial domain
    C_SPATIAL, MatDCT = RCdecompressJPEG(C_STRUCT, nargout=2)
    # 70
    # Compute Variance in spatial domain ....
    WienerResidual = C_SPATIAL - wiener(C_SPATIAL, concat([2, 2]))
    # 73
    Variance = VarianceEstimationDCT2D(WienerResidual, 3, 3)
    # 74
    # ... and apply the covariance transformation to DCT domain
    # funVar = @(x) reshape( diag(MatDCT*diag(x(:))*MatDCT')  , 8 , 8 ) ./ ( C_STRUCT.quant_tables{1}.^2 );
    # VarianceDCT = blkproc(Variance,[8 8],funVar);

    # In this code we replaced the blkproc with nested loops and simplied covariance linear transformation
    MatDCTq = MatDCT ** 2
    # 81
    Qvec = ravel(C_STRUCT.quant_tables[1])
    # 82
    for idx in arange(1, 64).reshape(-1):
        MatDCTq[idx, arange()] = MatDCTq(idx, arange()) / Qvec(idx) ** 2
    # 83

    VarianceDCT = vec2im(dot(MatDCTq, im2vec(Variance, concat([8, 8]))), concat([0, 0]), concat([8, 8]))
    # 85
    # VarianceDCT = zeros(size(C_SPATIAL));
    # for idxR=1:8:size( Variance, 1)
    #    for idxC=1:8:size( Variance, 2)
    #        x = Variance(idxR:idxR+7 , idxC:idxC+7);
    #        VarianceDCT(idxR:idxR+7 , idxC:idxC+7) = reshape( MatDCTq * x(:) , 8,8);
    #    end
    # end
    VarianceDCT[VarianceDCT < 1e-05] = 1e-05
    # 93
    # Compute Fisher information and smooth it
    FisherInformation = 1.0 / VarianceDCT ** 2
    # 96
    # Post Filter
    tmp = zeros(size(FisherInformation) + 16)
    # 99
    tmp[arange(9, end() - 8), arange(9, end() - 8)] = FisherInformation
    # 100
    tmp[arange(1, 8), arange()] = tmp(arange(9, 16), arange())
    # 101
    tmp[arange(end() - 7, end()), arange()
        ] = tmp(arange(end() - 15, end() - 8), arange())
    # 102
    tmp[arange(), arange(1, 8), arange()] = tmp(arange(), arange(9, 16))
    # 103
    tmp[arange(), arange(end() - 7, end()), arange()
        ] = tmp(arange(), arange(end() - 15, end() - 8))
    # 104
    FisherInformation = tmp(arange(1, end() - 16), arange(1, end() - 16)) + dot(tmp(arange(9, end() - 8), arange(1, end() - 16)), 3) + tmp(arange(17, end()), arange(1, end() - 16)) + dot(tmp(arange(1, end() - 16), arange(9, end() - 8)), 3) + dot(tmp(
        arange(9, end() - 8), arange(9, end() - 8)), 4) + dot(tmp(arange(17, end()), arange(9, end() - 8)), 3) + tmp(arange(1, end() - 16), arange(17, end())) + dot(tmp(arange(9, end() - 8), arange(17, end())), 3) + tmp(arange(17, end()), arange(17, end()))
    # 105
    # Compute embedding change probabilities and execute embedding
    FI = ravel(FisherInformation).T
    # 108
    C_COEFFS = C_STRUCT.coef_arrays[1]
    # 110
    S_COEFFS = copy(C_COEFFS)
    # 111
    # Compute message nbnzAC and message lenght (in NATS !!)
    nzAC = sum(ravel(C_COEFFS) != 0) - sum(sum(sum(C_COEFFS(arange(1,
                                                                   end(), 8), arange(1, end(), 8), arange()) != 0)))
    # 114
    messageLenght = round(dot(dot(Payload, nzAC), log(2)))
    # 115
    beta = TernaryProbs(FI, messageLenght)
    # 117
    # Simulate embedding
    beta = dot(2, beta)
    # 120
    r = rand(1, numel(C_COEFFS))
    # 121
    ModifPM1 = (r < beta)
    # 122

    r = rand(1, numel(VarianceDCT))
    # 123
    S_COEFFS[ModifPM1] = C_COEFFS(ModifPM1) + dot(2, (round(r(ModifPM1)))) - 1
    # 124

    S_COEFFS[S_COEFFS > 1024] = 1024
    # 125

    S_COEFFS[S_COEFFS < - 1023] = - 1023
    # 126
    ChangeRate = sum(ravel(ModifPM1)) / numel(C_COEFFS)
    # 127

    pChange = reshape(beta, size(C_COEFFS))
    # 128
    S_STRUCT = copy(C_STRUCT)
    # 130
    S_STRUCT.coef_arrays[1] = S_COEFFS
    # 131
    S_STRUCT.dc_huff_tables = copy(cellarray([]))
    # 132
    S_STRUCT.ac_huff_tables = copy(cellarray([]))
    # 133
    Deflection = sum(multiply(ravel(pChange), ravel(FI)))
    # 135
    return S_STRUCT, pChange, ChangeRate, Deflection


# if __name__ == '__main__':
#     pass

    # Beginning of the supporting functions

    # JPEG Image decompression and obtention of a single (64x64) matrix for DCT transform


def meshgrid(x: int):
    # col2d = np.array([[col for col in range(x)] for _ in range(x)])
    # row2d = np.array([[row for _ in range(x)] for row in range(x)])
    return np.meshgrid(np.arange(0,x), np.arange(0,x))

def extract_quantization_table(im: Image):
    return np.resize(im.quantization[0],(8,8))

@function
def RCdecompressJPEG(imJPEG=None, *args, **kwargs):
    varargin = RCdecompressJPEG.varargin
    nargin = RCdecompressJPEG.nargin

    # DCT matrix
    cc, rr = meshgrid(x=8)
    # 144
    T = dot(sqrt(2 / 8), np.cos(multiply(dot(math.pi, (dot(2, cc) + 1)), rr) / (dot(2, 8))))
    # 145

    T[0, :] = T[0, :] / sqrt(2)
    # 146

    dct64_mtx = np.zeros((64, 64))
    # 149
    for i in range(64):
        dcttmp = np.zeros((8,8))
    # 150
        dcttmp[i%8, int(i/8)] = 1
    # 150
        TTMP = dot(dot(T, dcttmp), T.T)
    # 150
        dct64_mtx[:, i] = np.ravel(TTMP)
    # 150

    # Apply image decompression
    DCTcoefs = imJPEG.coef_arrays[0]
        # 153
    QM = imJPEG.quant_tables[1]
    # 154
    imDecompress = vec2im(dot(dct64_mtx.T, (multiply(im2vec(
        DCTcoefs, concat([8, 8])), ravel(QM)))) + 128, concat([0, 0]), concat([8, 8]))
    # 155
    return imDecompress, dct64_mtx


# if __name__ == '__main__':
#     pass

    # Estimation of the pixels' variance based on a 2D-DCT (trigonometric polynomial) model
# Same function as in MiPOD


@function
def VarianceEstimationDCT2D(Image=None, BlockSize=None, Degree=None, *args, **kwargs):
    varargin = VarianceEstimationDCT2D.varargin
    nargin = VarianceEstimationDCT2D.nargin

    # verifying the integrity of input arguments
    if logical_not(mod(BlockSize, 2)):
        error('The block dimensions should be odd!!')

    if (Degree > BlockSize):
        error('Number of basis vectors exceeds block dimension!!')

    # number of parameters per block
    q = dot(Degree, (Degree + 1)) / 2
    # 170

    BaseMat = zeros(BlockSize)
    # 173
    BaseMat[1, 1] = 1
    # 173
    G = zeros(BlockSize ** 2, q)
    # 174
    k = 1
    # 175
    for xShift in arange(1, Degree).reshape(-1):
        for yShift in arange(1, (Degree - xShift + 1)).reshape(-1):
            G[arange(), k] = reshape(
                idct2(circshift(BaseMat, concat([xShift - 1, yShift - 1]))), BlockSize ** 2, 1)
    # 178
            k = k + 1
    # 179

    # Estimate the variance
    PadSize = floor(dot(BlockSize / 2, concat([1, 1])))
    # 184
    I2C = im2col(padarray(Image, PadSize, 'symmetric'),
                 dot(BlockSize, concat([1, 1])))
    # 185
    PGorth = eye(BlockSize ** 2) - \
        (dot(G, (numpy.linalg.solve((dot(G.T, G)), G.T))))
    # 186
    EstimatedVariance = reshape(
        sum((dot(PGorth, I2C)) ** 2) / (BlockSize ** 2 - q), size(Image))
    # 187
    return EstimatedVariance


# if __name__ == '__main__':
#     pass

    # Computing the embedding change probabilities
# Updated from MiPOD for speed purposes


@function
def TernaryProbs(FI=None, payload=None, *args, **kwargs):
    varargin = TernaryProbs.varargin
    nargin = TernaryProbs.nargin

    load('ixlnx3_5.mat')

    L, R = deal(0.1, 10, nargout=2)
    # 196
    fL = h_tern(1.0 / invxlnx3_fast(dot(L, FI), ixlnx3)) - payload
    # 198
    fR = h_tern(1.0 / invxlnx3_fast(dot(R, FI), ixlnx3)) - payload
    # 199

    while dot(fL, fR) > 0:

        if fL > 0:
            L = copy(R)
            # 203
            R = dot(2, R)
            # 204
            fR = h_tern(1.0 / invxlnx3_fast(dot(R, FI), ixlnx3)) - payload
            # 205
        else:
            R = copy(L)
            # 207
            L = L / 2
            # 208
            fL = h_tern(1.0 / invxlnx3_fast(dot(L, FI), ixlnx3)) - payload
            # 209

    # Search for the labmda in the specified interval
    i = 0
    # 214
    M = (L + R) / 2
    # 215
    fM = h_tern(1.0 / invxlnx3_fast(dot(M, FI), ixlnx3)) - payload
    # 216
    while (abs(fM) > max(2, payload / 1000.0) and i < 20):

        if dot(fL, fM) < 0:
            R = copy(M)
            # 219
            fR = copy(fM)
            # 219
        else:
            L = copy(M)
            # 221
            fL = copy(fM)
            # 221
        i = i + 1
        # 223
        M = (L + R) / 2
        # 224
        fM = h_tern(1.0 / invxlnx3_fast(dot(M, FI), ixlnx3)) - payload
        # 225

    # Compute beta using the found lambda
    beta = 1.0 / invxlnx3_fast(dot(M, FI), ixlnx3)
    # 228
    return beta


# if __name__ == '__main__':
#     pass

    # Fast solver of y = x*log(x-2) paralellized over all pixels
# Updated from MiPOD for speed purposes


@function
def invxlnx3_fast(y=None, f=None, *args, **kwargs):
    varargin = invxlnx3_fast.varargin
    nargin = invxlnx3_fast.nargin

    i_large = y > 1000
    # 235
    i_small = y <= 1000
    # 236
    iyL = floor(y(i_small) / 0.05) + 1
    # 238
    iyR = iyL + 1
    # 239
    iyR[iyR > 20000] = 20000
    # 240
    x = zeros(size(y))
    # 242
    x[i_small] = f(iyL) + multiply((y(i_small) - dot((iyL - 1), 0.05)), (f(iyR) - f(iyL)))
    # 243
    z = y(i_large) / log(y(i_large) - 2)
    # 245
    z = y(i_large) / log(z - 2)
    # 246
    x[i_large] = y(i_large) / log(z - 2)
    # 247
    return x


# if __name__ == '__main__':
    # pass

    # Ternary entropy function expressed in nats


@function
def h_tern(Probs=None, *args, **kwargs):
    varargin = h_tern.varargin
    nargin = h_tern.nargin

    p0 = 1 - dot(2, Probs)
    # 252
    P = concat([[ravel(p0)], [ravel(Probs)], [ravel(Probs)]])
    # 253
    H = - (multiply(P, log(P)))
    # 254
    H[(P < eps)] = 0
    # 255
    Ht = nansum(H)
    # 256
    return Ht


if __name__ == '__main__':
    print("hi")
    pass
