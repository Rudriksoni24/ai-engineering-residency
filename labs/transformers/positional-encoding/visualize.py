import torch
import matplotlib.pyplot as plt
from positional_encoding import positional_encoding

def generate_pe_heatmap():
    # 1. Choose sequence length and hidden dimension parameters 
    # High dimensions make it easy to see wave pattern decay/frequencies
    SEQUENCE_LENGTH = 100
    D_MODEL = 512

    print(f"📊 Generating Positional Encoding Matrix... Shape: ({SEQUENCE_LENGTH}x{D_MODEL})")
    
    # 2. Compute the deterministic matrix using your imported function
    pe_matrix = positional_encoding(sequence_length=SEQUENCE_LENGTH, d_model=D_MODEL)
    
    # 3. Initialize and configure the plot layout
    plt.figure(figsize=(12, 8), dpi=150)
    
    # Using a diverging colormap ('RdBu') to clearly isolate positive vs negative values
    # We transpose the matrix to match your requested layout: Dimension on Y, Position on X
    heatmap = plt.pcolormesh(pe_matrix.t().numpy(), cmap='RdBu', vmin=-1.0, vmax=1.0)
    
    # 4. Set visual and functional anchors
    plt.title("Sinusoidal Positional Encoding Wavefront Space", fontsize=14, pad=15, weight='bold')
    plt.xlabel("Token Position (sequence_length) ───>", fontsize=11, labelpad=10)
    plt.ylabel("Embedding Dimension (d_model) ───>", fontsize=11, labelpad=10)
    
    # Add colorbar indicator
    cbar = plt.colorbar(heatmap, pad=0.02)
    cbar.set_label("Encoding Intensity Value (Sine/Cosine)", fontsize=10)
    
    # Grid formatting for better clarity
    plt.grid(False) 
    
    # 5. Export structural image asset to disk
    output_filename = "positional_encoding.png"
    plt.savefig(output_filename, bbox_inches='tight')
    plt.close()
    
    print(f"🎨 Wavefront chart successfully exported and saved as: {output_filename}")
    print("💡 Observation Note: Look at the top vs bottom rows. Lower dimensions (bottom) show high-frequency waves, while higher dimensions (top) stabilize into longer wavelengths.")

if __name__ == "__main__":
    generate_pe_heatmap()
