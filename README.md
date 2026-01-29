# Who Made It? 🔍

An AI-powered web application that reveals the gender of inventors and creators behind products, services, and inventions throughout history.

![Who Made It Banner](https://img.shields.io/badge/Stack-React%20%7C%20FastAPI%20%7C%20MongoDB-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 🌟 Features

- **AI-Powered Analysis**: Uses OpenAI GPT-4o-mini to identify inventors and their gender
- **Real-Time Statistics**: Live scoreboard tracking men vs women creators
- **Category Breakdown**: Visual analytics showing gender distribution across different fields
- **Milestone Tracking**: Dynamic counter celebrating every 100,000 queries
- **Smart Filtering**: Automatically excludes natural items (not invented by humans)
- **Beautiful UI**: Neo-Brutalist design with Syne and Outfit fonts

## 🚀 Live Demo

- **Frontend**: [Deployed on Vercel](#)
- **Backend**: [Deployed on Render.com](#)

## 🛠️ Tech Stack

**Frontend:**
- React 18
- Tailwind CSS
- Framer Motion (animations)
- React CountUp (number animations)
- Phosphor Icons
- Axios

**Backend:**
- FastAPI (Python)
- OpenAI API (GPT-4o-mini)
- Motor (Async MongoDB driver)
- Pydantic (data validation)

**Database:**
- MongoDB Atlas

**Hosting:**
- Frontend: Vercel
- Backend: Render.com
- Database: MongoDB Atlas (M0 Free Tier)

## 📦 Installation

### Prerequisites
- Node.js 16+
- Python 3.11+
- MongoDB Atlas account
- OpenAI API key

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/cOzYByte/Who-Made-It.git
   cd Who-Made-It
   ```

2. **Set up Backend:**
   ```bash
   cd backend
   pip install -r requirements-production.txt
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY and MONGO_URL
   uvicorn server:app --reload
   ```

3. **Set up Frontend:**
   ```bash
   cd frontend
   yarn install
   # Create .env file with REACT_APP_BACKEND_URL=http://localhost:8000
   yarn start
   ```

4. **Visit:** http://localhost:3000

## 🌐 Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions to:
- Render.com (Backend)
- Vercel (Frontend)
- MongoDB Atlas (Database)

## 🎨 Design Philosophy

**Neo-Brutalism with a Purpose:**
- Sharp edges and thick borders for visual impact
- International Klein Blue (#002FA7) for men
- Signal Orange (#FF4500) for women
- Syne font for massive, attention-grabbing headings
- Outfit font for clean, readable body text
- No gradients – pure, bold colors only

## 🔒 Privacy & Security

- No user accounts required
- No personal data collected
- All queries are anonymous
- API keys stored securely in environment variables
- Natural items (not human inventions) are not saved to the database

## 📊 API Endpoints

```
GET  /api/              # Health check
POST /api/analyze       # Analyze an invention
GET  /api/stats         # Get global statistics
GET  /api/queries       # Get recent queries
GET  /api/categories    # Get category breakdown
GET  /api/milestones    # Get milestone history
```

## 🙏 Acknowledgments

- Built with [Emergent.sh](https://emergent.sh) - AI-powered development platform
- OpenAI for GPT-4o-mini API
- Vercel for frontend hosting
- Render.com for backend hosting
- MongoDB for database infrastructure

---

Made with ❤️ by [cOzYByte](https://github.com/cOzYByte)
