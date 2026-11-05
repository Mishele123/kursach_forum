"""Run integration tests in a disposable PostgreSQL database and Redis namespace."""
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from config import Config


def run():
    os.chdir(ROOT)
    config = Config()
    name = 'forum_test_' + secrets.token_hex(6)
    env = {**os.environ, 'POSTGRES_DB': name, 'REDIS_KEY_PREFIX': name}
    def pg(*args):
        subprocess.run(['docker', 'compose', 'exec', '-T', 'postgres', *args], check=True)
    pg('createdb', '-U', config.postgres.user, name)
    try:
        with tempfile.TemporaryDirectory(prefix='forum-uploads-') as uploads:
            env['UPLOAD_DIR'] = uploads
            def migrate(*args):
                subprocess.run([sys.executable, '-m', 'alembic', *args], cwd=ROOT / 'backend', env=env, check=True)
            def sql(statement):
                result = subprocess.run(['docker', 'compose', 'exec', '-T', 'postgres',
                    'psql', '-U', config.postgres.user, '-d', name, '-At', '-v', 'ON_ERROR_STOP=1'],
                    input=statement, text=True, capture_output=True, check=True)
                return result.stdout.strip()
            # Verify migration of an actual legacy cover, including rollback.
            migrate('upgrade', '0008')
            sql("INSERT INTO users (username) VALUES ('migration_test'); "
                "INSERT INTO posts (author_id,title,text,category,photo_filename) "
                "SELECT id,'Legacy','Photo','route','0123456789abcdef0123456789abcdef.jpg' "
                "FROM users WHERE username='migration_test';")
            migrate('upgrade', 'head')
            assert sql('SELECT filename FROM post_photos') == '0123456789abcdef0123456789abcdef.jpg'
            migrate('downgrade', '0008')
            assert sql('SELECT photo_filename FROM posts') == '0123456789abcdef0123456789abcdef.jpg'
            for args in [('upgrade', 'head'), ('check',), ('downgrade', 'base'), ('upgrade', 'head')]:
                subprocess.run([sys.executable, '-m', 'alembic', *args], cwd=ROOT / 'backend', env=env, check=True)
            subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], env=env, check=True)
    finally:
        pg('dropdb', '--force', '-U', config.postgres.user, name)
        # Delete only this run's Redis namespace, never shared application sessions.
        import redis
        client = redis.Redis(host=config.redis.host, port=config.redis.port, password=config.redis.password)
        keys = list(client.scan_iter(match=name + ':*'))
        if keys:
            client.delete(*keys)
        client.close()


if __name__ == '__main__':
    run()
