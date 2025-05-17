# **Sakura Mangás Downloader**  

## **📌 Visão Geral**  
O **Sakura Mangás Downloader** é uma ferramenta Python para baixar mangás completos ou capítulos individuais do [sakuramangas.org](https://sakuramangas.org/).  

**Autor:** Etoshy  
**Repositório:** [github.com/etoshy/Sakura-Mangas-Downloader](https://github.com/etoshy/Sakura-Mangas-Downloader)  

---

## **📂 Estrutura de Arquivos**  
```
Sakura-Mangas-Downloader/  
│
├── code/  
│   ├── cap.py          # Baixa capítulos  
│   └── manga.py        # Extrai mangás completos  
│
├── menu.py             # Menu interativo  
│
└── mangas/             # Pasta de downloads  
    ├── [Nome do Mangá]/  
    │   ├── manga_info.json        # Metadados do mangá  
    │   ├── manga_caps.html        # Lista de capítulos (HTML)  
    │   ├── links_caps.json        # Links para download  
    │   └── [Número do Capítulo]/  
    │       ├── capitulo_info.json # Dados do capítulo  
    │       ├── capitulo_pages.json # Links das páginas  
    │       └── pages/  
    │           ├── 001.jpg       # Páginas baixadas  
    │           ├── 002.jpg  
    │           └── ...  
```

---

## **📜 Funcionamento dos Scripts**  

### **1. `menu.py` (Menu Principal)**  
🔹 **Opções:**  
- **1. Baixar Capítulo**  
  - Aceita:  
    - Links diretos (ex: `https://sakuramangas.org/ler/xxx`)  
    - Arquivos `links_caps.json` (gerados pelo `manga.py`)  
- **2. Baixar Mangá Completo**  
  - Aceita links de obras (ex: `https://sakuramangas.org/obras/xxx`)  
  - Gera estrutura com metadados + links para download futuro.  
- **3. Sair**  

🔹 **Fluxo Automático:**  
Após baixar um mangá, o menu **oferece baixar os capítulos** usando os `links_caps.json` gerados.  

---

### **2. `code/manga.py` (Download de Mangás Completos)**  
🔹 **O que faz:**  
- Extrai:  
  - Título, autor, sinopse (`manga_info.json`)  
  - Lista de capítulos (`links_caps.json`)  
- **Não baixa as páginas diretamente** (só prepara os links).  

🔹 **Como Usar:**  
```bash
python code/manga.py "https://sakuramangas.org/obras/nome-do-manga/"
```
🔹 **Saída:**  
```
mangas/  
└── [Nome do Mangá]/  
    ├── manga_info.json  
    ├── links_caps.json  
    └── ...  
```

---

### **3. `code/cap.py` (Download de Capítulos)**  
🔹 **O que faz:**  
- Baixa capítulos **via:**  
  - **Links diretos** (ex: `https://sakuramangas.org/ler/xxx`).  
  - **Arquivos JSON** (`links_caps.json` ou `capitulo_pages.json`).  
- Organiza em pastas numeradas com as páginas.  

🔹 **Estrutura Gerada:**  
```
mangas/Nome do Mangá/2/  
├── capitulo_info.json  
├── capitulo_pages.json  
└── pages/  
    ├── 001.jpg  
    ├── 002.jpg  
    └── ...  
```

🔹 **Modos de Uso:**  
1. **Via link direto:**  
```bash
python code/cap.py "https://sakuramangas.org/ler/cap-xxx"
```  
2. **Via `links_caps.json` (após `manga.py`):**  
```bash
python code/cap.py "mangas/Nome do Mangá/links_caps.json"
```  
3. **Baixar um capítulo específico via `capitulo_pages.json`:**  
```bash
python code/cap.py "mangas/Nome do Mangá/2/capitulo_pages.json"
```

---

## **🔍 SEO & Otimização**   
- "Baixar mangás Sakura completos"  
- "Sakura Mangás Downloader tutorial"  
- "Como baixar mangás de sakuramangas.org"  
- "Ferramenta Python para mangás offline"  

---

## **✅ Resumo das Funcionalidades**  
✔ **Menu interativo** (facilita o uso).  
✔ **Suporte a mangás completos + capítulos avulsos**.  
✔ **Gera JSONs** para continuar downloads depois.  
✔ **Estrutura organizada**:  
   - `manga_info.json` (dados da obra).  
   - `capitulo_info.json` (dados do capítulo).  
   - `pages/` (imagens numeradas).  

🔗 **GitHub:** [github.com/etoshy/Sakura-Mangas-Downloader](https://github.com/etoshy/Sakura-Mangas-Downloader)  

