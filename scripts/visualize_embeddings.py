#!/usr/bin/env python3
"""
Elite Estate - 3D pgvector Embedding Visualizer
This script fetches embeddings from the PostgreSQL database, performs dimensionality
reduction (PCA and t-SNE), and builds a gorgeous, interactive 3D HTML dashboard.
"""

import os
import sys
import json
import webbrowser
import subprocess
import http.server
import socketserver
import urllib.parse
import socket
import threading

# ------------------------------------------------------------------------------
# 1. Dependency Management
# ------------------------------------------------------------------------------
REQUIRED_PACKAGES = {
    "psycopg2": "psycopg2-binary",
    "numpy": "numpy",
    "pandas": "pandas",
    "sklearn": "scikit-learn",
    "plotly": "plotly"
}

def install_dependencies():
    """Checks and installs missing dependencies."""
    missing = []
    for module_name, pip_name in REQUIRED_PACKAGES.items():
        try:
            __import__(module_name)
        except ImportError:
            missing.append(pip_name)
            
    if missing:
        print(f"[PACKAGES] Missing required libraries: {', '.join(missing)}")
        print("[PACKAGES] Installing dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
            print("[PACKAGES] Dependencies installed successfully!\n")
        except Exception as e:
            print(f"[ERROR] Failed to install dependencies: {e}")
            print("Please run manually: pip install psycopg2-binary numpy pandas scikit-learn plotly")
            sys.exit(1)

# Run dependency check before anything else
install_dependencies()

# Now import the libraries
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

# ------------------------------------------------------------------------------
# Global State for local HTTP server API
# ------------------------------------------------------------------------------
properties_data = []
embeddings_data = None
pca_model = None
coords_tsne_data = None
env_vars = {}
output_path = ""

# ------------------------------------------------------------------------------
# 2. Environment & Database Loading
# ------------------------------------------------------------------------------
def load_env():
    """Loads environment variables from .env file, checking multiple paths."""
    env_paths = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    ]
    
    env_vars_dict = {}
    loaded_path = None
    
    for path in env_paths:
        if os.path.exists(path):
            loaded_path = path
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        env_vars_dict[k.strip()] = v.strip().strip('"').strip("'")
            break
            
    if loaded_path:
        print(f"[ENV] Loaded environment configuration from: {loaded_path}")
    else:
        print("[ENV] Warning: .env file not found. Falling back to default database credentials.")
        
    return env_vars_dict

def get_db_connection(env):
    """Establishes database connection to PostgreSQL."""
    import psycopg2
    
    user = env.get("POSTGRES_USER", "postgres")
    password = env.get("POSTGRES_PASSWORD", "admin")
    db_name = env.get("POSTGRES_DB", "real_estate")
    
    # When running on host, POSTGRES_HOST=postgres (inside docker) is not reachable.
    # We map it to localhost.
    host = env.get("POSTGRES_HOST", "localhost")
    if host == "postgres":
        host = "localhost"
        
    port = env.get("POSTGRES_PORT", "5432")
    
    print(f"[DB] Connecting to database at {host}:{port}/{db_name}...")
    
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
            port=port
        )
        return conn
    except Exception as e:
        raise ConnectionError(f"Database connection failed: {e}")

