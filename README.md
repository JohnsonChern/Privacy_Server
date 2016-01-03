This is application of privacy filter on Demo app for [Privacy Server](https://github.com/JohnsonChern/Privacy_Server).

### How to use

#####Setup basic environment
1. This demo app uses `requests` and `flask`. If you have `pip`, simply do
   ```
   $ pip install requests flask psycopg2

   ```
   Or simply
   ```
   $ pip install -r requirement_app.txt

   ```

2. Edit `config.py` to point the app to a server.

##### Run for static test
1. Run the original server at localhost with:
```
$ python app.py
```

2. Run modified server at localhost with:
```
$ python app.py
```

3. You will need local database support to see dynamic interation on how this policy works

   * Confirm that psycopg2 and postgresql is isntalled properly
   
   * Please read and modify config_db.py and the run setup_db.py
