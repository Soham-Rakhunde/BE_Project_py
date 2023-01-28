# Generated with SMOP  0.41
from smop.libsmop import *
import numpy as np

# C:\Users\soham\OneDrive\Desktop\341a4625-cec0-45df-9753-7f9e16f8832c_v4.0\code\jpegtbx\im2vec.m

    # IM2VEC  Reshape 2D image blocks into an array of column vectors
    
    #    V=IM2VEC(IM,BLKSIZE[,PADSIZE])
    
    #    [V,ROWS,COLS]=IM2VEC(IM,BLKSIZE[,PADSIZE])
    
    #    IM is an image to be separated into non-overlapping blocks and
#    reshaped into an MxN array containing N blocks reshaped into Mx1
#    column vectors.  IM2VEC is designed to be the inverse of VEC2IM.
    
    #    BLKSIZE is a scalar or 1x2 vector indicating the size of the blocks.
    
    #    PADSIZE is a scalar or 1x2 vector indicating the amount of vertical
#    and horizontal space to be skipped between blocks in the image.
#    Default is [0 0].  If PADSIZE is a scalar, the same amount of space
#    is used for both directions.  PADSIZE must be non-negative (blocks
#    must be non-overlapping).
    
    #    ROWS indicates the number of rows of blocks found in the image.
#    COLS indicates the number of columns of blocks found in the image.
    
    #    See also VEC2IM.
    
    # Phil Sallee 5/03
    
    
@function
def im2vec(im=None,bsize=None,padsize=None,*args,**kwargs):
    varargin = im2vec.varargin
    nargin = im2vec.nargin

    bsize=bsize + concat([0,0])
# 28
    if (nargin < 3):
        padsize=0
# 31
    
    padsize=padsize + concat([0,0])
# 33
    if (any(padsize < 0)):
        error('Pad size must not be negative.')
    
    imsize=size(im)
# 38
    y=bsize(1) + padsize(1)
# 39
    x=bsize(2) + padsize(2)
# 40
    rows=floor((imsize(1) + padsize(1)) / y)
# 41
    cols=floor((imsize(2) + padsize(2)) / x)
# 42
    t=zeros(dot(y,rows),dot(x,cols))
# 44
    imy=dot(y,rows) - padsize(1)
# 45
    imx=dot(x,cols) - padsize(2)
# 46
    t[arange(1,imy),arange(1,imx)]=im(arange(1,imy),arange(1,imx))
# 47
    np.transpose()
    t=reshape(t,y,rows,x,cols)
# 48
    t=reshape(permute(t,concat([1,3,2,4])),y,x,dot(rows,cols))
# 49
    v=t(arange(1,bsize(1)),arange(1,bsize(2)),arange(1,dot(rows,cols)))
# 50
    v=reshape(v,dot(y,x),dot(rows,cols))
# 51