# ------------------------------------------------------------------------------
# 3. Data Processing & Dimensionality Reduction
# ------------------------------------------------------------------------------
def fetch_properties_data(conn):
    """Retrieves properties and their description vectors from PostgreSQL."""
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'properties'
        );
    """)
    if not cursor.fetchone()[0]:
        raise ValueError("The 'properties' table does not exist in the database.")
        
    # Query properties
    query = """
        SELECT id, title, price, property_type, listing_type, city, description, area, description_vector
        FROM properties
        WHERE description_vector IS NOT NULL;
    """
    
    print("[DB] Querying database for property embeddings...")
    cursor.execute(query)
    rows = cursor.fetchall()
    
    if not rows:
        raise ValueError("No property vectors found in the database.")
        
    print(f"[DB] Found {len(rows)} properties with embedded description vectors.")
    
    properties = []
    embeddings = []
    
    for row in rows:
        prop_id, title, price, prop_type, list_type, city, description, area, vec = row
        
        # Parse vector if it's a string, or keep it if it's already a list
        if isinstance(vec, str):
            # pgvector sometimes comes back as a string '[0.12, -0.45, ...]'
            vec = [float(x) for x in vec.strip("[]").split(",")]
            
        properties.append({
            "id": prop_id,
            "title": title,
            "price": float(price) if price else 0.0,
            "property_type": prop_type,
            "listing_type": list_type,
            "city": city,
            "description": description,
            "area": float(area) if area else 0.0
        })
        embeddings.append(vec)
        
    return properties, np.array(embeddings)

def perform_dimensionality_reduction(embeddings):
    """Reduces embeddings from 768 dimensions to 3D coordinates using PCA and t-SNE."""
    n_samples = len(embeddings)
    print(f"[ML] Reducing dimensions of {n_samples} embeddings (shape: {embeddings.shape})...")
    
    # 1. PCA Reduction
    print("[ML] Computing PCA (3 components)...")
    pca = PCA(n_components=3, random_state=42)
    coords_pca = pca.fit_transform(embeddings)
    explained_variance = float(np.sum(pca.explained_variance_ratio_) * 100)
    print(f"[ML] PCA Explained Variance (Top 3): {explained_variance:.2f}%")
    
    # 2. t-SNE Reduction
    print("[ML] Computing t-SNE (3 components)...")
    # Perplexity should be less than the number of samples
    perplexity = min(30, max(2, n_samples - 1))
    
    tsne = TSNE(
        n_components=3, 
        perplexity=perplexity, 
        random_state=42,
        init='pca' if n_samples > 30 else 'random'
    )
    coords_tsne = tsne.fit_transform(embeddings)
    
    return coords_pca, coords_tsne, explained_variance, perplexity, pca

# ------------------------------------------------------------------------------
# 4. Standalone HTML Dashboard Template
# ------------------------------------------------------------------------------
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en" class="h-full bg-slate-950 text-slate-100">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elite Estate AI - 3D Embedding Explorer</title>
    <!-- Tailwind CSS for modern structure -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Plotly.js for interactive 3D scatter plots -->
    <script src="https://cdn.plot.ly/plotly-2.24.1.min.js"></script>
    <!-- FontAwesome for high-quality utility icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Google Fonts: Inter and Outfit -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #050814;
        }
        h1, h2, h3, .font-display {
            font-family: 'Outfit', sans-serif;
        }
        .glass-panel {
            background: rgba(15, 23, 42, 0.45);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .glass-sidebar {
            background: rgba(10, 15, 30, 0.7);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255, 255, 255, 0.06);
        }
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.1);
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        /* Glow animations */
        .neon-glow-primary {
            text-shadow: 0 0 10px rgba(99, 102, 241, 0.5), 0 0 20px rgba(99, 102, 241, 0.2);
        }
    </style>
</head>
<body class="h-full overflow-hidden flex flex-col md:flex-row">

    <!-- 1. SIDEBAR (CONTROLS & DETAILS) -->
    <aside class="w-full md:w-96 glass-sidebar flex flex-col z-10 flex-shrink-0 h-1/2 md:h-full overflow-y-auto">
        <!-- Logo / Title -->
        <div class="p-6 border-b border-slate-800/80">
            <div class="flex items-center gap-3">
                <div class="p-2.5 bg-indigo-600/20 border border-indigo-500/40 rounded-xl text-indigo-400">
                    <i class="fa-solid fa-cubes fa-lg"></i>
                </div>
                <div>
                    <h1 class="text-xl font-bold tracking-tight text-white neon-glow-primary">Elite Estate AI</h1>
                    <p class="text-xs text-indigo-400 font-medium tracking-wide uppercase">3D Embedding Explorer</p>
                </div>
            </div>
        </div>

        <!-- Section: Controls -->
        <div class="p-6 border-b border-slate-800/50 space-y-5">
            <!-- Projection Algorithm -->
            <div>
                <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Dimensionality Reduction</label>
                <div class="grid grid-cols-2 gap-2 bg-slate-900/80 p-1 rounded-xl border border-slate-800">
                    <button id="btn-pca" onclick="setAlgorithm('pca')" class="py-2 px-3 text-xs font-semibold rounded-lg transition-all duration-300 bg-indigo-600 text-white shadow-md shadow-indigo-600/20">
                        PCA <span class="block text-[9px] font-normal text-indigo-200">Global structure</span>
                    </button>
                    <button id="btn-tsne" onclick="setAlgorithm('tsne')" class="py-2 px-3 text-xs font-semibold rounded-lg transition-all duration-300 text-slate-400 hover:text-white">
                        t-SNE <span class="block text-[9px] font-normal text-slate-500">Local clusters</span>
                    </button>
                </div>
            </div>

            <!-- Color By -->
            <div>
                <label for="color-by" class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Color Coding</label>
                <div class="relative">
                    <select id="color-by" onchange="updateVisualization()" class="w-full bg-slate-900 border border-slate-800 text-sm rounded-xl px-4 py-2.5 text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 appearance-none cursor-pointer">
                        <option value="property_type">Property Type</option>
                        <option value="listing_type">Listing Type (Sale/Rent)</option>
                        <option value="city">City</option>
                        <option value="price">Price (Value spectrum)</option>
                    </select>
                    <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none text-slate-500">
                        <i class="fa-solid fa-chevron-down text-xs"></i>
                    </div>
                </div>
            </div>

            <!-- Search -->
            <div>
                <div class="flex justify-between items-center mb-2">
                    <label for="search-box" class="block text-xs font-semibold text-slate-400 uppercase tracking-wider">Search Properties</label>
                    <div class="flex items-center gap-1.5 bg-slate-950 px-2 py-0.5 rounded-md border border-slate-800">
                        <button id="search-mode-keyword" onclick="setSearchMode('keyword')" class="text-[10px] font-bold px-1.5 py-0.5 rounded transition-all text-slate-400 hover:text-white">Keyword</button>
                        <button id="search-mode-semantic" onclick="setSearchMode('semantic')" class="text-[10px] font-bold px-1.5 py-0.5 rounded transition-all bg-indigo-600 text-white shadow-sm shadow-indigo-600/20">Semantic</button>
                    </div>
                </div>
                <div class="relative">
                    <input type="text" id="search-box" oninput="debounceSearch(this.value)" placeholder="Ask AI: 'luxurious villa with a pool'..." 
                           class="w-full bg-slate-900 border border-slate-800 text-sm rounded-xl pl-10 pr-4 py-2.5 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500">
                    <div class="absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-500">
                        <i class="fa-solid fa-magnifying-glass text-xs" id="search-icon"></i>
                    </div>
                </div>
                <div class="flex justify-between items-center mt-1.5 px-0.5">
                    <div id="search-results-info" class="text-xs text-indigo-400/80 hidden"></div>
                    <div id="api-status-badge" class="text-[10px] font-medium text-slate-500 flex items-center gap-1 cursor-pointer">
                        <span class="h-1.5 w-1.5 rounded-full bg-slate-500"></span> API: Offline
                    </div>
                </div>
                
                <!-- Expanded Settings Panel -->
                <div id="api-config-container" class="mt-2 p-3 bg-slate-950/80 border border-slate-800 rounded-xl space-y-2.5 hidden">
                    <div>
                        <label for="api-url-input" class="block text-[9px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Backend API URL</label>
                        <div class="flex gap-1.5">
                            <input type="text" id="api-url-input" value="http://localhost:8000" class="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-slate-200 text-xs w-full focus:outline-none focus:border-indigo-500">
                            <button onclick="checkApiConnection()" class="bg-indigo-600 hover:bg-indigo-500 text-white text-xs px-2.5 py-1 rounded-lg font-medium transition-all shadow-sm shadow-indigo-600/10">Test</button>
                        </div>
                    </div>
                    <div>
                        <label for="ollama-url-input" class="block text-[9px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Local Ollama URL</label>
                        <input type="text" id="ollama-url-input" value="http://localhost:11434" class="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-slate-200 text-xs w-full focus:outline-none focus:border-indigo-500">
                    </div>
                    <div>
                        <label for="gemini-key-input" class="block text-[9px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Gemini API Key</label>
                        <input type="password" id="gemini-key-input" placeholder="Injected from .env or enter key" class="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-slate-200 text-xs w-full focus:outline-none focus:border-indigo-500">
                    </div>
                    <div class="text-[9px] text-slate-500 leading-normal">
                        <i class="fa-solid fa-triangle-exclamation text-amber-500/75 mr-0.5"></i> Keep this file private if it contains your Gemini key.
                    </div>
                </div>
                
                <div id="semantic-matches-container" class="mt-3 space-y-2 max-h-48 overflow-y-auto pr-1 hidden"></div>
            </div>
        </div>

        <!-- Section: Property details (Dynamic) -->
        <div class="flex-grow p-6 flex flex-col justify-between">
            <div id="details-container">
                <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Property Details</label>
                <div id="details-placeholder" class="text-center py-10 px-4 border border-dashed border-slate-800 rounded-2xl bg-slate-950/40">
                    <i class="fa-solid fa-hand-pointer text-slate-600 text-3xl mb-3"></i>
                    <p class="text-sm text-slate-400 font-medium">Click an embedding node in 3D space to inspect property details</p>
                </div>
                
                <!-- Detail Card (Initially hidden) -->
                <div id="detail-card" class="hidden space-y-4">
                    <div>
                        <div class="flex justify-between items-start gap-2">
                            <span id="detail-type" class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider"></span>
                            <span id="detail-listing" class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider"></span>
                        </div>
                        <h2 id="detail-title" class="text-lg font-bold text-white mt-2 leading-snug"></h2>
                        <p id="detail-location" class="text-xs text-slate-400 mt-1">
                            <i class="fa-solid fa-location-dot text-indigo-400 mr-1"></i> <span id="detail-city"></span>
                        </p>
                    </div>
                    
                    <div class="p-3.5 bg-slate-900/60 rounded-xl border border-slate-800/80 flex justify-between items-center">
                        <div>
                            <span class="block text-[10px] text-slate-500 uppercase tracking-wider">Price</span>
                            <span id="detail-price" class="text-base font-extrabold text-emerald-400"></span>
                        </div>
                        <div class="text-right">
                            <span class="block text-[10px] text-slate-500 uppercase tracking-wider">Area</span>
                            <span id="detail-area" class="text-sm font-bold text-slate-200"></span>
                        </div>
                    </div>

                    <div>
                        <span class="block text-xs font-semibold text-slate-400 mb-1">Description Semantic context:</span>
                        <div class="p-3 bg-slate-950/60 border border-slate-900 rounded-xl max-h-40 overflow-y-auto">
                            <p id="detail-desc" class="text-xs text-slate-300 leading-relaxed"></p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Stats & Specs footer -->
            <div class="mt-6 pt-4 border-t border-slate-800/50 flex justify-between text-[10px] text-slate-500 font-mono">
                <span>Vector Dimension: 768</span>
                <span id="stat-extra"></span>
            </div>
        </div>
    </aside>

    <!-- 2. MAIN 3D CHART CANVAS -->
    <main class="flex-grow h-1/2 md:h-full relative bg-[#04060f]">
        <!-- Fullscreen Canvas -->
        <div id="plotly-chart" class="w-full h-full"></div>
        
        <!-- Legend Indicator/Helper on top-left of chart -->
        <div class="absolute top-5 left-5 pointer-events-none bg-slate-950/80 px-4 py-2 rounded-xl border border-slate-800 flex items-center gap-3">
            <span class="flex h-2 w-2 relative">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
            </span>
            <span class="text-xs font-semibold text-indigo-200 tracking-wide uppercase" id="selected-algorithm-label">PCA PROJECTION</span>
        </div>

        <div class="absolute bottom-5 right-5 glass-panel p-3.5 rounded-xl text-xs text-slate-300 pointer-events-none space-y-1.5 border border-slate-700/30 max-w-xs shadow-xl shadow-black/40">
            <h3 class="font-bold text-white mb-1"><i class="fa-solid fa-circle-info text-indigo-400 mr-1"></i> Interactive Help</h3>
            <div class="flex items-center gap-2"><i class="fa-solid fa-rotate text-slate-400 w-4"></i> Left-Click + Drag to Rotate</div>
            <div class="flex items-center gap-2"><i class="fa-solid fa-arrows-up-down-left-right text-slate-400 w-4"></i> Right-Click + Drag to Pan</div>
            <div class="flex items-center gap-2"><i class="fa-solid fa-magnifying-glass-plus text-slate-400 w-4"></i> Scroll / Pinch to Zoom</div>
            <div class="flex items-center gap-2"><i class="fa-solid fa-circle-nodes text-slate-400 w-4"></i> Hover/Click node for metadata</div>
        </div>
    </main>

    <!-- Data Injection -->
    <script>
        // Data injected from Python
        const propertiesData = _DATA_PLACEHOLDER_;
        const pcaStats = _PCA_STATS_;
        const tsneStats = _TSNE_STATS_;
        const pcaMean = _PCA_MEAN_;
        const pcaComponents = _PCA_COMPONENTS_;
        const propertyEmbeddings = _PROPERTY_EMBEDDINGS_;
        const geminiApiKey = _GEMINI_API_KEY_;

        let currentQueryCoords = null; // will store { pca: [x,y,z], tsne: [x,y,z] }
        let currentQueryEmbedding = null; // will store the 768D query embedding
        let currentSearchQueryText = '';

        // Colors corresponding to dark design tokens
        const colors = {
            villa: '#f43f5e',      // rose-500
            apartment: '#3b82f6',  // blue-500
            house: '#10b981',      // emerald-500
            studio: '#a855f7',     // purple-500
            office: '#eab308',     // yellow-500
            default: '#64748b',    // slate-500
            
            sale: '#ec4899',       // pink-500
            rent: '#14b8a6',       // teal-500
            
            cities: ['#6366f1', '#8b5cf6', '#d946ef', '#ff007f', '#f97316', '#22c55e', '#06b6d4', '#eab308']
        };

        let currentAlgorithm = 'pca'; // 'pca' or 'tsne'
        let currentSearchQuery = '';
        let searchMode = 'semantic'; // 'semantic' or 'keyword'
        let matchedPropertyIds = new Set();
        let semanticMatches = []; // holds ordered semantic search response items

        // Initialize view
        document.addEventListener('DOMContentLoaded', () => {
            setAlgorithm('pca');
            checkApiConnection();
            
            // Wire API url status click toggle
            document.getElementById('api-status-badge').addEventListener('click', () => {
                const configContainer = document.getElementById('api-config-container');
                configContainer.classList.toggle('hidden');
            });
        });

        function setAlgorithm(alg) {
            currentAlgorithm = alg;
            
            // Update Active Buttons
            const btnPca = document.getElementById('btn-pca');
            const btnTsne = document.getElementById('btn-tsne');
            const label = document.getElementById('selected-algorithm-label');
            const statExtra = document.getElementById('stat-extra');
            
            if (alg === 'pca') {
                btnPca.className = "py-2 px-3 text-xs font-semibold rounded-lg transition-all duration-300 bg-indigo-600 text-white shadow-md shadow-indigo-600/20";
                btnTsne.className = "py-2 px-3 text-xs font-semibold rounded-lg transition-all duration-300 text-slate-400 hover:text-white";
                label.innerText = "PCA 3D PROJECTION";
                statExtra.innerText = `Explained Var: ${pcaStats.explained_variance.toFixed(1)}%`;
            } else {
                btnTsne.className = "py-2 px-3 text-xs font-semibold rounded-lg transition-all duration-300 bg-indigo-600 text-white shadow-md shadow-indigo-600/20";
                btnPca.className = "py-2 px-3 text-xs font-semibold rounded-lg transition-all duration-300 text-slate-400 hover:text-white";
                label.innerText = "t-SNE 3D PROJECTION";
                statExtra.innerText = `Perplexity: ${tsneStats.perplexity}`;
            }
            
            updateVisualization();
        }

        // Color mapper helper
        function getColorMap(colorBy) {
            const mappings = {};
            const uniqueValues = new Set(propertiesData.map(p => p[colorBy]));
            
            if (colorBy === 'property_type') {
                return colors;
            } else if (colorBy === 'listing_type') {
                return {
                    sale: colors.sale,
                    rent: colors.rent
                };
            } else if (colorBy === 'city') {
                let index = 0;
                uniqueValues.forEach(val => {
                    mappings[val] = colors.cities[index % colors.cities.length];
                    index++;
                });
                return mappings;
            }
            return null; // Numeric/Price uses scales
        }

        function updateVisualization() {
            const colorBy = document.getElementById('color-by').value;
            const colorMap = getColorMap(colorBy);
            
            // Build Plotly traces based on groups
            let traces = [];
            
            if (colorBy === 'price') {
                const x = [], y = [], z = [], texts = [], prices = [], sizes = [], indices = [], opacities = [];
                
                propertiesData.forEach((p, idx) => {
                    const coords = p[currentAlgorithm];
                    x.push(coords[0]);
                    y.push(coords[1]);
                    z.push(coords[2]);
                    texts.push(p.title);
                    prices.push(p.price);
                    indices.push(idx);
                    
                    const size = Math.min(20, Math.max(8, (p.area / 100) * 3));
                    sizes.push(size);
                    
                    const matchesSearch = isPropertyMatched(p);
                    opacities.push(matchesSearch ? 0.85 : 0.15);
                });
                
                traces.push({
                    x: x, y: y, z: z,
                    mode: 'markers',
                    text: texts,
                    customdata: indices,
                    marker: {
                        size: sizes,
                        color: prices,
                        colorscale: 'Portland',
                        showscale: true,
                        colorbar: {
                            title: {
                                text: 'Price (TND)',
                                font: { color: '#94a3b8', size: 10 }
                            },
                            tickfont: { color: '#94a3b8', size: 9 },
                            thickness: 15,
                            len: 0.6
                        },
                        opacity: opacities,
                        line: { color: 'rgba(255,255,255,0.1)', width: 1 }
                    },
                    type: 'scatter3d',
                    name: 'Properties'
                });
            } else {
                const groups = {};
                propertiesData.forEach((p, idx) => {
                    const val = p[colorBy] || 'unknown';
                    if (!groups[val]) groups[val] = [];
                    groups[val].push({ prop: p, index: idx });
                });
                
                Object.keys(groups).forEach(groupName => {
                    const x = [], y = [], z = [], texts = [], sizes = [], indices = [], opacities = [];
                    
                    groups[groupName].forEach(item => {
                        const coords = item.prop[currentAlgorithm];
                        x.push(coords[0]);
                        y.push(coords[1]);
                        z.push(coords[2]);
                        texts.push(`${item.prop.title}<br>${item.prop.city} | ${item.prop.property_type.toUpperCase()}`);
                        indices.push(item.index);
                        
                        const size = Math.min(22, Math.max(9, (item.prop.area / 100) * 3));
                        sizes.push(size);
                        
                        const matchesSearch = isPropertyMatched(item.prop);
                        opacities.push(matchesSearch ? 0.9 : 0.15);
                    });
                    
                    const traceColor = colorMap ? (colorMap[groupName] || colors.default) : colors.default;
                    
                    traces.push({
                        x: x, y: y, z: z,
                        mode: 'markers',
                        text: texts,
                        customdata: indices,
                        marker: {
                            size: sizes,
                            color: traceColor,
                            opacity: opacities,
                            line: { color: 'rgba(255,255,255,0.2)', width: 1 }
                        },
                        type: 'scatter3d',
                        name: groupName.charAt(0).toUpperCase() + groupName.slice(1)
                    });
                });
            }
            
            // Add connection lines to top 5 L2 and top 5 Cosine matches
            if (currentQueryCoords && currentQueryCoords[currentAlgorithm] && currentQueryEmbedding) {
                const qCoords = currentQueryCoords[currentAlgorithm];
                
                const l2Dists = [];
                const cosineDists = [];
                
                for (let i = 0; i < propertyEmbeddings.length; i++) {
                    const pEmb = propertyEmbeddings[i];
                    
                    // L2 distance
                    let l2Sum = 0;
                    for (let j = 0; j < 768; j++) {
                        const diff = currentQueryEmbedding[j] - pEmb[j];
                        l2Sum += diff * diff;
                    }
                    l2Dists.push({ index: i, dist: Math.sqrt(l2Sum) });
                    
                    // Cosine distance
                    let dotProduct = 0;
                    let normA = 0;
                    let normB = 0;
                    for (let j = 0; j < 768; j++) {
                        dotProduct += currentQueryEmbedding[j] * pEmb[j];
                        normA += currentQueryEmbedding[j] * currentQueryEmbedding[j];
                        normB += pEmb[j] * pEmb[j];
                    }
                    const cosineDist = 1.0 - (dotProduct / (Math.sqrt(normA) * Math.sqrt(normB) + 1e-8));
                    cosineDists.push({ index: i, dist: cosineDist });
                }
                
                l2Dists.sort((a, b) => a.dist - b.dist);
                cosineDists.sort((a, b) => a.dist - b.dist);
                
                const top5L2 = l2Dists.slice(0, 5);
                const top5Cosine = cosineDists.slice(0, 5);
                
                // Construct L2 lines trace (color: vibrant rose/pink #f43f5e)
                const l2X = [], l2Y = [], l2Z = [];
                top5L2.forEach(item => {
                    const pCoords = propertiesData[item.index][currentAlgorithm];
                    l2X.push(qCoords[0], pCoords[0], null);
                    l2Y.push(qCoords[1], pCoords[1], null);
                    l2Z.push(qCoords[2], pCoords[2], null);
                });
                
                traces.push({
                    x: l2X,
                    y: l2Y,
                    z: l2Z,
                    mode: 'lines',
                    line: {
                        color: 'rgba(244, 63, 94, 0.65)', // Semi-transparent Rose/Pink for L2 halo
                        width: 6.0
                    },
                    type: 'scatter3d',
                    name: 'Top 5 L2 Neighbors (Euclidean)',
                    hoverinfo: 'none'
                });
                
                // Construct Cosine lines trace (color: vibrant cyan #06b6d4)
                const cosX = [], cosY = [], cosZ = [];
                top5Cosine.forEach(item => {
                    const pCoords = propertiesData[item.index][currentAlgorithm];
                    cosX.push(qCoords[0], pCoords[0], null);
                    cosY.push(qCoords[1], pCoords[1], null);
                    cosZ.push(qCoords[2], pCoords[2], null);
                });
                
                traces.push({
                    x: cosX,
                    y: cosY,
                    z: cosZ,
                    mode: 'lines',
                    line: {
                        color: '#06b6d4', // Vibrant Cyan core for Cosine
                        width: 2.5,
                        dash: 'dash' // Dashed line to contrast when overlapping
                    },
                    type: 'scatter3d',
                    name: 'Top 5 Cosine Neighbors',
                    hoverinfo: 'none'
                });
            }
            
            // Add a distinct glowing gold diamond marker for the query node if active
            if (currentQueryCoords && currentQueryCoords[currentAlgorithm]) {
                const qCoords = currentQueryCoords[currentAlgorithm];
                traces.push({
                    x: [qCoords[0]],
                    y: [qCoords[1]],
                    z: [qCoords[2]],
                    mode: 'markers+text',
                    text: [`🔍 QUERY: "${currentSearchQueryText}"`],
                    textposition: 'top center',
                    marker: {
                        size: 15,
                        color: '#fbbf24', // Neon Gold/Yellow
                        symbol: 'diamond',
                        line: { color: '#ffffff', width: 2 },
                        opacity: 1.0
                    },
                    textfont: {
                        color: '#fbbf24',
                        family: 'Outfit, sans-serif',
                        size: 12,
                        weight: 'bold'
                    },
                    type: 'scatter3d',
                    name: 'Search Query'
                });
            }
            
            const layout = {
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                scene: {
                    xaxis: {
                        gridcolor: 'rgba(51, 65, 85, 0.3)',
                        zerolinecolor: 'rgba(71, 85, 105, 0.4)',
                        backgroundcolor: '#070b19',
                        showbackground: true,
                        color: '#64748b',
                        tickfont: { size: 9 },
                        title: { text: 'Dim 1', font: { size: 10 } }
                    },
                    yaxis: {
                        gridcolor: 'rgba(51, 65, 85, 0.3)',
                        zerolinecolor: 'rgba(71, 85, 105, 0.4)',
                        backgroundcolor: '#070b19',
                        showbackground: true,
                        color: '#64748b',
                        tickfont: { size: 9 },
                        title: { text: 'Dim 2', font: { size: 10 } }
                    },
                    zaxis: {
                        gridcolor: 'rgba(51, 65, 85, 0.3)',
                        zerolinecolor: 'rgba(71, 85, 105, 0.4)',
                        backgroundcolor: '#070b19',
                        showbackground: true,
                        color: '#64748b',
                        tickfont: { size: 9 },
                        title: { text: 'Dim 3', font: { size: 10 } }
                    },
                    camera: {
                        eye: { x: 1.6, y: 1.6, z: 1.2 }
                    }
                },
                margin: { l: 0, r: 0, b: 0, t: 0 },
                legend: {
                    font: { color: '#cbd5e1', size: 11 },
                    bgcolor: 'rgba(10, 15, 30, 0.6)',
                    bordercolor: 'rgba(255, 255, 255, 0.05)',
                    borderwidth: 1,
                    x: 0.9,
                    y: 0.9
                },
                hoverlabel: {
                    bgcolor: '#0f172a',
                    bordercolor: '#1e293b',
                    font: { color: '#f8fafc', family: 'Inter', size: 11 }
                }
            };
            
            const config = {
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['resetCameraLastSave3d', 'hoverClosest3d'],
                displaylogo: false
            };
            
            Plotly.newPlot('plotly-chart', traces, layout, config);
            
            document.getElementById('plotly-chart').on('plotly_click', function(data) {
                if (data.points && data.points.length > 0) {
                    const point = data.points[0];
                    if (point.customdata !== undefined) {
                        selectProperty(point.customdata);
                    }
                }
            });
        }

        let searchDebounceTimeout = null;

        function debounceSearch(val) {
            clearTimeout(searchDebounceTimeout);
            searchDebounceTimeout = setTimeout(() => {
                handleSearch(val);
            }, 350);
        }

        function isPropertyMatched(p) {
            if (currentSearchQuery === '') return true;
            if (searchMode === 'semantic') {
                return matchedPropertyIds.has(p.id);
            } else {
                return p.title.toLowerCase().includes(currentSearchQuery) ||
                       p.description.toLowerCase().includes(currentSearchQuery) ||
                       p.city.toLowerCase().includes(currentSearchQuery);
            }
        }

        // Generates the embedding for the query by calling local APIs or falling back to synthetic
        async function fetchQueryEmbedding(queryText) {
            const customOllamaUrl = document.getElementById('ollama-url-input')?.value.trim();
            const customGeminiKey = document.getElementById('gemini-key-input')?.value.trim();
            
            // 1. Try local server API first
            if (window.location.protocol.startsWith('http')) {
                try {
                    const res = await fetch(`/api/search?query=${encodeURIComponent(queryText)}`);
                    if (res.ok) {
                        const data = await res.json();
                        return { type: 'server_response', data: data };
                    }
                } catch (e) {
                    console.log("Local server API search failed, trying client-side embedding...", e);
                }
            }
            
            // 2. Try direct call to local Ollama
            const ollamaUrl = customOllamaUrl || 'http://localhost:11434';
            try {
                const res = await fetch(`${ollamaUrl}/api/embeddings`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ model: 'nomic-embed-text', prompt: queryText })
                });
                if (res.ok) {
                    const data = await res.json();
                    return { type: 'embedding', vector: data.embedding };
                }
            } catch (e) {
                console.log("Direct Ollama call failed:", e);
            }
            
            // 3. Try direct call to Gemini API
            const finalGeminiKey = customGeminiKey || geminiApiKey;
            if (finalGeminiKey) {
                try {
                    const url = `https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key=${finalGeminiKey}`;
                    const res = await fetch(url, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            content: { parts: [{ text: queryText }] }
                        })
                    });
                    if (res.ok) {
                        const data = await res.json();
                        return { type: 'embedding', vector: data.embedding.values };
                    }
                } catch (e) {
                    console.log("Direct Gemini API call failed:", e);
                }
            }
            
            return null;
        }

        // Projects a 768D vector into 3D using PCA mean and components
        function projectPca(embedding) {
            const x = [];
            for (let i = 0; i < 3; i++) {
                let val = 0;
                for (let j = 0; j < 768; j++) {
                    val += (embedding[j] - pcaMean[j]) * pcaComponents[i][j];
                }
                x.push(val);
            }
            return x;
        }

        // Projects a 768D vector into 3D using K-NN interpolation on t-SNE property coords
        function projectTsne(embedding) {
            const dists = [];
            for (let i = 0; i < propertiesData.length; i++) {
                const p = propertiesData[i];
                const p_emb = propertyEmbeddings[i];
                let distSq = 0;
                for (let j = 0; j < 768; j++) {
                    const diff = embedding[j] - p_emb[j];
                    distSq += diff * diff;
                }
                dists.push({ index: i, dist: Math.sqrt(distSq) });
            }
            
            dists.sort((a, b) => a.dist - b.dist);
            
            const k = Math.min(5, dists.length);
            let weightSum = 0;
            const coords = [0, 0, 0];
            
            for (let i = 0; i < k; i++) {
                const d = dists[i];
                const weight = 1.0 / (d.dist + 1e-8);
                const pCoords = propertiesData[d.index].tsne;
                coords[0] += pCoords[0] * weight;
                coords[1] += pCoords[1] * weight;
                coords[2] += pCoords[2] * weight;
                weightSum += weight;
            }
            
            return [coords[0] / weightSum, coords[1] / weightSum, coords[2] / weightSum];
        }

        // Generates a mock embedding matching the synthetic data generation to place the query node in the correct cluster
        function generateSyntheticQueryEmbedding(queryText) {
            const vec = new Array(768).fill(0).map(() => (Math.random() - 0.5) * 0.1);
            const text = queryText.toLowerCase();
            
            if (text.includes("villa")) {
                for (let j = 0; j < 150; j++) vec[j] += 0.3;
            } else if (text.includes("apartment")) {
                for (let j = 150; j < 300; j++) vec[j] += 0.3;
            } else if (text.includes("house")) {
                for (let j = 300; j < 450; j++) vec[j] += 0.3;
            } else if (text.includes("studio")) {
                for (let j = 450; j < 600; j++) vec[j] += 0.3;
            }
            
            if (text.includes("sale") || text.includes("buy")) {
                for (let j = 600; j < 680; j++) vec[j] += 0.15;
            } else if (text.includes("rent")) {
                for (let j = 680; j < 768; j++) vec[j] += 0.15;
            }
            
            return vec;
        }

        // Computes cosine similarity in browser
        function computeLocalSemanticSearch(queryEmbedding) {
            const matches = [];
            for (let i = 0; i < propertiesData.length; i++) {
                const p = propertiesData[i];
                const p_emb = propertyEmbeddings[i];
                
                let dotProduct = 0;
                let normA = 0;
                let normB = 0;
                for (let j = 0; j < 768; j++) {
                    dotProduct += queryEmbedding[j] * p_emb[j];
                    normA += queryEmbedding[j] * queryEmbedding[j];
                    normB += p_emb[j] * p_emb[j];
                }
                
                let similarity = dotProduct / (Math.sqrt(normA) * Math.sqrt(normB) + 1e-8);
                
                const text = currentSearchQuery;
                const words = text.split(/\\s+/).filter(w => w.length > 2);
                let keywordMatchCount = 0;
                const searchTarget = (p.title + " " + p.description).toLowerCase();
                words.forEach(w => {
                    if (searchTarget.includes(w)) {
                        keywordMatchCount++;
                    }
                });
                
                if (keywordMatchCount > 0) {
                    similarity += 0.15 * keywordMatchCount;
                }
                
                matches.push({
                    id: p.id,
                    similarity: Math.min(1.0, similarity),
                    title: p.title,
                    price: p.price,
                    city: p.city,
                    area: p.area,
                    property_type: p.property_type,
                    listing_type: p.listing_type
                });
            }
            
            matches.sort((a, b) => b.similarity - a.similarity);
            return matches;
        }

        async function handleSearch(val) {
            currentSearchQuery = val.trim().toLowerCase();
            
            const info = document.getElementById('search-results-info');
            const matchesContainer = document.getElementById('semantic-matches-container');
            const searchIcon = document.getElementById('search-icon');
            
            if (currentSearchQuery === '') {
                info.classList.add('hidden');
                matchesContainer.classList.add('hidden');
                matchedPropertyIds.clear();
                semanticMatches = [];
                currentQueryCoords = null;
                currentQueryEmbedding = null;
                currentSearchQueryText = '';
                updateVisualization();
                return;
            }
            
            if (searchMode === 'semantic') {
                searchIcon.className = "fa-solid fa-spinner animate-spin text-indigo-400 text-xs";
                
                try {
                    const apiUrl = document.getElementById('api-url-input').value.trim();
                    const isApiOnline = document.getElementById('api-status-badge').innerText.includes('Online');
                    
                    let data = null;
                    let queryEmbedding = null;
                    let isLocal = false;
                    let isSynthetic = false;
                    
                    // 1. Fetch query embedding / search results
                    const result = await fetchQueryEmbedding(val);
                    
                    if (result && result.type === 'server_response') {
                        // The local python server did all the work
                        data = result.data.matches;
                        currentQueryCoords = result.data.query_coords;
                        currentQueryEmbedding = result.data.query_vector;
                        isLocal = true;
                        isSynthetic = result.data.mode === 'synthetic';
                    } else {
                        // We generated the raw embedding (or failed and got null)
                        let emb = result ? result.vector : null;
                        if (!emb) {
                            emb = generateSyntheticQueryEmbedding(val);
                            isSynthetic = true;
                        }
                        queryEmbedding = emb;
                        currentQueryEmbedding = emb;
                        
                        // Compute local semantic search matches
                        data = computeLocalSemanticSearch(queryEmbedding);
                        
                        // Project query embedding in 3D
                        currentQueryCoords = {
                            pca: projectPca(queryEmbedding),
                            tsne: projectTsne(queryEmbedding)
                        };
                        isLocal = true;
                    }
                    
                    currentSearchQueryText = val;
                    semanticMatches = data;
                    matchedPropertyIds = new Set(data.map(p => p.id));
                    
                    let statusLabel = isLocal ? "Local AI" : "FastAPI Backend";
                    if (isSynthetic) statusLabel += " (Demo Mode)";
                    
                    info.innerText = `🔍 ${statusLabel}: Found ${data.length} matches`;
                    info.classList.remove('hidden');
                    
                    renderSemanticMatchesList();
                    
                } catch (error) {
                    console.error("Semantic search failed:", error);
                    info.innerText = `⚠️ Semantic search failed, using Keyword Search`;
                    info.classList.remove('hidden');
                    
                    searchMode = 'keyword';
                    updateSearchModeButtons();
                    matchesContainer.classList.add('hidden');
                } finally {
                    searchIcon.className = "fa-solid fa-magnifying-glass text-xs";
                }
            } else {
                let matchedCount = 0;
                propertiesData.forEach(p => {
                    if (p.title.toLowerCase().includes(currentSearchQuery) ||
                        p.description.toLowerCase().includes(currentSearchQuery) ||
                        p.city.toLowerCase().includes(currentSearchQuery)) {
                        matchedCount++;
                    }
                });
                
                info.innerText = `🔍 Found ${matchedCount} matching properties`;
                info.classList.remove('hidden');
                matchesContainer.classList.add('hidden');
                
                // For keyword mode, project a synthetic point based on input text
                const queryEmbedding = generateSyntheticQueryEmbedding(val);
                currentQueryCoords = {
                    pca: projectPca(queryEmbedding),
                    tsne: projectTsne(queryEmbedding)
                };
                currentQueryEmbedding = queryEmbedding;
                currentSearchQueryText = val;
            }
            
            updateVisualization();
        }

        function renderSemanticMatchesList() {
            const container = document.getElementById('semantic-matches-container');
            container.innerHTML = '';
            
            if (semanticMatches.length === 0) {
                container.innerHTML = '<div class="text-xs text-slate-500 text-center py-2">No semantic matches found.</div>';
                container.classList.remove('hidden');
                return;
            }
            
            semanticMatches.forEach((match, index) => {
                const localIndex = propertiesData.findIndex(p => p.id === match.id);
                if (localIndex === -1) return;
                
                const prop = propertiesData[localIndex];
                const rank = index + 1;
                
                const itemDiv = document.createElement('div');
                itemDiv.className = "p-2.5 bg-slate-900/60 hover:bg-indigo-950/40 border border-slate-800/80 hover:border-indigo-500/30 rounded-xl transition-all cursor-pointer flex justify-between items-start gap-2 group";
                itemDiv.onclick = () => {
                    selectProperty(localIndex);
                    focusNodeInPlotly(localIndex);
                };
                
                itemDiv.innerHTML = `
                    <div class="flex-grow min-w-0">
                        <div class="flex items-center gap-1.5 mb-1">
                            <span class="px-1.5 py-0.5 rounded text-[8px] font-bold uppercase tracking-wider bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">#${rank} Match</span>
                            <span class="text-[9px] text-slate-400 truncate">${prop.city}</span>
                        </div>
                        <h4 class="text-xs font-semibold text-slate-200 truncate group-hover:text-indigo-300 transition-colors">${prop.title}</h4>
                    </div>
                    <div class="text-right flex-shrink-0">
                        <span class="text-xs font-bold text-emerald-400">${prop.price.toLocaleString()} TND</span>
                        <span class="block text-[8px] text-slate-500">${prop.area} m²</span>
                    </div>
                `;
                
                container.appendChild(itemDiv);
            });
            
            container.classList.remove('hidden');
        }

        function focusNodeInPlotly(index) {
            const chartDiv = document.getElementById('plotly-chart');
            if (!chartDiv || !chartDiv.data) return;
            
            let foundTrace = -1;
            let foundPoint = -1;
            
            for (let t = 0; t < chartDiv.data.length; t++) {
                const trace = chartDiv.data[t];
                if (trace.customdata) {
                    const pIdx = trace.customdata.indexOf(index);
                    if (pIdx !== -1) {
                        foundTrace = t;
                        foundPoint = pIdx;
                        break;
                    }
                }
            }
            
            if (foundTrace !== -1 && foundPoint !== -1) {
                try {
                    Plotly.Fx.hover('plotly-chart', [
                        { curveNumber: foundTrace, pointNumber: foundPoint }
                    ]);
                } catch (e) {
                    console.log("Hover effect not supported:", e);
                }
            }
        }

        function setSearchMode(mode) {
            searchMode = mode;
            updateSearchModeButtons();
            
            const searchVal = document.getElementById('search-box').value;
            handleSearch(searchVal);
        }

        function updateSearchModeButtons() {
            const btnKeyword = document.getElementById('search-mode-keyword');
            const btnSemantic = document.getElementById('search-mode-semantic');
            const searchBox = document.getElementById('search-box');
            
            if (searchMode === 'semantic') {
                btnSemantic.className = "text-[10px] font-bold px-1.5 py-0.5 rounded bg-indigo-600 text-white shadow-sm shadow-indigo-600/20 transition-all";
                btnKeyword.className = "text-[10px] font-bold px-1.5 py-0.5 rounded text-slate-400 hover:text-white transition-all";
                searchBox.placeholder = "Ask AI: 'luxurious villa with pool'...";
            } else {
                btnKeyword.className = "text-[10px] font-bold px-1.5 py-0.5 rounded bg-indigo-600 text-white shadow-sm shadow-indigo-600/20 transition-all";
                btnSemantic.className = "text-[10px] font-bold px-1.5 py-0.5 rounded text-slate-400 hover:text-white transition-all";
                searchBox.placeholder = "Search title, description, city...";
            }
        }

        async function checkApiConnection() {
            const apiUrl = document.getElementById('api-url-input').value.trim();
            const badge = document.getElementById('api-status-badge');
            
            try {
                const res = await fetch(apiUrl + "/");
                if (res.ok) {
                    badge.innerHTML = '<span class="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></span> API: Online';
                    badge.className = "text-[10px] font-semibold text-emerald-400 flex items-center gap-1 cursor-pointer";
                    if (document.getElementById('search-box').value === '') {
                        searchMode = 'semantic';
                        updateSearchModeButtons();
                    }
                    return true;
                }
            } catch (e) {
                // Ignore and fall through to offline handling
            }
            
            // Check if we are running in HTTP mode (local server)
            if (window.location.protocol.startsWith('http')) {
                badge.innerHTML = '<span class="h-1.5 w-1.5 rounded-full bg-indigo-500 animate-pulse"></span> Local Server';
                badge.className = "text-[10px] font-semibold text-indigo-400 flex items-center gap-1 cursor-pointer";
                searchMode = 'semantic';
                updateSearchModeButtons();
                return true;
            }
            
            badge.innerHTML = '<span class="h-1.5 w-1.5 rounded-full bg-rose-500"></span> API: Offline';
            badge.className = "text-[10px] font-medium text-slate-500 flex items-center gap-1 cursor-pointer";
            searchMode = 'keyword';
            updateSearchModeButtons();
            return false;
        }

        function selectProperty(index) {
            const p = propertiesData[index];
            
            document.getElementById('details-placeholder').classList.add('hidden');
            const card = document.getElementById('detail-card');
            card.classList.remove('hidden');
            
            document.getElementById('detail-title').innerText = p.title;
            document.getElementById('detail-city').innerText = p.city;
            document.getElementById('detail-desc').innerText = p.description;
            document.getElementById('detail-area').innerText = `${p.area} m²`;
            
            const formattedPrice = p.listing_type === 'sale' 
                ? `${p.price.toLocaleString()} TND` 
                : `${p.price.toLocaleString()} TND/mo`;
            document.getElementById('detail-price').innerText = formattedPrice;
            
            const typeBadge = document.getElementById('detail-type');
            typeBadge.innerText = p.property_type;
            
            let typeColor = 'bg-slate-700 text-slate-100';
            if (p.property_type === 'villa') typeColor = 'bg-rose-500/20 text-rose-300 border border-rose-500/30';
            else if (p.property_type === 'apartment') typeColor = 'bg-blue-500/20 text-blue-300 border border-blue-500/30';
            else if (p.property_type === 'house') typeColor = 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30';
            else if (p.property_type === 'studio') typeColor = 'bg-purple-500/20 text-purple-300 border border-purple-500/30';
            typeBadge.className = `px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${typeColor}`;
            
            const listingBadge = document.getElementById('detail-listing');
            listingBadge.innerText = p.listing_type === 'sale' ? 'FOR SALE' : 'FOR RENT';
            listingBadge.className = p.listing_type === 'sale'
                ? 'px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-pink-500/20 text-pink-300 border border-pink-500/30'
                : 'px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-teal-500/20 text-teal-300 border border-teal-500/30';
        }
    </script>
</body>
</html>
"""

