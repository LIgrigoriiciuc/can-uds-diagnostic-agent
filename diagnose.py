import can
import ollama
from dtc_knowledge import DTC_KNOWLEDGE

SID_READ_DTC = 0x19
SUBFUNC_REPORT_DTC_BY_STATUS_MASK = 0x02
REQUEST_ID  = 0x7E0
RESPONSE_ID = 0x7E8

def read_dtcs_from_ecu():
    bus = can.interface.Bus(channel='vcan0', interface='socketcan')
    request_data = [SID_READ_DTC, SUBFUNC_REPORT_DTC_BY_STATUS_MASK, 0xFF, 0, 0, 0, 0, 0]
    msg = can.Message(arbitration_id=REQUEST_ID, data=request_data, is_extended_id=False)
    bus.send(msg)

    response = bus.recv(timeout=2.0)
    bus.shutdown()

    if response is None or response.data[0] != 0x59:
        return []

    codes = []
    payload = response.data[3:]
    for i in range(0, len(payload) - 2, 3):
        code = (payload[i] << 8) | payload[i + 1]
        if code != 0:
            codes.append(code)
    return codes

def explain_dtc(code):
    info = DTC_KNOWLEDGE.get(code)
    if info is None:
        return f"No local knowledge base entry for code {hex(code)}."

    prompt = f"""You are a car diagnostic assistant. Explain this fault code to a car owner in plain, non-technical English.

Code: {info['code']} - {info['description']}
Common causes: {', '.join(info['common_causes'])}

Do not add technical details beyond what's given above. Do not guess whether the mixture is "rich" or "lean" beyond what the description states. Give a short, friendly explanation (3-4 sentences) of what this means and what they should do next."""
    response = ollama.generate(model='llama3.2', prompt=prompt)
    return response['response']

if __name__ == "__main__":
    print("Querying ECU for active DTCs over UDS...")
    codes = read_dtcs_from_ecu()

    if not codes:
        print("No active DTCs reported.")
    else:
        for code in codes:
            print(f"\n--- {hex(code)} ---")
            explanation = explain_dtc(code)
            print(explanation)
