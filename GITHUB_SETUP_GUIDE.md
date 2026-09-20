# GitHub Repository Setup Guide

This guide walks you through configuring your SaveZero repository on GitHub for maximum discoverability.

## Step 1: Update Repository Description

1. Go to https://github.com/mvrao94/savezero
2. Click the **⚙️ Settings** icon (or "Edit repository details" near the top right)
3. In the "About" section, update:

### Description
```
Bulk-delete Instagram saved posts with a self-healing local Python automation tool
```

### Website (optional)
If you create documentation or a landing page, add it here.

### Topics
Add these topics (click "Add topics" if not visible):

```
instagram
instagram-automation
python
browser-automation
productivity
cleanup
automation
selenium
instagram-scraper
instagram-tools
bulk-delete
saved-posts
python3
chrome-automation
self-healing
```

**Why these topics matter:**
- They help GitHub categorize your project
- They appear in GitHub's Explore and search results
- Users can click topics to find similar projects
- Topics are used in GitHub's trending algorithms

4. Check these boxes if appropriate:
   - [ ] Releases (once you create v1.0.0)
   - [ ] Packages (if you publish to PyPI)

5. Click **"Save changes"**

## Step 2: Enable GitHub Features

### Enable Discussions (Optional but Recommended)
1. Go to **Settings** → **General**
2. Scroll to **Features** section
3. Check ☑️ **Discussions**
4. This gives users a place to ask questions without opening issues

### Enable GitHub Projects (Optional)
1. In **Features** section
2. Check ☑️ **Projects**
3. Useful for tracking roadmap and feature development

### Enable Wiki (Optional)
1. In **Features** section
2. Check ☑️ **Wiki**
3. For extended documentation beyond README

## Step 3: Create Your First Release

Creating a release makes your project look more established.

1. Go to **Releases** (right sidebar on main repo page)
2. Click **"Create a new release"** or **"Draft a new release"**
3. Fill in:

**Tag version:** `v0.1.0`

**Release title:** `SaveZero v0.1.0 - Initial Public Release`

**Description:**
```markdown
## 🎉 First Public Release

SaveZero is now ready for public use! This release includes:

### Features
- 🚀 Fast in-browser API mode (~2,000+ posts/hour)
- 🖱️ Visual UI mode with full browser automation
- 🔄 Self-healing recovery from browser crashes
- ⏱️ Tiered cooldown system (40/1000/2000 post milestones)
- 🎯 Dynamic selector resolution
- 🔒 Zero-credential authentication via Chrome profile

### Platforms
- ✅ Windows
- ✅ macOS  
- ✅ Linux

### Installation

```bash
pip install git+https://github.com/mvrao94/savezero.git
savezero --username your_instagram_username
```

See [README.md](https://github.com/mvrao94/savezero#readme) for full documentation.

### ⚠️ Important Notes
- SaveZero is designed to pace requests and halt on action-block signals
- This does not guarantee Instagram won't restrict your account
- Use at your own discretion

### What's Next?
- [ ] PyPI package distribution
- [ ] Comprehensive test suite
- [ ] Demo GIF/video
- [ ] Collection-specific clearing

**Full Changelog**: https://github.com/mvrao94/savezero/commits/v0.1.0
```

4. Check **"Set as the latest release"**
5. Click **"Publish release"**

## Step 4: Add Social Preview Image (Optional but Impactful)

Create a 1280x640px image showing SaveZero in action.

1. Go to **Settings** → **General**
2. Scroll to **Social preview**
3. Click **"Edit"**
4. Upload your image (1280x640px recommended)

**Image ideas:**
- Screenshot of SaveZero terminal + Instagram UI
- Logo/brand with tagline
- Before/after saved post count

**Tools:**
- Canva (templates available)
- Figma
- Photoshop/GIMP

## Step 5: Pin Important Issues

Once you have issues or discussions:

1. Open an important issue (e.g., "Roadmap", "Known Issues", "FAQ")
2. Click **"Pin issue"** (right sidebar)
3. Pinned issues appear at the top of the Issues tab

## Step 6: Add Repository Stats Badges (Optional)

Add these to your README for instant credibility:

```markdown
[![GitHub stars](https://img.shields.io/github/stars/mvrao94/savezero?style=social)](https://github.com/mvrao94/savezero/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/mvrao94/savezero?style=social)](https://github.com/mvrao94/savezero/network/members)
[![GitHub issues](https://img.shields.io/github/issues/mvrao94/savezero)](https://github.com/mvrao94/savezero/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/mvrao94/savezero)](https://github.com/mvrao94/savezero/pulls)
[![CI](https://github.com/mvrao94/savezero/workflows/CI/badge.svg)](https://github.com/mvrao94/savezero/actions)
```

## Verification Checklist

After completing setup, verify:

- [ ] Repository has a clear, benefit-focused description
- [ ] At least 10 relevant topics are added
- [ ] Issue templates appear when creating new issues
- [ ] GitHub Actions CI workflow is running (check Actions tab)
- [ ] First release (v0.1.0) is published
- [ ] README.md displays correctly with proper formatting
- [ ] CONTRIBUTING.md, SECURITY.md, and CHANGELOG.md are accessible
- [ ] Social preview image displays when sharing (optional)

## Next Steps: Launch Strategy

Once your repository is configured:

1. **Week 1: Polish & Test**
   - Get 5-10 real users to test
   - Fix critical bugs
   - Gather feedback

2. **Week 2: Create Demo**
   - Follow [DEMO_RECORDING_GUIDE.md](./DEMO_RECORDING_GUIDE.md)
   - Add demo GIF to README
   - Create short technical writeup

3. **Week 3: Soft Launch**
   - Post to relevant communities (with permission)
   - Share on Twitter/LinkedIn with compelling story
   - Submit to relevant newsletters/aggregators

4. **Week 4: Hacker News Launch**
   - Post as "Show HN: SaveZero – Bulk-delete Instagram saved posts"
   - Engage authentically with comments
   - Be ready to fix bugs quickly

## Communities to Target

**When you're ready to promote:**

### Reddit (read rules first)
- r/Python (Saturday self-promotion threads)
- r/learnpython
- r/productivity
- r/Instagram (be careful, check rules)
- r/automation

### Forums & Communities
- Hacker News (Show HN)
- Lobsters
- IndieHackers
- ProductHunt (requires good demo)

### Social Media
- Twitter/X with hashtags: #Python #Automation #Instagram #OpenSource
- LinkedIn (tech professionals audience)
- Dev.to (write a technical article)

### Direct Outreach
- Python Weekly newsletter
- Awesome Python lists
- GitHub Explore (organic via topics)

## Important Reminders

1. **Never buy stars or use star-exchange services**
2. **Don't spam communities** - only post where self-promotion is allowed
3. **Engage authentically** with feedback and questions
4. **Fix bugs quickly** during launch period
5. **Celebrate small wins** - 10 genuine users > 100 empty stars

---

Good luck with your launch! 🚀