def generate_visualization(properties, coords_pca, coords_tsne, pca_variance, tsne_perplexity, pca_mean, pca_components, property_embeddings, gemini_api_key):
    """Integrates coordinates into the HTML template and writes it to a file."""
    processed_properties = []
    for i, p in enumerate(properties):
        p_data = p.copy()
        p_data["pca"] = coords_pca[i].tolist()
        p_data["tsne"] = coords_tsne[i].tolist()
        processed_properties.append(p_data)
        
    pca_stats = {
        "explained_variance": pca_variance
    }
    
    tsne_stats = {
        "perplexity": tsne_perplexity
    }
    
    # Inject data into template
    html_content = HTML_TEMPLATE.replace("_DATA_PLACEHOLDER_", json.dumps(processed_properties))
    html_content = html_content.replace("_PCA_STATS_", json.dumps(pca_stats))
    html_content = html_content.replace("_TSNE_STATS_", json.dumps(tsne_stats))
    html_content = html_content.replace("_PCA_MEAN_", json.dumps(pca_mean))
    html_content = html_content.replace("_PCA_COMPONENTS_", json.dumps(pca_components))
    html_content = html_content.replace("_PROPERTY_EMBEDDINGS_", json.dumps(property_embeddings))
    html_content = html_content.replace("_GEMINI_API_KEY_", json.dumps(gemini_api_key))
    
    output_filename = "real_estate_embeddings_3d.html"
    output_path_file = os.path.join(os.getcwd(), output_filename)
    
    with open(output_path_file, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"\n[DONE] Visualizer generated successfully!")
    print(f"[DONE] Output dashboard file: {output_path_file}")
    return output_path_file

