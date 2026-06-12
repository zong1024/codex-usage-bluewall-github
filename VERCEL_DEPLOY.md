# Vercel Deployment Guide

## Step 1: Push to GitHub

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

## Step 2: Import to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `vercel`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

## Step 3: Set Environment Variables

In Vercel project settings, add:

| Variable | Value |
|----------|-------|
| `GITHUB_USERNAME` | your-github-username |
| `GITHUB_REPO` | codex-usage-bluewall-github |

## Step 4: Deploy

Click "Deploy" and wait for build to complete.

## Step 5: Get Your URL

After deployment, you'll get a URL like:
```
https://your-project.vercel.app
```

## Step 6: Use in GitHub Profile

Add to your GitHub Profile README:

```markdown
## AI Coding Activity

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://your-project.vercel.app/api/svg">
  <img alt="AI Coding Blue Wall" src="https://your-project.vercel.app/api/svg">
</picture>
```

## Custom Domain (Optional)

1. Go to Vercel project settings
2. Click "Domains"
3. Add your custom domain
4. Update DNS records as instructed

## Auto-Deploy

Vercel automatically redeploys when you push to GitHub. So just run:

```bash
./scripts/update-full.sh --commit --push
```

And your SVG will update within minutes!
