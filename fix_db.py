import sqlite3
conn = sqlite3.connect('instance/driftdater.db')
conn.execute('DELETE FROM alembic_version')
conn.commit()
conn.close()
print('done')