# ------------------------------------------------------------------------------
# 5. Synthetic Data Generator (Demo Mode Fallback)
# ------------------------------------------------------------------------------
def generate_synthetic_data():
    """Generates synthetic properties and embeddings for demo purposes."""
    print("[DEMO] Generating synthetic property data and embeddings...")
    
    cities = ["Gammarth", "Sidi Bou Said", "Hammamet", "Lac 2", "La Marsa", "Bizerte", "Carthage"]
    property_types = ["villa", "apartment", "house", "studio"]
    listing_types = ["sale", "rent"]
    
    titles_templates = {
        "villa": [
            "Ocean Breeze Mansion", "Mediterranean Dream Estate", "Golden Sands Villa", 
            "Carthage Heritage House", "Olive Grove Retreat", "Desert Rose Villa",
            "Azure Coast Villa", "Lavender Fields Estate"
        ],
        "apartment": [
            "Blue Horizon Penthouse", "Urban Oasis Lofts", "Emerald Garden Apartment",
            "Sapphire Bay Residence", "Skyline Business Suite", "Palm Grove Apartment",
            "Roman Ruins View Apartment", "Old Port Studio", "Central Park Residence",
            "Modern Tech Loft"
        ],
        "house": [
            "Coral Reef Cottage", "Mountain Peak Lodge", "Sun-Kissed Bungalow", 
            "Historic Medina Mansion", "Jasmine Valley Estate"
        ],
        "studio": [
            "Minimalist Urban Studio", "Cozy Lakeside Studio", "Downtown Artist Loft"
        ]
    }
    
    descriptions = {
        "villa": "Luxurious spacious beachfront property with private infinity pool, large garden, garage, smart home features, and panoramic sea views.",
        "apartment": "Modern contemporary penthouse loft in downtown business district with high-speed internet, elevator access, fitness center, and terrace.",
        "house": "Charming historical family house with traditional architecture, central heating, garden courtyard, and proximity to city ruins.",
        "studio": "Compact cozy studio apartment perfect for students and professionals, fully furnished, close to public transport."
    }
    
    np.random.seed(42)
    properties = []
    embeddings = []
    
    # Generate 45 synthetic properties
    for i in range(45):
        prop_type = np.random.choice(property_types)
        listing_type = np.random.choice(listing_types)
        city = np.random.choice(cities)
        
        # Get a title template
        titles = titles_templates[prop_type]
        title = titles[i % len(titles)]
        title = f"{title} #{i+101}"
        
        # Price calculations
        if prop_type == "villa":
            base_price = 1200000 if listing_type == "sale" else 4500
        elif prop_type == "apartment":
            base_price = 320000 if listing_type == "sale" else 2200
        elif prop_type == "house":
            base_price = 550000 if listing_type == "sale" else 1800
        else: # studio
            base_price = 120000 if listing_type == "sale" else 950
            
        price = base_price * np.random.uniform(0.8, 1.4)
        
        # Area calculations
        if prop_type == "villa":
            area = np.random.uniform(350, 950)
        elif prop_type == "apartment":
            area = np.random.uniform(90, 240)
        elif prop_type == "house":
            area = np.random.uniform(120, 400)
        else: # studio
            area = np.random.uniform(35, 75)
            
        desc = f"{descriptions[prop_type]} Located in the premium district of {city}."
        
        properties.append({
            "id": i + 1,
            "title": title,
            "price": round(price, -2 if price > 10000 else 0),
            "property_type": prop_type,
            "listing_type": listing_type,
            "city": city,
            "description": desc,
            "area": round(area, 1)
        })
        
        # Generate synthetic 768D vector with semantic clustering characteristics
        vec = np.random.normal(0, 0.05, 768)
        
        # Cluster properties based on type (simulates semantic features)
        if prop_type == "villa":
            vec[0:150] += 0.3
        elif prop_type == "apartment":
            vec[150:300] += 0.3
        elif prop_type == "house":
            vec[300:450] += 0.3
        elif prop_type == "studio":
            vec[450:600] += 0.3
            
        # Cluster properties based on listing type
        if listing_type == "sale":
            vec[600:680] += 0.15
        else:
            vec[680:768] += 0.15
            
        embeddings.append(vec.tolist())
        
    print(f"[DEMO] Created {len(properties)} synthetic properties across 4 semantic clusters.")
    return properties, np.array(embeddings)

