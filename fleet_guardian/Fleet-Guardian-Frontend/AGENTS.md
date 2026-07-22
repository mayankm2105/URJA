# EV Fleet APM Dashboard

This is the frontend for the EV Fleet APM Dashboard. It connects to the FastAPI backend to display real-time asset health and recommendations.

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   npm run build
   ```

## Environment Variables

- `VITE_API_BASE_URL`: The URL of the FastAPI backend. Defaults to `http://localhost:8000`.
