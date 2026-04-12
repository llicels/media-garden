import requests
from itertools import chain

   
def popularMovies(page):
    

    url = f"https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page={page}&sort_by=popularity.desc"

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2MjcxOWViYTE0YTJhNzhlODU1Y2ZkOWRiZWI4YWMxYiIsIm5iZiI6MTcyMDkwNTY3MS4zMjk3ODksInN1YiI6IjY2OTJlZWY5MWZlYjk4NDZmNzg5M2MxNCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.EZlh_1YVpTg-K-NUJKrDr3MoqTH4Cx9YgMW3KCIPkak"
    }

    response = requests.get(url, headers=headers).json()

    numberOfResults = len(response["results"])

    movies = [None]*numberOfResults

    for i in range (numberOfResults):
        image = f"http://image.tmdb.org/t/p/w500/{response['results'][i]['poster_path']}"
        id = int(response["results"][i]["id"])
        link = f"https://multiembed.mov/?video_id={id}&tmdb=1"
        #here
        movies[i]=[response["results"][i]["title"], image, link, id]

    return(movies)

def popularSeries(page):
    

    url = f"https://api.themoviedb.org/3/discover/tv?include_adult=false&include_video=false&language=en-US&page={page}&sort_by=popularity.desc"

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2MjcxOWViYTE0YTJhNzhlODU1Y2ZkOWRiZWI4YWMxYiIsIm5iZiI6MTcyMDkwNTY3MS4zMjk3ODksInN1YiI6IjY2OTJlZWY5MWZlYjk4NDZmNzg5M2MxNCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.EZlh_1YVpTg-K-NUJKrDr3MoqTH4Cx9YgMW3KCIPkak"
    }

    response = requests.get(url, headers=headers).json()

    numberOfResults = len(response["results"])

    series = [None]*numberOfResults

    for i in range (numberOfResults):
        image = f"http://image.tmdb.org/t/p/w500/{response['results'][i]['poster_path']}"
        id = response["results"][i]["id"]
        link = f"https://vidsrc.to/embed/tv/{id}"
        series[i]=[response["results"][i]["name"], image, link, id]

    return(series)

def search(name):
    url = f"https://api.themoviedb.org/3/search/multi?query={name}&include_adult=false&language=en-US&page=1"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2MjcxOWViYTE0YTJhNzhlODU1Y2ZkOWRiZWI4YWMxYiIsIm5iZiI6MTcyMDkwNTY3MS4zMjk3ODksInN1YiI6IjY2OTJlZWY5MWZlYjk4NDZmNzg5M2MxNCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.EZlh_1YVpTg-K-NUJKrDr3MoqTH4Cx9YgMW3KCIPkak"
    }
    response = requests.get(url, headers=headers).json()
    numberOfResults = len(response["results"])

    content = [None]*numberOfResults
        
    for i in range (numberOfResults):
        id = response["results"][i]["id"]
        
        if response["results"][i]["media_type"]=="movie":
            a = response["results"][i]["poster_path"]
            image = f"http://image.tmdb.org/t/p/w500/{a}"
            link = f"https://vidsrc.to/embed/movie/{id}"
            if image != "http://image.tmdb.org/t/p/w500/None":
                content[i]=[response["results"][i]["title"],image,link, id, response["results"][i]["media_type"]]
        elif response["results"][i]["media_type"]=="tv":
            a = response["results"][i]["poster_path"]
            image = f"http://image.tmdb.org/t/p/w500/{a}"
            link = f"https://vidsrc.to/embed/tv/{id}"
            if image != "http://image.tmdb.org/t/p/w500/None":
                content[i]=[response["results"][i]["name"],image,link, id, response["results"][i]["media_type"]]

                            
                
    for j in range (len(content)):
        if None in content:
            content.remove(None)
                
    return(content)
  
def seriesInfo(id):
  url=f"https://api.themoviedb.org/3/tv/{id}"
  headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2MjcxOWViYTE0YTJhNzhlODU1Y2ZkOWRiZWI4YWMxYiIsIm5iZiI6MTcyMDkwNTY3MS4zMjk3ODksInN1YiI6IjY2OTJlZWY5MWZlYjk4NDZmNzg5M2MxNCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.EZlh_1YVpTg-K-NUJKrDr3MoqTH4Cx9YgMW3KCIPkak"
    }

  response = requests.get(url, headers=headers).json()
  numberSeasons=response['number_of_seasons']
  
  info = [None]*numberSeasons
  for i in range(0, numberSeasons):
      info[i]=[i+1, response['seasons'][i]['episode_count']]
      
  
  return(info)

  