# ------------------------------------------------------------------------------
# 6. HTTP Server Helpers & Handlers
# ------------------------------------------------------------------------------
def find_free_port(start_port=8050):
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                port += 1

def get_query_embedding_local(text, env):
    """
    Attempts to get query embedding using Ollama nomic-embed-text.
    Tries OLLAMA_HOST from environment first, then common addresses.
    """
    import requests
    ollama_host_env = env.get("OLLAMA_HOST", "localhost")
    hosts_to_try = [ollama_host_env, "localhost", "127.0.0.1", "host.docker.internal"]
    
    # Remove duplicates preserving order
    seen = set()
    hosts = []
    for h in hosts_to_try:
        if h not in seen:
            seen.add(h)
            hosts.append(h)
            
    for host in hosts:
        clean_host = host.replace("http://", "").replace("https://", "").split(":")[0]
        url = f"http://{clean_host}:11434/api/embeddings"
        try:
            response = requests.post(
                url,
                json={"model": "nomic-embed-text", "prompt": text},
                timeout=1.5
            )
            if response.status_code == 200:
                return response.json()["embedding"]
        except Exception:
            continue
            
    return None

class VisualizerHTTPHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress request logging to keep console clean
        pass
        
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        # 1. Serve dashboard file
        if parsed_path.path in ["/", "/index.html", "/real_estate_embeddings_3d.html"]:
            try:
                with open(output_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(content.encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error reading dashboard file: {e}".encode("utf-8"))
                
        # 2. Local search API endpoint
        elif parsed_path.path == "/api/search":
            query_params = urllib.parse.parse_qs(parsed_path.query)
            query_text = query_params.get("query", [""])[0]
            
            if not query_text:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing query parameter")
                return
                
            try:
                query_vector = get_query_embedding_local(query_text, env_vars)
                is_synthetic = False
                
                if query_vector is None:
                    is_synthetic = True
                    query_vector = np.random.normal(0, 0.05, 768)
                    query_text_lower = query_text.lower()
                    if "villa" in query_text_lower:
                        query_vector[0:150] += 0.3
                    elif "apartment" in query_text_lower:
                        query_vector[150:300] += 0.3
                    elif "house" in query_text_lower:
                        query_vector[300:450] += 0.3
                    elif "studio" in query_text_lower:
                        query_vector[450:600] += 0.3
                    if "sale" in query_text_lower or "buy" in query_text_lower:
                        query_vector[600:680] += 0.15
                    elif "rent" in query_text_lower:
                        query_vector[680:768] += 0.15
                else:
                    query_vector = np.array(query_vector)
                    
                # Project query embedding using fitted PCA
                pca_coords = pca_model.transform([query_vector])[0].tolist()
                
                # Interpolate query embedding using K-NN in t-SNE space
                dists = np.linalg.norm(embeddings_data - query_vector, axis=1)
                k = min(5, len(dists))
                nearest_indices = np.argsort(dists)[:k]
                nearest_dists = dists[nearest_indices]
                
                # Weight by inverse distance
                weights = 1.0 / (nearest_dists + 1e-8)
                weights /= np.sum(weights)
                
                tsne_coords = np.sum(coords_tsne_data[nearest_indices] * weights[:, np.newaxis], axis=0).tolist()
                
                # Compute Cosine Similarity for search ranking
                dot_products = np.dot(embeddings_data, query_vector)
                norms = np.linalg.norm(embeddings_data, axis=1) * np.linalg.norm(query_vector)
                similarities = dot_products / (norms + 1e-8)
                
                if is_synthetic:
                    words = [w.strip() for w in query_text.lower().split() if len(w.strip()) > 2]
                    for i, prop in enumerate(properties_data):
                        title_desc = (prop["title"] + " " + prop["description"]).lower()
                        match_count = sum(1 for w in words if w in title_desc)
                        if match_count > 0:
                            similarities[i] += 0.15 * match_count
                    similarities = np.clip(similarities, -1.0, 1.0)
                    
                top_indices = np.argsort(similarities)[::-1]
                matches = []
                for idx in top_indices:
                    prop = properties_data[idx]
                    matches.append({
                        "id": prop["id"],
                        "similarity": float(similarities[idx]),
                        "title": prop["title"],
                        "price": prop["price"],
                        "city": prop["city"],
                        "area": prop["area"],
                        "property_type": prop["property_type"],
                        "listing_type": prop["listing_type"]
                    })
                    
                response_payload = {
                    "query_coords": {
                        "pca": pca_coords,
                        "tsne": tsne_coords
                    },
                    "query_vector": query_vector.tolist(),
                    "matches": matches,
                    "mode": "synthetic" if is_synthetic else "real"
                }
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(response_payload).encode("utf-8"))
                
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Search failed: {e}".encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

# ------------------------------------------------------------------------------
# 7. Execution Main Block
# ------------------------------------------------------------------------------
def main():
    global properties_data, embeddings_data, pca_model, coords_tsne_data, env_vars, output_path
    
    print("====================================================")
    print("  Elite Estate: 3D pgvector Embedding Visualizer    ")
    print("====================================================\n")
    
    use_demo = "--demo" in sys.argv
    properties = []
    embeddings = None
    env = {}
    
    if use_demo:
        properties, embeddings = generate_synthetic_data()
    else:
        try:
            env = load_env()
            conn = get_db_connection(env)
            properties, embeddings = fetch_properties_data(conn)
            conn.close()
        except Exception as e:
            print(f"\n[INFO] Database connection or query failed: {e}")
            print("\nSuggestions to connect to your real database:")
            print("  1. Make sure your Docker container 'real_estate_db' is running (docker ps).")
            print("  2. Ensure PostgreSQL port 5432 is mapped in docker-compose.yml.")
            print("  3. Run the database seed script: docker exec -it FastAPI_backend python seed.py")
            print("  4. Check your .env configuration file.")
            print("\n[INFO] Starting DEMO mode with synthetic embeddings so you can try the visualizer immediately!")
            print("--------------------------------------------------------------------------------\n")
            properties, embeddings = generate_synthetic_data()
            
    if len(properties) < 3:
        print("[ERROR] Need at least 3 property embeddings to compute a 3D projection.")
        sys.exit(1)
        
    coords_pca, coords_tsne, pca_variance, tsne_perplexity, pca = perform_dimensionality_reduction(embeddings)
    
    # Load env for visualizer configuration
    if not env:
        env = load_env()
        
    gemini_api_key = env.get("GEMINI_API_KEY", "")
    
    output_file = generate_visualization(
        properties=properties, 
        coords_pca=coords_pca, 
        coords_tsne=coords_tsne, 
        pca_variance=pca_variance, 
        tsne_perplexity=tsne_perplexity,
        pca_mean=pca.mean_.tolist(),
        pca_components=pca.components_.tolist(),
        property_embeddings=embeddings.tolist(),
        gemini_api_key=gemini_api_key
    )
    
    # Assign global variables for server handler
    properties_data = properties
    embeddings_data = embeddings
    pca_model = pca
    coords_tsne_data = coords_tsne
    env_vars = env
    output_path = output_file
    
    # Start local HTTP server
    port = find_free_port(8051)
    print(f"\n[SERVER] Starting local visualizer server on http://localhost:{port}...")
    
    # Use a custom threaded server so it performs cleanly
    class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
        allow_reuse_address = True
        
    server = ThreadingHTTPServer(("127.0.0.1", port), VisualizerHTTPHandler)
    
    # Open dashboard in system default browser
    print(f"[SERVER] Opening dashboard in browser: http://localhost:{port}")
    webbrowser.open(f"http://localhost:{port}")
    
    print("\n------------------------------------------------------------")
    print(f" Dashboard is running on: http://localhost:{port}")
    print(" Press Ctrl+C to stop the local server and exit.")
    print("------------------------------------------------------------\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[SERVER] Stopping local server...")
        server.shutdown()
        server.server_close()
        print("[SERVER] Server stopped. Goodbye!")

if __name__ == "__main__":
    main()
