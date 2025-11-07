curl -X POST "http://127.0.0.1:8000/log-in" \
     -H "Content-Type: application/json" \
     -d '{"email": "cristiancaraballo112@gmail.com"}'

JWT="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjcmlzdGlhbmNhcmFiYWxsbzExMkBnbWFpbC5jb20iLCJleHAiOjE3NjI1NDM4OTV9.9fG0k5ZEGo0RZa7lr1CM4WYJUie-TWOKUEOcjH0M"

curl -X GET "http://127.0.0.1:8000/verify-login?token=$JWT&email=cristiancaraballo112@gmail.com"

curl -X GET "http://127.0.0.1:8000/users/me" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $JWT"