#!/usr/bin/env python
# coding: utf-8
# a python code to calcualte timeseries of NDVI values from USGS Landsat images. 
# In[54]:

if __name__ == '__main__':

    import os
    import pandas as pd
    import requests
    import numpy as np
    from dask.distributed import Client
    from dask.distributed import wait, progress
    import matplotlib.pyplot as plt
    import datetime as dt
    from landsatxplore.api import API
    from skimage import io
    import dask.array as da
    from dask.distributed import Client, LocalCluster
    import numpy as np
    from dask.distributed import progress
    import datetime as dt
    import pandas as pd
    import matplotlib.pyplot as plt


    B4_FILES = [f for f in os.listdir('/users/urihpc5/LANDSAT_PAR/data/') if f.endswith('_B4.TIF')]

    np.savetxt('filelist_b4.txt', B4_FILES, fmt='%s')


    #setup cluster
    cluster = LocalCluster()
    client = Client(cluster)


    #define module to calculate average NDVI
    def avNDVI(scene):
        dir = '/users/urihpc5/LANDSAT_PAR/data/'
        Str = scene.strip()[:-6]
        #read filename from path with B3 and B4 as extensio
        B4 = io.imread(dir + Str +'B4.TIF')
        B3 = io.imread(dir + Str +'B3.TIF')
        #use dask array to convert TIFF in to dask array.
        nir = da.from_array(B4,chunks=(2408,2408))
        red = da.from_array(B3,chunks=(2408,2408))
        denom = np.add(nir,red)
        denom = np.where(denom==0,np.nan,denom)
        NDVI = (nir-red)/denom
        #calc NDVI
        av_ndvi = da.nanmean(NDVI).compute()
        return av_ndvi

#--open text file and read filename as scenes
    dir = '/users/urihpc5/LANDSAT_PAR/data/'
    f = open(dir+'filelist_b4.txt','r')
    scenes = f.readlines()

#get datetime from filename
    date = []
    for s in scenes:
        dtm = dt.datetime.strptime(s[17:25],'%Y%m%d')
        date.append(dtm)

        # In[61]:


    andvi = client.map(avNDVI,scenes)

    progress(andvi)
    res = client.gather(andvi)


    ndvi_frame = pd.DataFrame()
    ndvi_frame['scenes'] = scenes
    ndvi_frame['ndvi'] = res
    ndvi_frame.to_csv('ndvi_avg.csv')

    fig = plt.figure()

    plt.scatter(date,res,color='red')
    plt.title('Timeseries of NDVI Values')
    plt.xlabel('Year')
    plt.ylabel('Average NDVI')
    plt.show()

    # Because we can't display figure objects on Oscar, save the figure to a file.
    fig.savefig('avg_ndvi.png')
    print('Image save complete')
