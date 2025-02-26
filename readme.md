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
