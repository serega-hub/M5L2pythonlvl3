import sqlite3
from config import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


class DB_Map():
    def __init__(self, database):
        self.database = database
    
    # ---------- ТАБЛИЦЫ ----------

    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users_cities (
                    user_id INTEGER,
                    city_id TEXT,
                    FOREIGN KEY(city_id) REFERENCES cities(id)
                )
            ''')

    def create_settings_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id INTEGER PRIMARY KEY,
                    color TEXT
                )
            ''')

    # ---------- ГОРОДА ----------

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]
                conn.execute(
                    'INSERT INTO users_cities VALUES (?, ?)',
                    (user_id, city_id)
                )
                return 1
            else:
                return 0

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT cities.city 
                FROM users_cities  
                JOIN cities ON users_cities.city_id = cities.id
                WHERE users_cities.user_id = ?
            ''', (user_id,))
            return [row[0] for row in cursor.fetchall()]

    def select_all_cities(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('SELECT city FROM cities LIMIT 50')
            return [row[0] for row in cursor.fetchall()]

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT lat, lng
                FROM cities  
                WHERE city = ?
            ''', (city_name,))
            return cursor.fetchone()
    def select_cities_by_country(self, country):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT city FROM cities WHERE country=? LIMIT 10",
                (country,)
            )
            return [row[0] for row in cursor.fetchall()]
    # ---------- ЦВЕТ ----------

    def set_color(self, user_id, color):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''
                INSERT INTO user_settings (user_id, color)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET color=?
            ''', (user_id, color, color))

    def get_color(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(
                'SELECT color FROM user_settings WHERE user_id=?',
                (user_id,)
            )
            row = cur.fetchone()
            return row[0] if row else 'red'

    # ---------- КАРТА ----------

    def create_grapf(self, path, cities, user_id):
        plt.clf()

        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.set_global()

        ax.add_feature(cfeature.LAND, facecolor='lightgreen')
        ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.RIVERS)
        ax.add_feature(cfeature.LAKES)

        color = self.get_color(user_id)

        for city in cities:
            coords = self.get_coordinates(city)
            if coords is None:
                continue

            lat, lon = coords
            plt.plot(lon, lat, marker='o',
                     color=color,
                     transform=ccrs.Geodetic())
            plt.text(lon + 1, lat + 1, city,
                     fontsize=8,
                     transform=ccrs.Geodetic())

        plt.savefig(path)
        plt.close()
        return path

    # ---------- РАССТОЯНИЕ ----------

    def draw_distance(self, city1, city2):
        plt.clf()
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines()

        lat1, lon1 = self.get_coordinates(city1)
        lat2, lon2 = self.get_coordinates(city2)

        plt.plot([lon1, lon2], [lat1, lat2],
                 color='blue', linewidth=2, marker='o',
                 transform=ccrs.Geodetic())

        plt.savefig(city1 + '_' + city2 + '.png')
        plt.close()
        return city1 + '_' + city2 + '.png'


if __name__ == "__main__":
    m = DB_Map(DATABASE)
    m.create_user_table()
    m.create_settings_table()
