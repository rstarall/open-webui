# CORS配置：使用分号(;)分隔多个域名，不要使用逗号(,)
export CORS_ALLOW_ORIGIN="http://localhost:5173;http://42.193.237.200:5173"
PORT="${PORT:-8080}"
uvicorn open_webui.main:app --port $PORT --host 0.0.0.0 --forwarded-allow-ips '*' --reload
