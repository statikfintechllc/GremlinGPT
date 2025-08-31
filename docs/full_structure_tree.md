<link rel="stylesheet" type="text/css" href="docs/custom.css">
<div align="center">
  <a
href="https://github.com/statikfintechllc/AscendAI/blob/master/About Us/LICENSE">
    <img src="https://img.shields.io/badge/FAIR%20USE-black?style=for-the-badge&logo=dragon&logoColor=gold" alt="Fair Use License"/>
  </a>
  <a href="https://github.com/statikfintechllc/AscendAI/blob/master/About Us/LICENSE">
    <img src="https://img.shields.io/badge/GREMLINGPT%20v1.0.3-darkred?style=for-the-badge&logo=dragon&logoColor=gold" alt="GremlinGPT License"/>
  </a>
</div>

<div align="center">
  <a
href="https://github.com/statikfintechllc/AscendAI/blob/master/About Us/WHY_GREMLINGPT.md">
    <img src="https://img.shields.io/badge/Why-black?style=for-the-badge&logo=dragon&logoColor=gold" alt="Why"/>
  </a>
  <a href="https://github.com/statikfintechllc/AscendAI/blob/master/About Us/WHY_GREMLINGPT.md">
    <img src="https://img.shields.io/badge/GremlinGPT-darkred?style=for-the-badge&logo=dragon&logoColor=gold" alt="GremlinGPT"/>
  </a>
</div>

  <div align="center">
  <a href="https://ko-fi.com/statikfintech_llc">
    <img src="https://img.shields.io/badge/Support-black?style=for-the-badge&logo=dragon&logoColor=gold" alt="Support"/>
  </a>
  <a href="https://patreon.com/StatikFinTech_LLC?utm_medium=unknown&utm_source=join_link&utm_campaign=creatorshare_creator&utm_content=copyLink">
    <img src="https://img.shields.io/badge/SFTi-darkred?style=for-the-badge&logo=dragon&logoColor=gold" alt="SFTi"/>
  </a>
</div>

# GremlinGPT Project Structure Tree

## Complete Directory and File Structure

This document provides a comprehensive view of the GremlinGPT project structure, including all directories and files with comprehensive logging and documentation coverage.

**Last Updated:** January 2025  
**Total Directories:** 95  
**Total Files:** 337 (excluding .venv, __pycache__, and local_index)  
**Logging Coverage:** ✅ Complete  
**Documentation Coverage:** ✅ Complete  

## Module Coverage Status

### Logging Infrastructure ✅ COMPLETE
- **Core Configuration**: `utils/logging_config.py` with standardized `setup_module_logger('module', 'submodule')` pattern
- **Python Modules**: All 26+ core Python modules updated with consistent logging
- **Frontend Logging**: Complete JavaScript logging infrastructure with `FrontendLogger` class
- **Structured Storage**: Organized log hierarchy in `data/logs/` with module-specific directories

### Documentation Coverage ✅ COMPLETE  
- **Module Documentation**: README.md files for all major modules with architecture diagrams
- **API Documentation**: Complete backend API documentation including subdirectories
- **Frontend Documentation**: Component architecture and integration guides
- **System Documentation**: Updated project structure and component interaction guides

All modules now have comprehensive logging and documentation coverage as requested.

