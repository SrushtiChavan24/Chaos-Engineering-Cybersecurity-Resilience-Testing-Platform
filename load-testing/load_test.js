// Load test — run with: k6 run --env BASE_URL=<url> load_test.js
// Writes a JSON summary to results/results_phase3.json so the
// orchestrator can read it programmatically.

import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:5000';

export const options = {
  stages: [
    { duration: '30s', target: 20 },
    { duration: '30s', target: 50 },
    { duration: '30s', target: 100 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.05'],
  },
};

export default function () {
  const res = http.get(`${BASE_URL}/data`);
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  sleep(0.5);
}

export function handleSummary(data) {
  return {
    '../results/results_phase3.json': JSON.stringify(data, null, 2),
    stdout: '', // still prints default summary to console too
  };
}
