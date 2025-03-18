## Database migration

for first Initialization only:

```bash
    flask db init
```

for creating a migration script:

```bash
    flask db migrate -m "migration message"
```

```bash
    flask db upgrade
```

```bash
    flask db downgrade
```

## Setting up server for public acces

for starting server

```bash
    flask run
```

for making server public

```bash
    ssh -p 443 -R0:127.0.0.1:5000 qr@a.pinggy.io
```
