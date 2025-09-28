# Ollama Dockerfile example
FROM golang:1.22 as builder
WORKDIR /app
COPY . .
RUN go build -o ollama .

FROM debian:bullseye-slim
WORKDIR /app
COPY --from=builder /app/ollama .
EXPOSE 11434
CMD ["./ollama", "serve"]
