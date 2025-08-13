# 🧪 Testing Guide

## ⚡ Quick Test

Run the comprehensive test suite:

```bash
python test_stonks.py
```

## 📋 Test Coverage

Tests cover:
- Data provider functionality
- Chart generation
- Error handling
- Configuration management
- Input validation

## 🔍 Test Structure

### **DataProvider Tests**
- Base class functionality
- Abstract method enforcement
- Error handling

### **PolygonProvider Tests**
- API request handling
- Data parsing
- Error scenarios
- Rate limiting

### **CoinGeckoProvider Tests**
- Free API integration
- Data format validation
- Network error handling

### **StonksChart Tests**
- Chart generation
- Data processing
- Visualization quality
- Edge cases

### **Configuration Tests**
- Environment variable loading
- Default value fallbacks
- Validation rules

## 🛠️ Running Specific Tests

```bash
# Run specific test class
python -m unittest test_stonks.TestPolygonProvider

# Run specific test method
python -m unittest test_stonks.TestPolygonProvider.test_get_historical_data

# Run with verbose output
python -m unittest test_stonks -v

# Run with coverage (if coverage.py installed)
coverage run test_stonks.py
coverage report
```

## 🧩 Mocking

Tests use `unittest.mock` to isolate components:
- API responses are mocked
- Network calls are intercepted
- External dependencies are controlled

## 📊 Test Results

Expected output:
```text
.......
----------------------------------------------------------------------
Ran 7 tests in 0.123s

OK
```

## 🚨 Troubleshooting

- **Import errors**: Ensure all dependencies are installed
- **Test failures**: Check if APIs are accessible
- **Mock issues**: Verify test isolation
- **Coverage gaps**: Add tests for untested code paths
