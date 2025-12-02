import gradio as gr
import struct
import time
import html

# --- 1. ChaCha20 Logic ---

def rotl32(x, n):
    return ((x << n) & 0xffffffff) | (x >> (32 - n))

def quarter_round(x, a, b, c, d):
    x[a] = (x[a] + x[b]) & 0xffffffff
    x[d] ^= x[a]
    x[d] = rotl32(x[d], 16)

    x[c] = (x[c] + x[d]) & 0xffffffff
    x[b] ^= x[c]
    x[b] = rotl32(x[b], 12)

    x[a] = (x[a] + x[b]) & 0xffffffff
    x[d] ^= x[a]
    x[d] = rotl32(x[d], 8)

    x[c] = (x[c] + x[d]) & 0xffffffff
    x[b] ^= x[c]
    x[b] = rotl32(x[b], 7)
    return x

def make_initial_state(key, counter, nonce):
    constants = [0x61707865, 0x3320646e, 0x79622d32, 0x6b206574]
    key = (key + b'\0'*32)[:32]
    key_ints = list(struct.unpack('<8L', key))
    nonce = (nonce + b'\0'*12)[:12]
    nonce_ints = list(struct.unpack('<3L', nonce))
    return constants + key_ints + [counter] + nonce_ints

# --- 2. Visualization Helpers ---

def get_matrix_html(state, title, description, active_indices=None):
    if active_indices is None:
        active_indices = []
        
    html_content = f"""
    <div class="neon-container">
        <h2 style="margin-bottom: 5px;">{title}</h2>
        <p style="opacity: 0.8; margin-bottom: 15px;">{description}</p>
        <div class="matrix-grid">
    """
    
    labels = ["CONST"]*4 + ["KEY"]*8 + ["COUNT"] + ["NONCE"]*3
    
    for i in range(16):
        hex_val = f"{state[i]:08x}"
        style_class = "matrix-cell active" if i in active_indices else "matrix-cell"
        
        html_content += f"""
        <div class="{style_class}">
            <div class="cell-label">{i} ({labels[i]})</div>
            <div class="cell-val">{hex_val}</div>
        </div>
        """
    html_content += "</div></div>"
    return html_content

def get_xor_table_html(plaintext, keystream, ciphertext):
    html_content = """
    <div class="neon-container" style="margin-top: 20px;">
        <h2>🔐 Step 4: XOR Operation (Final)</h2>
        <table class="xor-table">
            <tr>
                <th>Char</th>
                <th>Plain (Hex)</th>
                <th>XOR</th>
                <th>KeyStream Byte</th>
                <th>=</th>
                <th>Cipher (Hex)</th>
            </tr>
    """
    decoded_text = []
    for b in plaintext:
        if 32 <= b <= 126:
            decoded_text.append(chr(b))
        else:
            decoded_text.append('.')

    for p_byte, k_byte, c_byte, char in zip(plaintext, keystream, ciphertext, decoded_text):
        html_content += f"""
        <tr>
            <td>{char}</td>
            <td>{p_byte:02x}</td>
            <td>⊕</td>
            <td>{k_byte:02x}</td>
            <td>=</td>
            <td style="color: #fff; font-weight: bold;">{c_byte:02x}</td>
        </tr>
        """
    html_content += "</table></div>"
    return html_content

# --- 3. Animation Generator ---

def run_chacha_demo(key_str, nonce_str, plain_str, speed):
    delay = float(speed)
    key_bytes = key_str.encode('utf-8')
    nonce_bytes = nonce_str.encode('utf-8')
    initial_state = make_initial_state(key_bytes, 1, nonce_bytes)
    state = list(initial_state)
    
    yield get_matrix_html(state, "🟢 Step 1: Initialization", "State matrix setup with Constants, Key, Counter, and Nonce.")
    time.sleep(delay * 2)
    
    column_rounds = [(0,4,8,12), (1,5,9,13), (2,6,10,14), (3,7,11,15)]
    diagonal_rounds = [(0,5,10,15), (1,6,11,12), (2,7,8,13), (3,4,9,14)]
    
    for r in range(0, 20, 2):
        msg = f"Round {r+1}/20: Column Mixing (Mixing columns vertically)"
        active_indices = [idx for grp in column_rounds for idx in grp]
        for indices in column_rounds:
            state = quarter_round(state, *indices)
        yield get_matrix_html(state, "🔄 Step 2: Rounds Loop", msg, active_indices)
        time.sleep(delay)

        msg = f"Round {r+2}/20: Diagonal Mixing (Mixing diagonals)"
        active_indices = [idx for grp in diagonal_rounds for idx in grp]
        for indices in diagonal_rounds:
            state = quarter_round(state, *indices)
        yield get_matrix_html(state, "🔄 Step 2: Rounds Loop", msg, active_indices)
        time.sleep(delay)
        
    final_keystream_ints = []
    for i in range(16):
        val = (state[i] + initial_state[i]) & 0xffffffff
        final_keystream_ints.append(val)
        
    yield get_matrix_html(final_keystream_ints, "➕ Step 3: Final Addition", "Added original state to mixed state to generate the Keystream Block.")
    time.sleep(delay * 2)
    
    keystream_bytes = struct.pack('<16L', *final_keystream_ints)
    pt_bytes = plain_str.encode('utf-8')[:64]
    ct_bytes = bytearray()
    
    for i in range(len(pt_bytes)):
        ct_bytes.append(pt_bytes[i] ^ keystream_bytes[i])
        
    final_html = get_matrix_html(final_keystream_ints, "✅ Encryption Complete", "Keystream generated.")
    final_html += get_xor_table_html(pt_bytes, keystream_bytes, ct_bytes)
    
    yield final_html

