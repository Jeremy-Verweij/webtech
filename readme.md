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

for running it on the internet

```bash
    ssh -p 443 -R0:127.0.0.1:5000 qr@a.pinggy.io
```
