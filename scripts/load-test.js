import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 20,
  duration: '30s',
  thresholds: {
    http_req_failed: ['rate<0.05'],           
    http_req_duration: ['p(95)<1000'],        
  },
};

export default function () {
  const feed = http.get('http://127.0.0.1:8000/posts?limit=5');
  check(feed, { 'feed status 200': (r) => r.status === 200 });
  sleep(1);

  const login = http.post('http://127.0.0.1:8000/auth/login',
    JSON.stringify({ email: 'alice@example.com', password: 'TestPassword123', remember_me: true }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  check(login, { 'login status 200': (r) => r.status === 200 });
  sleep(1);
}