# --- 4. Python SVG Flowchart Generator ---

def generate_flowchart_svg():
    """
    Generates an SVG flowchart using pure Python string manipulation.
    This avoids external dependencies or JS issues.
    """
    # SVG Configuration
    width = 800
    height = 600
    box_w = 180
    box_h = 50
    center_x = width // 2
    
    # Colors (Neon Theme)
    c_stroke = "#39ff14"
    c_fill = "#111"
    c_text = "#39ff14"
    c_bg = "#050505"
    
    svg = f'<svg width="100%" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="background-color:{c_bg}; font-family: monospace;">'
    
    # Helper to draw box
    def draw_box(x, y, text, dashed=False):
        stroke_dash = 'stroke-dasharray="5,5"' if dashed else ''
        return f"""
        <rect x="{x - box_w//2}" y="{y}" width="{box_w}" height="{box_h}" rx="10" fill="{c_fill}" stroke="{c_stroke}" stroke-width="2" {stroke_dash} />
        <text x="{x}" y="{y + box_h//2 + 5}" fill="{c_text}" text-anchor="middle" font-size="14">{text}</text>
        """

    # Helper to draw arrow
    def draw_arrow(x1, y1, x2, y2, label=""):
        marker = f"""
        <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="{c_stroke}" />
            </marker>
        </defs>
        """
        line = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c_stroke}" stroke-width="2" marker-end="url(#arrowhead)" />'
        txt = f'<text x="{(x1+x2)//2 + 5}" y="{(y1+y2)//2}" fill="#fff" font-size="12">{label}</text>' if label else ""
        return marker + line + txt

    # Draw Nodes
    y_start = 20
    gap = 80
    
    # Inputs
    svg += draw_box(center_x - 200, y_start, "Key (256-bit)")
    svg += draw_box(center_x, y_start, "Nonce (96-bit)")
    svg += draw_box(center_x + 200, y_start, "Counter (32-bit)")
    
    # Initial State
    y_state = y_start + gap
    svg += draw_box(center_x, y_state, "Initial State (4x4)")
    
    # Arrows to State
    svg += draw_arrow(center_x - 200, y_start + box_h, center_x - 20, y_state)
    svg += draw_arrow(center_x, y_start + box_h, center_x, y_state)
    svg += draw_arrow(center_x + 200, y_start + box_h, center_x + 20, y_state)
    
    # Rounds Loop
    y_loop = y_state + gap
    svg += draw_box(center_x, y_loop, "20 Rounds Loop", dashed=True)
    svg += draw_arrow(center_x, y_state + box_h, center_x, y_loop)
    
    # Inner Rounds (visualized as side steps)
    y_rounds = y_loop + gap
    svg += draw_box(center_x - 120, y_rounds, "Column Rounds")
    svg += draw_box(center_x + 120, y_rounds, "Diagonal Rounds")
    
    # Arrows for rounds
    svg += draw_arrow(center_x, y_loop + box_h, center_x - 120, y_rounds)
    svg += draw_arrow(center_x, y_loop + box_h, center_x + 120, y_rounds)
    svg += draw_arrow(center_x - 120, y_rounds + box_h, center_x, y_rounds + box_h + 40)
    svg += draw_arrow(center_x + 120, y_rounds + box_h, center_x, y_rounds + box_h + 40)
    
    # Add Initial State
    y_add = y_rounds + gap + 20
    svg += draw_box(center_x, y_add, "Add Initial State")
    svg += draw_arrow(center_x, y_rounds + box_h + 40, center_x, y_add) # from loop exit
    
    # Keystream
    y_key = y_add + gap
    svg += draw_box(center_x, y_key, "Keystream Block")
    svg += draw_arrow(center_x, y_add + box_h, center_x, y_key)
    
    # XOR
    y_xor = y_key + gap
    svg += draw_box(center_x, y_xor, "XOR with Plaintext")
    svg += draw_arrow(center_x, y_key + box_h, center_x, y_xor)
    
    # Ciphertext
    y_final = y_xor + gap
    svg += f'<circle cx="{center_x}" cy="{y_final + 25}" r="35" fill="{c_stroke}" />'
    svg += f'<text x="{center_x}" y="{y_final + 30}" fill="#000" text-anchor="middle" font-weight="bold">Cipher</text>'
    svg += draw_arrow(center_x, y_xor + box_h, center_x, y_final)

    svg += "</svg>"
    return svg

# --- 5. UI Setup ---

# Fixed CSS for input boxes (added height/padding)
css_styles = """
<style>
body, .gradio-container { background-color: #050505 !important; font-family: 'Courier New', monospace; }
h1, h2, span, p, label { color: #39ff14 !important; }

/* Fixed Input Styling - Height and Padding increased */
input, textarea, .gr-input, .gr-box, .gr-form { 
    background-color: #111 !important; 
    border: 1px solid #39ff14 !important; 
    color: #39ff14 !important;
    min-height: 50px !important; /* Fix for shrinking */
    padding: 10px !important;    /* Fix for text cut-off */
    font-size: 16px !important;
}

button.primary-btn { background-color: #39ff14 !important; color: #000 !important; font-weight: bold !important; border: none !important; }

/* Neon Helpers */
.neon-container { border: 1px solid #39ff14; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(57, 255, 20, 0.2); background-color: #0a0a0a; }
.matrix-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 15px; }
.matrix-cell { background-color: #111; border: 1px solid #333; padding: 10px; text-align: center; border-radius: 4px; transition: all 0.3s ease; }
.matrix-cell.active { border-color: #39ff14; box-shadow: 0 0 15px #39ff14; transform: scale(1.02); }
.cell-label { font-size: 0.7em; color: #888; }
.cell-val { font-size: 1.1em; font-weight: bold; color: #39ff14; }
.xor-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
.xor-table th, .xor-table td { border: 1px solid #333; padding: 8px; text-align: center; color: #39ff14; }
.xor-table th { border-bottom: 2px solid #39ff14; }
</style>
"""

# Info Text for Tab 3
about_text = """
## ℹ️ What is ChaCha20?

**ChaCha20** is a stream cipher developed by Daniel J. Bernstein. It is a modification of the Salsa20 cipher, designed to provide better diffusion and resistance to cryptanalysis while maintaining high performance.

### 🔑 Key Components:
1.  **State Matrix**: A 4x4 grid of 32-bit words (16 words total).
    * **Words 0-3**: Constants ("expand 32-byte k").
    * **Words 4-11**: The 256-bit Key (User provided).
    * **Word 12**: Block Counter (Starts at 1, increments for each block).
    * **Words 13-15**: The 96-bit Nonce (Unique per message).

### 🔄 The Algorithm Steps:
1.  **Initialization**: The state is populated with the constants, key, counter, and nonce.
2.  **Rounds (Mixing)**: The state undergoes 20 rounds of mixing.
    * **Column Rounds**: Mixes the 4 columns vertically.
    * **Diagonal Rounds**: Mixes the diagonals.
    * *The "Quarter Round" operation involves Addition, XOR, and Bitwise Rotation (ARX).*
3.  **Finalize**: The original initial state is added (modulo 2^32) to the scrambled state. This makes the process irreversible.
4.  **Keystream**: The result is the "Keystream Block".
5.  **Encryption**: The Plaintext is **XORed** with this Keystream to produce Ciphertext.

### 🚀 Why use it?
* **Speed**: It is extremely fast in software, often faster than AES on platforms without dedicated AES hardware (like mobile phones).
* **Security**: Used by Google (TLS), Cloudflare, and in protocols like SSH and WireGuard.
"""

with gr.Blocks() as demo:
    gr.HTML(css_styles)
    gr.Markdown("# 🔐 ChaCha20 Algo Visualizer")
    
    with gr.Tabs():
        # --- TAB 1: EXECUTION ---
        with gr.TabItem("▶️ Run Algorithm"):
            with gr.Row():
                with gr.Column(scale=1):
                    t_key = gr.Textbox(label="Key (32 chars max)", value="SecretKey1234567890123456789012")
                    t_nonce = gr.Textbox(label="Nonce", value="Nonce123")
                    t_plain = gr.Textbox(label="Plaintext", value="Hello Gradio!")
                    t_speed = gr.Slider(0.1, 2.0, value=0.5, label="Step Delay (Seconds)")
                    btn_run = gr.Button("Start Visualization", elem_classes=["primary-btn"])
                
                with gr.Column(scale=2):
                    out_display = gr.HTML(label="Visual Output")
            
            btn_run.click(fn=run_chacha_demo, inputs=[t_key, t_nonce, t_plain, t_speed], outputs=out_display)

        # --- TAB 2: FLOWCHART ---
        with gr.TabItem("📊 Flowchart"):
            gr.Markdown("### ChaCha20 Process Flow (Generated by Python)")
            # Direct Python-to-SVG call
            gr.HTML(value=generate_flowchart_svg())

        # --- TAB 3: INFO ---
        with gr.TabItem("ℹ️ About ChaCha20"):
            gr.Markdown(about_text)

if __name__ == "__main__":
    demo.queue().launch()
