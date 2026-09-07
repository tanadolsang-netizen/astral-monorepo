# ComfyUI Local Setup on Windows (NVIDIA)

## Hardware Requirements
- NVIDIA GPU with ≥6 GB VRAM (≥8 GB for SDXL)
- RTX 5060 8GB: SDXL comfortable, Flux possible with optimizations

## Installation
```bash
pipx install comfy-cli
comfy --skip-prompt install --nvidia
comfy --skip-prompt launch --background
```

## Model Downloads

### SDXL (~6.5 GB)
```bash
comfy model download \
  --url "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors" \
  --relative-path models/checkpoints
```

### SDXL VAE (required for SDXL workflows)
```bash
comfy model download \
  --url "https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors" \
  --relative-path models/vae
```

### SD 1.5 (~4 GB, lighter)
```bash
comfy model download \
  --url "https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors" \
  --relative-path models/checkpoints
```

## Direct REST API (More Reliable Than Scripts)

The `run_workflow.py` scripts can fail with 500 errors due to template format issues.
Direct REST API is more reliable:

```python
import json, urllib.request

workflow = {
    '4': {'inputs': {'ckpt_name': 'sd_xl_base_1.0.safetensors'}, 'class_type': 'CheckpointLoaderSimple'},
    '6': {'inputs': {'text': 'your prompt here', 'clip': ['4', 1]}, 'class_type': 'CLIPTextEncode'},
    '7': {'inputs': {'text': 'bad quality, blurry', 'clip': ['4', 1]}, 'class_type': 'CLIPTextEncode'},
    '5': {'inputs': {'width': 512, 'height': 512, 'batch_size': 1}, 'class_type': 'EmptyLatentImage'},
    '3': {'inputs': {'seed': 42, 'steps': 30, 'cfg': 7, 'sampler_name': 'dpmpp_2m', 'scheduler': 'karras', 'denoise': 1, 'model': ['4', 0], 'positive': ['6', 0], 'negative': ['7', 0], 'latent_image': ['5', 0]}, 'class_type': 'KSampler'},
    '8': {'inputs': {'samples': ['3', 0], 'vae': ['4', 2]}, 'class_type': 'VAEDecode'},
    '9': {'inputs': {'filename_prefix': 'output', 'images': ['8', 0]}, 'class_type': 'SaveImage'}
}

payload = json.dumps({'prompt': workflow}).encode()
req = urllib.request.Request('http://127.0.0.1:8188/api/prompt', data=payload, headers={'Content-Type':'application/json'})
resp = urllib.request.urlopen(req, timeout=30)
print('Status:', resp.status)
```

## Critical: Workflow JSON Format

**`_meta` must be a dict, not a string:**
```python
# CORRECT
'_meta': {'title': 'Load Checkpoint'}

# WRONG (causes AttributeError: 'str' object has no attribute 'get')
'_meta': 'Load Checkpoint'
```

**SDXL requires VAEDecode between KSampler and SaveImage:**
```
KSampler → VAEDecode → SaveImage
```

Without VAEDecode: `Return type mismatch: received_type(LATENT) mismatch input_type(IMAGE)`

## Output Location
Default: `~/Documents/comfy/ComfyUI/output/`

## Hardware Check
```bash
python scripts/hardware_check.py --json
```
