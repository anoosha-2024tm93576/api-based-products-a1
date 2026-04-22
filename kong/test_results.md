# Kong API Gateway Test Results

## Test 1 — Rate Limiting

### Command

```bash
for i in {1..6}; do curl -i http://localhost:8000/api; done
```

### Expected Behavior

- Requests 1-5: `502 Bad Gateway` (Kong forwards to upstream, Flask not running)
- Request 6: `429 Too Many Requests` (rate limit exceeded)

### Output

```
Request 1: HTTP/1.1 502 | RateLimit-Remaining: 4
Request 2: HTTP/1.1 502 | RateLimit-Remaining: 3
Request 3: HTTP/1.1 502 | RateLimit-Remaining: 2
Request 4: HTTP/1.1 502 | RateLimit-Remaining: 1
Request 5: HTTP/1.1 502 | RateLimit-Remaining: 0
Request 6: HTTP/1.1 429 Too Many Requests ✅
```

### Key Headers Observed

```
X-RateLimit-Limit-Minute: 5
X-RateLimit-Remaining-Minute: 0
RateLimit-Limit: 5
RateLimit-Remaining: 0
```

### Conclusion

Kong correctly enforced the rate limit of 5 requests per minute.
On the 6th request, it returned 429 Too Many Requests without
forwarding the request to the upstream server.

---

## Test 2 — Request Size Limiting

### Command

```bash
python3 -c "print('x' * 2000000)" > bigfile.txt
curl -i -X POST http://localhost:8000/api -H "Content-Type: application/json" -d @bigfile.txt
```

### Expected Behavior

- Body size is ~2MB, exceeding the 1MB limit
- Kong should reject the request with `413 Request Entity Too Large`

### Output

```
HTTP/1.1 413 Request Entity Too Large
Content-Type: application/json; charset=utf-8
X-Kong-Response-Latency: 2
Server: kong/3.6.1

{
  "message": "Request size limit exceeded",
  "request_id": "7d8ea4069757647feb843021701f0071"
}
```

### Conclusion

Kong correctly rejected the oversized request before it reached
the upstream server, returning 413 Request Entity Too Large
with the message "Request size limit exceeded".

---

## Summary


| Plugin                | Config            | Result                        |
| --------------------- | ----------------- | ----------------------------- |
| rate-limiting         | 5 requests/minute | ✅ 429 returned on 6th request |
| request-size-limiting | 1MB max body      | ✅ 413 returned for 2MB body   |


