# SoloTagger v0.20 Modified | Original work by Solo | https://sololo.xyz
# Detailed Documentation: https://sololo.xyz/article/24
# Update date: 20260313

import os
import re
import base64
import json
import ctypes
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

CONFIG_FILE = "config.json"
PROMPT_FILE = "prompt.txt"
DEFAULT_TEMPERATURE = 0.0
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"


def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_image_data_url(image_path, image_base64):
    ext = os.path.splitext(image_path)[1].lower()
    mime_type = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(ext, "image/jpeg")
    return f"data:{mime_type};base64,{image_base64}"


def enable_ansi_colors():
    if os.name != "nt":
        return
    try:
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        pass


def print_error(message):
    print(f"{RED}{message}{RESET}")


def print_warning(message):
    print(f"{YELLOW}{message}{RESET}")


def print_success(message):
    print(f"{GREEN}{message}{RESET}")


def pause_for_user(message="Press Enter to exit..."):
    try:
        input(message)
    except EOFError:
        pass


def print_completion_report(report):
    print("\n" + "=" * 40)
    print("Run report")
    status = report.get("status", "Unknown")
    if status == "Completed":
        print_success(f"Status: {status}")
    else:
        print_error(f"Status: {status}")

    image_folder = report.get("image_folder")
    if image_folder:
        print(f"Image folder: {image_folder}")

    model = report.get("model")
    if model:
        print(f"Model: {model}")

    if "total_images" in report:
        print(f"Images found: {report['total_images']}")
    if "pending_images" in report:
        pending_images = report["pending_images"]
        if pending_images > 0:
            print_warning(f"Pending images: {pending_images}")
        else:
            print(f"Pending images: {pending_images}")
    if "skipped_images" in report:
        skipped_images = report["skipped_images"]
        if skipped_images > 0:
            print_warning(f"Skipped existing tags: {skipped_images}")
        else:
            print(f"Skipped existing tags: {skipped_images}")
    if "success_count" in report:
        success_count = report["success_count"]
        if success_count > 0:
            print_success(f"Processed successfully: {success_count}")
        else:
            print_error(f"Processed successfully: {success_count}")
    if "failed_count" in report:
        failed_count = report["failed_count"]
        if failed_count > 0:
            print_error(f"Failed: {failed_count}")
        else:
            print_success(f"Failed: {failed_count}")

    message = report.get("message")
    if message:
        if status == "Completed":
            print_success(message)
        else:
            print_error(message)

    print("=" * 40)


def load_prompts(base_dir):
    prompt_path = os.path.join(base_dir, PROMPT_FILE)
    if not os.path.exists(prompt_path):
        print_error(f"Error: prompt file not found: {prompt_path}")
        return None

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
    except Exception as e:
        print_error(f"Error: failed to read prompt file: {e}")
        return None

    title_pattern = re.compile(r"^==(.+)==$", re.MULTILINE)
    matches = list(title_pattern.finditer(raw_text))

    if not matches:
        print_error("Error: no prompt sections found in prompt.txt.")
        return None

    prompts = []
    for i, match in enumerate(matches):
        title = match.group(1).strip()
        content_start = match.end()
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(raw_text)
        content = raw_text[content_start:content_end].strip()
        if content:
            prompts.append({"title": title, "text": content})

    return prompts


def escape_prompt_text(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    return "\n".join(lines)


def load_config(base_dir):
    config_path = os.path.join(base_dir, CONFIG_FILE)
    if not os.path.exists(config_path):
        print_error(f"Error: config file not found: {config_path}")
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        print_error(f"Error: failed to load config file: {e}")
        return None

    return config


def check_api_access(api_url, timeout=2):
    req = Request(api_url, method="GET")
    try:
        with urlopen(req, timeout=timeout):
            return True
    except HTTPError:
        return True
    except:
        return False


def derive_models_url(api_url):
    marker = "/chat/completions"
    if marker not in api_url:
        return None
    return api_url.split(marker)[0] + "/models"


def fetch_available_model_ids(models_url, timeout=5):
    req = Request(models_url, method="GET")
    try:
        with urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8")
        data = json.loads(body)
    except Exception:
        return None

    model_ids = set()
    for item in data.get("data", []):
        if isinstance(item, dict):
            model_id = item.get("id")
            if isinstance(model_id, str) and model_id.strip():
                model_ids.add(model_id)
    return model_ids


def post_json(api_url, payload, timeout=120):
    data = json.dumps(payload).encode("utf-8")
    req = Request(
        api_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=timeout) as response:
        response_text = response.read().decode("utf-8")
    return json.loads(response_text)


def select_config_item(display_name, options):
    if len(options) == 1: return options[0]
    print(f"\nPlease select {display_name}:")
    for i, item in enumerate(options, start=1):
        print(f"{i}. {item.get('title')}")
    while True:
        choice = input(f"Enter number (1-{len(options)}, default 1): ").strip()
        if choice == "": return options[0]
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]


