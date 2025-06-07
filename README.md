

---

# 🧬 GeneHack AMR

**GeneHack AMR** is an interactive web platform for rapid identification of antimicrobial resistance (AMR) genes and data-driven antibiotic recommendations from bacterial genome sequences. It leverages NCBI BLAST, AI-powered reporting, and intuitive visualizations to empower researchers and clinicians in the fight against antibiotic resistance.

---

## 🚀 Features

- Upload or paste bacterial genome sequences (FASTA or raw DNA)
- Detect AMR genes using BLAST against NCBI databases
- Get AI-generated summary reports and antibiotic recommendations
- Explore results with interactive visualizations and tables
- Save and revisit previous analyses

---

## 🛠️ Setup Instructions

### 1. **Clone the Repository**

```bash
git clone https://github.com/yourusername/genehack-amr.git
cd genehack-amr
```

### 2. **Create and Activate a Virtual Environment**

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 4. **Set Up Environment Variables**

Create a `.env` file in the project root with your OpenAI API key:

```
OPENAI_API_KEY=sk-...
```

Or, set the environment variable in your shell before running the app.

### 5. **Run the Application**

```bash
streamlit run app.py
```
or
```bash
streamlit run app.py --server.address localhost --server.port 8501
```

The app will open in your browser at `http://localhost:8501`.

---

## 📂 Project Structure

```
.
├── app.py                  # Main Streamlit app
├── requirements.txt        # Python dependencies
├── utils/                  # Bioinformatics, AI, and visualization modules
├── data/                   # Database and AMR data utilities
├── .streamlit/             # Streamlit configuration
├── genehack.db             # Local database (auto-created)
└── README.md
```

---

## 🧑‍🔬 Usage

1. Upload a FASTA file or paste a DNA sequence in the sidebar.
2. Click "Analyze Sequence" to run BLAST and AI-powered analysis.
3. Review predicted genes, protein sequences, and antibiotic recommendations in the results tabs.
4. Save your analysis for future reference.

---

## 🤝 Contributing

Contributions are welcome! Please open issues or pull requests for improvements, bug fixes, or new features.

---

## 📜 License

MIT License

---

**Empowering the scientific and medical community with rapid, AI-driven AMR analysis.**

---
