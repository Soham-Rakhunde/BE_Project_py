# Generated with SMOP  0.41
from smop.libsmop import *
# C:\Users\soham\OneDrive\Desktop\341a4625-cec0-45df-9753-7f9e16f8832c_v4.0\code\jpegtbx\vec2im.m

    # VEC2IM  Reshape and combine column vectors into a 2D image
    
    #    IM=VEC2IM(V[,PADSIZE,BLKSIZE,ROWS,COLS])
    
    #    V is an MxN array containing N Mx1 column vectors which will be reshaped
#    and combined to form image IM.
    
    #    PADSIZE is a scalar or a 1x2 vector indicating the amount of vertical and
#    horizontal space to be added as a border between the reshaped vectors.
#    Default is [0 0].  If PADSIZE is a scalar, the same amount of space is used
#    for both directions.
    
    #    BLKSIZE is a scalar or a 1x2 vector indicating the size of the blocks.
#    Default is sqrt(M).
    
    #    ROWS indicates the number of rows of blocks in the image. Default is
#    floor(sqrt(N)).
    
    #    COLS indicates the number of columns of blocks in the image.  Default
#    is ceil(N/ROWS).
    
    #    See also IM2VEC.
    
    # Phil Sallee 5/03
    
    
@function
def vec2im(v=None,padsize=None,bsize=None,rows=None,cols=None,*args,**kwargs):
    varargin = vec2im.varargin
    nargin = vec2im.nargin

    m=size(v,1)
# C:\Users\soham\OneDrive\Desktop\341a4625-cec0-45df-9753-7f9e16f8832c_v4.0\code\jpegtbx\vec2im.m:28
    n=size(v,2)
# C:\Users\soham\OneDrive\Desktop\341a4625-cec0-45df-9753-7f9e16f8832c_v4.0\code\jpegtbx\vec2im.m:29
    if (nargin < 2):
        padsize=concat([0,0])
# C:\Users\soham\OneDrive\Desktop\341a4625-cec0-45df-9753-7f9e16f8832c_v4.0\code\jpegtbx\vec2im.m:32
    
    padsize=padsize + concat([0,0])
# C:\Users\soham\OneDrive\Desktop\341a4625-cec0-45df-9753-7f9e16f8832c_v4.0\code\jpegtbx\vec2im.m:34
    if (any(padsize < 0)):
        error('Pad size must not be negative.')
    
    if (nargin < 3):
        bsize=floor(sqrt(m))
# C:\Users\soham\OneDrive\Desktop\341a4625-cec0-45df-9753-7f9e16f8832c_v4.0\code\jpegtbx\vec2im.m:40
    
    bsize=bsize + concat([0,0])
# C:\Users\soham\OneDrive\Desktop\341a4625-cec0-45df-9753-7f9e16f8832c_v4.0\code\jpegtbx\vec2im.m:42
    if (prod(bsize) != m):
        error('Block size does not match size of input vectors.')
    
    if (nargin < 4):
        rows=floor(sqrt(n))
# C:\Users\soham\OneDrive\Desktop\341a4625-cec0-45df-9753-7f9e16f8832c_v4.0\code\jpegtbx\vec2im.m:48
    
    if (nargin < 5):
        cols=ceil(n / rows)
# C:\Users\soham\OneDrive\Desktop\341a4625-cec0-45df-9753-7f9e16f8832c_v4.0\code\jpegtbx\vec2im.m:51
    
    # make image
    y=bsize(1) + padsize(1)
# C:\Users\soham\OneDrive\Desktop\341a4625-cec0-45df-9753-7f9e16f8832c_v4.0\code\jpegtbx\vec2im.m:55
    x=bsize(2) + padsize(2)
# C:\Users\soham\OneDrive\Desktop\341a4625-cec0-45df-9753-7f9e16f8832c_v4.0\code\jpegtbx\vec2im.m:56
    t=zeros(y,x,dot(rows,cols))
# C:\Users\soham\OneDrive\Desktop\341a4625-cec0-45df-9753-7f9e16f8832c_v4.0\code\jpegtbx\vec2im.m:57
    t[arange(1,bsize(1)),arange(1,bsize(2)),arange(1,n)]=reshape(v,bsize(1),bsize(2),n)
# C:\Users\soham\OneDrive\Desktop\341a4625-cec0-45df-9753-7f9e16f8832c_v4.0\code\jpegtbx\vec2im.m:58
    t=reshape(t,y,x,rows,cols)
# C:\Users\soham\OneDrive\Desktop\341a4625-cec0-45df-9753-7f9e16f8832c_v4.0\code\jpegtbx\vec2im.m:59
    t=reshape(permute(t,concat([1,3,2,4])),dot(y,rows),dot(x,cols))
# C:\Users\soham\OneDrive\Desktop\341a4625-cec0-45df-9753-7f9e16f8832c_v4.0\code\jpegtbx\vec2im.m:60
    im=t(arange(1,dot(y,rows) - padsize(1)),arange(1,dot(x,cols) - padsize(2)))
# C:\Users\soham\OneDrive\Desktop\341a4625-cec0-45df-9753-7f9e16f8832c_v4.0\code\jpegtbx\vec2im.m:61