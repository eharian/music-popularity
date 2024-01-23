#!/usr/bin/env python
# coding: utf-8

# In[1]:


# load all necessary libraries
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
pd.options.mode.chained_assignment = None  # default='warn'


# In[2]:


# load data from saved datasets
billboard_df = pd.read_csv('./datasets/billboard_hot_100.csv')
spotify_df = pd.read_csv('./datasets/spotify.csv')
tiktok_df = pd.read_csv('./datasets/tiktok.csv')


# In[3]:


# remove duplicates from the tiktok dataset
tiktok_df = tiktok_df.drop_duplicates(subset=['track_id']).copy()

# remove the first column as it is a proxy id
tiktok_df = tiktok_df.iloc[:, 1:]

# some songs have different ids like if a song is released as both a single or in an album.
# so we want to remove it as they are essentialy the same song
tiktok_df = tiktok_df.drop_duplicates(subset=['track_name', 'artist_name'], keep='first')

# remove the duration in minutes as the duration in ms is already available
del tiktok_df['duration_mins']


# In[4]:


# look at data types of data
tiktok_df.info()


# In[5]:


# take the columns with numerial values
numerical_features=tiktok_df.select_dtypes(include=['int64','float64']).columns.tolist()


# In[6]:


numerical_features


# In[7]:


# create a histogram for TikTok data
j=1
d=1

top=tiktok_df[numerical_features].columns[0:7]
bottom=tiktok_df[numerical_features].columns[7:13]
fig= make_subplots(rows=2, cols=7, start_cell ='top-left', subplot_titles=numerical_features)


for idx, k in enumerate(bottom):
    for idx2, i in enumerate(top):
        if j<len(top)+1:
            fig.add_trace(go.Histogram(x=tiktok_df[i], name=numerical_features[idx2]),row=1,col=j)
            j+=1
    if d<len(bottom)+1:
        fig.add_trace(go.Histogram(x=tiktok_df[k], name = numerical_features[idx]),row=2,col=d)
        d+=1
fig.update_layout(bargap=.2,width=1100,height=500, title_text='TikTok Data')
fig.show()


# ![newplot.png](newplot.png)

# The list of histograms above show the audio features of all the tracks in the TikTok dataset. The duration histogram can be ignored because songs used in TikTok videos are not of full length, so it is irrelevant for our case. There seems to be a similarity in the graphs of danceability, energy and loudness. This inferrence makes sense because there are a lot of dance challenges in TikTok, so music with higher danceability should be preffered but this requires more analysis in comparison to the Spotify data.
# 
# What is interesting to note is that there are a lot of songs with low popularity. According to the Spotify API, the popularity is calculated by algorithm and is based, in the most part, on the total number of plays the track has had and how recent those plays are. This is actually a great indication as it implies that there are plenty of new songs being used in TikTok which may contribute to its positio in the hot 100 billboard chart. Later we will look at these songs and check if they are shared among the other dataset.

# In[8]:


# correlation matrix of TikTok data
plt.figure(figsize=(15,9))
sns.heatmap(tiktok_df.corr(),annot=True,cmap='viridis');


# Above is the correlation matrix of the TikTok data, higher value numbers means a positive relationship and vice versa for lower values. There are a lot of variables in play that contribute to the entire dataset, but this can be unfeasible when analyzing as some variables might contribute very minimally. To figure out which components can encompass a majority of the information, we will perform a principal component analysis on the audio features, which reduces the dimensionality of large datasets

# In[9]:


X = tiktok_df.loc[:, numerical_features].values
# Standardizing the features
X = StandardScaler().fit_transform(X)


pca = PCA(n_components=13)
pca.fit(X)


# In[10]:


plt.plot(np.cumsum(pca.explained_variance_ratio_))
plt.xlabel("Number of Components")
plt.ylabel("Explained Variance")
plt.show()


# In[11]:


for i in range(13):
    print(f'Variance explained by the {i+1}th component: {np.cumsum(pca.explained_variance_ratio_*100)[i]}' )


# Based on the correlation matrix, I assumed that only a few components would be needed to capture the data, but after performing the PCA, to get most of the data, about 8 or 9 components are needed. It is still reduced from the original 13 though. Next, we will explore the audio features of the hot 100 billboard tracks then compare the data with that of the TikTok dataset

# In[12]:


# create a histogram for hot 100 data
j=1
d=1

top=spotify_df[numerical_features].columns[0:7]
bottom=spotify_df[numerical_features].columns[7:13]
fig= make_subplots(rows=2, cols=7, start_cell ='top-left', subplot_titles=numerical_features)


