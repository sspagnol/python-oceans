# -*- coding: utf-8 -*-
def smoo2(A, hei, wid, kind='hann', badflag=-9999, beta=14):
  """
  Usage
  -----
  As = smoo2(A, hei, wid, kind='hann', badflag=-9999, beta=14)

  Description
  -----------
  Calculates the smoothed array 'As' from the original array 'A' using the specified
  window of type 'kind' and shape ('hei','wid').

  Parameters
  ----------
  A       : 2D array
            Array to be smoothed.

  hei     : integer
            Window height. Must be odd and greater than or equal to 3.

  wid     : integer
            Window width. Must be odd and greater than or equal to 3.

  kind    : string, optional
            One of the window types available in the numpy module:

            hann (default) : Gaussian-like. The weight decreases toward the ends. Its end-points are zeroed.
            hamming        : Similar to the hann window. Its end-points are not zeroed, therefore it is
                             discontinuous at the edges, and may produce undesired artifacts.
            blackman       : Similar to the hann and hamming windows, with sharper ends.
            bartlett       : Triangular-like. Its end-points are zeroed.
            kaiser         : Flexible shape. Takes the optional parameter "beta" as a shape parameter.
                             For beta=0, the window is rectangular. As beta increases, the window gets narrower.

            Refer to the numpy functions for details about each window type.

  badflag : float, optional
            The bad data flag. Elements of the input array 'A' holding this value are ignored.

  beta    : float, optional
            Shape parameter for the kaiser window. For windows other than the kaiser window,
            this parameter does nothing.

  Returns
  -------
  As      : 2D array
            The smoothed array.

  ---------------------------------------
  André Palóczy Filho (paloczy@gmail.com)
  April 2012
  ==============================================================================================================
  """
  import numpy as np

  ###########################################
  ### Checking window type and dimensions ###
  ###########################################
  kinds = ['hann', 'hamming', 'blackman', 'bartlett', 'kaiser']
  if ( kind not in kinds ):
    raise ValueError('Invalid window type requested: %s'%kind)
  
  if ( np.mod(hei,2) == 0 ) or ( np.mod(wid,2)  == 0 ):
    raise ValueError('Window dimensions must be odd')

  if (hei <= 1) or (wid <= 1):
    raise ValueError('Window shape must be (3,3) or greater')

  ##############################
  ### Creating the 2D window ###
  ##############################
  if ( kind == 'kaiser' ): # if the window kind is kaiser (beta is required)
    wstr = 'np.outer(np.kaiser(hei, beta), np.kaiser(wid, beta))'
  else: # if the window kind is hann, hamming, blackman or bartlett (beta is not required)
    if kind == 'hann':
      kind = 'hanning' # converting the correct window name (Hann) to the numpy function name (numpy.hanning)
    wstr = 'np.outer(np.' + kind + '(hei), np.' + kind + '(wid))' # computing outer product to make a 2D window out of the original 1d windows
  wdw = eval(wstr)

  A = np.asanyarray(A)
  Fnan = np.isnan(A)
  imax, jmax = A.shape
  As = np.nan*np.ones( (imax, jmax) )

  for i in xrange(imax):
    for j in xrange(jmax):
      ### default window parameters
      wupp = 0
      wlow = hei
      wlef = 0
      wrig = wid
      lh = np.floor(hei/2)
      lw = np.floor(wid/2)

      ### default array ranges (functions of the i,j indices)
      upp = i-lh
      low = i+lh+1
      lef = j-lw
      rig = j+lw+1

      ##################################################
      ### Tiling window and input array at the edges ###
      ##################################################
      #upper edge
      if upp < 0:
        wupp = wupp-upp
        upp = 0

      #left edge
      if lef < 0:
        wlef = wlef-lef
        lef = 0

      #bottom edge
      if low > imax:
        ex = low-imax
        wlow = wlow-ex
        low = imax

      #right edge
      if rig > jmax:
        ex = rig-jmax
        wrig = wrig-ex
        rig = jmax

      ###############################################
      ### Computing smoothed value at point (i,j) ###
      ###############################################
      Ac = A[upp:low, lef:rig]
      wdwc = wdw[wupp:wlow, wlef:wrig]
      fnan = np.isnan(Ac)
      Ac[fnan] = 0; wdwc[fnan] = 0 # eliminating NaNs from mean computation
      fbad = Ac==badflag
      wdwc[fbad] = 0               # eliminating bad data from mean computation
      a = Ac * wdwc
      As[i,j] = a.sum() / wdwc.sum()

  As[Fnan] = np.nan # Assigning NaN to the positions holding NaNs in the input array

  return As
