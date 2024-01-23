import sys
import requests
from bs4 import BeautifulSoup
import csv
import os.path
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

'''
Scrape the billboard hot 100 songs from the given url
'''
def scrape_billboard(url, N):
    
    content = requests.get(url)
    soup = BeautifulSoup(content.content, 'html.parser')
    columns = ['chart_pos', 'track_name', 'artist_name', 'lastweek_pos', 'peak_pos', 'wks_on_chart', 'status']
    billboard_data = []
    i = 0    # needed to print data if flag is True

    # Get all the divs with the song information
    song_containers = soup.find_all('div', {'class': 'o-chart-results-list-row-container'})

    for song_container in song_containers:
        # create dictionary to store data
        song_info = dict.fromkeys(columns)
        info_list = []
        flag = 0 # 0 means not new song, 1 means new in chart, 2 means re-entry
        # all other song information between the name is stored in a span
        other_info = song_container.find_all('span')
        for info in other_info:
            info = info.get_text().strip()
            # if there is a new song or a re-entry in the billboard, there will be more information given
            # the flag is added to determine if a song is new, a re-entry or have been in the chart
            print(info)
            if 'NEW' in info:
                flag = 1
            elif 'RE-\nENTRY' in info:
                flag = 2
            else:
                info_list.append(info)

        # even though some information should be integers, if a new song appears, it would be makrked as -
        song_info['chart_pos'] = int(info_list[0])
        song_info['track_name'] = song_container.find('h3', {'id': 'title-of-a-story'}).get_text().strip()
        song_info['artist_name'] = info_list[1]
        song_info['lastweek_pos'] = info_list[2]
        song_info['peak_pos'] = info_list[3]
        song_info['wks_on_chart'] = info_list[4]
        if flag == 1:
            song_info['status'] = 'new'
        elif flag == 2:
            song_info['status'] = 're-entry'
        else:
            song_info['status'] = 'no-change'

        billboard_data.append(song_info)
        # print first 5 entries if flag is True
        if i < N:
            print(song_info)
        i += 1

        # convert the information to a dataframe
        df = pd.DataFrame(billboard_data, columns=columns)
        
    return billboard_data, df

'''
Scrape the song information from the hot 100 list through the Spotify API
'''
def scrape_spotify(billboard_data, N):
    client_id = '4b40a6c88b6a4c45b6116f04c01fc55d'
    secret = '2224cdce4f954277880098f7920832f7'
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=secret) 
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    columns = ['track_id','track_name','artist_name','duration','release_date','popularity','danceability',
                'energy','key','loudness','mode','speechiness','acousticness','instrumentalness','liveness','valence','tempo']
    billboard_data = billboard_data.values.tolist()
    spotify_data = []

    for i in range(len(billboard_data)):
        track_info = dict.fromkeys(columns)
        name = billboard_data[i][1].replace('.', ' ')
        name = name.replace('\'', '')
        artist = billboard_data[i][2].split(' ')[0]

        track_results = sp.search(q=f'track:{name}, artist:{artist}', type='track', limit=1)
        # Spotify API is finicky, sometimes the track will be found if the artist is not in the query
        if track_results['tracks']['items'] == []:
            track_results = sp.search(q=f'track:{name}', type='track', limit=1)

        # Spotify API uses id for most of it's query, since we only have the song name and artist, need to get the ids first 
        for track in track_results['tracks']['items']:
            track_info['track_id'] = track['id']
            track_info['track_name'] = billboard_data[i][1]
            track_info['artist_name'] = billboard_data[i][2]
            track_info['release_date'] = track['album']['release_date']
            track_info['popularity'] = track['popularity']

        # get audio features of a given track id
        track_features = sp.audio_features(tracks=track_info['track_id'])
        track_info['duration'] = track_features[0]['duration_ms']
        track_info['danceability'] = track_features[0]['danceability'] 
        track_info['energy'] =  track_features[0]['energy']
        track_info['key'] = track_features[0]['key']
        track_info['loudness'] = track_features[0]['loudness'] 
        track_info['mode'] = track_features[0]['mode'] 
        track_info['speechiness'] = track_features[0]['speechiness']
        track_info['acousticness'] = track_features[0]['acousticness']
        track_info['instrumentalness'] = track_features[0]['instrumentalness']
        track_info['liveness'] = track_features[0]['liveness'] 
        track_info['valence'] = track_features[0]['valence']
        track_info['tempo'] = track_features[0]['tempo']

        # print first 5 entries if flag is True
        if i < N:
            print(track_info)

        spotify_data.append(track_info) 

    # convert the information to a dataframe
    df = pd.DataFrame(spotify_data, columns=columns)

    return spotify_data, df

