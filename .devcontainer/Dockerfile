FROM golang as builder

COPY tools /go-build

WORKDIR /go-build/docker-health-check
RUN go mod download
RUN go build -o /usr/bin/docker-health-check cmd/main.go

# TODO: Replace once our image becomes public
# FROM ghcr.io/truenas/apps_validation:latest
FROM apps_valid

COPY --from=builder /usr/bin/docker-health-check /usr/bin/docker-health-check