for idx, k in enumerate(bottom):
    for idx2, i in enumerate(top):
        if j<len(top)+1:
            fig.add_trace(go.Histogram(x=spotify_df[i], name=numerical_features[idx2]),row=1,col=j)
            j+=1
    if d<len(bottom)+1:
        fig.add_trace(go.Histogram(x=spotify_df[k], name = numerical_features[idx]),row=2,col=d)
        d+=1
fig.update_layout(bargap=.2,width=1100,height=500, title_text='Billboard hot 100 Data')
fig.show()


# ![newplot%20%281%29.png](newplot%20%281%29.png)

# On first glance, it is instantly noticeable that the popularity is skewed to the right which makes sense since songs in the hot 100 billboard should be popular in streaming services. An interesting thing to note is that the there are a lot of songs which have lower danceability, which is counter intuitive of the assessment made with the TikTok data. Lower danceability with lower valence seems to go in pair whereby if a song is less "positive", it would be likely be less danceable. But in terms of the other histograms, the trend is very similar.
# 
# This is only looking at the datasets from a birds eye view, now we will extract the songs that appear in both the billboard hot 100 and the TikTok dataset and make inferences from it

# In[13]:


# find the tracks that exist in the billboard hot 100 and TikTok dataset
j = 0
shared_tracks = pd.DataFrame(columns = spotify_df.columns.values)
shared_tracks['status'] = 0
artist_count = {}
for i, track in enumerate(billboard_df['track_name']):
    # need to make lower case because the formatting is inconsistent from the TikTok dataset
    billboard_track = track.lower().strip()
    artist = billboard_df['artist_name'][i]
    
    # find the index of the data from the dataframe
    idx = tiktok_df.index[billboard_track == tiktok_df['track_name'].str.lower().values].tolist()
    if idx:
        shared_tracks = shared_tracks.append(spotify_df.loc[i], ignore_index=True)
        shared_tracks['status'][j] = billboard_df['status'][i]
        j += 1
        
        artist_count[artist] = artist_count.get(artist, 0) + 1


# In[14]:


shared_tracks.head()


# In[15]:


# create a histogram for shared data
j=1
d=1

top=shared_tracks[numerical_features].columns[0:7]
bottom=shared_tracks[numerical_features].columns[7:13]
fig= make_subplots(rows=2, cols=7, start_cell ='top-left', subplot_titles=numerical_features)


for idx, k in enumerate(bottom):
    for idx2, i in enumerate(top):
        if j<len(top)+1:
            fig.add_trace(go.Histogram(x=shared_tracks[i], name=numerical_features[idx2]),row=1,col=j)
            j+=1
    if d<len(bottom)+1:
        fig.add_trace(go.Histogram(x=shared_tracks[k], name = numerical_features[idx]),row=2,col=d)
        d+=1
fig.update_layout(bargap=.2,width=1100,height=500, title_text='Shared Data')
fig.show()


# In[16]:


print(f'Number of shared tracks between datasets: {len(shared_tracks)}')
print('Statuses of songs in hot 100 billboard chart:')
print(shared_tracks['status'].value_counts())
print(f"The artist with the most songs in both datasets is: {max(artist_count, key=artist_count.get)}")

from datetime import date
cum_days = 0
billboard_date = date(2021, 6, 6)
for dates in shared_tracks['release_date']:
    split_date = dates.split('-')
    track_date = date(int(split_date[0]), int(split_date[1]), int(split_date[2]))
    delta = billboard_date - track_date
    cum_days += delta.days
avg_days = (cum_days / len(shared_tracks['release_date']))
print(f'Average number of days song is released before billboard of the week: {avg_days}')


# ![newplot%20%282%29.png](newplot%20%282%29.png)

# From the small function, we were able to determine how many tracks were shared between the TikTok and the hot 100 dataset. There were 2 re-entries and 3 new tracks that made it into the chart for that week. I was pleasantly surprised when finding out 39/100 songs were featured in both datasets. Even though it is less than 50%, considering there are a plethora of songs and remixes used in TikTok, these songs were popular in the app. Due to some re-entries and no changes for songs that have been on the charts for months, it is hard to infer the importance of release date.
# 
# From the graph above, I was intrigued when analyzing the histograms, I expected that the tracks would have higher danceability and energy as dance challenges is a main trend in TikTok. The songs are also more acoustic which is also opposite of what I thought the popular tracks would be.