'''
Read the data from the tiktok.csv dataset.
There is a lot of duplicate data in the dataset but I am leaving it here as it is the raw data given.
The duplicates and processing of the data will be handled in part 3 of the project
'''
def scrape_tiktok(file, N):
    # the dataframe will be used in the analysis section
    df = pd.read_csv(file)
    with open (file, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        # skip header
        next(reader)

        for i, row in enumerate(reader):
                if i < N:
                    print(row)

    f.close()
    # remove first column as it is only the row number
    df = df.iloc[:, 1:]
    return df

'''
Write data to csv file
'''
def write_to_csv(data, header, file_path):
    with open (file_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header)

        writer.writeheader()
        writer.writerows(data)
    f.close()
    print(f'Successfuly written data to {file_path}')

    return

def get_data():
    url = "https://www.billboard.com/charts/hot-100/2021-06-06/"
    N = 0
    billboard_data, billboard_df = scrape_billboard(url, N)
    spotify_data, spotify_df = scrape_spotify(billboard_df, N)
    tiktok_df = scrape_tiktok(tiktok_file, N)
    
    return billboard_df, spotify_df, tiktok_df

'''
Main Function
'''
def main():
    url = "https://www.billboard.com/charts/hot-100/2021-06-06/"
    tiktok_file = os.path.join('datasets', 'tiktok.csv')
    N = 0

    # Return the complete scraped datasets
    if len(sys.argv) < 2:
        print("Hot 100 Billboard data:")
        billboard_data, billboard_df = scrape_billboard(url, N)
        print(billboard_df)
        print("\nSpotify data:")
        spotify_data, spotify_df = scrape_spotify(billboard_df, N)
        print(spotify_df)
        print("\nTikTok data:")
        tiktok_df = scrape_tiktok(tiktok_file, N)
        print(tiktok_df)
        
        
    # This will scrape the data but return only N entries of each dataset and 5 by default
    elif sys.argv[1] == '--scrape':
        if len(sys.argv) > 2:
            N = int(sys.argv[2])
        else:
            N = 5
        print("Hot 100 Billboard data:")
        _, billboard_df = scrape_billboard(url, N)
        print("\nSpotify data:")
        scrape_spotify(billboard_df, N)
        print("\nTikTok data:")
        scrape_tiktok(tiktok_file, N)

    # This will return the static dataset scraped from the web and stored in database or CSV file
    elif sys.argv[1] == '--static':
        try:
            file_path = sys.argv[2]
            billboard_data, billboard_df = scrape_billboard(url, N)
            billboard_header = ['chart_pos', 'track_name', 'artist_name', 'lastweek_pos', 'peak_pos', 'wks_on_chart', 'status']
            write_to_csv(billboard_data, billboard_header, file_path)

            # code below is to save data from API because it takes a while to load
            '''
            spotify_data, _ = scrape_spotify(billboard_df, print_data)
            spotify_header = ['track_id','track_name','artist_name','duration','release_date','popularity','danceability',
                'energy','key','loudness','mode','speechiness','acousticness','instrumentalness','liveness','valence','tempo']
            write_to_csv(spotify_data, spotify_header, file_path)
            '''

        except Exception as e:
            print(f'Exception: {e}')
            return
        

if __name__ == '__main__':
    main()
