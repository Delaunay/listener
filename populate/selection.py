# -*- coding: utf-8 -*-
__author__ = 'Pierre Delaunay'


from Database.movies import *
from tmdb import *

db = 'I:/my_db.db'

engine = create_engine('sqlite:///' + db, echo=False)
s = create_db(engine)

info = TMDbAPY("844238e82e0809bc08bb0d3c1d0842aa")

for i in s.query(Movie).order_by(Movie.added.desc()).limit(25).all():

    print(i.title, i.year)
    print(info.movie_search(i.title, i.year))