# Demo Recording Guide for SaveZero

This guide explains how to create a compelling 15-30 second demo GIF/video for the SaveZero README.

## Goal

Show potential users **exactly what SaveZero does** without requiring them to read documentation.

## Target Flow

```
Instagram → 2,847 saved posts
              ↓
          SaveZero
              ↓
        automatic cleanup
              ↓
           0 saved
```

## Recording Steps

### 1. Preparation

**Before recording:**
- Have an Instagram account with 50-100 saved posts (or use demo data)
- Clean up your desktop/browser for a professional look
- Close unnecessary browser tabs and applications
- Set your terminal to a readable font size (16pt+)
- Use a clean terminal color scheme

**Test accounts:**
- Consider creating a test Instagram account specifically for demo purposes
- Save 50-100 posts manually or use an automated script to save sample posts
- This prevents your personal data from appearing in the demo

### 2. What to Capture

**Scene 1 (3-5 seconds): The Problem**
- Open Instagram in Chrome
- Navigate to your saved posts collection
- Show the total count prominently (e.g., "284 saved posts")
- Optional: Scroll briefly to show the large collection

**Scene 2 (2-3 seconds): Starting SaveZero**
- Switch to terminal
- Show the command:
  ```bash
  savezero --username demo_account
  ```
- Hit Enter

**Scene 3 (15-20 seconds): The Automation**
- Split screen or quick cuts between:
  - Terminal showing progress output
  - Browser showing posts being unsaved
- Key output to capture:
  ```
  [INFO] Starting SaveZero...
  [INFO] Authenticated successfully
  [INFO] Processing saved posts...
  [INFO] Cleared 50 posts...
  [INFO] Cleared 100 posts...
  [INFO] Cleared 150 posts...
  ```

**Scene 4 (2-3 seconds): The Result**
- Show Instagram saved collection
- Display "0 saved posts" or empty state
- Terminal shows completion message

### 3. Recording Tools

#### Option A: GIF (Recommended for README)

**Tools:**
- **Windows**: ScreenToGif (free, open source)
- **macOS**: Gifski + QuickTime or GIPHY Capture
- **Linux**: Peek or Gifski

**Settings:**
- Frame rate: 10-15 FPS (smooth but small file size)
- Resolution: 1280x720 or 1920x1080
- Optimize/compress the GIF (aim for <5MB)

#### Option B: Video (Alternative)

**Tools:**
- **Windows**: OBS Studio or Windows Game Bar
- **macOS**: QuickTime Screen Recording
- **Linux**: SimpleScreenRecorder or OBS Studio

**Settings:**
- Format: MP4 (H.264)
- Resolution: 1920x1080
- Frame rate: 30 FPS
- Duration: 15-30 seconds max

**Convert to GIF:**
```bash
# Using ffmpeg
ffmpeg -i demo.mp4 -vf "fps=10,scale=1280:-1:flags=lanczos" -c:v gif demo.gif

# Or use online converters like:
# - ezgif.com
# - cloudconvert.com
```

### 4. Editing Tips

**Keep it fast:**
- Speed up slow sections (especially browser loading)
- Cut out waiting time between actions
- Aim for 15-30 seconds total

**Add annotations (optional):**
- Text overlay showing post count
- Arrows highlighting key UI elements
- Progress indicators

**Tools for editing:**
- **GIF**: ezgif.com (online, free)
- **Video**: DaVinci Resolve (free), iMovie (macOS), Shotcut (cross-platform)

### 5. Quality Checklist

Before publishing, verify:

- [ ] Total duration is 15-30 seconds
- [ ] Text in terminal is readable
- [ ] Instagram UI is clearly visible
- [ ] File size is reasonable (<5MB for GIF, <10MB for video)
- [ ] No personal/sensitive information visible
- [ ] The "before" and "after" states are obvious
- [ ] The automation is clearly shown in action

### 6. Alternative: Screenshot Sequence

If creating a GIF/video is challenging, create a 4-panel image sequence:

```
+-------------------+-------------------+
|   Before: 284     |   Command:        |
|   saved posts     |   $ savezero ...  |
+-------------------+-------------------+
|   Processing...   |   After: 0        |
|   [terminal]      |   saved posts     |
+-------------------+-------------------+
```

**Tools:**
- Any image editor (GIMP, Photoshop, Figma, Canva)
- Screenshot tool + basic composition

### 7. Adding to README

Once you have the demo:

**For GIF hosted on GitHub:**
```markdown
## Demo

![SaveZero Demo](./assets/demo.gif)
```

**For externally hosted media:**
```markdown
## Demo

![SaveZero Demo](https://example.com/savezero-demo.gif)
```

**For video (with YouTube):**
```markdown
## Demo

[![SaveZero Demo](https://img.youtube.com/vi/VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=VIDEO_ID)
```

### 8. Sample Terminal Output to Show

Make sure your demo captures output like:

```
[2026-09-20 23:45:12] [INFO] SaveZero v0.1.0
[2026-09-20 23:45:12] [INFO] Initializing Chrome automation profile...
[2026-09-20 23:45:15] [INFO] Navigating to saved collection...
[2026-09-20 23:45:18] [INFO] Authentication detected!
[2026-09-20 23:45:19] [INFO] Starting cleanup in API mode...
[2026-09-20 23:45:20] [INFO] ✓ Cleared post 1/284
[2026-09-20 23:45:22] [INFO] ✓ Cleared post 2/284
...
[2026-09-20 23:50:30] [INFO] ✓ Cleared post 284/284
[2026-09-20 23:50:30] [INFO] 🎉 Complete! Cleared 284 posts, skipped 0
```

## Example Demo Scripts

### Script 1: "Quick Demo"
1. Show Instagram: "284 saved posts"
2. Terminal: `savezero --username demo`
3. Fast-forward through processing (speed up 4-8x)
4. Show result: "0 saved posts"
5. Text overlay: "SaveZero - Bulk-delete saved Instagram posts"

### Script 2: "Technical Demo"
1. Split screen: Instagram (left) + Terminal (right)
2. Start SaveZero
3. Show posts disappearing in real-time as terminal progresses
4. Highlight milestone pauses
5. Show completion

### Script 3: "Problem-Solution Demo"
1. Frustrated user clicking "Unsave" manually (1-2 clicks)
2. Text: "2,847 more to go... 😩"
3. Cut to: "Or use SaveZero"
4. Show automation
5. Result: Empty saved collection, happy user

## Questions?

Open an issue with the "question" label if you need help recording your demo!

---

**Remember**: The demo should make someone think "Oh, I need this!" within the first 5 seconds.