def select_simple_option(display_name, options):
    if len(options) == 1: return options[0]
    print(f"\nPlease select {display_name}:")
    for i, item in enumerate(options, start=1):
        print(f"{i}. {item}")
    while True:
        choice = input(f"Enter number (1-{len(options)}, default 1): ").strip()
        if choice == "": return options[0]
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]


def select_model(models):
    model_items = list(models.items())
    if len(model_items) == 1: return model_items[0][1]
    print("\nPlease select a model:")
    for key, value in model_items:
        print(f"{key}. {value}")
    while True:
        choice = input("Enter number (default 1): ").strip()
        if choice == "": return model_items[0][1]
        if choice in models: return models[choice]


def resolve_path(base_dir, maybe_relative_path):
    if os.path.isabs(maybe_relative_path): return maybe_relative_path
    return os.path.normpath(os.path.join(base_dir, maybe_relative_path))


def main():
    enable_ansi_colors()
    report = {
        "status": "Failed",
        "success_count": 0,
        "failed_count": 0,
    }
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config = load_config(base_dir)
    if config is None:
        report["message"] = "Configuration could not be loaded."
        return report

    prompts = load_prompts(base_dir)
    if prompts is None:
        report["message"] = "Prompt data could not be loaded."
        return report

    image_folder_item = select_simple_option("image folder", config["image_folders"])
    target_model = select_model(config["models"])
    prompt_item = select_config_item("Prompt", prompts)

    image_folder = resolve_path(base_dir, image_folder_item)
    api_url = config["API_URL"]
    prompt_text = escape_prompt_text(prompt_item["text"])
    report["image_folder"] = image_folder
    report["model"] = target_model

    if not os.path.isdir(image_folder):
        print_error(f"Error: folder does not exist: {image_folder}")
        report["message"] = f"Folder does not exist: {image_folder}"
        return report

    files = [f for f in os.listdir(image_folder) if f.lower().endswith(IMAGE_EXTENSIONS)]
    available_files = [f for f in files if not os.path.exists(os.path.join(image_folder, f"{os.path.splitext(f)[0]}.txt"))]
    report["total_images"] = len(files)
    report["pending_images"] = len(available_files)
    report["skipped_images"] = len(files) - len(available_files)

    if not available_files:
        print_warning("No new images to process.")
        report["status"] = "No work"
        report["message"] = "No new images to process."
        return report

    print(f"Processing {len(available_files)} images with model: {target_model}\n")

    for index, file in enumerate(available_files):
        img_path = os.path.join(image_folder, file)
        txt_path = os.path.join(image_folder, f"{os.path.splitext(file)[0]}.txt")

        try:
            img_base64 = encode_image(img_path)
            image_data_url = get_image_data_url(img_path, img_base64)

            
            payload = {
                "model": target_model,
                "messages": [
                    {
                        "role": "system",
                        "content": prompt_text
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": image_data_url}},
                            {"type": "text", "text": "Please tag this image."}
                        ]
                    }
                ],
                "temperature": DEFAULT_TEMPERATURE
            }

            print(f"[{index+1}/{len(available_files)}] Processing: {file}")
            response_data = post_json(api_url, payload, timeout=120)
            tags = response_data["choices"][0]["message"]["content"].strip()

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(tags)
            report["success_count"] += 1
            report["pending_images"] -= 1

        except Exception as e:
            print_error(f"Error processing {file}: {e}")
            report["failed_count"] += 1

    report["status"] = "Completed" if report["failed_count"] == 0 else "Completed with errors"
    report["message"] = "Task completed!"
    print("\nTask completed!")
    return report


if __name__ == "__main__":
    try:
        report = main()
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        report = {
            "status": "Failed",
            "success_count": 0,
            "failed_count": 0,
            "message": f"Unexpected error: {e}",
        }

    print_completion_report(report)
    pause_for_user()