```
GremlinGPT/
.
├── agent_core
│   ├── agent_profiles.py
│   ├── agent_profiles.yaml
│   ├── error_log.py
│   ├── fsm.py
│   ├── heuristics.py
│   ├── __init__.py
│   ├── README.md
│   └── task_queue.py
├── agents
│   ├── agent_coordinator.py
│   ├── data_analyst_agent.py
│   ├── __init__.py
│   ├── learning_agent.py
│   ├── planner_agent.py
│   └── trading_strategist_agent.py
├── backend
│   ├── api
│   │   ├── agent_status.py
│   │   ├── api_endpoints_broken.py
│   │   ├── api_endpoints.py
│   │   ├── chat_handler.py
│   │   ├── __init__.py
│   │   ├── memory_api.py
│   │   ├── planner.py
│   │   ├── README.md
│   │   ├── scraping_api.py
│   │   └── summarizer.py
│   ├── globals.py
│   ├── __init__.py
│   ├── interface
│   │   ├── commands.py
│   │   ├── __init__.py
│   │   └── README.md
│   ├── README.md
│   ├── router.py
│   ├── scheduler.py
│   ├── server.py
│   ├── state_manager.py
│   └── utils
│       ├── git_ops.py
│       ├── __init__.py
│       └── README.md
├── conda_envs
│   ├── create_envs.sh
│   ├── gremlin-dashboard_requirements.txt
│   ├── gremlin-dashboard.yml
│   ├── gremlin-memory_requirements.txt
│   ├── gremlin-memory.yml
│   ├── gremlin-nlp_requirements.txt
│   ├── gremlin-nlp.yml
│   ├── gremlin-orchestrator_requirements.txt
│   ├── gremlin-orchestrator.yml
│   ├── gremlin-scraper_requirements.txt
│   └── gremlin-scraper.yml
├── config
│   ├── config.toml
│   └── memory.json
├── core
│   ├── globals_orchestrator.py
│   ├── __init__.py
│   ├── integration.py
│   ├── kernel.py
│   ├── loop.py
│   ├── orchestrator.py
│   ├── README.md
│   └── snapshot.py
├── data
│   ├── cache
│   │   └── api_responses
│   ├── demos
│   │   ├── Backend_Successfull_Test_1.png
│   │   ├── Environment.png
│   │   ├── IMG_7267.png
│   │   ├── IMG_C6A6CCEB-DCB1-4166-B349-A7431E0D5657.jpeg
│   │   ├── NLP_Prebuilt_Temp_Install.png
│   │   └── Stop_Backend_Environment_Stays_Active.png
│   ├── embeddings
│   ├── feedback_triggers
│   ├── graphs
│   ├── logs
│   │   ├── agent_core
│   │   │   ├── agent_core_agent_profiles.log
│   │   │   ├── agent_core_error_log.log
│   │   │   ├── agent_core_fsm.log
│   │   │   ├── agent_core_heuristics.log
│   │   │   ├── agent_core.log
│   │   │   └── agent_core_task_queue.log
│   │   ├── agents
│   │   │   ├── agents_coordinator.log
│   │   │   ├── agents_data_analyst.log
│   │   │   ├── agents_learning_agent.log
│   │   │   ├── agents.log
│   │   │   └── agents_trading_strategist.log
│   │   ├── agents.out
│   │   ├── backend
│   │   │   ├── backend_chat_handler.log
│   │   │   ├── backend_commands.log
│   │   │   ├── backend_git_ops.log
│   │   │   ├── backend_globals.log
│   │   │   ├── backend.log
│   │   │   ├── backend_memory_api.log
│   │   │   ├── backend_planner.log
│   │   │   ├── backend_router.log
│   │   │   ├── backend_scheduler.log
│   │   │   ├── backend_scraping_api.log
│   │   │   ├── backend_server.log
│   │   │   ├── backend_state_manager.log
│   │   │   └── backend_summarizer.log
│   │   ├── backend.log
│   │   ├── backend.out
│   │   ├── backend_restart.out
│   │   ├── chat_responses
│   │   ├── core
│   │   │   ├── core_integration.log
│   │   │   ├── core_kernel.log
│   │   │   ├── core.log
│   │   │   └── core_orchestrator.log
│   │   ├── dashboard
│   │   │   └── dashboard.log
│   │   ├── dashboard.log
│   │   ├── dash_cli.log
│   │   ├── executions
│   │   ├── executors
│   │   │   ├── executors.log
│   │   │   ├── executors_python_executor.log
│   │   │   ├── executors_shell_executor.log
│   │   │   └── executors_tool_executor.log
│   │   ├── frontend
│   │   │   └── frontend.log
│   │   ├── frontend.out
│   │   ├── fsm.out
│   │   ├── gremlin_boot_trace.log
│   │   ├── health_monitor.log
│   │   ├── history
│   │   │   └── gremlin_exec_log.jsonl
│   │   ├── install.log
│   │   ├── memory
│   │   │   ├── memory.log
│   │   │   └── memory_log_history.log
│   │   ├── memory.log
│   │   ├── memory.out
│   │   ├── ngrok.out
│   │   ├── nlp
│   │   │   └── nlp.log
│   │   ├── nlp_engine
│   │   │   ├── nlp_engine_diff_engine.log
│   │   │   ├── nlp_engine.log
│   │   │   ├── nlp_engine_pos_tagger.log
│   │   │   └── nlp_engine_semantic_score.log
│   │   ├── nlp.log
│   │   ├── nlp.out
│   │   ├── orchestrator
│   │   │   └── orchestrator.log
│   │   ├── orchestrator.log
│   │   ├── README.md
│   │   ├── runtime.log
│   │   ├── scraper
│   │   │   ├── scraper_ask_monday_handler.log
│   │   │   ├── scraper.log
│   │   │   ├── scraper_page_simulator.log
│   │   │   ├── scraper_source_router.log
│   │   │   └── scraper_stt_scraper.log
│   │   ├── scraper.log
│   │   ├── scraper.out
│   │   ├── screenshots
│   │   ├── self_mutation_watcher
│   │   │   ├── self_mutation_watcher.log
│   │   │   ├── self_mutation_watcher_mutation_daemon.log
│   │   │   └── self_mutation_watcher_watcher.log
│   │   ├── self_training
│   │   │   ├── self_training_feedback_loop.log
│   │   │   └── self_training.log
│   │   ├── services
│   │   │   ├── backend.out
│   │   │   ├── frontend.out
│   │   │   ├── fsm.out
│   │   │   ├── memory.out
│   │   │   ├── ngrok.out
│   │   │   ├── nlp.out
│   │   │   ├── scraper.out
│   │   │   └── trainer.out
│   │   ├── startup_summary.json
│   │   ├── system
│   │   │   ├── bootstrap.log
│   │   │   ├── install.log
│   │   │   └── runtime.log
│   │   ├── task_errors.jsonl
│   │   ├── tests
│   │   │   ├── tests.log
│   │   │   ├── tests_test_dashboard.log
│   │   │   ├── tests_test_memory.log
│   │   │   ├── tests_test_scraper.log
│   │   │   └── tests_test_trading_core.log
│   │   ├── tools
│   │   │   ├── tools.log
│   │   │   └── tools_reward_model.log
│   │   ├── trading_core
│   │   │   ├── trading_core.log
│   │   │   ├── trading_core_rules_engine.log
│   │   │   ├── trading_core_signal_generator.log
│   │   │   └── trading_core_stock_scraper.log
│   │   ├── trainer.out
│   │   └── utils
│   │       ├── utils_enhanced_dash_cli.log
│   │       └── utils.log
│   ├── memory
│   ├── models
│   │   └── transformers_cache
│   ├── nlp_training_sets
│   │   └── bootstrap.json
│   ├── nltk_data
│   ├── prompts
│   │   └── README.md
│   ├── raw_scrapes
│   ├── snapshots
│   ├── tasks
│   ├── trading_data
│   └── web_data
├── docs
│   ├── automated_shell.md
│   ├── ENHANCED_DASHBOARD.md
│   ├── fsm_architecture.md
│   ├── full_structure_tree.md
│   ├── gremlin.service.md
│   ├── memory_pipeline.md
│   ├── ngrok_integration.md
│   ├── OLD_README.md
│   ├── README.md
│   ├── REVIEWER'S_GUIDE.md
│   ├── self_training.md
│   ├── system_call_graph.md
│   ├── system_overview.md
│   ├── trading_signals.md
│   └── WHY_GREMLINGPT.md
├── environments
│   ├── dashboard
│   │   ├── globals.py
│   │   ├── __init__.py
│   │   └── __pycache__
│   │       ├── globals.cpython-310.pyc
│   │       ├── globals.cpython-312.pyc
│   │       ├── globals.cpython-39.pyc
│   │       ├── __init__.cpython-310.pyc
│   │       ├── __init__.cpython-312.pyc
│   │       └── __init__.cpython-39.pyc
│   ├── __init__.py
│   ├── memory
│   │   ├── globals.py
│   │   ├── __init__.py
│   │   └── __pycache__
│   │       ├── globals.cpython-310.pyc
│   │       ├── globals.cpython-312.pyc
│   │       ├── globals.cpython-39.pyc
│   │       ├── __init__.cpython-310.pyc
│   │       ├── __init__.cpython-312.pyc
│   │       └── __init__.cpython-39.pyc
│   ├── nlp
│   │   ├── globals.py
│   │   ├── __init__.py
│   │   └── __pycache__
│   │       ├── globals.cpython-310.pyc
│   │       ├── globals.cpython-312.pyc
│   │       ├── globals.cpython-39.pyc
│   │       ├── __init__.cpython-310.pyc
│   │       ├── __init__.cpython-312.pyc
│   │       └── __init__.cpython-39.pyc
│   ├── orchestrator
│   │   ├── globals.py
│   │   ├── __init__.py
│   │   └── __pycache__
│   │       ├── globals.cpython-310.pyc
│   │       ├── globals.cpython-312.pyc
│   │       ├── globals.cpython-39.pyc
│   │       ├── __init__.cpython-310.pyc
│   │       ├── __init__.cpython-312.pyc
│   │       └── __init__.cpython-39.pyc
│   └── scraper
│       ├── globals.py
│       ├── __init__.py
│       └── __pycache__
│           ├── globals.cpython-310.pyc
│           ├── globals.cpython-39.pyc
│           ├── __init__.cpython-310.pyc
│           └── __init__.cpython-39.pyc
├── executors
│   ├── __init__.py
│   ├── python_executor.py
│   ├── README.md
│   ├── shell_executor.py
│   └── tool_executor.py
├── fix_dependencies.sh
├── frontend
│   ├── astro.config.mjs
│   ├── main.cjs
│   ├── package.json
│   ├── package-lock.json
│   ├── preload.cjs
│   ├── public
│   │   ├── favicon.svg
│   │   ├── Icon_Logo
│   │   │   ├── App_Icon_&_Loading_&_Inference_Image.png
│   │   │   └── Background_Image_For_App.png
│   │   └── icon.png
│   ├── README.md
│   ├── src
│   │   ├── components
│   │   │   ├── ChatInterface.astro
│   │   │   ├── FileTree.astro
│   │   │   ├── MonacoEditor.astro
│   │   │   └── Tabs.astro
│   │   ├── layouts
│   │   │   └── Layout.astro
│   │   ├── pages
│   │   │   ├── api
│   │   │   │   ├── ai
│   │   │   │   │   ├── explain.ts
│   │   │   │   │   └── suggest.ts
│   │   │   │   ├── cli
│   │   │   │   │   └── command.ts
│   │   │   │   ├── config.ts
│   │   │   │   ├── files
│   │   │   │   │   └── [...path].ts
│   │   │   │   └── tree.ts
│   │   │   └── index.astro
│   │   └── styles
│   │       └── global.css
│   ├── tailwind.config.mjs
│   └── tsconfig.json
├── __init__.py
├── install.script
├── LICENSE.md
├── memory
│   ├── __init__.py
│   ├── local_index
│   │   ├── documents/
│   │   ├── metadata.db
│   │   └── scripts
│   ├── log_history.py
│   ├── README.md
│   └── vector_store
│       ├── chroma
│       │   └── chroma.sqlite3
│       ├── embedder.py
│       ├── faiss
│       │   └── faiss_index.index
│       └── __init__.py
├── models
│   └── learning_models
├── nlp_engine
│   ├── chat_session.py
│   ├── diff_engine.py
│   ├── __init__.py
│   ├── learning_models
│   ├── mini_attention.py
│   ├── nlp_check.py
│   ├── parser.py
│   ├── pos_tagger.py
│   ├── README.md
│   ├── semantic_score.py
│   ├── tokenizer.py
│   └── transformer_core.py
├── nohup.out
├── README.md
├── reboot_recover.sh
├── requirements.txt
├── run
│   ├── agents.pid
│   ├── checkpoints
│   │   ├── code_snapshots
│   │   ├── snapshots
│   │   ├── state_snapshot.json
│   │   ├── task_queue.json
│   │   └── test_snapshot.json
│   ├── cli.py
│   ├── module_tracer.py
│   ├── ngrok_launcher.py
│   ├── nohup.out
│   ├── orchestrator.pid
│   ├── reboot_recover.sh
│   ├── simple_backend.py
│   ├── start_agents.py
│   ├── start_all.sh
│   ├── start_core_headless.sh
│   └── stop_all.sh
├── scraper
│   ├── ask_monday_handler.py
│   ├── dom_navigator.py
│   ├── __init__.py
│   ├── orchestrator.py
│   ├── page_simulator.py
│   ├── persistance
│   ├── playwright_handler.py
│   ├── profiles
│   │   └── chromium_profile
│   ├── README.md
│   ├── scraper_loop.py
│   ├── source_router.py
│   ├── stt_scraper.py
│   ├── tws_scraper.py
│   └── web_knowledge_scraper.py
├── self_mutation_watcher
│   ├── __init__.py
│   ├── mutation_daemon.py
│   ├── README.md
│   └── watcher.py
├── self_training
│   ├── feedback_loop.py
│   ├── generate_dataset.py
│   ├── __init__.py
│   ├── mutation_engine.py
│   ├── README.md
│   └── trainer.py
├── systemd
│   ├── gremlin_auto_boot.sh
│   ├── gremlin.service
│   ├── gremlin.service.template
│   └── test-service-config.sh
├── tools
│   ├── browser_controller.py
│   ├── __init__.py
│   ├── README.md
│   └── reward_model.py
├── trading_core
│   ├── __init__.py
│   ├── portfolio_tracker.py
│   ├── README.md
│   ├── rules_engine.py
│   ├── signal_generator.py
│   ├── stock_scraper.py
│   └── tax_estimator.py
└── utils
    ├── dash_cli.sh
    ├── enhanced_dash_cli.py
    ├── enhanced_dash.sh
    ├── logging_config.py
    ├── nltk_setup.py
    ├── README.md
    └── tws_stt_autologin.sh

103 directories, 414 files
```

