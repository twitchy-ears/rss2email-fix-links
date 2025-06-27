# rss2email-fix-links
A small post-processing script for rss2email to add image links back into the content.

So basically I've been playing around with
[rss2email](https://github.com/rss2email/rss2email) for getting the
content from a Mastodon user feed and emailing that to an account.

This works fine, however posts with images don't include the images
themselves, or any indication that the post has an image.

This is a small post processing script that looks for media content in
the kind of RSS feed outputted by Mastodon and attempts to re-add the
img tags back in along with any alt-text available.

You use it by putting the script somewhere in your `$PYTHONPATH` set
of directories.

Then you add this to your `.config/rss2email.conf`

```
post-process = fix_links process
```

Then it should be done.  This is a quick bodge, and it works for me,
but that may not mean it works for you :) Tested against Mastodon
v4.3.8
