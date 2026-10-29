# AI Yako V7 — offline evidence milestone

This update adds a separate GUI and CLI; it does not modify V6, Django models, URLs or migrations.

Run on local Linux desktop:

    cd app_qvac_financial/clients/desktop/linux
    python3 -m unittest -v test_yako_v7.py
    python3 yako_v7_desktop.py
    python3 yako_v7_engine.py --scenario "urgent guaranteed leverage"

For a compatible llama.cpp-style GGUF CLI runner, specify --runner, --model and --model-sha256. The pinned digest checks model integrity, NOT authenticity; obtain the expected digest from a trusted independent source. The runner may execute arbitrary native code: only use trusted binaries. This generic adapter is NOT verified QVAC integration. The optional --isolate-network attempts a Linux network namespace and fails closed when unavailable; otherwise no offline network isolation is guaranteed. For an actual offline demonstration, disconnect network at the OS level and independently verify that the runner does not access the network. Do not share sensitive scenario data in reports. WDK and signing remain disabled. No model or runner is bundled or downloaded.
