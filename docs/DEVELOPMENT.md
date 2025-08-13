# 🔧 Development Guide

## 🏗️ Project Structure

```text
stonks-bot/
├── stonks.py          # Core chart generation logic
├── bot.py             # Discord bot implementation
├── config.py          # Configuration management
├── test_stonks.py     # Test suite
├── github_actions.py  # CI/CD automation
├── .github/           # GitHub Actions workflows
├── pics/              # Generated charts
├── scripts/           # Deployment scripts
└── docs/              # Documentation
```

## 🎯 Architecture

### **Provider Pattern**
- Abstract `DataProvider` base class
- Concrete implementations: `PolygonProvider`, `CoinGeckoProvider`
- Easy to add new data sources

### **Singleton Pattern**
- Efficient `StonksChart` instance management
- Prevents multiple chart instances
- Optimized memory usage

### **Separation of Concerns**
- Clear separation between data, logic, and presentation
- Modular design for easy maintenance
- Testable components

### **Async Support**
- Full async/await support for Discord bot
- Non-blocking API calls
- Responsive user experience

## 🧹 Code Quality

### **Type Hints**
- Full Python type annotations
- Better IDE support
- Runtime type checking

### **Error Handling**
- Comprehensive exception management
- Custom `StonksError` class
- User-friendly error messages

### **Logging**
- Structured logging throughout
- Environment-based log levels
- Debug information for development

### **Documentation**
- Detailed docstrings
- Inline comments
- API documentation

## 🔄 Development Workflow

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/stonks-bot.git
   cd stonks-bot
   ```

2. **Setup Environment**
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run Tests**
   ```bash
   python test_stonks.py
   ```

4. **Make Changes**
   - Follow PEP 8 style guide
   - Add type hints
   - Update tests
   - Update documentation

5. **Test Locally**
   ```bash
   python bot.py
   ```

6. **Submit PR**
   - Clear commit messages
   - Include tests
   - Update documentation

## 📝 Code Standards

- **PEP 8**: Python style guide compliance
- **Type Hints**: All functions and methods
- **Docstrings**: Google style format
- **Error Handling**: Specific exception types
- **Testing**: 90%+ coverage target

## ⚡ Adding New Features

### **New Data Provider**
1. Extend `DataProvider` base class
2. Implement required methods
3. Add tests
4. Update configuration
5. Document usage

### **New Chart Type**
1. Extend `StonksChart` class
2. Add visualization method
3. Update bot commands
4. Add examples
5. Test thoroughly

### **New Bot Command**
1. Add command handler in `bot.py`
2. Implement logic
3. Add help text
4. Test with Discord
5. Update documentation

## 🔍 Debugging

- **Log Levels**: Use `LOG_LEVEL=DEBUG` for verbose output
- **API Testing**: Test individual providers separately
- **Chart Generation**: Use `save=True` for local file output
- **Network Issues**: Check rate limits and API status

## 📚 Resources

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Polygon.io API Docs](https://polygon.io/docs/)
- [CoinGecko API Docs](https://www.coingecko.com/en/api/documentation)
- [Matplotlib Documentation](https://matplotlib.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
