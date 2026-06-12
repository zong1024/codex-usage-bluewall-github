# AI Coding Blue Wall - Vercel

This is the Vercel deployment for AI Coding Blue Wall.

## API Endpoints

### GET /api/svg

Returns an SVG image showing your AI coding activity.

**Query Parameters:**
- `days` (optional): Number of days to show (default: 365)

**Example:**
```
https://your-project.vercel.app/api/svg?days=90
```

### GET /

Preview page showing your AI coding activity.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GITHUB_USERNAME` | Your GitHub username |
| `GITHUB_REPO` | Repository name |

## Development

```bash
npm install
npm run dev
```

## Deployment

Push to GitHub and Vercel will auto-deploy.

## License

MIT
