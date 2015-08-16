from Database.movies import *


def setup(db2='I:/my_db.db'):

    def add_server(db, con):
        engine = create_engine('sqlite:///' + db, echo=True)
        s = create_db(engine)

        for i in con:
            a = XDCCServer()
            a.url  = i[0]
            a.ssl  = i[1]
            a.port = i[2]
            nick   = i[3]

            s.add(a)
            s.flush()

            for j in i[4]:
                c = XDCCChannel()
                c.channel = j
                c.xdcc_server = a.id

                s.add(c)

            # if not s.query(exists().where(and_(XDCCServer.url == i[0], XDCCServer.channel == i[2]))).scalar():
            #     s.add(XDCCServer(url=i[0], channel=i[2], port=i[1]))

        s.commit()

    connection = [
            # ("irc.1andallIRC.net",      False, 6667,        "dbbld", ["#cosmic"]),
            # ("irc.eu.abjects.net",      True,  9999,        "dbbld", ["#moviegods", "#beast-xdcc"]),
            # ("irc.abandoned-irc.net",   False, 6667,        "dbbld", ["#porn-hq", "#zombie-warez"]),
            # ("irc.rizon.net",           True,  9999,        "dbbld", ["#1warez"]),
            # ("irc.xerologic.net",       True,  6697,        "dbbld", ["#warez"]),
            # ("irc.otaku-irc.net",       True,  6601,        "dbbld", ["#serial_us"]),
            ("irc.criten.net",          True,  7500,        "dbbld", [
                 "#elitewarez",
                 "#channel",
                 "#materwarez",
                 "#0day-mp3s"
            ]),
    ]

    add_server(db2, connection)


