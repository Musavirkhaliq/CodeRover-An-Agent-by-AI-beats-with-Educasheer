
# 🤖 Coding Agent with Memory and RL

This project implements a **coding agent** that can:
- Use **memory** (including a neural network–based memory store).
- Learn better workflows via **Reinforcement Learning (RL)**.
- Orchestrate between **tools**, a **decision-making LLM**, and a **code-writing LLM**.
- Continuously improve how it selects **which workflow** and **which memories** to use.


## 📂 Project Structure


```markdown
coding-agent/
│── README.md
│── requirements.txt
│── setup.py
│── .env
│
│── configs/             # YAML configs for agent, memory, RL
│── data/
│   ├── memory\_store/    # persisted memory
│   ├── logs/            # execution logs
│   └── datasets/        # training datasets
│
│── src/
│   ├── orchestrator/    # high-level agent controller
│   ├── llms/            # orchestrator + code writer LLMs
│   ├── memory/          # memory NN, retriever, vector DB
│   ├── rl/              # RL environment, trainer, policy
│   ├── tools/           # modular tools (search, executor, etc.)
│   ├── utils/           # logging, config loader, metrics
│   └── main.py          # entry point
│
└── tests/               # unit tests

```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/coding-agent.git
cd coding-agent
````

### 2. Set up environment

```bash
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

* Copy `.env.example` → `.env`
* Add keys for your LLM provider (e.g., OpenAI, Anthropic, local LLaMA)

```env
OPENAI_API_KEY=your_key_here
```

---

## 🧠 Components

### Orchestrator

The **brain** of the system.

* Plans workflows.
* Decides which memory and tools to use.

### Memory

* **Neural network–based memory** for storing context.
* **Vector store** for fast retrieval.
* Helps agent reuse past experiences.

### LLMs
### 🚀 Enhanced Capabilities
- 🧩 **Dual-LLM orchestration** for better division of reasoning and execution.  
- 🎛️ **Multi-temperature generation** (`0.3 / 0.7 / 1.0`) for controlled creativity.  
- 🔍 **Automatic output comparison** for best result selection.  
- ⚙️ **Flexible integration** via `llm_factory.py` for multiple model backends.  
- 🧠 **Improved testing suite** covering LLM, memory, and orchestrator modules.

---
# ⚡️ New Updates — Dual-LLM Orchestration & Multi-Temperature Code Generation

### 🧠 Dual-Model Setup
The project now integrates **two powerful LLM components**:
- **Orchestrator LLM** – handles reasoning, planning, and coordination.
- **Code Writer LLM** – generates, tests, and refines executable code.

Each execution generates **three code outputs** using different **temperature values**:
- `0.3` → precise and deterministic  
- `0.7` → balanced between accuracy and creativity  
- `1.0` → highly creative and exploratory  

The system then **compares all three results** and automatically selects the **best-performing output**.
### 🧪 Example Run
```bash
python run.py
```
This triggers the orchestrator to:
1. Call the **Orchestrator LLM** for task reasoning.  
2. Use the **Code Writer LLM** to generate code at 3 temperatures.  
3. Compare outputs and select the **most optimal one**.

### Tools

* Sandbox code executor.
* File manager.
* Web/document search.
* Extendable with custom tools.

### RL Training

* Defines environment (`environment.py`)
* Optimizes policy for **workflow selection** and **memory usage**.

---

## 🛠 Usage

Run the agent:

```bash
python src/main.py
```

Train with RL:

```bash
python src/rl/trainer.py
```

Run tests:

```bash
pytest tests/
```

---

## 🧪 Roadmap

* [ ] Implement basic orchestrator loop.
* [ ] Add memory NN integration.
* [ ] RL-based workflow optimization.
* [ ] Expand toolset (web search, debugging assistant).
* [ ] Add persistence layer for long-term memory.

---

## 🤝 Contributing

1. Fork the repo.
2. Create a feature branch: `git checkout -b feature/my-feature`.
3. Commit changes: `git commit -m "Add feature"`.
4. Push and open a Pull Request.

---

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.

```
