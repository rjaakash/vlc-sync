# ▶️ VLC Sync

Personal automation for VLC Android nightly builds.

I made this repo for myself.

I only use VLC nightly builds, and they are not available on the Play Store or F-Droid.  
To get them, I had to open the browser, search for VLC, go through the official site, navigate to the Android page, then documentation, then the nightly section, and finally reach the correct build page to download the APK and install it manually from the file manager. Since nightly updates frequently, I had to do this almost every day.

Even with bookmarks, it still meant opening the browser, going to bookmarks, opening the page, downloading the APK, and installing it manually.

That got annoying.

So I automated it.

This repo watches VLC nightly builds, downloads the latest APK, and publishes it as a GitHub release. After that, I just use [Obtainium](https://github.com/ImranR98/Obtainium), so updates happen automatically in the background and I don’t have to do anything anymore.

---

## 🙏 Credits

- VLC Android builds by **[VideoLAN](https://www.videolan.org/vlc/)**
- Automation powered by **[GitHub Actions](https://github.com/apps/github-actions)**
