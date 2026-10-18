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