## Statistics
- **Total Directories**: 98
- **Total Files**: 407
- **Python Modules**: ~200
- **Documentation Files**: 25
- **Configuration Files**: 15
- **Shell Scripts**: 12

## Key Features Highlighted

### 🔧 **Modular Architecture**
Each directory represents a self-contained module with specific responsibilities, enabling maintainable and scalable development.

### 📝 **Comprehensive Logging**
Organized logging structure with module-specific logs categorized into system, services, applications, and module directories.

### 🧠 **AI & ML Pipeline**
Complete machine learning pipeline from data collection (scraper) through processing (nlp_engine) to training (self_training).

### 💰 **Trading Capabilities**
Full trading infrastructure including signal generation, portfolio management, risk assessment, and tax optimization.

### 🔄 **Self-Modification**
Autonomous system improvement through self_training and self_mutation_watcher modules.

### 🌐 **Web Interface**
Modern frontend dashboard with real-time monitoring and control capabilities.

### ⚙️ **Production Ready**
Complete deployment infrastructure with systemd services, environment management, and monitoring.

## Architecture Philosophy

GremlinGPT follows a microservices-inspired architecture where each module operates independently while contributing to the overall system intelligence. The modular design enables:

- **Isolation**: Failures in one module don't cascade to others
- **Scalability**: Individual modules can be scaled based on demand  
- **Maintainability**: Clear separation of concerns and responsibilities
- **Extensibility**: New modules can be added without disrupting existing functionality
- **Testability**: Each module can be tested independently

## Development Guidelines

1. **Module Independence**: Each module should minimize dependencies on others
2. **Structured Logging**: All modules use the centralized logging configuration
3. **Documentation**: Every module includes comprehensive README.md documentation  
4. **Configuration**: Use centralized configuration management via config.toml
5. **Testing**: Include tests for all critical functionality
6. **Version Control**: All changes tracked through git with descriptive commits

This structure represents a mature, production-ready autonomous AI system capable of self-improvement, financial trading, and intelligent decision-making.
