# Titan Core (Go)

## Overview

The `core-go` directory contains Go implementations of Titan system components. Go provides excellent performance, concurrency primitives, and is well-suited for building standalone services and CLI tools.

## Purpose

This Go core provides:
- **High-performance computing** for critical operations
- **Standalone service components** that can run independently
- **Efficient concurrency** using Go's goroutines
- **Cross-platform binaries** for easy deployment

## Project Structure

```
core-go/
├── commander/          # Flash loan optimization package
├── config/            # Configuration management package
├── enum/              # Chain enumeration package
├── simulation/        # Simulation engine package
├── main.go            # Main entry point
├── titan-core         # Compiled binary
├── go.mod             # Go module definition
├── go.sum             # Dependency checksums
└── README.md          # This file
```

## Key Dependencies

- **go-ethereum**: Official Ethereum implementation and library
- **gorilla/mux** (if used): HTTP routing
- **Other dependencies**: See `go.mod` for complete list

## Building from Source

### Prerequisites

- Go 1.21 or higher

### Build Binary

```bash
cd core-go
go build -o titan-core ./main.go
```

The compiled binary will be `titan-core` in the current directory.

### Build and Install

To install to your `$GOPATH/bin`:

```bash
cd core-go
go install
```

## Running

### Execute the Binary

```bash
./titan-core
```

### With Arguments

```bash
./titan-core --config /path/to/config.json
```

## Packages

### commander/
Flash loan optimization algorithms:
- Optimal loan size calculation
- Profit maximization
- Risk assessment logic

### config/
Configuration management:
- Environment variable loading
- Chain definitions
- Contract addresses
- RPC endpoints

### enum/
Chain enumeration:
- Chain ID mapping
- Network name resolution
- Provider management

### simulation/
Simulation engine:
- On-chain queries
- TVL calculations
- Balance verification

## Testing

```bash
# Test all packages
go test ./...

# Test specific package
go test ./commander

# Run with verbose output
go test -v ./...

# Run with coverage
go test -cover ./...
```

## Development

### Adding New Packages

1. Create a new directory in `core-go/`
2. Add Go files with package declaration
3. Update `main.go` to import and use the package
4. Add tests in `packagename_test.go` files
5. Update this README

### Code Style

Follow standard Go conventions:
- Use `gofmt` to format code
- Use `golint` for linting
- Follow effective Go practices
- Add godoc comments for exported functions

### Building for Different Platforms

```bash
# Linux
GOOS=linux GOARCH=amd64 go build -o titan-core-linux ./main.go

# macOS
GOOS=darwin GOARCH=amd64 go build -o titan-core-macos ./main.go

# Windows
GOOS=windows GOARCH=amd64 go build -o titan-core-windows.exe ./main.go

# ARM (for Raspberry Pi, etc.)
GOOS=linux GOARCH=arm64 go build -o titan-core-arm ./main.go
```

## Integration with Titan System

The Go core can be used in several ways:

1. **Standalone Service**: Run as an independent service
2. **CLI Tool**: Use from command line
3. **Library**: Import packages in other Go projects
4. **API Server**: Expose functionality via HTTP endpoints

## Performance

Go provides excellent performance characteristics:
- Fast compilation
- Efficient memory usage
- Built-in concurrency with goroutines
- No runtime dependencies (static binaries)

## Further Documentation Needed

- [ ] Detailed API documentation for each Go package
- [ ] Configuration file schema and examples
- [ ] Advanced usage scenarios and patterns
- [ ] Performance benchmarks compared to Python/Rust
- [ ] Deployment best practices for production
- [ ] Integration examples with other Titan components

## Contributing

When contributing Go code:
1. Run `gofmt` before committing
2. Add tests for new functionality
3. Update godoc comments
4. Follow Go naming conventions
5. Keep packages focused and cohesive

## Dependencies Management

```bash
# Add new dependency
go get github.com/example/package

# Update dependencies
go get -u ./...

# Tidy up go.mod and go.sum
go mod tidy

# Verify dependencies
go mod verify
```

## License

This module is part of the Titan 2.0 project and follows the same MIT License.

## Support

For issues related to Go core:
- Build issues: Check Go version (`go version`)
- Dependency issues: Run `go mod tidy`
- Runtime issues: Check binary permissions

See main README.md for general support information.
