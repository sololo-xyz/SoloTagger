# SoloTagger

## Official website: sololo.xyz

### SoloTagger is an LLM-based image captioning tool.

SoloTagger is just a simple Python script with two basic functions:

1. Send images and tagging instructions to **LLM**.
2. Receive the output from LLM and save it into a TXT file.

SoloTagger itself does **not** run the model. It relies on a third-party LLM runtime and has currently been tested with **LM Studio on Windows 11**. Ollama should also work, but it hasn’t been tested.

If you want to connect to a **remote API**, you’ll need to make a simple modification to the script to add the **API key**.

## Installation and Usage
### Download

Clone the repository:

```git clone https://github.com/sololo-xyz/SoloTagger.git```

### Run

Navigate to the SoloTagger directory, then start SoloTagger with:

```python SoloTagger.py```

So SoloTagger does not include unnecessary third-party libraries just for convenience. It has **zero external dependencies**. As long as you have Python installed, you can run it.

For installation and usage details, please refer to the documentation:

https://sololo.xyz/article/24-solotagger-local-joycaption-beta-one-gguf-setup-on-windows-via-lm-studio

For prompt editing, please refer to the documentation:

https://sololo.xyz/article/25-solotagger-v012-easier-prompt-editing



## Usage Notes

Because I often create **LoRAs for text-to-image models**, I frequently need to generate **caption files** for images. At the moment, **SoloTagger** is the main captioning tool I use.

My LoRA works can be browsed and downloaded from my website:  [sololo.xyz](https://sololo.xyz/)

SoloTagger is currently designed mainly for **small LLMs that can run locally**, such as the **Qwen3.5 series** and **JoyCaption**. My personal recommendations are:

- **Qwen3.5 9B GGUF**
- **JoyCaption beta one GGUF**

These two small models provide a good balance of **speed and output quality** on my laptop.

My laptop specs are: **RTX 5060 (8GB VRAM)** and **32GB RAM**. If your hardware is more powerful, you can choose **larger models** for better results.
