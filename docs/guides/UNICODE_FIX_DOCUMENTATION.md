# Unicode Encoding Fix for Windows Logging

## Problem

When running the Titan Super Agent System on Windows with the default cp1252 encoding, the application crashes with `UnicodeEncodeError` when attempting to log messages containing emoji characters:

```
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f680' in position 53: character maps to <undefined>
```

This error occurs because:
- Windows console uses cp1252 encoding by default
- Emoji characters (🚀, ✅, 🔨, 🦀, 🎮, etc.) are Unicode characters that cannot be encoded in cp1252
- Python's logging module writes to stdout/stderr which may not support these characters

## Solution

The fix reconfigures Python's stdout and stderr streams to use UTF-8 encoding **before** any logging is initialized. This is done at the top of each affected Python file:

```python
# Configure UTF-8 encoding for Windows console output
# This must be done before any imports that might trigger logging
import sys
import os

if sys.platform == 'win32':
    # Set environment variable for Python IO encoding
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Reconfigure stdout and stderr to use UTF-8 encoding
    # This allows emoji and other Unicode characters to be displayed correctly
    # on Windows systems where the default console encoding is cp1252
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    else:
        # Fallback for older Python versions
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
```

### Key Points

1. **Platform-specific**: Only applies on Windows (`sys.platform == 'win32'`)
2. **Early execution**: Must run before any imports that might trigger logging
3. **Backward compatible**: Includes fallback for Python versions without `reconfigure()`
4. **Error handling**: Uses `errors='replace'` to replace unencodable characters instead of crashing
5. **Environment variable**: Sets `PYTHONIOENCODING='utf-8'` for consistency

## Files Modified

The fix has been applied to the following files:

### Core Agent Files
- `agents/super_agent_manager.py`
- `agents/specialized/orchestrator_agent.py`

### Main Application Files
- `mainnet_health_monitor.py`
- `production_deployment.py`
- `mainnet_orchestrator.py`
- `dashboard_server.py`
- `full_scale_test.py`

### Simulation Files
- `run_90day_simulation.py`
- `comprehensive_simulation.py`
- `run_real_strategy_simulation.py`
- `run_robust_90day_live_simulation.py`
- `train_hf_ranker.py`

### Simulation Module Files
- `simulation/historical_data_fetcher.py`
- `simulation/simulation_engine.py`
- `simulation/system_comparison.py`

## Testing

### Existing Tests
- `test_logging_unicode.py` - Tests emoji logging functionality
- `test_unicode_encoding_fix.py` - Tests Unicode export functionality

### New Test
- `test_windows_encoding_fix.py` - Comprehensive validation of the UTF-8 encoding fix

### Running Tests

```bash
# Test logging with Unicode characters
python test_logging_unicode.py

# Test Windows encoding fix
python test_windows_encoding_fix.py

# Test Unicode export
python test_unicode_encoding_fix.py
```

All tests pass on Linux systems. On Windows systems, the fix ensures that emoji characters are properly displayed in console output and log files.

## Impact

- ✅ **Fixes** the UnicodeEncodeError on Windows systems
- ✅ **Maintains** compatibility with Linux/Unix systems (UTF-8 is already default)
- ✅ **Preserves** emoji characters in log files (UTF-8 encoding)
- ✅ **No breaking changes** - only adds encoding configuration

## Future Considerations

If new Python files are added that:
1. Use emoji characters in logging
2. May be executed as standalone scripts on Windows

They should include the same UTF-8 encoding configuration at the top of the file.

## References

- Python Issue: https://bugs.python.org/issue13216
- Windows Console Encoding: https://docs.python.org/3/library/sys.html#sys.stdout
- Unicode in Python: https://docs.python.org/3/howto/unicode.html
