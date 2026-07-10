#### can-uds-diagnostic-agent

AI diagnostic agent for simulated vehicle CAN/UDS traffic. Reads DTCs off a virtual ECU and explains them in plain English using a local LLM.

##### how it works

`ecu_sim.py` broadcasts fake engine signals on a real SocketCAN bus (`vcan0`). `uds_ecu.py` listens for UDS requests and responds like a real ECU would - Read Data by Identifier (0x22) and Read DTC (0x19). `diagnose.py` sends a DTC request over UDS, then feeds whatever comes back into a local Ollama model to explain it.

##### setup

Needs `vcan` kernel support, which the default WSL2 kernel doesn't have. I compiled a custom kernel with `CONFIG_CAN`/`CONFIG_CAN_VCAN` enabled to get this working.

```bash
sudo apt install can-utils zstd
pip install python-can cantools pytest ollama --break-system-packages
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2
```

```bash
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

##### running it

Three terminals:

```bash
python3 ecu_sim.py     # broadcasts RPM/coolant
python3 uds_ecu.py     # UDS responder
python3 diagnose.py    # reads DTC, explains it
```

##### tests

```bash
pytest -v
```

Covers the C codec (verified against a real captured frame), and both UDS services - positive and negative responses.

##### files

- `engine.dbc` - signal defs for RPM/coolant, based on OBD-II PID conventions
- `ecu_sim.py` - periodic ECU broadcast
- `can_codec.c` - native C encode/decode, verified against `cantools` output
- `test_can_codec.py` - pytest for the C codec
- `uds_ecu.py` - UDS service responder (0x22, 0x19)
- `test_uds.py` - pytest for both UDS services
- `diagnose.py` - UDS query + local LLM explanation
- `dtc_knowledge.py` - small DTC reference table

##### prompt engineering note

First version of the explainer prompt let the model guess technical details not in the knowledge base. For P0171 ("System Too Lean") it explained the mixture as "too rich" - backwards. Tightened the prompt to explicitly forbid inferring lean/rich beyond what's given, and it started answering correctly and consistently. Small example of why grounding + constraints matter for factual accuracy, not just style.

##### not done

Only handles one DTC at a time - a real response with multiple codes needs ISO-TP to split across frames, didn't get to that. DID numbers are made up for this project, not from a real manufacturer spec.
