## 🎉 First Public Release

SaveZero is now ready for public use! This release includes all core features for safely bulk-deleting Instagram saved posts.

### ✨ Features

- 🚀 **Fast in-browser API mode** - Clears ~2,000+ posts/hour using direct fetch calls
- 🖱️ **Visual UI mode** - Full browser automation with DOM traversal and simulated clicks
- 🔄 **Self-healing recovery** - Automatically handles browser crashes and connection drops
- ⏱️ **Tiered cooldown system** - Smart pauses at 40/1,000/2,000 post milestones
- 🎯 **Dynamic selector resolution** - Works around Instagram's obfuscated CSS classes
- 🔒 **Zero-credential authentication** - Uses your Chrome profile, never asks for passwords
- 🛡️ **Built-in safety** - Detects action-block signals and halts automatically

### 💻 Platforms Supported

- ✅ Windows
- ✅ macOS  
- ✅ Linux

### 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/mvrao94/savezero.git
cd savezero

# Install dependencies
pip install -r requirements.txt

# Run SaveZero
python cleaner.py --username your_instagram_username
```

Or install directly:

```bash
pip install git+https://github.com/mvrao94/savezero.git
savezero --username your_instagram_username
```

### 📖 Documentation

- [README](https://github.com/mvrao94/savezero#readme) - Complete usage guide
- [CONTRIBUTING](https://github.com/mvrao94/savezero/blob/main/CONTRIBUTING.md) - How to contribute
- [SECURITY](https://github.com/mvrao94/savezero/blob/main/SECURITY.md) - Security policy

### ⚠️ Important Safety Notes

- SaveZero is designed to pace requests and halt on known action-block signals
- **This does not guarantee Instagram won't restrict your account**
- Unsaving is a private action on your own library
- Instagram enforces hourly velocity limits
- Use at your own discretion

### 🗺️ Roadmap

Future improvements planned:

- [ ] Comprehensive test suite
- [ ] Demo GIF/video
- [ ] PyPI package distribution
- [ ] Multiple Instagram account support
- [ ] Progress export/import for long sessions
- [ ] Collection-specific clearing (beyond "All Posts")

### 🐛 Known Issues

- Instagram's platform changes may occasionally break selectors (will be fixed promptly)
- Action block detection is best-effort, not comprehensive
- Very large collections (10,000+ posts) may require multiple sessions

### 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guide](https://github.com/mvrao94/savezero/blob/main/CONTRIBUTING.md).

### 📝 Changelog

See [CHANGELOG.md](https://github.com/mvrao94/savezero/blob/main/CHANGELOG.md) for detailed version history.

### 📄 License

MIT License - see [LICENSE](https://github.com/mvrao94/savezero/blob/main/LICENSE) for details.

---

**Full Changelog**: https://github.com/mvrao94/savezero/commits/v0.1.0

**Questions or issues?** Open an issue on GitHub or check our [documentation](https://github.com/mvrao94/savezero#readme).

Thank you for trying SaveZero! ⭐ Star the repo if you find it useful!
