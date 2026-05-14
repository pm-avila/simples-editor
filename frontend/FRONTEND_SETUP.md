# SIMPLES Editor - Frontend Setup

## 🚀 Development Setup

### Prerequisites
- Node.js 18+
- npm or yarn
- Supabase project (https://app.supabase.com)

### Installation

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Configure Supabase:**
```bash
# Copy the example environment file
cp .env.example .env.local

# Edit .env.local with your Supabase credentials
```

3. **Get your Supabase credentials:**
   - Go to https://app.supabase.com/project/[YOUR_PROJECT_ID]/settings/api
   - Copy the **Project URL** and paste into `VITE_SUPABASE_URL`
   - Copy the **anon public** key and paste into `VITE_SUPABASE_ANON_KEY`

### Running Development Server

```bash
npm run dev
```

The app will be available at http://localhost:5173

### Build for Production

```bash
npm run build
```

Output will be in `dist/` directory.

## 🎨 Homepage Features

The SIMPLES Editor now includes a retro-futuristic homepage with:
- ASCII art logo with neon glow effects
- CRT monitor grid pattern background
- Terminal-style cards with project information
- Responsive design (mobile-first)
- Keyboard accessibility

## 🔐 Authentication Flow

1. **Homepage** → User sees retro landing page with SIMPLES branding
2. **Click "Entrar"** → Transition to login screen
3. **Enter credentials** → Authenticate with Supabase
4. **IDE** → Full development environment for SIMPLES code
5. **Logout** → Return to homepage

## 📝 Environment Variables

```env
# Required for Supabase authentication
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
```

## 🚨 Troubleshooting

### Login not working?
1. Check browser console for error messages
2. Verify Supabase credentials in `.env.local`
3. Ensure Supabase project is active and allows password authentication
4. Check network tab for failed requests to Supabase API

### Build errors?
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

## 📦 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── auth/          # Login and authentication screens
│   │   ├── home/          # Homepage with landing page
│   │   └── ide/           # IDE editor and shell
│   ├── lib/               # Utilities (Supabase, API)
│   ├── app.tsx            # Main app component with routing
│   ├── main.tsx           # React entry point
│   └── styles.css         # Global styles
├── index.html             # HTML entry point
├── config.js              # Runtime Supabase configuration
├── vite.config.ts         # Vite build configuration
├── tsconfig.json          # TypeScript configuration
└── package.json           # Dependencies and scripts
```

## 🎯 Key Technologies

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **TypeScript** - Type-safe JavaScript
- **Supabase** - Authentication and backend
- **Monaco Editor** - Code editor
- **xterm.js** - Terminal emulator
